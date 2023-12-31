# Generated by Django 3.2.19 on 2023-06-22 12:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PriceAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hotel_name', models.CharField(max_length=200)),
                ('check_in_date', models.DateField()),
                ('check_out_date', models.DateField()),
                ('number_of_adults', models.IntegerField()),
                ('number_of_rooms', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=7)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_alerts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
