# Generated by Django 3.2.12 on 2022-06-27 05:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tag', '0001_initial'),
        ('user', '0004_auto_20220622_0155'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountInterest',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.account')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tag.tag')),
            ],
        ),
    ]
