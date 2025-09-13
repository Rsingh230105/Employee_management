from django.contrib import admin
from .models import Employee,Role,Department

 # from Employee_mangement.emp_app.models import Employee

# Register your models here.
admin.site.register(Employee)
admin.site.register(Role)
admin.site.register(Department)
