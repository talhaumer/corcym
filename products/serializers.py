from django.db import transaction
from rest_framework import serializers
from products.models import Products

class ChoiceField(serializers.ChoiceField):

	def to_representation(self, obj):
		if obj == '' and self.allow_blank:
			return obj
		return self._choices[obj]

	def to_internal_value(self, data):
		# To support inserts with the value
		if data == '' and self.allow_blank:
			return ''

		for key, val in self._choices.items():
			if val == data:
				return key
		self.fail('invalid_choice', input=data)


class ProductSerializers(serializers.ModelSerializer):
	product_name = serializers.CharField(required= True)
	doctor_name = serializers.CharField(required= True)
	product_type = ChoiceField(choices = Products.PRODUCT_TYPE)
	description = serializers.CharField(required=True)
	video_link = serializers.CharField(required=True, allow_blank= True, allow_null = True)
	country = serializers.CharField(required=True)
	doctor_image = serializers.ImageField(required= True)


	class Meta:
		model = Products
		fields = ('id', 'country', 'product_name', 'doctor_name','product_type','description','video_link','doctor_image')


	def create(self, validated_data):
		return Products.objects.create(**validated_data)