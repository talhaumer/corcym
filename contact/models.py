from django.db import models
from django.utils.text import slugify
from model_utils import Choices


# Create your models here.
class IWouldLikeTo(models.Model):
	title = models.CharField(db_column= "Title", max_length = 255)
	title_code = models.SlugField(max_length=255, unique=True, default= '')
	class Meta:
		db_table = 'IWouldLikeTo'

	def __str__(self):
		return self.title

	def save(self, *args, **kwargs):
		try:
			if not self.pk:
				self.title_code = slugify(self.title)
			super().save()
		except Exception:
			raise


class Specialty(models.Model):
	title = models.CharField(db_column= "Title", max_length = 255)
	title_code = models.SlugField(max_length=255, unique=True, default= '')
	class Meta:
		db_table = 'Specialty'

	def __str__(self):
		return self.title

	def save(self, *args, **kwargs):
		try:
			if not self.pk:
				self.title_code = slugify(self.title)
			super().save()
		except Exception:
			raise


class InterestIn(models.Model):
	title = models.CharField(db_column= "Title", max_length = 255)
	title_code = models.SlugField(max_length=255, unique=True, default= '')
	class Meta:
		db_table = 'InterestIn'


	def save(self, *args, **kwargs):
		try:
			if not self.pk:
				self.title_code = slugify(self.title)
			super().save()
		except Exception:
			raise

class Contact(models.Model):
	interest_in = models.ManyToManyField(InterestIn,  db_column='InterestInID', related_name= "interest_in_contact", default = None)
	specialty = models.ForeignKey(Specialty,  db_column='SpecialtyID', related_name= "specialty_id", on_delete = models.CASCADE)
	i_would_like_to = models.ForeignKey(IWouldLikeTo, db_column = "IWouldLikeToID", related_name = "i_would_like_to_contact", on_delete = models.CASCADE)
	notes = models.TextField(db_column = "Notes", blank = True, null = True, default = "")
	name = models.CharField(db_column = "Name", blank = True, null = True, default = "", max_length = 255)
	surname = models.CharField(db_column = "SurName", blank = True, null = True, default = "", max_length = 255)
	name_of_hospital = models.CharField(db_column = "NameOfHospital", blank = True, null = True, default = "", max_length = 255)
	email = models.EmailField(unique=False, db_column="Email", help_text="Email Field")
	city = models.CharField(db_column='City', max_length=255, null = True, blank = True)
	country = models.CharField(db_column='Country', max_length=255)
	comment = models.TextField(db_column = "Comment", blank = True, null = True, default = "")
	
	class Meta:
		db_table = "Contact"

	# def save(self, *args, **kwargs):
	# 	try:
	# 		if not self.pk:
	# 			self.country = slugify(self.country)
	# 		super().save()
	# 	except Exception:
	# 		raise


def query_contact_by_args(query_object, **kwargs):
	ORDER_COLUMN_CHOICES = Choices(
	('0', 'id'),
	('1', 'notes'),
	('2', 'name'),
	('3', 'surname'),
	('4', 'name_of_hospital'),
	('5', 'email'),
	('6', 'city'),
	('7', 'country'),
	('8', 'comment'),
	('9', 'interest_in'),
	('10', 'specialty'),
	('11', 'i_would_like_to')
	)
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
		queryset = Contact.objects.filter(query_object)
		total = queryset.count()

		if search_value:
			queryset = queryset.filter(Q(id__icontains=search_value) |
											Q(name__icontains=search_value) |
											Q(surname__icontains=search_value) |
											Q(notes__icontains=search_value) |
											Q(name_of_hospital__icontains=search_value) |
											Q(city__icontains=search_value) |
											Q(email__icontains=search_value) |
											Q(country__icontains=search_value) |
											Q(comment__icontains=search_value) |
											Q(interest_in__icontains=search_value) |
											Q(i_would_like_to__icontains=search_value) |
											Q(specialty__icontains=search_value)
											) 


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