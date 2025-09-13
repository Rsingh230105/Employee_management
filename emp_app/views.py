from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Employee, Role, Department
from datetime import datetime
from django.db.models import Q

# Create your views here.
def index(request):
    return render(request, 'index.html')


def all_emp(request):
    emps = Employee.objects.all()
    context = {
        'emps': emps
    }
    print(context)
    return render(request, 'all_emp.html', context)


def add_emp(request):
    if request.method == "POST":
        try:
            # Use .get() method to safely access POST data
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            salary = request.POST.get('salary', 0)
            dept_name = request.POST.get('dept', '')  # Changed from 'department' to 'dept'
            role_name = request.POST.get('role', '')
            bonus = request.POST.get('bonus', 0)
            hire_date = request.POST.get('hire_date', '')
            phone = request.POST.get('phone_number', '')

            # Validate required fields
            if not all([first_name, last_name, salary]):
                return HttpResponse("Please fill in all required fields")

            # Convert fields to appropriate types
            salary = int(salary) if salary else 0
            bonus = int(bonus) if bonus else 0

            # Handle phone number (it might be empty)
            if phone and phone.strip():
                try:
                    phone = int(phone)
                except ValueError:
                    phone = 0  # or use a default value
            else:
                phone = 0  # Use 0 as default instead of None

            # Handle hire_date
            if hire_date:
                hire_date = datetime.strptime(hire_date, '%Y-%m-%d').date()
            else:
                hire_date = datetime.now().date()

            # Get or create Department and Role objects
            try:
                dept = Department.objects.get(name=dept_name)
            except Department.DoesNotExist:
                # Create new department if it doesn't exist
                dept = Department.objects.create(name=dept_name, location="Unknown")

            try:
                role = Role.objects.get(name=role_name)
            except Role.DoesNotExist:
                # Create new role if it doesn't exist
                role = Role.objects.create(name=role_name)

            # Create and save the employee
            new_emp = Employee(
                first_name=first_name,
                last_name=last_name,
                salary=salary,
                bonus=bonus,
                phone=phone,
                dept=dept,
                role=role,
                hire_date=hire_date
            )
            new_emp.save()

            return HttpResponse('Employee Added Successfully')

        except ValueError as e:
            return HttpResponse(f"Invalid data provided: {str(e)}")
        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}")

    elif request.method == "GET":
        return render(request, 'add_emp.html')
    else:
        return HttpResponse("An error occurred")



def remove_emp(request, emp_id=None):
    if emp_id:
        # Handle the actual removal
        try:
            emp = Employee.objects.get(id=emp_id)
            emp_name = f"{emp.first_name} {emp.last_name}"
            emp.delete()
            return HttpResponse(f"Employee {emp_name} removed successfully!")
        except Employee.DoesNotExist:
            return HttpResponse("Employee not found!")
    else:
        # Display the list of employees to remove
        emps = Employee.objects.all()
        context = {
            'emps': emps
        }
        return render(request, 'remove_emp.html', context)


def filter_emp(request):
    if request.method == "POST":
        name = request.POST['name']
        dept= request.POST['dept']
        role = request.POST['role']
        emps = Employee.objects.all()

        if name:
            emps = emps.filter(Q(first_name__icontains=name)| Q(last_name__icontains=name))
        if dept:
            emps = emps.filter(dept__name=dept)
        if role:
            emps = emps.filter(role__name=role)

        context = {
            'emps': emps
        }

        return render(request, 'all_emp.html',context)
    elif request.method == "GET":
        return render(request, 'filter_emp.html')
    else:
        return HttpResponse("An error occurred")