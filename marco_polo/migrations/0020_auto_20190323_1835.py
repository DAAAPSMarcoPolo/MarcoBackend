# Generated by Django 2.1.5 on 2019-03-23 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marco_polo', '0019_auto_20190318_2034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='universe',
            name='stocks',
            field=models.ManyToManyField(related_name='stocks', to='marco_polo.Stock'),
        )
    ]
