# Generated by Django 3.2 on 2024-07-12 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_rename_recite_favorites_recipe'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipeingredient',
            name='amount',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]