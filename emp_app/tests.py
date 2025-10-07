from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Employee, Department, Role, Address
from django.utils import timezone
import os


class EmployeeResumeTest(TestCase):
	def setUp(self):
		self.dept = Department.objects.create(name='Engineering', location='HQ')
		self.role = Role.objects.create(name='Developer')
		self.addr = Address.objects.create(street='1 Main St', city='City', state='State', postal_code='12345')

	def test_create_employee_with_resume(self):
		small_pdf = SimpleUploadedFile('resume.pdf', b'%PDF-1.4 test pdf content', content_type='application/pdf')
		emp = Employee.objects.create(
			first_name='Test',
			last_name='User',
			email='test@example.com',
			phone='+911234567890',
			date_of_birth='1990-01-01',
			profile_picture=None,
			resume=small_pdf,
			address=self.addr,
			employee_id='EMP001',
			dept=self.dept,
			role=self.role,
			hire_date=timezone.now().date(),
			salary=1000.00
		)
		self.assertIsNotNone(emp.resume)
		# Stored filename may be altered by storage backend to avoid collisions.
		# Ensure it still contains the original base name and has .pdf extension.
		basename = os.path.basename(str(emp.resume))
		self.assertIn('resume', basename)
		self.assertTrue(basename.lower().endswith('.pdf'))
