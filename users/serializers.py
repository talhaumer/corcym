from django.db import transaction
from rest_framework import serializers
from users.models import User, Role, AccessLevel, UserOperator

class UserSerializer(serializers.ModelSerializer):
	email = serializers.EmailField(read_only=True)
	first_name = serializers.CharField(read_only = True)
	last_name = serializers.CharField(read_only = True)
	role = serializers.SerializerMethodField(required=False, read_only=True)
	def get_email(self, obj):
		try:
			return obj.email
		except:
			return ''

	class Meta:
		model = User
		fields = ('id', 'email', 'first_name', 'last_name', 'role')

	def get_role(self, obj):
		return obj.role.name


class OperatorRegistrationSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(read_only=True)
	first_name = serializers.CharField(required=True)
	last_name = serializers.CharField(required=True)
	is_active = serializers.BooleanField(required=False, read_only=True)
	email = serializers.EmailField(required=True)
	password = serializers.CharField(required=True)
	class Meta:
		model = User
		fields = ("id", "first_name", "last_name", "is_approved", "is_active", "email",  'password')

	def create(self, validated_data):
		with transaction.atomic():
			password = validated_data.pop('password')
			validated_data["role"] = Role.get_role_by_code(code=AccessLevel.OPERATOR_CODE)
			user = User.objects.create(**validated_data)
			user.set_password(password)
			user.save()
			UserOperator.add_useroperator(user=user)
				# raise IntegrityError
			return user

	def get_role(self, obj):
		return obj.role.name

class UpdateUserSerializer(serializers.ModelSerializer):
	first_name = serializers.CharField(read_only = False)
	last_name = serializers.CharField(read_only = False)
	password = serializers.CharField(required = False)
	class Meta:
		model = User
		fields = ('id', 'first_name', 'last_name', 'password')

	def update(self, instance, validated_data):
		with transaction.atomic():
			password = validated_data.pop('password')
			instance.first_name = validated_data.get('first_name', instance.first_name)
			instance.last_name = validated_data.get('last_name', instance.last_name)
			instance.set_password(password)
			instance.save()
			return instance