# Generated by Django 3.1.1 on 2020-09-28 05:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CarMake',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('car_make', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='CarModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('car_model', models.CharField(max_length=50)),
                ('car_make', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='interface.carmake')),
            ],
        ),
        migrations.CreateModel(
            name='PersonFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dealership', models.CharField(max_length=100)),
                ('model', models.TextField()),
                ('price_msrp', models.IntegerField()),
                ('prices_first_discount', models.IntegerField()),
                ('prices_final_discount', models.IntegerField()),
                ('url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, null=True, unique=True)),
                ('zip_code', models.IntegerField()),
                ('zip_dist', models.IntegerField(default=250)),
                ('car_make', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='interface.carmake')),
                ('car_model', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='interface.carmodel')),
            ],
        ),
    ]
