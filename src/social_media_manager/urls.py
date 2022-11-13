from django.urls import path
from . import views


app_name = 'social_media_manager'
urlpatterns = [
    path('Dashboard', views.Dashboard, name='SocialMediaManagerDashboard'),
    path('Customers', views.CustomersPage, name='CustomersPage'),
    path('Add-Customer', views.AddCustomerPage, name='AddCustomerPage'),
    path('Customer/Update/<str:pk>',
         views.UpdateCustomerPage, name="UpdateCustomerPage"),
    path('Customer/Delete/<str:pk>',
         views.DeleteCustomerPage, name="DeleteCustomerPage"),
    path('Questionnaires', views.QuestionnairesPage, name='QuestionnairesPage'),
    path('Create-Questionnaire', views.CreateQuestionnairePage,
         name='CreateQuestionnairePage'),
    path('Questionnaire/Info/<str:pk>',
         views.QuestionnairePage, name='QuestionnairePage'),
    path('Publish-Questionnaire/<str:pk>',
         views.PublishQuestionnairePage, name='PublishQuestionnairePage'),
    path('Coles-Questionnaire/<str:pk>',
         views.ColesQuestionnairePage, name='ColesQuestionnairePage'),
    path('Edit-Questionnaire/<str:pk>',
         views.EditQuestionnairePage, name='EditQuestionnairePage'),
    path('Delete-QuestionnairePage/<str:pk>',
         views.DeleteQuestionnairePage, name='DeleteQuestionnairePage'),
    path('Questionnaire/Questions/<str:pk>',
         views.QuestionnaireQuestionsPage, name='QuestionnaireQuestionsPage'),
    path('Questionnaire/Result/<str:pk>',
         views.QuestionnaireResultPage, name='QuestionnaireResultPage'),
    path('Add-Question', views.AddQuestionPage, name='AddQuestionPage'),
]
