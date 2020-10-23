web: gunicorn PriceScraperInterface.PriceScraperInterface.wsgi 
python ./PriceScraperInterface/manage.py collectstatic --noinput
./PriceScraperInterface/manage.py migrate
