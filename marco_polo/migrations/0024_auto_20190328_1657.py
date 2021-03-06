# Generated by Django 2.1.5 on 2019-03-28 16:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('marco_polo', '0023_auto_20190327_1530'),
    ]

    operations = [
        migrations.CreateModel(
            name='BacktestVote',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('vote', models.BooleanField(default=None)),
                ('backtest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marco_polo.Backtest')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
