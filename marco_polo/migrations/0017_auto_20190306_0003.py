# Generated by Django 2.1.5 on 2019-03-06 00:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marco_polo', '0016_auto_20190303_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='universe',
            name='name',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='useduniverse',
            name='name',
            field=models.CharField(default='', max_length=100),
        ),
    ]
