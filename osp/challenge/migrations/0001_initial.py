# Generated by Django 3.2.12 on 2022-07-29 12:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0012_githubrepocontributor_githubuserfollowing_githubuserstarred'),
    ]

    operations = [
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=200)),
                ('image', models.ImageField(default='img/challenge/default.jpg', upload_to='img/challenge/')),
                ('sql', models.TextField()),
                ('max_progress', models.IntegerField(blank=True, default=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ChallengeAchieve',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('acheive_date', models.DateTimeField()),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.account')),
            ],
        ),
    ]
