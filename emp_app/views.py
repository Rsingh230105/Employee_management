from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponse
import csv
import xlsxwriter
from io import BytesIO
from .models import Employee, Department, Role, Address
from .forms import EmployeeForm, LoginForm

class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_employees'] = Employee.objects.count()
        context['departments'] = Department.objects.all()
        context['roles'] = Role.objects.all()
        return context

class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = "all_emp.html"
    context_object_name = "emps"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset().select_related("dept", "role").order_by("-created_at")
        q = self.request.GET.get("q", "").strip()
        dept = self.request.GET.get("dept", "").strip()
        role = self.request.GET.get("role", "").strip()
        status = self.request.GET.get("status", "").strip()

        if q:
            qs = qs.filter(
                Q(first_name__icontains=q) | 
                Q(last_name__icontains=q) |
                Q(employee_id__icontains=q) |
                Q(email__icontains=q)
            )
        if dept:
            qs = qs.filter(dept__name__iexact=dept)
        if role:
            qs = qs.filter(role__name__iexact=role)
        if status:
            qs = qs.filter(employment_status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["departments"] = Employee.objects.values_list("dept__name", flat=True).distinct()
        ctx["roles"] = Employee.objects.values_list("role__name", flat=True).distinct()
        ctx["q"] = self.request.GET.get("q", "")
        ctx["selected_dept"] = self.request.GET.get("dept", "")
        ctx["selected_role"] = self.request.GET.get("role", "")
        ctx["selected_status"] = self.request.GET.get("status", "")
        return ctx

class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = "view_emp.html"
    context_object_name = "employee"

class EmployeeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "add_emp.html"
    success_url = reverse_lazy("all_emp")

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        # Convert address_input into Address FK
        address_text = form.cleaned_data.get('address_input', '').strip()
        if address_text:
            # Try to find exact match; if none, create a new Address with the text in the street field
            addr_obj = Address.objects.filter(street__iexact=address_text).first()
            if not addr_obj:
                addr_obj = Address.objects.create(street=address_text, city='', state='', postal_code='', country='')
            # assign to the instance before saving
            form.instance.address = addr_obj

        response = super().form_valid(form)
        messages.success(self.request, f"Employee {self.object.get_full_name()} has been added successfully.")
        return response

    def form_invalid(self, form):
        # Surface form errors to the user to aid debugging when creation fails
        errors = []
        for f, err in form.errors.items():
            errors.append(f"{f}: {', '.join(err)}")
        if errors:
            messages.error(self.request, 'Could not create employee: ' + ' | '.join(errors))
        else:
            messages.error(self.request, 'Could not create employee: unknown validation error.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Provide existing addresses for datalist suggestions
        ctx['address_suggestions'] = Address.objects.values_list('street', flat=True).distinct()[:200]
        return ctx

class EmployeeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "edit_emp.html"
    context_object_name = 'employee'
    success_url = reverse_lazy("all_emp")

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        # Convert address_input into Address FK on update as well
        address_text = form.cleaned_data.get('address_input', '').strip()
        if address_text:
            addr_obj = Address.objects.filter(street__iexact=address_text).first()
            if not addr_obj:
                addr_obj = Address.objects.create(street=address_text, city='', state='', postal_code='', country='')
            form.instance.address = addr_obj

        response = super().form_valid(form)
        messages.success(self.request, f"Employee {self.object.get_full_name()} has been updated successfully.")
        return response

    def form_invalid(self, form):
        errors = []
        for f, err in form.errors.items():
            errors.append(f"{f}: {', '.join(err)}")
        if errors:
            messages.error(self.request, 'Could not update employee: ' + ' | '.join(errors))
        else:
            messages.error(self.request, 'Could not update employee: unknown validation error.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['address_suggestions'] = Address.objects.values_list('street', flat=True).distinct()[:200]
        return ctx

class EmployeeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Employee
    template_name = "remove_emp.html"
    success_url = reverse_lazy("all_emp")

    def test_func(self):
        return self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        employee = self.get_object()
        messages.success(request, f"Employee {employee.get_full_name()} has been removed successfully.")
        return super().delete(request, *args, **kwargs)

def export_employees_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employees.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Employee ID', 'Name', 'Email', 'Phone', 'Department', 'Role', 
                    'Status', 'Hire Date', 'Salary', 'Bonus'])
    
    employees = Employee.objects.select_related('dept', 'role').all()
    for emp in employees:
        writer.writerow([
            emp.employee_id,
            emp.get_full_name(),
            emp.email,
            emp.phone,
            emp.dept.name,
            emp.role.name,
            emp.get_employment_status_display(),
            emp.hire_date,
            emp.salary,
            emp.bonus
        ])
    
    return response

def export_employees_excel(request):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # Add header formatting
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#0d6efd',
        'color': 'white',
        'border': 1
    })
    
    # Write headers
    headers = ['Employee ID', 'Name', 'Email', 'Phone', 'Department', 'Role', 
              'Status', 'Hire Date', 'Salary', 'Bonus']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Write data
    employees = Employee.objects.select_related('dept', 'role').all()
    for row, emp in enumerate(employees, start=1):
        data = [
            emp.employee_id,
            emp.get_full_name(),
            emp.email,
            emp.phone,
            emp.dept.name,
            emp.role.name,
            emp.get_employment_status_display(),
            emp.hire_date.strftime('%Y-%m-%d'),
            emp.salary,
            emp.bonus
        ]
        for col, value in enumerate(data):
            worksheet.write(row, col, value)
    
    # Format columns
    worksheet.set_column('A:J', 15)  # Set width for all columns
    
    workbook.close()
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="employees.xlsx"'
    
    return response
