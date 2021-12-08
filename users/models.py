import uuid
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
from django.utils.text import slugify

class AccessLevel:
	"""
	Access levels for user roles.
	"""
	OPERATOR = 200
	SUPER_ADMIN = 900

	OPERATOR_CODE = "operator"
	SUPER_ADMIN_CODE = "super_admin"

	CHOICES = (
		(OPERATOR, "Operator"),
		(SUPER_ADMIN, 'Super_Admin'),
	)

	CODES = (
		(OPERATOR, "operator"),
		(SUPER_ADMIN, 'super-admin'),
	)
	DICT = dict(CHOICES)
	CODES_DICT = dict(CODES)


class Role(models.Model):
	""" Role model."""
	name = models.CharField(db_column='Name', max_length=255, unique=True)
	code = models.SlugField(db_column='Code', default='')
	description = models.TextField(db_column='Description', null=True, blank=True)
	access_level = models.IntegerField(db_column='AccessLevel', choices=AccessLevel.CHOICES, default=AccessLevel.OPERATOR)

	class Meta:
		db_table = 'Role'


	def __str__(self):
		return f'{self.name}'

	def save(self, *args, **kwargs):
		try:
			if not self.pk:
				self.code = slugify(self.name)
			super().save()
		except Exception:
			raise

	def get_role_by_code(self=None, code=None):
		try:
			return Role.objects.get(code__exact=code)
		except Exception as e:
			print(e)
			return e


class CustomUserManager(BaseUserManager):
	def create_user(self, email, password):
		user = self.model(email=email, password=password)
		user.role = Role.objects.get(code="super_admin")
		user.set_password(password)
		user.is_superuser = False
		user.is_approved = False
		user.is_active = False
		user.save(using=self._db)
		return user

	def create_superuser(self, email, password):
		user = self.create_user(email=email, password=password)
		user.is_superuser = True
		user.is_approved = True
		user.is_active = True
		user.role = Role.objects.get(code="super_admin")
		# Group.objects.get_or_create(name='Super_Admin')
		# user.groups.add(Super_Admin)
		user.save()
		return user


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
	email = models.EmailField(unique=True)
	first_name = models.CharField(db_column = 'FirstName', max_length = 255)
	last_name = models.CharField(db_column = 'LastName', max_length = 255)
	role = models.ForeignKey(Role, db_column='RoleId', related_name='user_role', on_delete=models.CASCADE, default=None)
	is_active = models.BooleanField(db_column='IsActive',default=False)
	is_approved = models.BooleanField(
		db_column='IsApproved', default=False)
	is_staff = models.BooleanField(db_column='IsStaff',default=True)
	

	objects = CustomUserManager()
	EMAIL_FIELD = 'email'
	USERNAME_FIELD = 'email'

	class Meta:
		db_table = 'Users'

	def __str__(self):
		return f'{self.first_name}'

	@property
	def full_name(self):
		full_name = f'{self.first_name} {self.last_name}'
		return full_name.strip()

	def get_short_name(self):
		return self.first_name

	def add_role(self, role_code=''):
		try:
			return Role.objects.get(code__exact=role_code)
		except:
			return ""


	def get_user_role(self):
		return self.role.name

class UserOperator(models.Model):
	user = models.ForeignKey(User, db_column='UserId', related_name='operator_user', on_delete=models.CASCADE)
	class Meta:
		db_table = 'UserOperator'


	def add_useroperator(self=None,user=None,city_id=None):
		try:
			local_user = {}
			local_user["user"] = user
			local_admin = UserOperator.objects.create(**local_user)
			return local_admin
		except Exception as e:
			return e 