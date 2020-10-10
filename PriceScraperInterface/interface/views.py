from . import forms, tasks
from .db_scripts import CarMakeDB, CarModelDB, RequestDB
from django.shortcuts import render


def home(request):
    if request.method == 'POST':
        form = forms.InputForm(request.POST)
        if form.is_valid():
            email = form['email'].value()
            zip_code = int(form['zip_code'].value())
            dist = int(form['dist'].value())
            min_stars = int(form['minimum_stars'].value())
            car_make = form['car_make'].value().lower().capitalize()
            car_model = form['car_model'].value().lower().capitalize()
            prices = form['frequency'].value().lower()

            cm = CarMakeDB()
            cm_id = cm.GetCarMake(car_make)[0][0]

            cmo = CarModelDB()
            if car_model not in [x[0] for x in cmo.CheckMake(cm_id)]:
                if any(car_model in make for make in [x[0] for x in cmo.CheckMake(cm_id)]):
                    cmo.CreateCarModel(car_model, cm_id)
                else:
                    raise ValueError(car_model + ' not part of available ' + car_make + ' models.')

            rdb = RequestDB()
            if email not in [x[0] for x in rdb.GetAllPersons()]:
                rdb.CreatePerson(email, zip_code, dist, cm_id, cmo.GetCarModel(car_model)[0][0], 1, min_stars)

            rdb._dconnect()
            cm._dconnect()
            cmo._dconnect()

            print('Car search started!')
            tasks.email_task.delay(car_make, car_model, zip_code, dist, min_stars, email, prices)

    else:
        form = forms.InputForm()
    return render(request, 'interface/base.html', {'form': form})


def second(request):
    return render(request, '<h2>hello again<h2>')