# Generated by Django 5.0.7 on 2024-07-31 09:51

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts_comments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_ai_reply', models.BooleanField(default=False)),
                ('time_sleep', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7200)])),
                ('creativity', models.FloatField(default=0.5, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)])),
                ('reply_or_dialogue', models.SmallIntegerField(choices=[(1, 'Reply'), (2, 'Dialogue')], default=1)),
                ('base_reply', models.CharField(default="I'm not available right now. I will answer later", max_length=1024)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='settings', to='posts_comments.post')),
            ],
        ),
    ]
