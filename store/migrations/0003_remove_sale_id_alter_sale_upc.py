# Generated by Django 5.0.2 on 2024-03-22 13:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_remove_sale_composite_primary_key'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sale',
            name='id',
        ),
        migrations.AlterField(
            model_name='sale',
            name='UPC',
            field=models.ForeignKey(help_text="Enter product's UPC", on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, related_name='sold', serialize=False, to='store.store_product'),
        ),
    ]