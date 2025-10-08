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
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
import base64
from io import BytesIO

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

        # Generate basic analytics charts using pandas + matplotlib and embed as base64 PNGs
        qs = Employee.objects.all().values('hire_date', 'dept__name', 'salary')
        if qs:
            df = pd.DataFrame(list(qs))
            # compute summary metrics
            try:
                salaries_series = pd.to_numeric(df['salary'].fillna(0))
                context['avg_salary'] = int(salaries_series.mean()) if len(salaries_series) else 0
            except Exception:
                context['avg_salary'] = 0
            # resumes count
            context['resumes_count'] = Employee.objects.filter(resume__isnull=False).count()

            # Set plotting rcParams (green palette) directly to avoid style file lookups
            try:
                plt.rcParams.update({
                    'figure.facecolor': 'white',
                    'axes.facecolor': 'white',
                    'axes.edgecolor': '#333333',
                    'axes.grid': True,
                    'grid.color': '#e6f0ea',
                    'grid.alpha': 0.6,
                    'axes.titlesize': 12,
                    'axes.labelsize': 10,
                    'xtick.color': '#333333',
                    'ytick.color': '#333333',
                    'font.size': 9,
                })
            except Exception:
                # ignore rcParam failures and use defaults
                pass
            primary_green = '#198754'
            accent_green = '#2f9d5c'
            light_green = '#a8e6cf'
            # Hires by month
            try:
                df['hire_date'] = pd.to_datetime(df['hire_date'])
                hires = df.groupby(df['hire_date'].dt.to_period('M')).size()
                # Make hires chart wider and clearer: formatted date ticks and integer y-axis
                fig, ax = plt.subplots(figsize=(9, 3.5), dpi=100)
                hires.index = hires.index.to_timestamp()
                ax.plot(hires.index, hires.values, marker='o', color=primary_green, linewidth=2)
                ax.fill_between(hires.index, hires.values, color=light_green, alpha=0.45)
                ax.set_title('Hires by Month')
                ax.set_ylabel('Hires')
                # Format x-axis as Month Year
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
                plt.setp(ax.get_xticklabels(), rotation=35, ha='right')
                # Ensure y-axis shows integer ticks starting at 0
                max_hires = int(hires.values.max()) if len(hires.values) else 0
                ax.set_ylim(0, max_hires + 1)
                ax.yaxis.set_major_locator(mtick.MaxNLocator(integer=True))
                ax.grid(True, alpha=0.35)
                # annotate points
                for x, y in zip(hires.index, hires.values):
                    ax.annotate(str(int(y)), xy=(x, y), xytext=(0, 6), textcoords='offset points', ha='center', fontsize=9)
                buf = BytesIO(); fig.tight_layout(); fig.savefig(buf, format='png'); buf.seek(0)
                context['chart_hires'] = base64.b64encode(buf.getvalue()).decode('utf-8')
                plt.close(fig)
            except Exception:
                context['chart_hires'] = None

            # Employees by department
            try:
                dept_counts = df['dept__name'].value_counts()
                # Department counts: larger, rotated labels and bar annotations
                fig, ax = plt.subplots(figsize=(8, 3.5), dpi=100)
                colors = [accent_green if i % 2 == 0 else primary_green for i in range(len(dept_counts))]
                bars = ax.bar(dept_counts.index.astype(str), dept_counts.values, color=colors, edgecolor='#ffffff')
                ax.set_title('Employees by Department')
                ax.set_ylabel('Count')
                plt.setp(ax.get_xticklabels(), rotation=35, ha='right')
                # annotate bars with counts
                for bar in bars:
                    h = int(bar.get_height())
                    ax.annotate(str(h), xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 6), textcoords='offset points', ha='center', fontsize=9)
                ax.yaxis.set_major_locator(mtick.MaxNLocator(integer=True))
                buf = BytesIO(); fig.tight_layout(); fig.savefig(buf, format='png'); buf.seek(0)
                context['chart_dept'] = base64.b64encode(buf.getvalue()).decode('utf-8')
                plt.close(fig)
            except Exception:
                context['chart_dept'] = None

            # Salary distribution
            try:
                salaries = pd.to_numeric(df['salary'].fillna(0))
                # Salary distribution: better x-axis formatting with thousands separators
                fig, ax = plt.subplots(figsize=(8, 3.5), dpi=100)
                bins = min(10, max(3, int(len(salaries) / 2))) if len(salaries) > 0 else 10
                ax.hist(salaries, bins=bins, color=accent_green, edgecolor='white')
                ax.set_title('Salary Distribution')
                ax.set_xlabel('Salary')
                ax.set_ylabel('Number of Employees')
                # Format x ticks with thousands separator
                ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, pos: f"{int(x):,}"))
                plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
                ax.grid(axis='y', alpha=0.35)
                buf = BytesIO(); fig.tight_layout(); fig.savefig(buf, format='png'); buf.seek(0)
                context['chart_salary'] = base64.b64encode(buf.getvalue()).decode('utf-8')
                plt.close(fig)
            except Exception:
                context['chart_salary'] = None
        else:
            context['chart_hires'] = context['chart_dept'] = context['chart_salary'] = None

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
