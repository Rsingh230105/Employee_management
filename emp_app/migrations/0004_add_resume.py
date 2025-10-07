"""
Migration to add resume FileField to Employee model.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("emp_app", "0003_address_alter_employee_options_employee_created_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='resume',
            field=models.FileField(blank=True, null=True, upload_to='resumes/'),
        ),
    ]
