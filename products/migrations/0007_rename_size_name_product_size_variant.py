# Generated by Django 5.1 on 2024-09-08 07:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_alter_colorvariant_price_alter_sizevariant_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='size_name',
            new_name='size_variant',
        ),
    ]
