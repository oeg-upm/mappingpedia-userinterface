from django.shortcuts import render
from django.http import JsonResponse
import os
import requests
import json

mappingpedia_engine_base_url = "http://mappingpedia-engine.linkeddata.es"
# mappingpedia_engine_base_url = "http://localhost:8090"
#mappingpedia_engine_base_url = "http://127.0.0.1:80/"
organization_id = "zaragoza_test"


def dataset_view(request):
    return render(request, 'dataset_view.html')


def dataset_register(request):
    distribution_download_url = request.POST['url']
    url = os.path.join(mappingpedia_engine_base_url, 'datasets', organization_id)
    data = {
        "distribution_download_url": distribution_download_url,
    }
    response = requests.post(url, data)
    if response.status_code == 200:
        dataset_id = json.loads(response.content)['dataset_id']
        return render(request, 'msg.html', {'msg': 'The dataset has been registered with id = '+dataset_id})
    else:
        return render(request, 'msg.html', {'msg': response.content})


def mapping_register(request):
    print request.POST
    dataset_id = request.POST['dataset_id']
    mapping_file_url = request.POST['mapping_file_url']
    url = os.path.join(mappingpedia_engine_base_url, 'mappings', organization_id, dataset_id)
    data = {
        "mappingDocumentDownloadURL": mapping_file_url
    }
    response = requests.post(url, data)
    if response.status_code == 200:
        print response.content
        download_url = json.loads(response.content)['mapping_document_download_url']
        return render(request, 'msg.html', {'msg': 'mappings has been registered with download_url: '+download_url})
    else:
        return render(request, 'msg.html', {'msg': 'error: '+response.content})


def mapping_view(request):
    return render(request, 'mapping_view.html')


# def get_mappings_for_dataset(request):
#     dataset_id = request.POST['dataset_id']
#     url = os.path.join(mappingpedia_engine_base_url, 'mappings', 'findMappingDocumentsByDatasetId?='+)
#     url = os.path.join(mappingpedia_engine_base_url)
#     requests.post()


def execute_view(request):
    return render(request, 'execute_view.html')


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
