from django.db import models


class CarMake(models.Model):
    car_make = models.CharField(name='car_make', max_length=20)

    def __str__(self):
        return self.car_make


class CarModel(models.Model):
    car_make = models.ForeignKey(CarMake, name='car_make', on_delete=models.CASCADE)
    car_model = models.CharField(name='car_model', max_length=50)

    def __str__(self):
        return self.car_make, self.car_model


class Person(models.Model):
    email = models.EmailField(name='email', unique=True, blank=False, null=True)
    zip_code = models.IntegerField(name='zip_code', unique=False, blank=False, null=False)
    zip_dist = models.IntegerField(name='zip_dist', unique=False, blank=False, null=False, default=250)
    min_stars = models.IntegerField(name='min_stars', unique=False, blank=False, null=False, default=2)
    car_make = models.ForeignKey(CarMake, name='car_make', on_delete=models.SET_NULL, null=True)
    car_model = models.ForeignKey(CarModel, name='car_model', on_delete=models.SET_NULL, null=True)
    frequency = models.IntegerField(name='freq', unique=False, blank=False, null=False, default=7)
    prices = models.CharField(name='prices', unique=False, blank=False, null=False, max_length=20, default='Full')


class PersonFiles(models.Model):
    email = models.ForeignKey(Person, name='email', on_delete=models.CASCADE, default=1)
    dealership = models.CharField(name='dealership', max_length=100, unique=False, blank=False, null=False)
    model = models.TextField(name='model', unique=False, blank=False, null=False)
    price_msrp = models.IntegerField(name='price_msrp', unique=False, blank=False, null=False)
    prices_first_discount = models.IntegerField(name='prices_first_discount', unique=False, blank=False, null=False)
    prices_final_discount = models.IntegerField(name='prices_final_discount', unique=False, blank=False, null=False)
    url = models.URLField(name='url', unique=False, blank=False, null=False)


class PersonFilesAlt(models.Model):
    email = models.ForeignKey(Person, name='email', on_delete=models.CASCADE, default=1)
    dealership = models.CharField(name='dealership', max_length=100, unique=False, blank=False, null=False)
    model = models.TextField(name='model', unique=False, blank=False, null=False)
    price_msrp = models.IntegerField(name='price_msrp', unique=False, blank=False, null=False)
    url = models.URLField(name='url', unique=False, blank=False, null=False)
