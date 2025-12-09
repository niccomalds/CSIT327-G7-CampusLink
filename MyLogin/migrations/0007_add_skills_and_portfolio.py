from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MyLogin', '0006_notification_is_archived_notification_is_favorite_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='skills',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='profile',
            name='portfolio_links',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
