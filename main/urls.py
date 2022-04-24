from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.application_new, name='home'),
    path('application_new', views.application_new, name='application_new'),
    path('application_true', views.application_true, name='application_true'),
    path('application_false', views.application_false, name='application_false'),
    path('login', views.loginPage, name='login'),
    path('logout', views.logoutUser, name='logout'),
    path('register', views.RegisterPage, name='register'),
    path('application/<slug:application_slug>', views.show_application, name='application'),
    path('timetable', views.timetable, name='timetable'),
    path('search/', views.SearchResultsView.as_view(), name='search_results'),
    path('search_timetable/', views.serch_timetable, name='search_timetable'),
    path('create/', views.create_timetable, name='create_timetable'),
    path('delete', views.delete_timetable, name='delete'),
    path('search_user/', views.search_all, name='search_all'),
    path('create_adm/<int:id>', views.create_adm, name='create_adm'),
    path('add/', views.add_category, name='add_category'),
    path('a', views.adm, name='admin'),
    path('help', views.help, name='go_help'),
    path('analysis', views.analysis, name='analysis'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
