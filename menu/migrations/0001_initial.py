# Generated by Django 2.1.15 on 2020-04-07 21:23

from django.conf import settings
import django.contrib.auth.models
import django.contrib.sites.models
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('menu_uid', models.AutoField(primary_key=True, serialize=False, verbose_name='UID')),
                ('menu_name', models.CharField(max_length=80, verbose_name='Menu Name')),
                ('menu_desc', models.CharField(blank=True, max_length=200, null=True, verbose_name='Menu Description')),
                ('menu_url', models.CharField(blank=True, max_length=256, null=True, verbose_name='Menu URL')),
                ('menu_sort_order', models.PositiveSmallIntegerField(default=1, verbose_name='Sort Order Number')),
                ('menu_isEnabled', models.BooleanField(default=True, verbose_name='Enabled')),
                ('menu_crte_dt', models.DateTimeField(auto_now_add=True, verbose_name='Created DateTime')),
                ('menu_mdfy_dt', models.DateTimeField(auto_now=True, verbose_name='Modified DateTime')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('menu_crte_user', models.ForeignKey(db_column='menu_crte_user_id', default=django.contrib.auth.models.User, editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='user_menu_creator', to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
                ('menu_mdfy_user', models.ForeignKey(db_column='menu_mdfy_user_id', default=django.contrib.auth.models.User, editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='user_menu_modifier', to=settings.AUTH_USER_MODEL, verbose_name='Modifier')),
                ('parent_menu', mptt.fields.TreeForeignKey(blank=True, db_column='menu_up_uid', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='menu_menu', to='menu.Menu', verbose_name='Parent Menu UID')),
                ('site', models.ForeignKey(db_column='site_id', default=django.contrib.sites.models.Site, on_delete=django.db.models.deletion.PROTECT, related_name='site_menu', to='sites.Site', verbose_name='Site')),
            ],
            options={
                'verbose_name': 'menu',
                'verbose_name_plural': 'menus',
                'db_table': 'blog_menu',
            },
        ),
    ]
