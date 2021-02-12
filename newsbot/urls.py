from django.urls import path, re_path

from . import views
from myApp.views import *

app_name='newsbot'

urlpatterns = [
    path('', views.index, name='index'),
    path('newsbot/', views.index, name='index'),
    path('load-data/', myView, name='myView'),
    path('dict-builder/', dictBuilder, name='dictBuilder'),
    path('some-more-data/', someMoreData, name='someMoreData'),
    path('some-more-articles/', moreArticles, name='moreArticles'),
]