from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Application, Timetable, Type_question, Type_employee
from django.views.generic import ListView
from django.contrib.auth import models
import random


@login_required(login_url='login')
def index(request):
    user = request.user.username
    if request.user.is_superuser:
        template = 'main/index.html'
        extends = 'main/base.html'
    elif request.user.groups.filter(name='User').exists():
        return redirect('logout')
    elif request.user.groups.filter(name='Employee').exists():
        template = 'main/index.html'
        extends = 'main/base.html'
        return render(request, template, {'title': 'Главная страница', 'extends': extends})
    elif request.user.groups.filter(name='Secretary').exists():
        template = 'main/index.html'
        extends = 'main/base_secretary.html'
    else:
        template = 'main/login.html'
    tasks = Application.objects.all()
    return render(request, template,
                  {'title': 'Главная страница', 'tasks': tasks, 'extends': extends, 'name': user})


@login_required(login_url='login')
def application_secretary_search(request):
    query1 = request.GET.get('id')
    query2 = request.GET.get('date_receipt')
    query3 = request.GET.get('FIO')
    query4 = request.GET.get('type_question')
    query5 = request.GET.get('ty')
    p = True
    if query1 != "":
        object_list = Application.objects.filter(
            Q(id=query1) & Q(status=query5)
        )
    elif query2 != "":
        object_list = Application.objects.filter(
            Q(date_receipt=query2) & Q(status=query5)
        )
    elif query3 != "":
        object_list = Application.objects.filter(
            Q(FIO=query3) & Q(status=query5)
        )
    elif query4 != "":
        o = Type_question.objects.get(name=query4)
        if o:
            object_list = Application.objects.filter(
                Q(type_question=o) & Q(status=query5)
            )
    else:
        object_list = ""
        p = False
    if len(object_list) == 0:
        p = False
    return render(request, 'main/table_search.html', {'title': 'Поиск',
                                                               'applications': object_list, 'flag': p})


@login_required(login_url='login')
def application_secretary(request):
    applications = Application.objects.filter(status='Confirmed Applications')
    return render(request, 'main/application_secretary.html', {'title': 'Подтвержденные заявки',
                                                               'applications': applications})


@login_required(login_url='login')
def application_new(request):
    if request.user.groups.filter(name='Employee').exists():
        flag = True
    else:
        flag = False
    if request.user.groups.filter(name='Secretary').exists():
        return HttpResponseNotFound("<h2>У вас нет прав на эту страницу, вернитесь назад</h2><br>")
    name = request.user.username
    role = request.user.groups.first()
    applications = Application.objects.filter(status='New Applications')
    return render(request, 'main/application_new.html', {'title': 'Новые заявки', 'applications': applications,
                                                         'name': name, 'role': role, 'flag': flag})


@login_required(login_url='login')
def application_employee(request):
    if request.user.groups.filter(name='Secretary').exists():
        return HttpResponseNotFound("<h2>У вас нет прав на эту страницу, вернитесь назад</h2><br>")
    employee = User.objects.filter(groups__name='Employee')
    return render(request, 'main/application_employee.html', {'employee': employee})


def application_list(request):
    if request.user.groups.filter(name='Secretary').exists():
        return HttpResponseNotFound("<h2>У вас нет прав на эту страницу, вернитесь назад</h2><br>")
    if request.method == "GET":
        date = request.GET.get("date")
        employee = request.GET.get("FIO")
        emp = User.objects.get(id=employee)
        app = Application.objects.filter(Q(date_application=date) | Q(id_employee=employee))
        return render(request, 'main/application_list.html', {'app': app, 'date': date, 'employee': emp})
    else:
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


@login_required(login_url='login')
def create_timetable(request):
    if request.user.groups.filter(name='Secretary').exists():
        return HttpResponseNotFound("<h2>У вас нет прав на эту страницу, вернитесь назад</h2><br>")
    if request.method == "POST":
        tom = Timetable()
        tom.time = request.POST.get("time")
        tom.id_employee = request.POST.get("id_employee")
        tom.date = request.POST.get("date")
        tom.condition = request.POST.get("bool")
        try:
            t = Timetable.objects.get(Q(time=tom.time) & Q(date=tom.date) & Q(id_employee=tom.id_employee))
        except Timetable.DoesNotExist:
            tom.save()
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


@login_required(login_url='login')
def adm(request):
    if request.user.groups.filter(name='Employee').exists():
        return HttpResponseNotFound("<h2>У вас нет прав на эту страницу, вернитесь назад</h2><br>")
    if request.user.groups.filter(name='Secretary').exists():
        return HttpResponseNotFound("<h2>У вас нет прав на эту страницу, вернитесь назад</h2><br>")
    group = models.Group.objects.get(name='Employee')
    users = group.user_set.all()
    return render(request, 'main/administration.html', {'title': 'Администрация', 'users': users})


@login_required(login_url='login')
def analysis(request):
    if request.user.groups.filter(name='admin').exists():
        return HttpResponseNotFound("<h2>У вас нет прав на эту страницу, вернитесь назад</h2><br>")
    if request.user.groups.filter(name='Secretary').exists():
        return HttpResponseNotFound("<h2>У вас нет прав на эту страницу, вернитесь назад</h2><br>")
    if request.method == 'POST':
        date = request.POST.get("date")
        date2 = request.POST.get("date2")
        if not date:
            return HttpResponseNotFound("<h2>Неверное указание даты</h2><br><p>Вернитесь назад и выберите дату</p>")
        question = Type_question.objects.all()
        a = []
        names = []
        c = {}
        all_len = len(Application.objects.filter(date_application__range=(date, date2)))
        for el in question:
            i = Application.objects.filter(Q(type_question=el) & Q(date_application__range=(date, date2)))
            names.append(el.name)
            a.append(len(i))
            c[el.name] = len(i)
        col_type = len(names)
        question_is_not = len(
            Application.objects.filter(Q(status="New Applications") | Q(status="Rejected Applications")).filter(
                Q(date_application__range=(date, date2))))
        question_is_yea = len(
            Application.objects.filter(status="Confirmed Applications").filter(Q(date_application__range=(date, date2))))
        sotr = {}
        ques = {}
        all = User.objects.all()
        for el in all:
            ques['Всего'] = len(Application.objects.filter(Q(id_employee=el.id) & Q(date_application__range=(date, date2))))
            ques['Решено'] = len(Application.objects.filter(Q(id_employee=el.id) & Q(status="Confirmed Applications")
                                                            & Q(date_application__range=(date, date2))))
            ques['На рассмотрении'] = len(
                Application.objects.filter(Q(id_employee=el.id) & ~Q(status="Confirmed Applications")
                                           & Q(date_application__range=(date, date2))))
            sotr[el.username] = ques
            ques = {}
        return render(request, 'main/analysis.html', {'title': 'Поиск', 'all': a, 'all_len': all_len,
                                                      'names': names, 'c': c, 'col_type': col_type,
                                                      'question_is_not': question_is_not,
                                                      'question_is_yea': question_is_yea, 'ques': sotr})
    else:
        question = Type_question.objects.all()
        a = []
        names = []
        c = {}
        all_len = len(Application.objects.all())
        for el in question:
            i = Application.objects.filter(type_question=el)
            names.append(el.name)
            a.append(len(i))
            c[el.name] = len(i)
        col_type = len(names)
        question_is_not = len(
            Application.objects.filter(Q(status="New Applications") | Q(status="Rejected Applications")))
        question_is_yea = len(Application.objects.filter(status="Confirmed Applications"))
        sotr = {}
        ques = {}
        all = User.objects.all()
        for el in all:
            ques['Всего'] = len(Application.objects.filter(id_employee=el.id))
            ques['Решено'] = len(Application.objects.filter(Q(id_employee=el.id) & Q(status="Confirmed Applications")))
            ques['На рассмотрении'] = len(
                Application.objects.filter(Q(id_employee=el.id) & ~Q(status="Confirmed Applications")))
            sotr[el.username] = ques
            ques = {}
        return render(request, 'main/analysis.html', {'title': 'Поиск', 'all': a, 'all_len': all_len,
                                                      'names': names, 'c': c, 'col_type': col_type,
                                                      'question_is_not': question_is_not,
                                                      'question_is_yea': question_is_yea, 'ques': sotr})


@login_required(login_url='login')
def search_all(request):
    if request.user.groups.filter(name='Secretary').exists():
        return HttpResponseNotFound("<h2>У вас нет прав на эту страницу, вернитесь назад</h2><br>")
    query1 = request.GET.get('FIO')
    if User.objects.filter(username=query1).exists():
        us = User.objects.get(username=query1)
    else:
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
    if query1 != "":
        object_list = User.objects.filter(
            Q(id=us.id)
        )
        return render(request, 'main/search_administration.html', {'title': 'Поиск', 'object_list': object_list,
                                                                   'user': us})
    else:
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


@login_required(login_url='login')
def add_category(request):
    if request.user.groups.filter(name='Secretary').exists():
        return HttpResponseNotFound("<h2>У вас нет прав на эту страницу, вернитесь назад</h2><br>")
    if request.method == "POST":
        t = Type_employee()
        i = request.POST.get("id")
        m = Type_question.objects.get(id=i)
        t.id_question = m
        t.name = m.name
        id = request.POST.get("user")
        t.id_employee = id
        t.save()
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


@login_required(login_url='login')
def create_adm(request, id):
    if request.user.groups.filter(name='Secretary').exists():
        return HttpResponseNotFound("<h2>У вас нет прав на эту страницу, вернитесь назад</h2><br>")
    type_question = Type_employee.objects.filter(id_employee=id)
    type_all = Type_question.objects.all()
    for el in type_question:
        type_all = type_all.exclude(id=el.id_question.id)
    if User.objects.filter(id=id).exists():
        user = User.objects.get(id=id)
    else:
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
    return render(request, 'main/create_adm.html', {'title': 'Администрация', 'user': user,
                                                    'type_question': type_question, 'type_all': type_all})


@login_required(login_url='login')
def delete_timetable(request):
    if request.user.groups.filter(name='Secretary').exists():
        return HttpResponseNotFound("<h2>У вас нет прав на эту страницу, вернитесь назад</h2><br>")
    date = request.GET.get('date')
    id = request.GET.get('id_employee')
    tim = request.GET.get('time')
    try:
        user = User.objects.get(id=id)
        i = user.id
        tim_tab = Timetable.objects.get(Q(id_employee=i) & Q(time=tim) & Q(date=date))
        tim_tab.delete()
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
    except Timetable.DoesNotExist:
        return HttpResponseNotFound("<h2>Timetable not found</h2>")


@login_required(login_url='login')
def serch_timetable(request):
    if request.user.groups.filter(name='Secretary').exists():
        return HttpResponseNotFound("<h2>У вас нет прав на эту страницу, вернитесь назад</h2><br>")
    query1 = request.GET.get('FIO')
    query2 = request.GET.get('date')
    if query1 and query2:
        us = User.objects.get(username=query1)
        object_list = Timetable.objects.filter(
            Q(id_employee=us.id) & Q(date=query2)
        )
        return render(request, 'main/search_results_timetable.html', {'title': 'Поиск',
                                                                      'object_list': object_list, 'user': us,
                                                                      'date': query2})
    else:
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


class SearchResultsView_timetable(ListView):
    model = Timetable
    template_name = 'main/search_results_timetable.html'
    title = 'adad'

    def get_queryset(self):  # новый
        query1 = self.request.GET.get('FIO')
        query2 = self.request.GET.get('date')
        us = User.objects.get(username=query1)
        if query1 != "":
            object_list = Timetable.objects.filter(
                Q(id_employee=us.id) & Q(date=query2)
            )
            return object_list


class SearchResultsView(ListView):
    model = Application
    template_name = 'main/search_results.html'

    def get_queryset(self):  # новый
        query1 = self.request.GET.get('id')
        query2 = self.request.GET.get('date_receipt')
        query3 = self.request.GET.get('FIO')
        query4 = self.request.GET.get('type_question')
        query5 = self.request.GET.get('ty')
        if query1 != "":
            object_list = Application.objects.filter(
                Q(id=query1) & Q(status=query5)
            )
            return object_list
        elif query2 != "":
            object_list = Application.objects.filter(
                Q(date_receipt=query2) & Q(status=query5)
            )
            return object_list
        elif query3 != "":
            object_list = Application.objects.filter(
                Q(FIO=query3) & Q(status=query5)
            )
            return object_list
        elif query4 != "":
            o = Type_question.objects.get(name=query4)
            if o:
                object_list = Application.objects.filter(
                    Q(type_question=o) & Q(status=query5)
                )
            return object_list


@login_required(login_url='login')
def timetable(request):
    if request.user.groups.filter(name='Secretary').exists():
        return HttpResponseNotFound("<h2>У вас нет прав на эту страницу, вернитесь назад</h2><br>")
    timetable_ = Timetable.objects.all()
    user2 = User.objects.all()
    user = []
    for el in user2:
        if el.groups.filter(name='Employee').exists():
            user.append(el)
    context = {
        'user': user,
        'timetable_': timetable_,
        'title': "Расписание"
    }
    return render(request, 'main/timetable.html', context=context)


@login_required(login_url='login')
def show_application(request, application_slug):
    user = []
    user2 = User.objects.all()
    for el in user2:
        if el.groups.filter(name='Employee').exists():
            user.append(el)
    application = get_object_or_404(Application, slug=application_slug)
    if request.method == "POST":
        application.text = request.POST.get("text")
        application.status = request.POST.get("status")
        application.id_employee = request.POST.get("id_employee")
        application.save()
        return HttpResponseRedirect("/")
    else:
        u2 = User.objects.get(id=application.id_employee)
        context = {
            'u2': u2,
            'user': user,
            'application': application,
            'title': application.id,
        }
    return render(request, 'main/application.html', context=context)


@login_required(login_url='login')
def create_application(request):
    type_ = Type_question.objects.all()
    user = User.objects.filter(groups__name='Employee')
    return render(request, 'main/create_application.html', {'title': 'Создание заявки', 'type': type_, 'user': user})


@login_required(login_url='login')
def app_save(request):
    a = Application()
    if request.method == 'POST':
        a.date_application = request.POST.get("date_application")
        a.time = request.POST.get("time")
        a.date_receipt = request.POST.get("date_receipt")
        inty = request.POST.get("type_question")
        b = Type_question.objects.get(id=inty)
        a.type_question = b
        a.id_employee = request.POST.get("id_employee")
        a.purpose_visit = request.POST.get("purpose_visit")
        a.text = ""
        a.FIO = request.POST.get("FIO")
        a.telephone = request.POST.get("telephone")
        a.email = request.POST.get("email")
        a.slug = "_" + str(a.date_application.day) + "_" + \
                 str(a.date_application.microsecond) + str(random.randint(0, 9999))
        a.save()
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
    else:
        return HttpResponseNotFound("<h2>Ошибка при записи</h2><br>")



@login_required(login_url='login')
def application_true(request):
    if request.user.groups.filter(name='Employee').exists():
        flag = True
    else:
        flag = False
    applications = Application.objects.filter(status='Confirmed Applications')
    return render(request, 'main/application_true.html', {'title': 'Подтвержденные заявки',
                                                          'applications': applications,
                                                          'flag': flag})


@login_required(login_url='login')
def application_false(request):
    if request.user.groups.filter(name='Employee').exists():
        flag = True
    else:
        flag = False
    if request.user.groups.filter(name='Secretary').exists():
        return HttpResponseNotFound("<h2>У вас нет прав на эту страницу, вернитесь назад</h2><br>")
    applications = Application.objects.filter(status='Rejected Applications')
    return render(request, 'main/application_false.html', {'title': 'Отклоненные заявки', 'applications': applications,
                                                           'flag': flag})


def help(request):
    return render(request, 'main/help.html')


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'имя пользователя и пароль неверный.')

        context = {}
        return render(request, 'main/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


def RegisterPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Аккаунт создан,' + user)
                return redirect('login')

        context = {'form': form}
        return render(request, 'main/register.html', context)
