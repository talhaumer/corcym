from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework.status import is_server_error
from django.core.exceptions import FieldError
from django.core.exceptions import ObjectDoesNotExist
from corcym import settings
from requests.auth import HTTPBasicAuth
import requests
from products.models import Products
from products.serializers import ProductSerializers
from django.db.models import Q
import time
from django.db.models import Count
from support.views import BaseAPIView
from datetime import date
from webinars.webinar_pdf import genrate_webinar_pdf
from corcym.settings import PATH_P
from corcym.settings import AWS_STORAGE_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, PATH_P
from botocore.exceptions import ClientError, ParamValidationError
import boto3
from webinars.webinar_reg_pdf import genrate_webinar_reg_pdf
from news.pagination import CustomPagination

# Create your views here.
class AddProductView(BaseAPIView):
	permission_classes = (AllowAny, )

	def upload_to_aws(self, local_file, bucket, s3_file):
		s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
			aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
		try:
			a = s3.upload_file(local_file, bucket, s3_file)
			print("Upload Successful", a)
			return True
		except FileNotFoundError:
			print("The file was not found")
			return False
		except NoCredentialsError:
			print("Credentials not available")
			return False
		except s3.exceptions:
			print("known error occured")
		except ClientError as e:
			print("Unexpected error: %s" % e)


	# def get(self, request, pk=None):
	# 	try:
	# 		if pk is not None:
	# 			webinars = WebinarRegistration.objects.get(id=pk)
	# 			serializer = WebinarRegistrationSerializers(webinars)
	# 			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of Webinar Registration',log_description='')
	# 		webinars = WebinarRegistration.objects.all()
	# 		serializer = WebinarRegistrationSerializers(webinars, many=True)
	# 		return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='Details of serializer',log_description='')
	# 	except WebinarRegistration.DoesNotExist:
	# 		return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="WebinarRegistration doesn't exists")
	# 	except FieldError:
	# 		return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
	# 	except Exception as e:
	# 		print(e)
	# 		return self.send_response(code=f'500',description=e)


	def post(self, request):
		try:
			data = request.data
			serializer = ProductSerializers(data= data)
			if serializer.is_valid():
				WebinarSaved = serializer.save()
				# path = f"{PATH_P}webuinar_registration_{serializer.data['first_name']}.pdf"
				# genrate_webinar_reg_pdf(serializer.data, path)
				# a = self.upload_to_aws(local_file =path,bucket = 'corcym', s3_file = f"upload/webuinar_registration_{serializer.data['first_name']}.pdf")
				# print( f"https://corcym.s3.eu-central-1.amazonaws.com/uploads/webuinar_registration_{serializer.data['first_name']}.pdf")
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='Product is created')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except WebinarRegistration.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Product doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)


class ProductsGetView(BaseAPIView, CustomPagination):
	permission_classes = (AllowAny, )
	pagination_class = CustomPagination
	def get(self, request, pk=None):
		try:
			products = Products.objects.all()
			results = self.paginate_queryset(products, request, view=self)
			serializer = ProductSerializers(results, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '200',description='Products Details',log_description='')
		except Products.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Products doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)


class BiologicalProductsGetView(BaseAPIView, CustomPagination):
	permission_classes = (AllowAny, )
	pagination_class = CustomPagination
	def get(self, request, pk=None):
		try:
			products = Products.objects.filter(product_type = 2)
			results = self.paginate_queryset(products, request, view=self)
			serializer = ProductSerializers(results, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '200',description='Products Details',log_description='')
		except Products.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Products doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)



class MechanicalProductsGetView(BaseAPIView, CustomPagination):
	permission_classes = (AllowAny, )
	pagination_class = CustomPagination
	def get(self, request, pk=None):
		try:
			products = Products.objects.filter(product_type = 1)
			results = self.paginate_queryset(products, request, view=self)
			serializer = ProductSerializers(results, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '200',description='Products Details',log_description='')
		except Products.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="Products doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)