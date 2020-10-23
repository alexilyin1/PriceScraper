web: gunicorn PriceScraper.PriceScraperInterface.wsgi --log-file 
python ./PriceScraperInterface/manage.py collectstatic --noinput
./PriceScraperInterface/manage.py migrate
