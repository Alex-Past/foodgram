# Generated by Django 3.2 on 2024-07-24 17:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20240724_1729'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shoppingcart',
            old_name='recipes',
            new_name='recipe',
        ),
    ]
