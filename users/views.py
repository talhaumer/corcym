from django.shortcuts import render
from support.views import BaseAPIView
from users.serializers import UserSerializer, OperatorRegistrationSerializer, UpdateUserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status
from users.models import User, AccessLevel, Role
from django.db import IntegrityError
from django.core.exceptions import FieldError
from django.core.exceptions import ObjectDoesNotExist





# Create your views here.

# Api for login of corcym admin
class AuthUserLoginView(BaseAPIView):
	
	permission_classes = (AllowAny, )

	def post(self, request, pk=None):
		password = request.data.get('password', '')
		email = request.data.get('email', '')
		try:
			user = authenticate(request, email=email, password=password)
			if user:
				if user.is_active:
					oauth_token = self.get_oauth_token(email, password)
					print(oauth_token)
					if 'access_token' in oauth_token:
						serializer = UserSerializer(user)
						user_data = serializer.data
						user_data['access_token'] = oauth_token.get('access_token')
						user_data['refresh_token'] = oauth_token.get('refresh_token')
						return self.send_response(success=True,code=f'200',status_code=status.HTTP_200_OK,payload=user_data,description='You are logged in!',log_description=f'User {user_data["email"]}. with id .{user_data["id"]}. has just logged in.')
					else:
						return self.send_response(description='Something went wrong with Oauth token generation.',code=f'500')
				else:
					description = 'Your account is blocked.'
					return self.send_response(success=False,code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,payload={},description=description)
			return self.send_response(success=False,code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,payload={},description='Email or password is incorrect.')
		except Exception as e:
			return self.send_response(code=f'500',description=e)

# Create opreator admin for corcym
class OperatorResgistarationView(BaseAPIView):
	authentication_classes = ()
	permission_classes = (AllowAny, )

	def post(self, request):
		try:
			data = request.data
			print(data)
			serializer = OperatorRegistrationSerializer(data=request.data)
			if serializer.is_valid():
				serializer.save()
				print(serializer.data)
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Operator is created')
			else:
				return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except IntegrityError as i:
			print(i)
			return self.send_response(code=f'422', description="Email already exists.", status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
		except User.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="User doesn't exists")
		except FieldError:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except Exception as e:
			return self.send_response(code=f'500',description=e)


# Api for login of operator of corcym
class LoginOperatorView(BaseAPIView):
	authentication_classes = ()
	permission_classes = ()

	def post(self, request, pk=None):
		email = request.data.get('email', '')
		password = request.data.get('password', '')
		print("this data is send from clinet in our Postman\n",request.data)
		try:
			user = authenticate(request, email=email, password=password)
			# print(user.role.access_level)
			if user:
				if user.role.access_level == AccessLevel.SUPER_ADMIN:
					return self.send_response(success=False,code=f'403',status_code=status.HTTP_403_FORBIDDEN,payload={},description='You do not have permission to perform this login')
				if user.is_active:
					oauth_token = self.get_oauth_token(email, password)
					print(oauth_token)
					if 'access_token' in oauth_token:
						serializer = UserSerializer(user)
						user_data = serializer.data
						user_data['access_token'] = oauth_token.get('access_token')
						user_data['refresh_token'] = oauth_token.get('refresh_token')
						# user_data['role'] = Role.objects.get(code="operator")
						# user_data['permision_ids'] = user.get_permission_ids()
						return self.send_response(success=True,code=f'200',status_code=status.HTTP_200_OK,payload=user_data,description='You are logged in!',log_description=f'User {user_data["first_name"]}. with id .{user_data["id"]}. has just logged in.')
					else:
						return self.send_response(description='Something went wrong with Oauth token generation.',code=f'500')
				else:
					description = 'Your account is blocked.'
					return self.send_response(success=False,code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,payload={},description=description)
			return self.send_response(success=False,code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,payload={},description='Email or password is incorrect.')
		except Exception as e:
			print(e)
			return self.send_response(code=f'500',description=e)

# Update corcrym admin superadmin password
class UpdateProfileView(BaseAPIView):
	permission_classes = (AllowAny,)

	def put(self, request, pk=None):
		"""
		In this api, only **Super Admin** and **Local Admin** can login. Other users won't be able to login through this API.
		**Mandatory Fields**
		* email
		* password
		"""
		try:
			if pk:
				user = User.objects.get(id=pk)
			# else:
			#     user = User.objects.get(id=request.user.id)
			#     message = "Super Admin Updated Successfully"
			serializer = UpdateUserSerializer(user, data=request.data)
			if serializer.is_valid():
				serializer.save()
				return self.send_response(success=True,code=f'200.', status_code=status.HTTP_200_OK, 
				# payload=serializer.data, 
				description="Local Admin Updated Successfully",
				)
			else:
				return self.send_response(
					code=f'422',
					status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
					description=serializer.errors
				)
		except User.DoesNotExist:
			return self.send_response(code=f'422.', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="User Does Not Exist ")
		except Exception as e:
			return self.send_response(code=f'500',description=e)
	# def put(self, request, pk=None):
	# 	try:
	# 		id = pk
	# 		exsisting_user = User.objects.get(id=id, status = True)
	# 		print(exsisting_user)
	# 		data = request.data
	# 		print(data)
	# 		serializer = UpdateUserSerializer(instance=exsisting_user, data=data, partial=True)
	# 		if serializer.is_valid():
	# 			news_saved = serializer.save()
	# 			print(serializer.data)
	# 			return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='News is updated successfuly')
	# 		return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
	# 	except ObjectDoesNotExist:
	# 		return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No News matches the given query.")
	# 	except User.DoesNotExist:
	# 		return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="News doesn't exists")
	# 	except FieldError as f:
	# 		print(f)
	# 		return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
	# 	except Exception as e:
	# 		return self.send_response(code=f'500',description=e)