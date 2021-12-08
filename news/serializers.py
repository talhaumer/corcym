from rest_framework import serializers
from news.models import News



class NewsSerializers(serializers.ModelSerializer):
	id = serializers.IntegerField(read_only = True)
	news_type = serializers.CharField(required = True)
	title = serializers.CharField(required = True)
	description = serializers.CharField(required = True)
	date = serializers.DateField(read_only = True)
	body = serializers.CharField(required = True)
	status = serializers.BooleanField(read_only = True)


	class Meta:
		model = News
		fields = ['id', 'news_type', 'title', 'description', 'body', 'status', 'date']

	def create(self, validated_data):
		news = News.objects.create(**validated_data)
		return news

	def update(self, instance, validated_data):
		instance.news_type = validated_data.get('news_type', instance.news_type)
		instance.title = validated_data.get('title', instance.title)
		instance.description = validated_data.get('description', instance.description)
		instance.body = validated_data.get('body', instance.body)
		instance.save()
		return instance


class NewsTableSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(read_only = True)
	news_type = serializers.CharField(read_only = True)
	title = serializers.CharField(read_only = True)
	description = serializers.CharField(read_only = True)
	body = serializers.CharField(read_only = True)
	date = serializers.DateField(read_only = True)
	status = serializers.BooleanField(read_only = True)

	class Meta:
		model = News
		fields = ['id', 'news_type', 'title', 'description', 'body', 'status', 'date']