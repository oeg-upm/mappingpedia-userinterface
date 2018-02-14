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
    url(r'execution_callback/(?P<id>\d+)', views.execution_callback),
    url(r'execution_list', views.execution_list),
    url(r'clear_session', views.clear_session),
    url(r'get_datasets', views.get_datasets),
    url(r'get_distributions', views.get_distributions),
    url(r'get_mappings', views.get_mappings),
    url(r'generate_mappings', views.generate_mappings),
    url(r'dataset', views.Dataset.as_view()),
    url(r'distribution', views.Distribution.as_view()),
    url(r'mapping', views.Mapping.as_view()),
    url(r'execute', views.Execute.as_view()),
    url(r'explore', views.Explore.as_view()),
    url(r'webhook', views.webhook),
    url(r'autocomplete', views.autocomplete),
    url(r'editor', views.editor),
    url(r'get_properties', views.get_properties),
    url(r'platform', views.Dataset.as_view()),
    url('', views.Dataset.as_view()),

]
