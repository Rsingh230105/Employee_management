# emp_app/admin.py
from django.contrib import admin
from .models import Employee, Role, Department

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "role", "dept", "salary", "phone", "hire_date", "resume")
    list_filter = ("dept", "role")
    search_fields = ("first_name", "last_name", "phone")
    ordering = ("-hire_date",)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "location")
    search_fields = ("name", "location")

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
