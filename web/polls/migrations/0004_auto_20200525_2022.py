# Generated by Django 3.0.6 on 2020-05-25 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0003_remove_question_pub_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='publish_date',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]