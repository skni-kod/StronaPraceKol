# Generated by Django 3.1.7 on 2021-03-10 16:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('papers', '0004_auto_20210310_1711'),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='comment',
            new_name='text',
        ),
    ]