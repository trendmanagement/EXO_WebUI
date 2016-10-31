from django.conf.urls import url, include
from django.contrib import admin
from app_quotes.views import *

urlpatterns = [
    url(r"^$", view_quotes_monitor, name='quotes_index'),
]