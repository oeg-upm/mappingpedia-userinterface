"""mappingpedia URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('dataset_view', views.dataset_view),
    url('dataset_register', views.dataset_register),
    url('mapping_view', views.mapping_view),
    url('mapping_register', views.mapping_register),
    # url('mapping_upload', views.mapping_upload),
    url('execution_view', views.execute_view),
    url('execute2', views.execute_mapping2),
    url('execute', views.execute_mapping),


]
