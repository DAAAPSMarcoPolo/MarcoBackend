# Generated by Django 2.1.5 on 2019-02-12 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marco_polo', '0005_auto_20190211_2149'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(default=None, max_length=20),
            preserve_default=False,
        ),
    ]
