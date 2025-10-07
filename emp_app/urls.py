# emp_app/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Authentication URLs
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    # Application URLs
    path("", views.IndexView.as_view(), name="index"),
    path("employees/", views.EmployeeListView.as_view(), name="all_emp"),
    path("employees/add/", views.EmployeeCreateView.as_view(), name="add_emp"),
    path("employees/<int:pk>/", views.EmployeeDetailView.as_view(), name="view_emp"),
    path("employees/<int:pk>/edit/", views.EmployeeUpdateView.as_view(), name="edit_emp"),
    path("employees/<int:pk>/delete/", views.EmployeeDeleteView.as_view(), name="remove_emp"),
    path("employees/export/csv/", views.export_employees_csv, name="export_csv"),
    path("employees/export/excel/", views.export_employees_excel, name="export_excel"),
]
