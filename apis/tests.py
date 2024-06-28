from django.test import TestCase
from .models import User, Role
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError

class UserTest(TestCase):
    
    def setUp(self):
        self.email = "testuser@example.com"
        self.username = "testuser"
        self.password = "testpassword123"

    def create_user(self, email=None, username=None, password=None, **extra_fields):
        if email is None:
            email = self.email
        if username is None:
            username = self.username
        if password is None:
            password = self.password
        return User.objects.create_user(email=email, username=username, password=password, **extra_fields)
    
    def create_superuser(self, email=None, username=None, password=None, **extra_fields):
        if email is None:
            email = self.email
        if username is None:
            username = self.username
        if password is None:
            password = self.password
        return User.objects.create_superuser(email=email, username=username, password=password, **extra_fields)
    
    def test_user_creation(self):
        user = self.create_user()
        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.email, self.email)
        self.assertEqual(user.username, self.username)
        self.assertTrue(user.check_password(self.password))
        self.assertEqual(user.role, Role.USER)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_superuser_creation(self):
        superuser = self.create_superuser()
        self.assertTrue(isinstance(superuser, User))
        self.assertEqual(superuser.email, self.email)
        self.assertEqual(superuser.username, self.username)
        self.assertTrue(superuser.check_password(self.password))
        self.assertEqual(superuser.role, Role.ADMIN)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
    
    def test_user_creation_without_email(self):
        with self.assertRaises(ValueError):
            self.create_user(email=None)
    
    def test_user_creation_without_username(self):
        with self.assertRaises(IntegrityError):
            self.create_user(username=None)
    
    def test_unique_email(self):
        self.create_user()
        with self.assertRaises(IntegrityError):
            self.create_user(email=self.email)
    
    def test_unique_username(self):
        self.create_user()
        with self.assertRaises(IntegrityError):
            self.create_user(username=self.username)
    
    def test_string_representation(self):
        user = self.create_user()
        self.assertEqual(str(user), user.email)
