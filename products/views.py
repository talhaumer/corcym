import boto3
from botocore.exceptions import ClientError, ParamValidationError
from django.core.exceptions import FieldError
from rest_framework import status
from rest_framework.permissions import AllowAny

from corcym.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_STORAGE_BUCKET_NAME,
    PATH_P,
)
from news.pagination import CustomPagination
from products.models import Products
from products.serializers import ProductSerializers
from support.views import BaseAPIView


# Create your views here.
class AddProductView(BaseAPIView):
    permission_classes = (AllowAny,)

    def upload_to_aws(self, local_file, bucket, s3_file):
        s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        try:
            a = s3.upload_file(local_file, bucket, s3_file)
            return True
        except FileNotFoundError:
            return False
        except NoCredentialsError:
            return False
        except s3.exceptions:
            print("known error occured")
        except ClientError as e:
            print("Unexpected error: %s" % e)

    def post(self, request):
        try:
            data = request.data
            serializer = ProductSerializers(data=data)
            if serializer.is_valid():
                WebinarSaved = serializer.save()
                return self.send_response(
                    success=True,
                    code=f"201",
                    status_code=status.HTTP_201_CREATED,
                    description="Product is created",
                )
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=serializer.errors,
            )
        except WebinarRegistration.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Product doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


class ProductsGetView(BaseAPIView, CustomPagination):
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

    def get(self, request, pk=None):
        try:
            products = Products.objects.all()
            results = self.paginate_queryset(products, request, view=self)
            serializer = ProductSerializers(results, many=True)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="200",
                description="Products Details",
                log_description="",
            )
        except Products.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Products doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


class BiologicalProductsGetView(BaseAPIView, CustomPagination):
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

    def get(self, request, pk=None):
        try:
            products = Products.objects.filter(product_type=2)
            results = self.paginate_queryset(products, request, view=self)
            serializer = ProductSerializers(results, many=True)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="200",
                description="Products Details",
                log_description="",
            )
        except Products.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Products doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)


class MechanicalProductsGetView(BaseAPIView, CustomPagination):
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

    def get(self, request, pk=None):
        try:
            products = Products.objects.filter(product_type=1)
            results = self.paginate_queryset(products, request, view=self)
            serializer = ProductSerializers(results, many=True)
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                code="200",
                description="Products Details",
                log_description="",
            )
        except Products.DoesNotExist:
            return self.send_response(
                code=f"422",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Products doesn't exists",
            )
        except FieldError:
            return self.send_response(
                code=f"500",
                description="Cannot resolve keyword given in 'order_by' into field",
            )
        except Exception as e:
            return self.send_response(code=f"500", description=e)
