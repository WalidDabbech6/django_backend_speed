from django.urls import re_path as url
from django.urls import path, include
from .views import *


urlpatterns = [
      path('api/create', CreateFormView.as_view()),
      path('api/submit/<code>', SubmitFormView.as_view()),
      path('api/<code>/responses/', ResponsesFormView.as_view()),
      path('api/<code>/resonse/<response_code>', ResponseFormView.as_view()),
      path('api/<code>/questions', FormQuestionsView.as_view()),
      path('api/delete/<code>', DeleteFormView.as_view()),
      path('api/update/<code>', UpdateFormView.as_view()), 
      path('api/question/create/<code>', CreateQuestionView.as_view()),
      path('api/choice/create/<code>', CreateChoiceView.as_view()),
      path('api/choice/delte/<code>', DeleteChoiceView.as_view()),
      path('api/question/update/<code>', UpdateQuestionView.as_view()),
      path('api/question/delete/<code>', DeleteQuestionView.as_view()), 
      path('api/rides', RidesView.as_view()), 



   
]