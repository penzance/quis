from django.conf.urls import url

import quis.views as views

urlpatterns = [
    url(r'^$', views.index, name='index'),
]
