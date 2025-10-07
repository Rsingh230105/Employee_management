from django.db import models
from django.core.validators import RegexValidator

class Department(models.Model):
    name = models.CharField(max_length=100, null=False)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=100, null=False)

    def __str__(self):
        return self.name

class Address(models.Model):
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='India')

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}"

class Employee(models.Model):
    EMPLOYMENT_STATUS = [
        ('FT', 'Full Time'),
        ('PT', 'Part Time'),
        ('CT', 'Contract'),
        ('IN', 'Intern')
    ]

    # Personal Information
    first_name = models.CharField(max_length=30, null=False)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        help_text="Enter phone number in format: '+999999999'.",
        null=True,
        blank=True
    )
    date_of_birth = models.DateField(null=True)
    profile_picture = models.ImageField(upload_to='employee_photos/', null=True, blank=True)
    # Resume / CV file
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)

    # Employment Information
    employee_id = models.CharField(max_length=10, unique=True, null=True, blank=True)
    dept = models.ForeignKey('Department', on_delete=models.CASCADE)
    role = models.ForeignKey('Role', on_delete=models.CASCADE)
    hire_date = models.DateField()
    employment_status = models.CharField(max_length=2, choices=EMPLOYMENT_STATUS, default='FT')

    # Compensation
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, null=True, blank=True)
    emergency_contact_phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        null=True,
        blank=True
    )
    emergency_contact_relation = models.CharField(max_length=50, null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['employee_id']),
            models.Index(fields=['dept']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_employment_status_display(self):
        return dict(self.EMPLOYMENT_STATUS)[self.employment_status]
