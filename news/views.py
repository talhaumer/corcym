from django.shortcuts import render
from django.shortcuts import render
from django.core.mail import EmailMessage
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework import viewsets
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework.status import is_server_error
from django.core.exceptions import FieldError
from django.core.exceptions import ObjectDoesNotExist
from corcym import settings
from requests.auth import HTTPBasicAuth
import requests
from support.views import BaseAPIView
from news.models import News, query_news_by_args
from news.serializers import NewsSerializers, NewsTableSerializer
from news.pagination import CustomPagination
from django.db.models import Q

# Create your views here.




# add corcym news
class NewsView(BaseAPIView, CustomPagination):
	permission_classes = (AllowAny, )
	pagination_class = CustomPagination
	def get(self, request, pk=None):
		try:
			news_t = request.query_params.get('type', '')
			if pk is not None:
				news = News.objects.get(id=pk, status = True)
				serializer = NewsSerializers(news)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '200',description='News Details',log_description='')
			elif news_t != '':
				news = News.objects.filter(news_type=news_t, status = True)
				serializer = NewsSerializers(news, many= True)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '200',description='News Details',log_description='')
			news = News.objects.filter(status = True)
			results = self.paginate_queryset(news, request, view=self)
			serializer = NewsSerializers(results, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '200',description='News Details',log_description='')
		except News.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="News doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)


	def post(self, request):
		try:
			data = request.data
			serializer = NewsSerializers(data= data)
			if serializer.is_valid():
				news_saved = serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='News is created successfuly')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except News.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="News doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)

	def put(self, request, pk=None):
		try:
			id = pk
			saved_news = News.objects.get(id=id, status = True)
			data = request.data
			serializer = NewsSerializers(instance=saved_news, data=data, partial=True)
			if serializer.is_valid():
				news_saved = serializer.save()
				return self.send_response(success=True, code=f'201', status_code=status.HTTP_201_CREATED, description='News is updated successfuly')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description=serializer.errors)
		except ObjectDoesNotExist:
			return self.send_response(code='422', status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description="No News matches the given query.")
		except News.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="News doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)




# get news data table
class TopNewsView(BaseAPIView, CustomPagination):
	permission_classes = (AllowAny, )
	pagination_class = CustomPagination
	def get(self, request, pk=None):
		try:
			if pk is not None:
				news = News.objects.get(id=pk, status = True)
				serializer = NewsSerializers(news)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='News Details ',log_description='')
			news = News.objects.filter(status = True).order_by('-id')[:4]
			serializer = NewsSerializers(news, many=True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='News Details ',log_description='')
		except News.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="News doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)


# soft delete of news
class PressReleaseView(BaseAPIView, CustomPagination):
	permission_classes = (AllowAny, )
	pagination_class = CustomPagination
	def get(self, request, pk=None):
		try:
			if pk is not None:
				news = News.objects.get(id=pk, status = True)
				serializer = NewsSerializers(news)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='News Details',log_description='')
			news_t = request.query_params.get('type', '')
			if news_t == "":
				news_t = 'press release'
			news = News.objects.filter(news_type=news_t, status = True)
			serializer = NewsSerializers(news, many= True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='News Details',log_description='')
		except News.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="News doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)


#
class NewsReleaseView(BaseAPIView, CustomPagination):
	permission_classes = (AllowAny, )
	pagination_class = CustomPagination
	def get(self, request, pk=None):
		try:
			if pk is not None:
				news = News.objects.get(id=pk,status = True)
				serializer = NewsSerializers(news)
				return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='News Details',log_description='')
			news_t = request.query_params.get('type', '')
			if news_t == "":
				news_t = 'news'
			news = News.objects.filter(news_type=news_t, status = True)
			serializer = NewsSerializers(news, many= True)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=serializer.data,code= '',description='News Details',log_description='')
		except News.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="News doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			return self.send_response(code=f'500',description=e)

# news datatable view 
class NewsViewSet(viewsets.ModelViewSet, BaseAPIView):
	permission_classes = (AllowAny, )
	queryset = News.objects.all()
	serializer_class = NewsTableSerializer

	def boolean(self, status):
		if status == 'true' or status == "True":
			return True
		else:
			return False

	def list(self, request, **kwargs):
		print(request.data)
		try:
			print("------------list=========")
			news_type =  request.query_params.get('news_type', None)
			status_news =  request.query_params.get('status', None)
			print(len(status_news))
			query_object = Q()
			print(query_object)
			if news_type:
				query_object &= Q(news_type = news_type)
			if status_news:
				query_object &= Q(status = self.boolean(status_news))

			query_object &= Q(deleted = False)

			print("-----------------------", query_object)
			news = query_news_by_args(query_object, **request.query_params)
			print("type of news", type(news))
			
			serializer = NewsTableSerializer(news['items'], many=True)
			print(serializer.data)
			
			result = dict()
			result['data'] = serializer.data
			result['draw'] = news['draw']
			result['recordsTotal'] = news['total']
			result['recordsFiltered'] = news['count']
			print("restlt:  \n", result)
			return self.send_response(success=True,status_code=status.HTTP_200_OK, payload=result,code= '200',description='News Details',log_description='')	
		except News.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="News doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			print(e)
			return self.send_response(code=f'500',description=e)

# soft delete of news
class DeleteNewsView(BaseAPIView, CustomPagination):
	permission_classes = (AllowAny, )
	pagination_class = CustomPagination
	def get(self, request, pk=None):
		try:
			if pk is not None:
				news = News.objects.get(id=pk)
				news.status = not news.status
				news.save()
				print(news.status)
				if news.status == False:
					return self.send_response(description= "News disabled successfuly",success=True,status_code=status.HTTP_200_OK, code='200')
				return self.send_response(description= "News enabled successfuly",success=True,status_code=status.HTTP_200_OK, code='200')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description='News not found ')
		except News.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="News doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			print(e)
			return self.send_response(code=f'500',description=e)



class DeletedNewsView(BaseAPIView, CustomPagination):
	permission_classes = (AllowAny, )
	pagination_class = CustomPagination
	def get(self, request, pk=None):
		try:
			if pk is not None:
				news = News.objects.get(id=pk)
				news.deleted = True
				news.save()
				print(news.status)
				return self.send_response(description= "News Deleted successfuly",success=True,status_code=status.HTTP_200_OK, code='200')
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, description='News not found ')
		except News.DoesNotExist:
			return self.send_response(code=f'422',status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,description="News doesn't exists")
		except FieldError:
			return self.send_response( code=f'500',description="Cannot resolve keyword given in 'order_by' into field")
		except Exception as e:
			print(e)
			return self.send_response(code=f'500',description=e)