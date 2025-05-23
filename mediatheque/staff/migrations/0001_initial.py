# Generated by Django 5.2.1 on 2025-05-14 06:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MediaStaff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('media_type', models.CharField(max_length=50)),
                ('is_available', models.BooleanField(default=True)),
                ('can_borrow', models.BooleanField(default=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
        ),
        migrations.CreateModel(
            name='BoardGameStaff',
            fields=[
                ('mediastaff_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='staff.mediastaff')),
                ('creators', models.CharField(max_length=100)),
                ('is_visible', models.BooleanField(default=True)),
                ('game_type', models.CharField(blank=True, max_length=100, null=True)),
            ],
            bases=('staff.mediastaff',),
        ),
        migrations.CreateModel(
            name='BookStaff',
            fields=[
                ('mediastaff_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='staff.mediastaff')),
                ('author', models.CharField(max_length=200)),
                ('available', models.BooleanField(default=True)),
            ],
            bases=('staff.mediastaff',),
        ),
        migrations.CreateModel(
            name='CDStaff',
            fields=[
                ('mediastaff_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='staff.mediastaff')),
                ('artist', models.CharField(max_length=200)),
            ],
            bases=('staff.mediastaff',),
        ),
        migrations.CreateModel(
            name='DVDStaff',
            fields=[
                ('mediastaff_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='staff.mediastaff')),
                ('producer', models.CharField(max_length=200)),
            ],
            bases=('staff.mediastaff',),
        ),
        migrations.CreateModel(
            name='StaffBorrowItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('borrow_date', models.DateTimeField(auto_now_add=True)),
                ('due_date', models.DateTimeField()),
                ('return_date', models.DateTimeField(blank=True, null=True)),
                ('is_returned', models.BooleanField(default=False)),
                ('media', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='staff_borrows_media', to='staff.mediastaff')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='staff_borrow_items', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'indexes': [models.Index(fields=['user', 'is_returned'], name='staff_staff_user_id_890c5e_idx')],
            },
        ),
    ]
