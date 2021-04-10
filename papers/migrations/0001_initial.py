# Generated by Django 3.1.7 on 2021-04-10 16:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import papers.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('edit_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('text', models.TextField()),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Paper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('original_author_id', models.IntegerField()),
                ('keywords', models.CharField(max_length=128)),
                ('description', models.TextField()),
                ('add_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_edit_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('approved', models.BooleanField(default=False)),
                ('authors', models.ManyToManyField(blank=True, related_name='authors', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StudentClub',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('acronym', models.CharField(max_length=12)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, upload_to=papers.models.paper_directory_path)),
                ('add_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('paper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='papers.paper')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('paper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='papers.paper')),
            ],
        ),
        migrations.AddField(
            model_name='paper',
            name='club',
            field=models.ForeignKey(default=papers.models.StudentClub.get_default_pk, on_delete=django.db.models.deletion.SET_DEFAULT, to='papers.studentclub'),
        ),
        migrations.AddField(
            model_name='paper',
            name='reviewers',
            field=models.ManyToManyField(blank=True, max_length=2, related_name='reviewers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='MessageSeen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seen_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='papers.message')),
                ('reader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='review',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='papers.review'),
        ),
        migrations.CreateModel(
            name='CoAuthor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('surname', models.CharField(max_length=32)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('paper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='papers.paper')),
            ],
        ),
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
