from django.test import TestCase
from .models import Case
from django.contrib.auth.models import User

class CaseModelTest(TestCase):
    def setUp(self):
        user = User.objects.create(username='testuser')
        Case.objects.create(case_name="Test Case", description="This is a test case", created_by=user)

    def test_case_str(self):
        case = Case.objects.get(case_name="Test Case")
        self.assertEqual(str(case), "Test Case")
