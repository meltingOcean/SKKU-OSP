# Generated by Django 4.0.5 on 2022-09-03 16:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='annualoverview',
            name='fork',
        ),
        migrations.RemoveField(
            model_name='annualoverview',
            name='fork_std',
        ),
        migrations.RemoveField(
            model_name='annualoverview',
            name='score_diff',
        ),
        migrations.RemoveField(
            model_name='annualoverview',
            name='score_std_diff',
        ),
        migrations.RemoveField(
            model_name='annualoverview',
            name='score_std_sum',
        ),
        migrations.RemoveField(
            model_name='annualoverview',
            name='score_sum',
        ),
        migrations.RemoveField(
            model_name='annualtotal',
            name='student_KP_diff',
        ),
        migrations.RemoveField(
            model_name='annualtotal',
            name='student_KP_sum',
        ),
        migrations.RemoveField(
            model_name='distscore',
            name='score_dept_diff',
        ),
        migrations.RemoveField(
            model_name='distscore',
            name='score_dept_pct_diff',
        ),
        migrations.RemoveField(
            model_name='distscore',
            name='score_dept_pct_sum',
        ),
        migrations.RemoveField(
            model_name='distscore',
            name='score_dept_std_diff',
        ),
        migrations.RemoveField(
            model_name='distscore',
            name='score_dept_std_sum',
        ),
        migrations.RemoveField(
            model_name='distscore',
            name='score_dept_sum',
        ),
        migrations.RemoveField(
            model_name='distscore',
            name='score_diff',
        ),
        migrations.RemoveField(
            model_name='distscore',
            name='score_sid_diff',
        ),
        migrations.RemoveField(
            model_name='distscore',
            name='score_sid_pct_diff',
        ),
        migrations.RemoveField(
            model_name='distscore',
            name='score_sid_pct_sum',
        ),
        migrations.RemoveField(
            model_name='distscore',
            name='score_sid_std_diff',
        ),
        migrations.RemoveField(
            model_name='distscore',
            name='score_sid_std_sum',
        ),
        migrations.RemoveField(
            model_name='distscore',
            name='score_sid_sum',
        ),
        migrations.RemoveField(
            model_name='distscore',
            name='score_sum',
        ),
        migrations.RemoveField(
            model_name='student',
            name='score_diff',
        ),
        migrations.RemoveField(
            model_name='student',
            name='score_sum',
        ),
    ]