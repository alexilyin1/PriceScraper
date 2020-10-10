import os
import csv
import psycopg2
import pandas as pd
from . import keys


class RequestDB:

    def __init__(self, db_name=keys.DB, db_user=keys.POSTGRES_USER, db_pass=keys.POSTGRES_PASS, host=keys.HOST):
        self.db_name = db_name
        self.db_user = db_user
        self.db_pass = db_pass
        self.host = host
        self.connection = None
        self.cursor = None

        self._connect()

    def _connect(self):
        self.connection = psycopg2.connect(database=self.db_name, host=self.host,
                                           user=self.db_user, password=self.db_pass)
        self.cursor = self.connection.cursor()

    def _dconnect(self):
        self.connection.close()
        self.cursor.close()

    def CreatePerson(self, email, zip, zip_dist, make, model, freq, min_stars):
        self.cursor.execute('INSERT INTO interface_person (email, zip_code, zip_dist, car_make_id, car_model_id, freq, min_stars) VALUES (%s, %s, %s, %s, %s, %s, %s);',
                            (email, zip, zip_dist, make, model, freq, min_stars, ))
        self.connection.commit()

    def GetID(self, email):
        self.cursor.execute('SELECT id FROM interface_person WHERE email = %s;',
                            (email,))
        res = self.cursor.fetchall()
        return res

    def GetPerson(self, email):
        self.cursor.execute('SELECT email, zip_code, zip_dist, car_make_id, car_model_id, freq, min_stars min FROM interface_person WHERE email = %s;',
                            (email,))
        res = self.cursor.fetchall()
        return res

    def GetAllPersons(self):
        self.cursor.execute('SELECT email FROM interface_person')
        res = self.cursor.fetchall()
        return res

    def drop_user(self, email):
        self.cursor.execute('DELETE FROM interface_person WHERE email = %s;',
                            (email, ))
        self.connection.commit()


class CarMakeDB:

    def __init__(self, db_name=keys.DB, db_user=keys.POSTGRES_USER, db_pass=keys.POSTGRES_PASS, host=keys.HOST):
        self.db_name = db_name
        self.db_user = db_user
        self.db_pass = db_pass
        self.host = host
        self.connection = None
        self.cursor = None

        self._connect()

    def _connect(self):
        self.connection = psycopg2.connect(database=self.db_name, host=self.host,
                                           user=self.db_user, password=self.db_pass)
        self.cursor = self.connection.cursor()

    def _dconnect(self):
        self.connection.close()
        self.cursor.close()

    def CreateCarMake(self, make):
        self.cursor.execute('INSERT INTO interface_carmake (car_make) VALUES (%s);',
                            (make,))
        self.connection.commit()

    def GetCarMake(self, make):
        self.cursor.execute('SELECT id, car_make FROM interface_carmake WHERE car_make = %s;',
                            (make,))
        res = self.cursor.fetchall()
        return res

    def GetAllMakes(self):
        self.cursor.execute('SELECT car_make FROM interface_carmake;')
        res = self.cursor.fetchall()
        return res

    def DropCarMake(self, make):
        self.cursor.execute('DELETE FROM interface_carmake WHERE car_make = %s;',
                            (make, ))
        self.connection.commit()


class CarModelDB:

    def __init__(self, db_name=keys.DB, db_user=keys.POSTGRES_USER, db_pass=keys.POSTGRES_PASS, host=keys.HOST):
        self.db_name = db_name
        self.db_user = db_user
        self.db_pass = db_pass
        self.host = host
        self.connection = None
        self.cursor = None

        self._connect()

    def _connect(self):
        self.connection = psycopg2.connect(database=self.db_name, host=self.host,
                                           user=self.db_user, password=self.db_pass)
        self.cursor = self.connection.cursor()

    def _dconnect(self):
        self.connection.close()
        self.cursor.close()

    def CreateCarModel(self, model, make_id):
        self.cursor.execute('INSERT INTO interface_carmodel (car_model, car_make_id) VALUES (%s, %s);',
                            (model, make_id,))
        self.connection.commit()

    def GetCarModel(self, model):
        self.cursor.execute('SELECT id, car_model FROM interface_carmodel WHERE car_model = %s;',
                            (model,))
        res = self.cursor.fetchall()
        return res

    def GetAllModels(self):
        self.cursor.execute('SELECT car_model FROM interface_carmodel;')
        res = self.cursor.fetchall()
        return res

    def CheckMake(self, id):
        self.cursor.execute('SELECT car_model FROM interface_carmodel WHERE car_make_id = %s;',
                            (id, ))
        res = self.cursor.fetchall()
        return res

    def DropCarModel(self, model):
        self.cursor.execute('DELETE FROM interface_carmake WHERE car_model = %s;',
                            (model, ))
        self.connection.commit()


class FileDB:

    def __init__(self, db_name=keys.DB, db_user=keys.POSTGRES_USER, db_pass=keys.POSTGRES_PASS, host=keys.HOST):
        self.db_name = db_name
        self.db_user = db_user
        self.db_pass = db_pass
        self.host = host
        self.connection = None
        self.cursor = None

        self._connect()

    def _connect(self):
        self.connection = psycopg2.connect(database=self.db_name, host=self.host,
                                           user=self.db_user, password=self.db_pass)
        self.cursor = self.connection.cursor()

    def _dconnect(self):
        self.connection.close()
        self.cursor.close()

    def InsertFile(self, filepath):
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for record in reader:
                self.cursor.execute("""INSERT INTO interface_personfiles (dealership, model, price_msrp, prices_first_discount, prices_final_discount, url, email_id)
                                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                    record)
                self.connection.commit()

    def InsertFileAlt(self, filepath):
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for record in reader:
                self.cursor.execute("""INSERT INTO interface_personfilesalt (dealership, model, price_msrp, url, email_id)
                                       VALUES (%s, %s, %s, %s, %s)""",
                                    record)
                self.connection.commit()

    def GetUserCSV(self, email_id) -> pd.DataFrame:
        self.cursor.execute('SELECT dealership, model, url, price_msrp, prices_first_discount, prices_final_discount FROM interface_personfiles WHERE email_id = %s;',
                            (email_id,))
        res = self.cursor.fetchall()

        csv_dat = [x[:] for x in res]
        dat = pd.DataFrame(csv_dat, columns=['Dealership Name', 'Model', 'URL', 'Price_MSRP', 'Price_First_Discount', 'Price_Final_Disocunt'])
        return dat

    def GetUserCSVAlt(self, email_id) -> pd.DataFrame:
        self.cursor.execute('SELECT dealership, model, url, price_msrp, FROM interface_personfilesalt WHERE email_id = %s;',
                            (email_id,))
        res = self.cursor.fetchall()

        csv_dat = [x[:] for x in res]
        dat = pd.DataFrame(csv_dat, columns=['Dealership Name', 'Model', 'URL', 'Price_MSRP'])
        return dat

    def DropUserCSV(self, email_id):
        self.cursor.execute('DELETE FROM interface_personfiles WHERE email_id = %s;',
                            (email_id, ))
        self.connection.commit()

    def DropUserCSVAlt(self, email_id):
        self.cursor.execute('DELETE FROM interface_personfilesalt WHERE email_id = %s;',
                            (email_id, ))
        self.connection.commit()



'''
dir = 'interface/static/interface/cars/us-car-models-data/'
cars_df = pd.concat(map(pd.read_csv, [dir+f for f in os.listdir(dir) if f.endswith('.csv')])).drop_duplicates(['make', 'model']).sort_values(['make', 'model'])


cm = CarMakeDB()
cmo = CarModelDB()


for make in cars_df['make'].unique():
    if make not in [x[0] for x in cm.GetAllMakes()]:
        cm.CreateCarMake(make)

for row in cars_df.iterrows():
    cmo.CreateCarModel(row[1]['model'], cm.GetCarMake(row[1]['make'])[0][0])


cm._dconnect()
cmo._dconnect()

fdb = FileDB()
fdb.InsertFile(os.path.join(os.path.abspath('.'), 'interface/static/interface/user_files/Ford_Ranger_within_10_miles_of_94404__prices.csv'))
fdb._dconnect()
'''