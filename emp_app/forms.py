from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Employee, Department, Role, Address

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'postal_code', 'country']
        widgets = {
            field: forms.TextInput(attrs={'class': 'form-control'})
            for field in fields
        }

class EmployeeForm(forms.ModelForm):
    hire_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )

    class Meta:
        model = Employee
        exclude = ['created_at', 'updated_at']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'dept': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'employment_status': forms.Select(attrs={'class': 'form-select'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'bonus': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_relation': forms.TextInput(attrs={'class': 'form-control'}),
        }

    # Provide a user-friendly address input (free text) that maps to Address FK
    address_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Start typing address or select from list'
        }),
        label='Address'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            # Hide the original Address FK select and replace with address_input visible to users
            if field == 'address':
                # use a hidden input for the FK to keep model binding but not show default select
                self.fields[field].widget = forms.HiddenInput()
                # Make sure the FK is not required on the form (we'll use address_input instead)
                self.fields[field].required = False
                continue
            if not isinstance(self.fields[field].widget, (forms.CheckboxInput, forms.RadioSelect)):
                self.fields[field].widget.attrs['placeholder'] = self.fields[field].label

        # If editing an instance, populate address_input with the string representation
        if self.instance and getattr(self.instance, 'address', None):
            self.fields['address_input'].initial = str(self.instance.address)

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            # Limit file size to 5MB
            max_mb = 5
            if resume.size > max_mb * 1024 * 1024:
                raise forms.ValidationError(f"Resume file size must be <= {max_mb} MB.")

            # Allow common resume file types (PDF, DOC/DOCX) and common image types (JPG/PNG)
            allowed_mimetypes = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'image/png',
                'image/jpeg'
            ]
            content_type = resume.content_type
            if content_type not in allowed_mimetypes:
                raise forms.ValidationError('Unsupported file type. Upload PDF or DOC/DOCX.')
        return resume

    def clean_address_input(self):
        # Normalize whitespace
        addr = self.cleaned_data.get('address_input', '').strip()
        return addr

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            if not phone.startswith('+'):
                phone = '+' + phone
            if not phone[1:].isdigit() or not (9 <= len(phone[1:]) <= 15):
                raise forms.ValidationError('Enter a valid phone number (+999999999).')
        return phone

    def clean_emergency_contact_phone(self):
        phone = self.cleaned_data.get('emergency_contact_phone')
        if phone:
            if not phone.startswith('+'):
                phone = '+' + phone
            if not phone[1:].isdigit() or not (9 <= len(phone[1:]) <= 15):
                raise forms.ValidationError('Enter a valid phone number (+999999999).')
        return phone

    def clean_salary(self):
        salary = self.cleaned_data.get('salary')
        if salary is not None and salary < 0:
            raise forms.ValidationError('Salary must be non-negative.')
        return salary

    def clean_bonus(self):
        bonus = self.cleaned_data.get('bonus')
        if bonus is not None and bonus < 0:
            raise forms.ValidationError('Bonus must be non-negative.')
        return bonus
