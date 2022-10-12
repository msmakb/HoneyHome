from django.shortcuts import render, redirect
from main.utils import getEmployeesTasks as EmployeeTasks
from main.utils import getUserBaseTemplate as base
from .forms import AddCustomerForm, AddPersonForm, CreateQuestionnaireForm, PublishQuestionnaireForm
from .models import Customer, Person, Questionnaire


def Dashboard(request):

    context = {'EmployeeTasks':EmployeeTasks(request)}
    return render(request, 'social_media_manager/dashboard.html', context)

def CustomersPage(request):
    Customers = Customer.objects.all()
    context = {'Customers':Customers, 'base':base(request), 'EmployeeTasks':EmployeeTasks(request)}
    return render(request, 'social_media_manager/customers.html', context)

def AddCustomerPage(request):
    person_form = AddPersonForm()
    Customer_form = AddCustomerForm()
    if request.method == 'POST':
        person_form = AddPersonForm(request.POST)
        Customer_form = AddCustomerForm(request.POST)
        if person_form.is_valid() and Customer_form.is_valid():
            person_form.save()
            person = Person.objects.all().order_by('-id')[0]
            instagram = Customer_form['instagram'].value()
            shopee = Customer_form['shopee'].value()
            facebook = Customer_form['facebook'].value()
            Customer.objects.create(person=person, instagram=instagram, 
                                    shopee=shopee, facebook=facebook)
            return redirect('CustomersPage')

    context = {'PersonForm':person_form, 'CustomerForm':Customer_form, 'base':base(request), 'EmployeeTasks':EmployeeTasks(request)}
    return render(request, 'social_media_manager/add_customer.html', context) 

def UpdateCustomerPage(request, pk):
    customer = Customer.objects.get(id=pk)
    person = Person.objects.get(id=customer.person.id)
    PersonForm = AddPersonForm(instance=person)
    CustomerForm = AddCustomerForm(instance=customer)
    if request.method == 'POST':
        PersonForm = AddPersonForm(request.POST, instance=person)
        CustomerForm = AddCustomerForm(request.POST, instance=customer)
        if PersonForm.is_valid() and CustomerForm.is_valid():
            PersonForm.save()
            CustomerForm.save()
            return redirect('CustomersPage')
    
    context = {'PersonForm':PersonForm, 'CustomerForm':CustomerForm, 'base':base(request), 'EmployeeTasks':EmployeeTasks(request)}
    return render(request, 'social_media_manager/update_customer.html', context) 

def DeleteCustomerPage(request, pk):
    customer = Customer.objects.get(id=pk)
    if request.method == "POST":
        customer.delete()
        return redirect('CustomersPage')

    context = {'Customer':customer, 'base':base(request), 'EmployeeTasks':EmployeeTasks(request)}
    return render(request, 'social_media_manager/delete_customer.html', context)

def QuestionnairesPage(request):
    Questionnaires = Questionnaire.objects.all()

    context = {'Questionnaires':Questionnaires, 'base':base(request), 'EmployeeTasks':EmployeeTasks(request)}
    return render(request, 'social_media_manager/questionnaires.html', context)

def CreateQuestionnairePage(request):
    form = CreateQuestionnaireForm()
    if request.method == "POST":
        form = CreateQuestionnaireForm(request.POST)
        if form.is_valid:
            form.save()
        return redirect('QuestionnairesPage')

    context = {'form':form, 'base':base(request), 'EmployeeTasks':EmployeeTasks(request)}
    return render(request, 'social_media_manager/create_questionnaire.html', context)

def QuestionnairePage(request, pk):
    questionnaire = Questionnaire.objects.get(id=pk)

    context = {'Questionnaire':questionnaire, 'base':base(request), 'EmployeeTasks':EmployeeTasks(request)}
    return render(request, 'social_media_manager/questionnaire.html', context)

def PublishQuestionnairePage(request, pk):
    form = PublishQuestionnaireForm()
    questionnaire = Questionnaire.objects.get(id=pk)
    if request.method == "POST":
        form = PublishQuestionnaireForm(request.POST)
        if form.is_valid:
            questionnaire.status = "Running"
            questionnaire.period = int(form['period'].value())
            questionnaire.save()
    
        return redirect('QuestionnairePage', pk)

    context = {'form':form, 'Questionnaire':questionnaire, 'base':base(request), 'EmployeeTasks':EmployeeTasks(request)}
    return render(request, 'social_media_manager/publish_questionnaire.html', context)

def ColesQuestionnairePage(request, pk):
    questionnaire = Questionnaire.objects.get(id=pk)
    if request.method == "POST":
        questionnaire.status = "Closed"
        questionnaire.save()
    
        return redirect('QuestionnairePage', pk)

    context = {'Questionnaire':questionnaire, 'base':base(request), 'EmployeeTasks':EmployeeTasks(request)}
    return render(request, 'social_media_manager/close_questionnaire.html', context)

def EditQuestionnairePage(request, pk):
    questionnaire = Questionnaire.objects.get(id=pk)
    form = CreateQuestionnaireForm(instance=questionnaire)
    if request.method == "POST":
        form = CreateQuestionnaireForm(request.POST, instance=questionnaire)
        if form.is_valid:
            form.save()
        return redirect('QuestionnairesPage')

    context = {'form':form,'Questionnaire':questionnaire, 'base':base(request), 'EmployeeTasks':EmployeeTasks(request)}
    return render(request, 'social_media_manager/edit_questionnaire.html', context)

def DeleteQuestionnairePage(request, pk):
    questionnaire = Questionnaire.objects.get(id=pk)
    if request.method == "POST":
        questionnaire.delete()
        return redirect('QuestionnairesPage')

    context = {'Questionnaire':questionnaire, 'base':base(request), 'EmployeeTasks':EmployeeTasks(request)}
    return render(request, 'social_media_manager/delete_questionnaire.html', context)

def QuestionnaireQuestionsPage(request, pk):
    questionnaire = Questionnaire.objects.get(id=pk)

    context = {'Questionnaire':questionnaire, 'base':base(request), 'EmployeeTasks':EmployeeTasks(request)}
    return render(request, 'social_media_manager/questionnaire_questions.html', context)

def AddQuestionPage(request):

    context = {'base':base(request),'EmployeeTasks':EmployeeTasks(request)}
    return render(request, 'social_media_manager/add_question.html', context)

def QuestionnaireResultPage(request, pk):
    questionnaire = Questionnaire.objects.get(id=pk)

    context = {'Questionnaire':questionnaire, 'base':base(request), 'EmployeeTasks':EmployeeTasks(request)}
    return render(request, 'social_media_manager/questionnaire_result.html', context)



