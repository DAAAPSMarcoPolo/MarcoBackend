# Generated by Django 2.1.5 on 2019-02-20 22:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marco_polo', '0009_alpacaapikeys'),
    ]

    operations = [
        migrations.RenameField(
            model_name='alpacaapikeys',
            old_name='user',
            new_name='user_id',
        ),
    ]