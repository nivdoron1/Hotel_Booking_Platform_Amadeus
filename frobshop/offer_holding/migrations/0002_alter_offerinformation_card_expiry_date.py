# Generated by Django 3.2.19 on 2023-08-10 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offer_holding', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offerinformation',
            name='card_expiry_date',
            field=models.CharField(help_text='Format: MM/YYYY', max_length=7),
        ),
    ]
