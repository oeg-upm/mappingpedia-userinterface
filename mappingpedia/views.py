from django.shortcuts import render
from django.http import JsonResponse
import os
import requests
import json
import random
import string


mappingpedia_engine_base_url = "http://mappingpedia-engine.linkeddata.es"
#mappingpedia_engine_base_url = "http://localhost:8090"
#mappingpedia_engine_base_url = "http://127.0.0.1:80/"
organization_id = "zaragoza_test"


def dataset_view(request):
    return render(request, 'dataset_view.html')


def dataset_register(request):
    url = os.path.join(mappingpedia_engine_base_url, 'datasets', organization_id)
    if 'url' in request.POST and request.POST['url'].strip() != '':
        print "url in POST"
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


def handle_uploaded_file(f):
    file_name = os.path.join('temp',get_random_test(size=4))
    print "file name: "+file_name
    with open(file_name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_name


def get_random_test(size = 8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(size))


def mapping_register(request):
    print request.POST
    dataset_id = request.POST['dataset_id']
    if 'mapping_file_url' in request.POST and request.POST['mapping_file_url'].strip() != '':
        mapping_file_url = request.POST['mapping_file_url']
        url = os.path.join(mappingpedia_engine_base_url, 'mappings', organization_id, dataset_id)
        data = {
            "mappingDocumentDownloadURL": mapping_file_url
        }
        response = requests.post(url, data)
    else:
        mapping_file = request.FILES['mapping_file']
        print mapping_file
        url = os.path.join(mappingpedia_engine_base_url, 'mappings', organization_id, dataset_id)
        print "the url"
        print url
        response = requests.post(url, files=[('mappingFile', mapping_file)])
    if response.status_code == 200:
        print response.content
        download_url = json.loads(response.content)['mapping_document_download_url']
        return render(request, 'msg.html', {'msg': 'mappings has been registered with download_url: '+download_url})
    else:
        return render(request, 'msg.html', {'msg': 'error: '+response.content})


def mapping_view(request):
    return render(request, 'mapping_view.html')


def execute_view(request):
    url = os.path.join(mappingpedia_engine_base_url, 'datasets')
    response = requests.get(url)
    if response.status_code == 200:
        datasets = json.loads(response.content)['results']
        return render(request, 'execute_view.html', {'datasets': datasets})
    else:
        return render(request, 'msg.html', {'msg': 'error'})



def execute_mapping(request):
    mapping_filename = request.POST['mapping_filename']
    dataset_id = request.POST['dataset_id']
    distribution_download_url = request.POST['distribution_url']
    url = os.path.join(mappingpedia_engine_base_url, 'executions', organization_id, dataset_id, mapping_filename)
    print url
    data = {
        "distribution_download_url": distribution_download_url,
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


def execute_mapping2(request):
    print "in execution 2"
    url = os.path.join(mappingpedia_engine_base_url, 'executions2')
    print url
    data = {
        "mapping_document_download_url": request.POST['mapping_document_download_url'],
        "organizationId":  organization_id,
        "datasetId": request.POST['dataset_id'],
        "distribution_download_url": request.POST['distribution_download_url']
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
