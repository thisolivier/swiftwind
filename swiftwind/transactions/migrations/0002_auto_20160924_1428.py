# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-24 14:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel('TransactionImportField', 'TransactionImportColumn')
    ]
