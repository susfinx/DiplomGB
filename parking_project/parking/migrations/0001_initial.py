# Generated by Django 5.0.1 on 2024-02-02 08:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=100)),
                ('is_owner', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='parking.user')),
                ('bank_details', models.CharField(max_length=100)),
            ],
            bases=('parking.user',),
        ),
        migrations.CreateModel(
            name='ParkingSpot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('hourly_rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('daily_rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('monthly_rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('is_available_hourly', models.BooleanField(default=True)),
                ('is_available_daily', models.BooleanField(default=True)),
                ('is_available_monthly', models.BooleanField(default=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parking_spots', to='parking.user')),
            ],
        ),
    ]
