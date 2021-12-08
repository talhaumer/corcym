from django.db import transaction
from rest_framework import serializers
from support.models import EmailSupport, Donation, HowCanWeHelpYou, IAm


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

class EmailSerializer(serializers.ModelSerializer):
	first_name = serializers.CharField(required= True)
	last_name = serializers.CharField(required= True)
	message = serializers.CharField(required = True)
	email = serializers.EmailField(required=True)
	state =serializers.CharField(required = True, allow_blank= True, allow_null = True)
	phone_number = serializers.CharField(required=True, allow_blank= True, allow_null = True)
	i_am = serializers.SerializerMethodField(required=False, read_only=True)
	i_am_id = serializers.IntegerField(required=True, write_only=True)
	city = serializers.CharField(required=True, allow_blank= True, allow_null = True)
	country = serializers.CharField(required=True)
	how_can_we_help = serializers.SerializerMethodField(required=False, read_only=True)
	how_can_we_help_id = serializers.IntegerField(required=True, write_only=True)



	class Meta:
		model = EmailSupport
		fields = ('id', 'country', 'city','first_name','i_am', 'i_am_id','last_name','email','message','state', 'phone_number', 'how_can_we_help', 'how_can_we_help_id')


	def create(self, validated_data):
		return EmailSupport.objects.create(**validated_data)


	# def get_city(self, obj):
	# 	return obj.city.cities_name

	def get_i_am(self, obj):
		return obj.i_am.title

	def get_how_can_we_help(self, obj):
		return obj.how_can_we_help.name




# class CitiesSerializer(serializers.ModelSerializer):
# 	cities_name = serializers.CharField(required= True)
# 	cities_code = serializers.CharField(read_only=True)
# 	class Meta:
# 		model = Cities
# 		fields = ['id','cities_name','cities_code']
# 		# read_only_fields = ('created','updated')
	
# 	def create(self, validated_data):
# 		return Cities.objects.create(**validated_data)

# 	def update(self, instance, validated_data):
# 		instance.cities_name = validated_data.get('cities_name', instance.cities_name)
# 		instance.save()
# 		return instance


# class CountriesSerializer(serializers.ModelSerializer):
# 	countries_name = serializers.CharField(required= True)
# 	countries_code = serializers.CharField(read_only=True)
# 	class Meta:
# 		model = Countries
# 		fields = ['id','countries_name','countries_code']
# 		# read_only_fields = ('created','updated')
	
# 	def create(self, validated_data):
# 		return Countries.objects.create(**validated_data)

# 	def update(self, instance, validated_data):
# 		instance.countries_name = validated_data.get('countries_name', instance.countries_name)
# 		instance.save()
# 		return instance



class DonationEmailSerializer(serializers.ModelSerializer):
	applicant_organization = serializers.CharField(required= True)
	name = serializers.CharField(required = True,  allow_blank= True, allow_null = True)
	applicant_organization_address =serializers.CharField(required=True)
	email = serializers.EmailField(required=True)
	organization_type = serializers.CharField(required=True)
	organization_tax_id = serializers.CharField(required = True,  allow_blank= True, allow_null = True)
	website = serializers.CharField(required = True,  allow_blank= True, allow_null = True)
	w9_form = serializers.FileField(required = False, allow_empty_file=False, allow_null=True)
	type_of_request = ChoiceField(choices = Donation.TYPE_OF_REQUEST)
	country = serializers.CharField(required=True)
	notes = serializers.CharField(required = False, allow_blank= True, allow_null = True)



	class Meta:
		model = Donation
		fields = ('id','country', 'email','type_of_request','w9_form','website', 'organization_tax_id','organization_type','applicant_organization_address','name', 'applicant_organization', 'notes')


	def create(self, validated_data):
		return Donation.objects.create(**validated_data)


	def get_country(self, obj):
		return obj.country.countries_name



class HowCanWeHelpYouSerializer(serializers.ModelSerializer):
	name = serializers.CharField(read_only = True)

	class Meta:
		model = HowCanWeHelpYou
		fields = ['id', 'name']


class WhoIAmViewSerializer(serializers.ModelSerializer):
	title = serializers.CharField(read_only = True)

	class Meta:
		model = IAm
		fields = ['id', 'title']



class EmailCountrySerializer(serializers.ModelSerializer):
	country = serializers.CharField(required=True)

	class Meta:
		model = EmailSupport
		fields = ['country']


class EmailCitySerializer(serializers.ModelSerializer):
	city = serializers.CharField(required=True)

	class Meta:
		model = EmailSupport
		fields = ['city']


class DonationCountrySerializer(serializers.ModelSerializer):
	country = serializers.CharField(required=True)

	class Meta:
		model = Donation
		fields = ['country']



class TypeRequestSerializer(serializers.ModelSerializer):
	type_of_request = ChoiceField(choices = Donation.TYPE_OF_REQUEST)
	class Meta:
		model = Donation
		fields = ['id','type_of_request']