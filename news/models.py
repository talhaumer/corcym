from django.db import models
from model_utils import Choices
from django.db.models import Q

# Create your models here.



ORDER_COLUMN_CHOICES = Choices(
	('0', 'id'),
	('1', 'news_type'),
	('2', 'title'),
	('3', 'description'),
	('4', 'body'),
	('5', 'date'),
)


class News(models.Model):
	news_type = models.CharField( max_length=255,db_column='NewsType')
	title = models.TextField( db_column= 'Title')
	description = models.TextField( db_column= 'Description')
	body = models.TextField( db_column= 'Body')
	date = models.DateField(auto_now_add=True)
	status = models.BooleanField(default=True)
	deleted = models.BooleanField(default=False)

	class Meta:
		db_table = 'News'




def query_news_by_args(query_object, **kwargs):
	try:
		print("---------------query_news_by_args---------------------------")
		draw = int(kwargs.get('draw', 10)[0])
		length = int(kwargs.get('length', 0)[0])
		start = int(kwargs.get('start', 0)[0])
		search_value = kwargs.get('search[value]', None)[0]
		order_column = kwargs.get('order[0][column]', None)[0]
		order = kwargs.get('order[0][dir]', None)[0]
		# print(order_column)

		order_column = ORDER_COLUMN_CHOICES[order_column]
		
		# print(query_object)
		# django orm '-' -> desc
		if order == 'desc':
			order_column = '-' + order_column
		print(query_object)
		queryset = News.objects.filter(query_object)
		total = queryset.count()

		if search_value:
			queryset = queryset.filter(Q(id__icontains=search_value) |
											Q(news_type__icontains=search_value) |
											Q(title__icontains=search_value) |
											Q(description__icontains=search_value) |
											Q(body__icontains=search_value) |
											Q(date__icontains=search_value))

		count = queryset.count()
		queryset = queryset.order_by(order_column)[start:start + length]
		return {
			'items': queryset,
			'count': count,
			'total': total,
			'draw': draw
		}
	except Exception as e:
		print("Exception")
		print(e)
		return {
			'items': 0,
			'count': 0,
			'total': 0,
			'draw': 0
		}