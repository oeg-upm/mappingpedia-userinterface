from django.shortcuts import render
from django.views import View
import os
import requests
import json
from django.views.decorators.csrf import csrf_exempt
from subprocess import call
from django.http import JsonResponse



mappingpedia_engine_base_url = "http://mappingpedia-engine.linkeddata.es"
#mappingpedia_engine_base_url = "http://localhost:8090"
#mappingpedia_engine_base_url = "http://127.0.0.1:80/"
organization_id = "zaragoza_test"


class Dataset(View):

    def get(self, request):
        return render(request, 'dataset_view.html', {'nav': 'dataset'})

    def post(self, request):
        if 'organization' not in request.POST or request.POST['organization'].strip() != '':
            organization = request.POST['organization']
        else:
            organization = organization_id
        url = os.path.join(mappingpedia_engine_base_url, 'datasets', organization)
        if 'url' in request.POST and request.POST['url'].strip() != '':
            distribution_download_url = request.POST['url']
            data = {
                "distribution_download_url": distribution_download_url,
            }
            response = requests.post(url, data)
        elif 'file' in request.FILES:
            distribution_file = request.FILES['file']
            response = requests.post(url, files=[('distribution_file', distribution_file)])
        else:
            print "ERROR"
            return "error"
        if response.status_code == 200:
            dataset_id = json.loads(response.content)['dataset_id']
            return render(request, 'msg.html', {'msg': 'The dataset has been registered with id = '+dataset_id})
        else:
            return render(request, 'msg.html', {'msg': response.content})


class Mapping(View):

    def get(self, request):
        return render(request, 'mapping_view.html', {'nav': 'mapping'})

    def post(self, request):
        if 'organization' not in request.POST or request.POST['organization'].strip() != '':
            organization = request.POST['organization']
        else:
            organization = organization_id
        if 'dataset_id' in request.POST:
            dataset_id = request.POST['dataset_id']
        else:
            return render(request, 'msg.html', {'msg': 'dataset id should not be empty'})
        if 'mapping_file_url' in request.POST and request.POST['mapping_file_url'].strip() != '':
            mapping_file_url = request.POST['mapping_file_url']
            url = os.path.join(mappingpedia_engine_base_url, 'mappings', organization, dataset_id)
            data = {
                "mappingDocumentDownloadURL": mapping_file_url
            }
            response = requests.post(url, data)
        else:
            mapping_file = request.FILES['mapping_file']
            print mapping_file
            url = os.path.join(mappingpedia_engine_base_url, 'mappings', organization, dataset_id)
            print "the url"
            print url
            response = requests.post(url, files=[('mappingFile', mapping_file)])
        if response.status_code == 200:
            print response.content
            download_url = json.loads(response.content)['mapping_document_download_url']
            return render(request, 'msg.html', {'msg': 'mappings has been registered with download_url: '+download_url})
        else:
            return render(request, 'msg.html', {'msg': 'error: '+response.content})


class Execute(View):

    def get(self, request):
        url = os.path.join(mappingpedia_engine_base_url, 'datasets')
        response = requests.get(url)
        if response.status_code == 200:
            datasets = json.loads(response.content)['results']
            return render(request, 'execute_view.html', {'datasets': datasets, 'nav': 'execute'})
        else:
            return render(request, 'msg.html', {'msg': 'error', 'nav': 'execute'})

    def post(self, request):
        print "in execution"
        if 'organization' not in request.POST or request.POST['organization'].strip() != '':
            organization = request.POST['organization']
        else:
            organization = organization_id
        url = os.path.join(mappingpedia_engine_base_url, 'executions2')
        print url
        language = request.POST['language']
        data = {
            "mapping_document_download_url": request.POST['mapping_document_download_url'],
            "organizationId":  organization_id,
            "datasetId": request.POST['dataset_id'],
            "distribution_download_url": request.POST['distribution_download_url'],
            "mappingLanguage": language,
        }
        print "data: "
        print data
        response = requests.post(url, data)
        if response.status_code is 200:
            result_url = json.loads(response.content)['mapping_execution_result_download_url']
            print "result : "
            print response.content
            return render(request, 'msg.html', {'msg': 'Execution results can be found here %s'%result_url})
        else:
            return render(request, 'msg.html', {'msg': 'error: '+response.content})


def home(request):
    return render(request, 'home.html')


@csrf_exempt
def webhook(request):
    from settings import BASE_DIR
    try:
        payload = json.loads(request.POST['payload'], strict=False)
        comm = "cd %s; git pull" % BASE_DIR
        print "git pull command: %s" % comm
        call(comm, shell=True)
        return JsonResponse({"status": "Ok"})
    except Exception as e:
        print "git_pull exception: " + str(e)
        return JsonResponse({"error": str(e)})