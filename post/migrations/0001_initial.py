# Generated by Django 2.1.15 on 2020-04-07 21:23

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import tagging.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('menu', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('post_uid', models.AutoField(primary_key=True, serialize=False, verbose_name='UID')),
                ('post_title', models.CharField(max_length=100, verbose_name='Title')),
                ('post_slug', models.SlugField(allow_unicode=True, help_text='one word for title alias.', max_length=100, verbose_name='Slug')),
                ('post_content', models.TextField(verbose_name='Content')),
                ('post_views', models.PositiveIntegerField(default=0, verbose_name='Views')),
                ('post_isEnabled', models.BooleanField(default=True, verbose_name='Enabled')),
                ('post_tag', tagging.fields.TagField(blank=True, max_length=255)),
                ('post_crte_dt', models.DateTimeField(auto_now_add=True, verbose_name='Created DateTime')),
                ('post_mdfy_dt', models.DateTimeField(auto_now=True, verbose_name='Modified DateTime')),
                ('menu', models.ForeignKey(db_column='menu_uid', on_delete=django.db.models.deletion.PROTECT, related_name='menu_post', to='menu.Menu', verbose_name='Menu')),
                ('post_crte_user', models.ForeignKey(db_column='post_crte_user_id', default=django.contrib.auth.models.User, editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='user_post_creator', to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
                ('post_mdfy_user', models.ForeignKey(db_column='post_mdfy_user_id', default=django.contrib.auth.models.User, editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='user_post_modifier', to=settings.AUTH_USER_MODEL, verbose_name='Modifier')),
            ],
            options={
                'verbose_name': 'post',
                'verbose_name_plural': 'posts',
                'db_table': 'blog_post',
                'ordering': ['-post_uid'],
            },
        ),
    ]
