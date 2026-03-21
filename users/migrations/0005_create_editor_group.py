from django.db import migrations
from django.contrib.auth.models import Group

def create_editor_group(apps, schema_editor):
    Group.objects.get_or_create(id=2, defaults={'name': 'editor'})

def delete_editor_group(apps, schema_editor):
    Group.objects.filter(id=2, name='editor').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0004_announcement_show_date'), 
    ]

    operations = [
        migrations.RunPython(create_editor_group, delete_editor_group),
    ]