# Generated by Django 5.2.1 on 2025-06-02 09:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0003_remove_bookstaff_available'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mediastaff',
            options={'permissions': [('can_view_media', 'Peut voir les détails d’un média')], 'verbose_name': 'Média', 'verbose_name_plural': 'Médias'},
        ),
    ]
