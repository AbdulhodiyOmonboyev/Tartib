import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0002_rename_usercategory_category'),
        ('tasks', '0002_alter_task_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='category',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='tasks',
                to='categories.category',
                verbose_name='Kategoriya'
            ),
        ),
        # Shuningdek, boshqa maydonlarni ham user so'ragandek tozalab olamiz (verbose_name larni olib tashlash va h.k.)
        migrations.AlterField(
            model_name='task',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='done',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='task',
            name='pri',
            field=models.CharField(
                choices=[('danger', 'Muhim'), ('amber', "O'rta"), ('gray', 'Past')],
                default='gray',
                max_length=10
            ),
        ),
        migrations.AlterField(
            model_name='task',
            name='time',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
    ]
