import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0001_initial'),
    ]

    operations = [
        # --- Enrollment changes ---
        # Add semester field
        migrations.AddField(
            model_name='enrollment',
            name='semester',
            field=models.IntegerField(
                default=1,
                validators=[django.core.validators.MinValueValidator(1)]
            ),
            preserve_default=False,
        ),
        # Update status choices
        migrations.AlterField(
            model_name='enrollment',
            name='status',
            field=models.CharField(
                choices=[('Active', 'Active'), ('Completed', 'Completed'), ('Dropped', 'Dropped')],
                default='Active',
                max_length=20,
            ),
        ),
        # Remove old unique_together
        migrations.AlterUniqueTogether(
            name='enrollment',
            unique_together=set(),
        ),
        # Add new unique_together with semester
        migrations.AlterUniqueTogether(
            name='enrollment',
            unique_together={('student', 'course', 'semester')},
        ),
        # Remove unused fields
        migrations.RemoveField(model_name='enrollment', name='created_at'),
        migrations.RemoveField(model_name='enrollment', name='updated_at'),

        # --- AcademicHistory changes ---
        # Remove old unique_together FIRST (references year_completed which still exists)
        migrations.AlterUniqueTogether(
            name='academichistory',
            unique_together=set(),
        ),
        # Add new fields with defaults for existing rows
        migrations.AddField(
            model_name='academichistory',
            name='institution_name',
            field=models.CharField(max_length=255, default='Unknown'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='academichistory',
            name='board_university',
            field=models.CharField(max_length=255, default='Unknown'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='academichistory',
            name='passing_year',
            field=models.IntegerField(
                default=2000,
                validators=[django.core.validators.MinValueValidator(1900)]
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='academichistory',
            name='percentage_cgpa',
            field=models.DecimalField(max_digits=5, decimal_places=2, default=0.0),
            preserve_default=False,
        ),
        # Remove old fields
        migrations.RemoveField(model_name='academichistory', name='previous_grades'),
        migrations.RemoveField(model_name='academichistory', name='year_completed'),
        migrations.RemoveField(model_name='academichistory', name='gpa'),
        migrations.RemoveField(model_name='academichistory', name='remarks'),
        migrations.RemoveField(model_name='academichistory', name='created_at'),
        migrations.RemoveField(model_name='academichistory', name='updated_at'),
        # Remove old unique_together that referenced year_completed
        migrations.AlterUniqueTogether(
            name='academichistory',
            unique_together=set(),
        ),
    ]
