# Generated by Django 2.2.12 on 2020-06-23 16:35

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import results.mixins.change_log


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0004_categoryforcompetitiontype_check_record_partial'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='approved',
            field=models.BooleanField(default=False, verbose_name='Approved'),
        ),
        migrations.AddField(
            model_name='competitionlevel',
            name='require_approval',
            field=models.BooleanField(default=False, verbose_name='Require approved competition to add results'),
        ),
        migrations.AddField(
            model_name='event',
            name='approved',
            field=models.BooleanField(default=False, verbose_name='Approved'),
        ),
        migrations.AddField(
            model_name='event',
            name='categories',
            field=models.TextField(blank=True, verbose_name='Competition categories'),
        ),
        migrations.AddField(
            model_name='event',
            name='international',
            field=models.BooleanField(default=False, verbose_name='International competition'),
        ),
        migrations.AddField(
            model_name='event',
            name='invitation',
            field=models.URLField(blank=True, verbose_name='Invitation URL'),
        ),
        migrations.AddField(
            model_name='event',
            name='notes',
            field=models.TextField(blank=True, verbose_name='Generic notes'),
        ),
        migrations.AddField(
            model_name='event',
            name='optional_dates',
            field=models.TextField(blank=True, verbose_name='Optional dates'),
        ),
        migrations.AddField(
            model_name='event',
            name='safety_plan',
            field=models.BooleanField(default=False, verbose_name='Safety plan exists'),
        ),
        migrations.AddField(
            model_name='event',
            name='toc_agreement',
            field=models.BooleanField(default=False, verbose_name='Terms and Conditions agreement'),
        ),
        migrations.AddField(
            model_name='event',
            name='web_page',
            field=models.URLField(blank=True, verbose_name='Web page'),
        ),
        migrations.CreateModel(
            name='EventContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('contact', 'Generic contact'), ('manager', 'Competition manager'), ('head judge', 'Head judge'), ('technical', 'Technical manager')], max_length=10, verbose_name='Contact type')),
                ('first_name', models.CharField(max_length=100, verbose_name='First name')),
                ('last_name', models.CharField(max_length=100, verbose_name='Last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Email address')),
                ('phone', models.CharField(blank=True, max_length=17, validators=[django.core.validators.RegexValidator(message='Phone number may start with "+" and only contain digits.', regex='^\\+?1?\\d{7,15}$')], verbose_name='Phone number')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='results.Event')),
            ],
            bases=(results.mixins.change_log.LogChangesMixing, models.Model),
        ),
    ]