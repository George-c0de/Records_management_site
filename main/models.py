from django.db import models
from django.urls import reverse
import datetime


class Type_question(models.Model):
    name = models.CharField('Название', max_length=50)

    def __str__(self):
        return self.name


class Type_employee(models.Model):
    id_employee = models.IntegerField('id_пользователя', default=0)
    id_question = models.ForeignKey(Type_question, default=0, on_delete=models.CASCADE)
    name = models.CharField('Название', default="1", max_length=50)


class Application(models.Model):
    date_application = models.DateTimeField('Дата подачи заявки')
    time = models.TimeField('Время подачи', default=datetime.datetime.now())
    date_receipt = models.DateField('Дата приема')
    type_question = models.ForeignKey(Type_question, on_delete=models.CASCADE)
    id_employee = models.IntegerField('id пользователя')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    purpose_visit = models.CharField('Цель визита', max_length=50)
    status = models.CharField('Состояние заявки', default='New Applications', max_length=50)
    # Confirmed Applications and Rejected Applications
    text = models.TextField('Решение')
    FIO = models.CharField('ФИО', max_length=100)
    telephone = models.IntegerField('Телефон')
    email = models.CharField('Почта', max_length=50)

    def get_absolute_url(self):
        return reverse('application', kwargs={'application_slug': self.slug})


class Timetable(models.Model):
    id_employee = models.IntegerField('id пользователя')
    time = models.TimeField('Время')
    date = models.DateField('Дата')
    condition = models.BooleanField('Состояние')


