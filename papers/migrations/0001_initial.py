# Generated by Django 3.1.14 on 2022-02-11 21:39

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
            name='Announcement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('value', models.CharField(default='', max_length=16)),
                ('tag', models.CharField(choices=[('correspondence', 'Zgodność z tematyką'), ('originality', 'Oryginalność'), ('merits', 'Poprawność merytoryczna'), ('presentation', 'Jakość prezentacji'), ('final_grade', 'Ocena końcowa')], max_length=16)),
                ('display_color', models.CharField(choices=[('primary', 'Primary'), ('secondary', 'Secondary'), ('success', 'Success'), ('danger', 'Danger'), ('warning', 'Warning'), ('info', 'Info'), ('light', 'Light'), ('dark', 'Dark')], default='primary', max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='MassEmailModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name_plural': 'Mass email',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('text', models.TextField()),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='NotificationPeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('period', models.IntegerField()),
                ('last_used', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Paper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('keywords', models.CharField(max_length=128)),
                ('description', models.TextField()),
                ('approved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('statement', models.PositiveIntegerField(default=0)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StudentClub',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('faculty', models.CharField(max_length=128)),
                ('patron', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, max_length=512, upload_to=papers.models.paper_directory_path)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('paper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='papers.paper')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('correspondence', models.ForeignKey(blank=True, limit_choices_to={'tag': 'correspondence'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='correspondence', to='papers.grade')),
                ('final_grade', models.ForeignKey(blank=True, limit_choices_to={'tag': 'final_grade'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='final_grade', to='papers.grade')),
                ('merits', models.ForeignKey(blank=True, limit_choices_to={'tag': 'merits'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='merits', to='papers.grade')),
                ('originality', models.ForeignKey(blank=True, limit_choices_to={'tag': 'originality'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='originality', to='papers.grade')),
                ('paper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='papers.paper')),
                ('presentation', models.ForeignKey(blank=True, limit_choices_to={'tag': 'presentation'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='presentation', to='papers.grade')),
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
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='papers.message')),
                ('reader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='paper',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='paper', to='papers.paper'),
        ),
        migrations.AddField(
            model_name='message',
            name='reviewer',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='reviewer', to=settings.AUTH_USER_MODEL),
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
    ]
