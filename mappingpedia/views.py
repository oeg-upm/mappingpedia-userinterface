from django.shortcuts import render
from django.views import View
import os
import requests
import json
from django.views.decorators.csrf import csrf_exempt
from subprocess import call
from django.http import JsonResponse
import random
import string

ckan_base_url = 'http://83.212.100.226/ckan/api/'
mappingpedia_engine_base_url = "http://mappingpedia-engine.linkeddata.es"
#mappingpedia_engine_base_url = "http://localhost:8090"
#mappingpedia_engine_base_url = "http://127.0.0.1:80/"
organization_id = "zaragoza_test"
#authorization = os.environ['authorization']


class Dataset(View):

    def get(self, request):
        organizations = get_organizations()
        return render(request, 'dataset_view.html', {'nav': 'dataset', 'organizations': organizations})

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
        organizations = get_organizations()
        datasets = get_datasets()
        return render(request, 'mapping_view.html', {'datasets': datasets, 'nav': 'mapping',
                                                     'organizations': organizations})

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
        organizations = get_organizations()
        datasets = get_datasets()
        return render(request, 'execute_view.html', {'datasets': datasets, 'nav': 'execute',
                                                     'organizations': organizations})

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


def get_organizations():
    url = os.path.join(ckan_base_url, 'action/organization_list')
    response = requests.get(url)
    organizations = []
    if response.status_code == 200:
        print "status_code is success"
        json_response = json.loads(response.content)
        if "success" in json_response and json_response["success"]:
            print "success ckan"
            organizations = json_response["result"]
        else:
            print "response: " + str(response.content)
    print 'organizations: '
    print organizations
    return organizations


def get_datasets():
    url = os.path.join(mappingpedia_engine_base_url, 'datasets')
    response = requests.get(url)
    datasets = []
    if response.status_code == 200:
        datasets = json.loads(response.content)['results']
    return datasets


def autocomplete(request):
    return render(request, 'autocomplete.html')


def editor(request):
    f = open('/Users/aalobaid/temp/mappingpedia/edificio-historico.csv')
    line = f.readline()
    headers = line.split(',')
    return render(request, 'editor.html', {'headers': headers, 'file_name': 'edificio-historico'})


def get_properties(request):
    if 'concept' in request.GET:
        concept = request.GET['concept'].strip()
        f = open('utils/schema-prop.json')
        properties_j = json.loads(f.read())
        if concept in properties_j:
            properties = list(set(properties_j[concept]))
            return JsonResponse({'properties': properties})
    return JsonResponse({'properties': []})


def generate_mappings(request):
    print request.POST
    mappings = []
    if 'file_name' not in request.POST:
        return JsonResponse({'error': 'file_name is not passed'})
    if 'entity_class'  not in request.POST:
        return JsonResponse({'error': 'entity_class is not passed'})
    if 'entity_column' not in request.POST:
        return JsonResponse({'error': 'entity_column is not passed'})

    for i in range(len(request.POST)):
        key = 'form_key_'+str(i)
        val = 'form_val_'+str(i)
        if key in request.POST and val in request.POST:
            if request.POST[val].strip() != '':
                element = {"key": request.POST[key], "val": request.POST[val]}
                mappings.append(element)
        else:
            break

    mapping_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    file_name = request.POST['file_name']
    entity_class = request.POST['entity_class']
    entity_column = request.POST['entity_column']
    property_column_mapping = ""
    single_property_mapping = """
        rr:predicateObjectMap [
          rr:predicateMap [ rr:constant schema:%s ];
          rr:objectMap    [ rr:termType rr:Literal; rr:column "\\"%s\\""; ];
        ];
    """

    proper_mappings_list = [single_property_mapping % (m["val"].replace('http://schema.org/',''), m["key"].upper()) for m in mappings]
    property_column_mapping = "\n".join(proper_mappings_list)
    mapping_file = """
    @prefix rr: <http://www.w3.org/ns/r2rml#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix dcat: <http://www.w3.org/ns/dcat#> .
    @prefix dct: <http://purl.org/dc/terms/> .
    @prefix mpv: <http://mappingpedia.linkeddata.es/vocab/> .
    @prefix skos: <http://www.w3.org/2004/02/skos/core#> .
    @prefix schema: <http://schema.org/> .
    @base <http://mappingpedia.linkeddata.es/resource/> .
    <%s>
        rr:logicalTable [
            rr:tableName  "\\"%s\\""
        ];

        rr:subjectMap [
            a rr:Subject; rr:termType rr:IRI; rr:class schema:%s;
            rr:column "\\"%s\\"";
        ];
        %s
    .
    """ % (mapping_id, file_name, entity_class, entity_column.upper(), property_column_mapping)
    print mapping_file
    return JsonResponse({'status': 'Ok'})