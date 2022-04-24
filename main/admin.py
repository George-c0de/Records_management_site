from django.contrib import admin
from .models import Application, Type_question, Timetable, Type_employee

admin.site.register(Application)
admin.site.register(Type_question)
admin.site.register(Timetable)
admin.site.register(Type_employee)


class BookInstanceAdmin(admin.ModelAdmin):
    list_filter = ('Дата', 'Тип', 'ФИО', 'Связка')
