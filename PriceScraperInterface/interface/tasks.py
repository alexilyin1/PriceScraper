import os
import csv
import bs4
import requests
from io import StringIO
import regex as re
import pandas as pd
from .keys import API
from .celery import app
from .db_scripts import RequestDB, FileDB
from usp.tree import sitemap_tree_for_homepage
from geopy.geocoders import Nominatim
from interruptingcow import timeout
from django.core.mail import EmailMessage
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)


def dealer_urls(car_make: str, model: str, zip_code: int, dist_range: int = 100, min_stars: int = 4, prices_arg='full'):
    api = API
    url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?'
    geoloc = Nominatim(user_agent="PriceScraper")

    try:
        lat = geoloc.geocode({'postalcode': zip_code})[1][0]
        long = geoloc.geocode({'postalcode': zip_code})[1][1]
    except:
        raise ValueError(str(zip_code) + ' is not a valid zip code, try again with an existing zip code')

    r = requests.get(url + 'query=' + car_make + '+Dealerships&location=' + str(lat) + ',' + str(long) + '&radius=' + str(dist_range) + '&key=' + api)
    ids = [res['place_id'] for res in r.json()['results']]
    print('Found ' + str(len(ids)) + ' matching ' + car_make + ' dealerships within ' + str(dist_range) + ' miles of ' + str(zip_code))

    url2 = 'https://maps.googleapis.com/maps/api/place/details/json?'
    print('Getting urls for matching ' + car_make + ' Dealers....')

    url_list = []
    for place_id in ids:
        try:
            request = requests.get(url2 + 'place_id=' + place_id + '&fields=name,rating,website' + '&key=' + api).json()
            print([request['result']['name'], request['result']['rating'], request['result']['website'].split('/')[2]])
            url_list.append([request['result']['name'], request['result']['rating'], request['result']['website'].split('/')[2]])
        except:
            pass

    # url_list = [[requests.get(url2 + 'place_id=' + place_id + '&fields=name,rating,website' + '&key=' + api).json()['result']['name'], requests.get(url2 + 'place_id=' + place_id + '&fields=name,rating,website' + '&key=' + api).json()['result']['rating'], 'https://' + requests.get(url2 + 'place_id=' + place_id + '&fields=name,rating,website' + '&key=' + api).json()['result']['website'].split('/')[2]] for place_id in ids if 'rating' in requests.get(url2 + 'place_id=' + place_id + '&fields=name,rating,website' + '&key=' + api).json()['result'] and 'website' in requests.get(url2 + 'place_id=' + place_id + '&fields=name,rating,website' + '&key=' + api).json()['result'] and car_make.lower() in requests.get(url2 + 'place_id=' + place_id + '&fields=name,rating,website' + '&key=' + api).json()['result']['website'].lower()]

    url_df = pd.DataFrame(url_list, columns=['Dealership Name', 'Rating', 'URL'])
    url_df = url_df[url_df['Rating'] >= min_stars]
    if len(url_df) == 0:
        raise ValueError('Too few rows remaining after filter. Try changing the minimum star rating for dealerships')

    sitemap = []
    for row in range(len(url_df)):
        url = url_df.iloc[row]['URL']
        if 'https' not in url:
            tree = sitemap_tree_for_homepage('https://' + url.replace('http://', ''))
        else:
            tree = sitemap_tree_for_homepage(url)

        try:
            with timeout(400, exception=RuntimeError):
                each = []
                for page in tree.all_pages():
                    if model.lower() in page.url.lower() and ('new' in page.url.lower() or 'inventory' in page.url.lower()):
                        each.append(page.url)
                    else:
                        pass
                sitemap.append(each)
        except RuntimeError as e:
            sitemap.append([])

    url_df['Sitemap'] = sitemap
    url_df = url_df[url_df['Sitemap'].str.len() > 0]

    prices_index = (1 if prices_arg == 'full' else 3)
    prices = []
    for i in range(len(url_df)):
        site = url_df.iloc[i]['Sitemap']
        for url in site:
            page = requests.get(url)
            soup = bs4.BeautifulSoup(page.content, 'html.parser')

            try:
                name = soup.find_all(text=re.compile('[0-9]{4} ' + car_make + ' ' + model + ' [A-Z|a-z]{1,10}'))
                price = [int(str(x).strip('$').replace(',', '')) for x in soup.find_all(text=re.compile('^\$[0-9]{2}\,[0-9]{3}'))]

                if len(price) == 0:
                    break

                if len(name[0]) > 120:
                    j = 1
                    while j < len(name):
                        if len(name[j]) > 120:
                            j += 1
                        else:
                            prices.append([url_df.iloc[i]['Dealership Name'], name[j], sorted(price[:prices_index]), url])
                            print('Getting price for a ' + name[j])
                            break
                    prices.append([url_df.iloc[i]['Dealership Name'], car_make + ' ' + model, sorted(price[:prices_index]), url])
                else:
                    print('Getting price for a ' + name[0])
                    prices.append([url_df.iloc[i]['Dealership Name'], name[0], sorted(price[:prices_index]), url])
            except Exception as e:
                print(e)
                pass

    prices_dat = pd.DataFrame(prices, columns=['Dealership Name', 'Model', 'Prices', 'URL'])

    if prices_arg == 'full':
        prices_dat = prices_dat[prices_dat['Prices'].str.len() > 2]
        prices_dat['Prices_MSRP'] = [x[2] for x in prices_dat['Prices']]
        prices_dat['Prices_First_Discount'] = [x[1] for x in prices_dat['Prices']]
        prices_dat['Prices_Final_Discount'] = [x[0] for x in prices_dat['Prices']]
        prices_dat = prices_dat.drop('Prices', axis=1)

    else:
        prices_dat['Prices_MSRP'] = [x[0] for x in prices_dat['Prices']]
        prices_dat = prices_dat.drop('Prices', axis=1)

    prices_dat.to_csv(os.path.join(os.path.abspath('.'), 'interface/static/interface/user_files/') + car_make + '_' + model + '_' + 'within_' + str(dist_range) + '_miles_of_' + str(zip_code) + '_' + '_prices_' + prices_arg + '.csv', index=False)


@app.task
def email_task(car_make: str, model: str, zip_code: int, dist_range: int, min_stars: int, recipient, prices_arg):
    dealer_urls(car_make, model, zip_code, dist_range, min_stars, prices_arg)

    dat = pd.read_csv(os.path.join(os.path.abspath('.'), 'interface/static/interface/user_files/') + car_make + '_' + model + '_' + 'within_' + str(dist_range) + '_miles_of_' + str(zip_code) + '_' + '_prices_' + prices_arg + '.csv').sort_values(['Dealership Name', 'Model'])

    rdb = RequestDB()
    fdb = FileDB()

    if prices_arg == 'full':
        id = rdb.GetID(recipient)[0][0]
        if len(fdb.GetUserCSV(id)) == 0:
            fdb.InsertFile(os.path.join(os.path.abspath('.'), 'interface/static/interface/user_files/' + car_make + '_' + model + '_' + 'within_' + str(dist_range) + '_miles_of_' + str(zip_code) + '_' + '_prices.csv'))

        previous_csv = fdb.GetUserCSV(id).sort_values(['Dealership Name', 'Model'])

        csvfile = StringIO()
        cols = dat.columns

        writer = csv.DictWriter(csvfile, fieldnames=cols)
        writer.writeheader()
        writer.writerows(dat.to_dict('r'))

        if dat.equals(previous_csv):
            email_sub = 'PriceScraper - No changes from previous run',
            email_txt = recipient + ' - There were no changes from the previous run for ' + car_make + ' ' + model + "'s within " + str(dist_range) + " of " + str(zip_code) + ". Visit the Price Scraper UI if you would like to edit the details captured in your report."
            email = EmailMessage(email_sub, email_txt, 'pricescraper@gmail.com', [recipient])
            email.attach(car_make+'_'+model+'_'+str(zip_code)+'_prices.csv',
                         csvfile.getvalue(),
                         'text/csv')
            email.send()
        else:
            avg_msrp = dat['Prices_MSRP'].mean()
            avg_first_discount = dat['Prices_First_Discount'].mean()
            avg_final_discount = dat['Prices_Final_Discount'].mean()

            diff = ", ".join(list(map(" - ".join, zip([x for x in dat['Model'].unique() if x not in previous_csv['Model'].unique()],
                                                      [x for x in dat['URL'].unique() if x not in previous_csv['URL'].unique()]))))

            email_sub = 'PriceScraper - New ' + car_make + ' ' + model + "'s found!",
            try:
                email_txt = recipient + ' - Here are the new ' + car_make + ' ' + model + "'s found within " + \
                            str(dist_range) + " of " + str(zip_code) + ". " + diff + ". " + \
                            "Average MSRP price - " + str(int(avg_msrp)) + "\n" + \
                            "Average First Discount price " + str(int(avg_first_discount)) + "\n" + \
                            "Average Final Discount price " + str(int(avg_final_discount)) + "\n" + \
                            "See the rest of the details attached below."
            except:
                raise ValueError('No valid prices returned, check your input and try again')
            email = EmailMessage(email_sub, email_txt, 'pricescraper@gmail.com', [recipient])
            email.attach(car_make + '_' + model + '_' + str(zip_code) + '_prices.csv',
                         csvfile.getvalue(),
                         'text/csv')
            email.send()
    else:
        id = rdb.GetID(recipient)[0][0]
        if len(fdb.GetUserCSV(id)) == 0:
            fdb.InsertFileAlt(os.path.join(os.path.abspath('.'), 'interface/static/interface/user_files/' + car_make + '_' + model + '_' + 'within_' + str(dist_range) + '_miles_of_' + str(zip_code) + '_' + '_prices.csv'))

        previous_csv = fdb.GetUserCSV(id).sort_values(['Dealership Name', 'Model'])

        csvfile = StringIO()
        cols = dat.columns

        writer = csv.DictWriter(csvfile, fieldnames=cols)
        writer.writeheader()
        writer.writerows(dat.to_dict('r'))

        if dat.equals(previous_csv):
            email_sub = 'PriceScraper - No changes from previous run',
            email_txt = recipient + ' - There were no changes from the previous run for ' + car_make + ' ' + model + "'s within " + str(dist_range) + " of " + str(zip_code) + ". Visit the Price Scraper UI if you would like to edit the details captured in your report."
            email = EmailMessage(email_sub, email_txt, 'pricescraper@gmail.com', [recipient])
            email.attach(car_make + '_' + model + '_' + str(zip_code) + '_prices.csv',
                         csvfile.getvalue(),
                         'text/csv')
            email.send()
        else:
            avg_msrp = dat['Prices_MSRP'].mean()

            diff = ", ".join(
                list(map(" - ".join, zip([x for x in dat['Model'].unique() if x not in previous_csv['Model'].unique()],
                                         [x for x in dat['URL'].unique() if x not in previous_csv['URL'].unique()]))))

            email_sub = 'PriceScraper - New ' + car_make + ' ' + model + "'s found!",
            try:
                email_txt = recipient + ' - Here are the new ' + car_make + ' ' + model + "'s found within " + \
                            str(dist_range) + " of " + str(zip_code) + ". " + diff + ". " + \
                            "Average MSRP price - " + str(int(avg_msrp)) + "\n" + \
                            "See the rest of the details attached below."
            except:
                raise ValueError('No valid prices returned, check your input and try again')
            email = EmailMessage(email_sub, email_txt, 'pricescraper@gmail.com', [recipient])
            email.attach(car_make + '_' + model + '_' + str(zip_code) + '_prices.csv',
                         csvfile.getvalue(),
                         'text/csv')
            email.send()
