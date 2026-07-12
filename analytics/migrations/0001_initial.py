from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='AnalyticsUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(unique=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('middle_name', models.CharField(blank=True, max_length=255, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=255, null=True)),
                ('educational_institution', models.CharField(blank=True, max_length=255, null=True)),
                ('course', models.IntegerField(default=0)),
                ('created_at', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={'abstract': False},
        ),
        migrations.CreateModel(
            name='AnalyticsTicket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_id', models.IntegerField(unique=True)),
                ('subject', models.CharField(blank=True, max_length=255, null=True)),
                ('max_points', models.IntegerField(default=0)),
                ('question_count', models.IntegerField(default=0)),
                ('difficulty', models.IntegerField(default=0)),
            ],
            options={'abstract': False},
        ),
        migrations.CreateModel(
            name='AnalyticsAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.IntegerField(default=0)),
                ('attempt_id', models.IntegerField(unique=True)),
                ('user_id', models.IntegerField(default=0)),
                ('ticket_id', models.IntegerField(default=0)),
                ('attempt_number', models.IntegerField(default=0)),
                ('score_earned', models.IntegerField(default=0)),
                ('max_score', models.IntegerField(default=0)),
                ('attempt_date', models.DateTimeField(blank=True, null=True)),
            ],
            options={'abstract': False},
        ),
    ]
