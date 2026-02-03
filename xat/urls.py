# xat/urls.py
from django.urls import path
from . import views

app_name = 'xat'

urlpatterns = [
    path('<int:event_pk>/send/', views.xat_send_message, name='send_message'),
    path('<int:event_pk>/messages/', views.xat_load_messages, name='load_messages'),
    path('message/<int:message_pk>/delete/', views.xat_delete_message, name='delete_message'),
    path('message/<int:message_pk>/highlight/', views.xat_highlight_message, name='highlight_message'),
]