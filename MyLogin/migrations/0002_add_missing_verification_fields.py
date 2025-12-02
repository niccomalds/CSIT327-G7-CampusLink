from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('MyLogin', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='verification_status',
            field=models.CharField(max_length=20, default='unverified'),
        ),
        migrations.AddField(
            model_name='profile',
            name='verification_documents',
            field=models.FileField(upload_to='verification_docs/', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='institutional_email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='verification_reason',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='verified_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='verification_submitted_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
