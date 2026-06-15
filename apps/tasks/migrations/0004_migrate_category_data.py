from django.db import migrations

def migrate_categories(apps, schema_editor):
    Task = apps.get_model('tasks', 'Task')
    Category = apps.get_model('categories', 'Category')
    
    # "Boshqa" nomli default kategoriya borligiga ishonch hosil qilish (agar kerak bo'lsa)
    # Lekin user har bir taskning useriga mos kategoriya yaratishni so'ragan
    
    for task in Task.objects.all():
        if task.cat:
            cat, _ = Category.objects.get_or_create(
                name=task.cat,
                user=task.user,
                defaults={}
            )
            task.category = cat
            task.save(update_fields=['category'])

def reverse_migrate_categories(apps, schema_editor):
    Task = apps.get_model('tasks', 'Task')
    for task in Task.objects.all():
        if task.category:
            task.cat = task.category.name
            task.save(update_fields=['cat'])

class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_add_category_fk'),
    ]

    operations = [
        migrations.RunPython(migrate_categories, reverse_migrate_categories),
    ]
