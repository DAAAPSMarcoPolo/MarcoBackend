# Generated by Django 2.1.5 on 2019-02-10 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marco_polo', '0003_auto_20190210_1842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='code_created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='firstlogin',
            field=models.BooleanField(default=True),
        ),
    ]
