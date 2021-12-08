from django.db import transaction
from rest_framework import serializers
from contact.models import Contact, Specialty, IWouldLikeTo, InterestIn




class ContactSerializers(serializers.ModelSerializer):
	notes = serializers.CharField(required = False ,  allow_blank = True, allow_null = True)
	comment  = serializers.CharField(required = False ,  allow_blank = True, allow_null = True)
	name = serializers.CharField(required= True)
	surname = serializers.CharField(required= True)
	email = serializers.EmailField(required=True)
	city = serializers.CharField(required=True, allow_blank= True, allow_null = True)
	country = serializers.CharField(required=True)
	name_of_hospital = serializers.CharField(required= True)
	interest_in = serializers.StringRelatedField(required=False, read_only=True)
	specialty = serializers.SerializerMethodField(required=False, read_only=True)
	i_would_like_to = serializers.SerializerMethodField(required=False, read_only=True)
	interest_in_id = serializers.ListField(required=True, write_only=True)
	specialty_id = serializers.IntegerField(required=True, write_only=True)
	i_would_like_to_id = serializers.IntegerField(required=True, write_only=True)

	class Meta:
		model = Contact
		fields = ('id', 'country', 'notes','comment','city','name','name_of_hospital','surname','email', 'interest_in', 'specialty', 'i_would_like_to', 'interest_in_id', 'specialty_id', 'i_would_like_to_id')


	def create(self, validated_data):
		try:
			interest_in_id = validated_data.pop('interest_in_id')
			contact = Contact.objects.create(**validated_data)
			contact.save()
			if interest_in_id:
				contact.interest_in.add(*interest_in_id)
			return contact
		except Exception as e:
			print(e)


	def get_interest_in(self, obj):
		return obj.interest_in.title

	def get_i_would_like_to(self, obj):
		return obj.i_would_like_to.title

	def get_specialty(self, obj):
		return obj.specialty.title



class IWouldLikeSerializers(serializers.ModelSerializer):
	title = serializers.CharField(read_only = True)
	title_code = serializers.CharField(read_only = True)

	class Meta:
		model  = IWouldLikeTo
		fields = ['id', 'title', 'title_code']


class SpecialtySerializers(serializers.ModelSerializer):
	title = serializers.CharField(read_only = True)
	title_code = serializers.CharField(read_only = True)

	class Meta:
		model  = Specialty
		fields = ['id', 'title', 'title_code']


class InterestInSerializers(serializers.ModelSerializer):
	title = serializers.CharField(read_only = True)
	title_code = serializers.CharField(read_only = True)

	class Meta:
		model  = InterestIn
		fields = ['id', 'title', 'title_code']