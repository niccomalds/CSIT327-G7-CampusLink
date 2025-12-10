# Generated migration for Supabase storage support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0010_posting_opportunity_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='resume_supabase_path',
            field=models.CharField(blank=True, max_length=500, null=True, help_text='Path to resume file in Supabase storage'),
        ),
        migrations.AddField(
            model_name='application',
            name='resume_signed_url',
            field=models.TextField(blank=True, null=True, help_text='Cached signed URL for resume access'),
        ),
        migrations.AddField(
            model_name='application',
            name='signed_url_expires_at',
            field=models.DateTimeField(blank=True, null=True, help_text='Timestamp when signed URL expires'),
        ),
        migrations.AddField(
            model_name='application',
            name='uses_supabase_storage',
            field=models.BooleanField(default=False, help_text='Whether this application uses Supabase storage for resume'),
        ),
    ]
