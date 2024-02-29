from rest_framework import serializers
from .models import *

class FormSerializer(serializers.ModelSerializer):
    questions = serializers.PrimaryKeyRelatedField(queryset=Questions.objects.all(), many=True)
    categoryTitle = serializers.SerializerMethodField('get_category')
    class Meta:
        model = Form
        fields= '__all__'
    def get_category(self,obj):
        return obj.category.name
class ChoiceSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Choices
        fields= '__all__'

class ResponseSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Responses
        fields= '__all__'

class AnswerSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields= '__all__'

class QuestionSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields= '__all__'
    

class QuestionChoice(serializers.ModelSerializer):
    choices = ChoiceSerilizer(many=True)
    id_question = serializers.SerializerMethodField('get_id')
    title = serializers.SerializerMethodField('get_title')
    is_mandatory = serializers.SerializerMethodField('get_is_manadatory')
    type = serializers.SerializerMethodField('get_type')
    Score = serializers.SerializerMethodField('get_score')

    class Meta:
        model = Questions
        exclude = ('id','question','required','question_type','score')
    def get_id(self, obj):
        return obj.id
    def get_title(self,obj):
        return obj.question
    def get_is_manadatory(self,obj):
        return obj.required
    def get_type(self,obj):
        return obj.question_type
    def get_score(self,obj):
        return obj.score
    

class RideSerilizer(serializers.ModelSerializer):
    origin = serializers.SerializerMethodField('get_origin')
    destination = serializers.SerializerMethodField('get_destination')
    price = serializers.SerializerMethodField('get_price')
   
    class Meta:
        model = Ride
        exclude = ('id',)
    def get_origin(self, obj):
        return obj.origin
    def get_destination(self,obj):
        return obj.destination
    def get_price(self,obj):
        print(self)
        return obj.price
   