# Generated by Django 2.1.7 on 2019-04-19 00:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marco_polo', '0029_auto_20190417_1704'),
    ]

    operations = [
        migrations.CreateModel(
            name='BacktestGraph',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('value', models.FloatField()),
                ('backtest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marco_polo.Backtest')),
            ],
        ),
    ]