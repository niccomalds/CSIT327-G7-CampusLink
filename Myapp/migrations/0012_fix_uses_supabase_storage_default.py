from django.db import migrations, models


def set_default_uses_supabase(apps, schema_editor):
    Application = apps.get_model('Myapp', 'Application')
    Application.objects.filter(uses_supabase_storage__isnull=True).update(uses_supabase_storage=False)


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0011_add_supabase_storage_fields'),
    ]

    operations = [
        migrations.RunPython(set_default_uses_supabase, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='application',
            name='uses_supabase_storage',
            field=models.BooleanField(default=False, help_text='Whether this application uses Supabase storage for resume'),
        ),
    ]
