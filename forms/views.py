from django.shortcuts import render
from rest_framework.views import APIView 
from rest_framework import generics , status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.serializers import serialize
from django.http import JsonResponse

from aymenProject.pagination import PageNumberPaginationDataOnly
from .serializers import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
import random
import string
import json

class CreateFormView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FormSerializer
    pagination_class = PageNumberPaginationDataOnly
    def get_queryset(self):
        query_set = Form.objects.all()
        return query_set
      
   
    def post(self,request):       
        code = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(30))
        choices = Choices(choice = "Option 1")
        choices.save()
        question = Questions(question_type = "multiple choice", question= "Untitled Question", required= False)
        question.save()
        question.choices.add(choices)
        category = Category.objects.get(pk=request.data["category"])
        question.save()
        form = Form(code = code, title = request.data['title'], creator=request.user)
        form.save()
        form.questions.add(question)
        form.category = category
        form.save()
        return Response(FormSerializer(form).data,status=status.HTTP_201_CREATED) 

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class SubmitFormView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self,request,code):
        answers = json.loads(request.body.decode('utf-8')) 
        for a in answers:
            print(a,answers[a],dir(answers[a]))
        try:
            form = Form.objects.get(code = code)
            code = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(20))
            if form.authenticated_responder:
                response = Responses(response_code = code, response_to = form, responder_ip = get_client_ip(request), responder = request.user)
                response.save()
            else:
                if not form.collect_email:
                    response = Responses(response_code = code, response_to = form, responder_ip = get_client_ip(request))
                    response.save()
                else:
                    response = Responses(response_code = code, response_to = form, responder_ip = get_client_ip(request), responder_email=request.POST["email-address"])
                    response.save()
            for i in answers:
                print('******',i)
                #Excluding csrf token
                if i == "csrfmiddlewaretoken" or i == "email-address":
                    continue
                question = form.questions.get(id = i)
                for j in answers[i]:
                    answer = Answer(answer=j, answer_to = question)
                    answer.save()
                    response.response.add(answer)
                    response.save()
            return Response(FormSerializer(form).data,status=status.HTTP_200_OK) 
 
        except Form.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)       
        
    # def get(self,request,code):
    #     try:
    #         form = Form.objects.get(code = code)
    #         return Response(data=FormSerializer(form).data)
    #     except Form.DoesNotExist:
    #         return Response(status=status.HTTP_404_NOT_FOUND) 
class ResponsesFormView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request,code):
        try:
            form = Form.objects.get(code = code)
            responsesSummary = []
            choiceAnswered = {}
            filteredResponsesSummary = {}
            for question in form.questions.all():
                answers = Answer.objects.filter(answer_to = question.id)
                if question.question_type == "multiple choice" or question.question_type == "checkbox":
                    choiceAnswered[question.question] = choiceAnswered.get(question.question, {})
                    for answer in answers:
                        choice = answer.answer_to.choices.get(choice = answer.answer).choice
                        choiceAnswered[question.question][choice] = choiceAnswered.get(question.question, {}).get(choice, 0) + 1
                responsesSummary.append({"question": QuestionSerilizer(question).data, "answers":json.loads(serialize("json",answers)) })
            for answr in choiceAnswered:
                filteredResponsesSummary[answr] = {}
                keys = choiceAnswered[answr].values()
                for choice in choiceAnswered[answr]:
                    filteredResponsesSummary[answr][choice] = choiceAnswered[answr][choice]
            resp = Responses.objects.filter(response_to = form)
            return Response(data={
                "form": FormSerializer(form).data,
                "responses": json.loads(serialize("json",resp)),
                "responsesSummary": responsesSummary,
                "filteredResponsesSummary": filteredResponsesSummary
            },status=status.HTTP_201_CREATED) 
        except Form.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)       

class ResponseFormView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request,code,response_code):
        try:
            formInfo = Form.objects.get(code = code)
            responseInfo = Responses.objects.filter(response_code = response_code)
            total_score = 0
            score = 0
            if responseInfo.count() == 0:
                return Response(status=status.HTTP_404_NOT_FOUND)            
            else: responseInfo = responseInfo[0]
            if formInfo.is_quiz:
                for i in formInfo.questions.all():
                    total_score += i.score
                for i in responseInfo.response.all():
                    if i.answer_to.question_type == "short" or i.answer_to.question_type == "paragraph":
                        if i.answer == i.answer_to.answer_key: score += i.answer_to.score
                    elif i.answer_to.question_type == "multiple choice":
                        answerKey = None
                        for j in i.answer_to.choices.all():
                            if j.is_answer: answerKey = j.id
                        if answerKey is not None and int(answerKey) == int(i.answer):
                            score += i.answer_to.score
                _temp = []
                for i in responseInfo.response.all():
                    if i.answer_to.question_type == "checkbox" and i.answer_to.pk not in _temp:
                        answers = []
                        answer_keys = []
                        for j in responseInfo.response.filter(answer_to__pk = i.answer_to.pk):
                            answers.append(int(j.answer))
                            for k in j.answer_to.choices.all():
                                if k.is_answer and k.pk not in answer_keys: answer_keys.append(k.pk)
                            _temp.append(i.answer_to.pk)
                        if answers == answer_keys: score += i.answer_to.score 
            return Response(data= {
            "form": FormSerializer(formInfo).data,
            "response": ResponseSerilizer(responseInfo).data,
            "score": score,
            "total_score": total_score
    },status=status.HTTP_200_OK)           
        except Responses.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)            
   

    
       


class DeleteFormView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FormSerializer
    def delete(self,request,code):
        try:
            form = Form.objects.get(code = code)
        except Form.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        operation = form.delete()
        data = {}
        if operation: 
            data["sucess"] = "deleted sucessfully"
        else:
            data["failure"] = "delete failed"      
        return Response(data=data)    


class UpdateFormView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FormSerializer
    def get(self,request,code):
        try:
            form = Form.objects.get(code = code)
            return Response(data=FormSerializer(form).data)
        except Form.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND) 
    def patch(self,request,code):
        try:
            form = Form.objects.get(code = code)
            print(form.title)
        except Form.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        data=request.data.copy()
        data['code'] = form.code
        data['creator'] = form.creator.pk
        data['category'] = request.data.get('category',form.category)
        data['questions'] = request.data.get('questions', form.questions.values_list(flat=True))
        data['title'] = request.data.get('title',form.title)
        serializer = FormSerializer(form,data=data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data) 
        return Response(serializer._errors,status=status.HTTP_400_BAD_REQUEST)


class CreateQuestionView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = QuestionSerilizer
    def get_queryset(self):
        return Questions.objects.all()
    def post(self,request,code): 
        data=request.data.copy()
        form = Form.objects.get(code=code)
        choices = Choices(choice = "Option 1")
        choices.save()
        question = Questions(question_type = "multiple choice", question= data['title'], required= data['is_manadatory'])
        question.save()
        question.choices.add(choices)
        question.save()
        form.questions.add(question)
        form.save()
        return Response(FormSerializer(form).data,status=status.HTTP_201_CREATED) 

class CreateChoiceView(APIView):
    def post(self,request,code): 
        question = Questions.objects.get(id=code)
        data=request.data.copy()

        choices = Choices(choice = data['title'])
        choices.save()
        question.choices.add(choices)
        question.save()
        return Response(QuestionChoice(question).data,status=status.HTTP_201_CREATED) 

class UpdateQuestionView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = QuestionSerilizer
    def get(self,request,code):
        try:
            question = Questions.objects.get(id = code)
            return Response(data={"question":QuestionChoice(question).data})
        except Form.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND) 

    def patch(self,request,code):
        try:
            question = Questions.objects.get(pk = code)
        except Form.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        print(request.data)
        data=request.data.copy()
        data['question'] = request.data.get('question',question.question) 
        data['question_type'] = request.data.get('question_type',question.question_type) 
        data['feedback'] = request.data.get('feedback',question.feedback) 
        data['answer_key'] = request.data.get('answer_key',question.answer_key)
        data['choices'] = request.data.get('choices',question.choices.values_list(flat=True))


        serializer = QuestionSerilizer(question,data=data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data["success"] = "updated sucessfully"
            return Response(data=data) 
        return Response(serializer._errors,status=status.HTTP_400_BAD_REQUEST)
    
class DeleteQuestionView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = QuestionSerilizer
    def delete(self,request,code):
        try:
            question = Questions.objects.get(pk = code)
        except Form.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        operation = question.delete()
        data = {}
        if operation: 
            data["sucess"] = "deleted sucessfully"
        else:
            data["failure"] = "delete failed"      
        return Response(data=data)


class DeleteChoiceView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChoiceSerilizer
    def delete(self,request,code):
        try:
            choice = Choices.objects.get(pk = code)
        except Choices.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        operation = choice.delete()
        data = {}
        if operation: 
            data["sucess"] = "deleted sucessfully"
        else:
            data["failure"] = "delete failed"      
        return Response(data=data)  
    
class FormQuestionsView(APIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPaginationDataOnly
    def get(self,request,code):
        query_set = Form.objects.get(code=code)
        query = Questions.objects.filter(id__in=query_set.questions.values_list('id',flat=True))
        serializer = QuestionChoice(query,many=True)
        result = serializer.data
        data =  {
            'questions' : result
        }
        return Response(data=data)