from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_migrate_category_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='cat',
        ),
    ]
