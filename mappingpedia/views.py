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
            if 'name' in request.POST and request.POST['name'].strip() != '':
                data['datasetTitle'] = request.POST['name']
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
        datasets = []#get_datasets()
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
        datasets = []#get_datasets()
        return render(request, 'execute_view.html', {'datasets': datasets, 'nav': 'execute',
                                                     'organizations': organizations})

    def post(self, request):
        print "in execution"
        if 'organization' not in request.POST:
            return render(request, 'msg.html', {'msg': 'error: organization is not passed'})
        if 'dataset' not in request.POST:
            return render(request, 'msg.html', {'msg': 'error: dataset is not passed'})
        if 'distribution' not in request.POST:
            return render(request, 'msg.html', {'msg': 'error: distribution is not passed'})
        if 'mapping' not in request.POST:
            return render(request, 'msg.html', {'msg': 'error: mapping is not passed'})
        organization_id = request.POST['organization']
        dataset_id = request.POST['dataset']
        distribution_id = request.POST['distribution']
        mapping_id = request.POST['mapping']
        distribution = get_distribution(distribution_id)
        if distribution is None:
            return render(request, 'msg.html', {'msg': 'error: getting distribution information from CKAN'})
        if distribution['format'].lower().strip() in ['json', 'xml']:
            language = 'rml'
        else:
            language = 'r2rml'
        url = os.path.join(mappingpedia_engine_base_url, 'executions2')
        print url
        data = {
            # "mapping_document_download_url": request.POST['mapping_document_download_url'],
            "mapping_document_id": mapping_id,
            "organization_id":  organization_id,
            "dataset_id": dataset_id,
            "distribution_download_url": distribution['url'],
            "mapping_language": language,
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


def get_datasets(request):
    print 'get_datasets'
    if 'organization' in request.GET:
        organization =  request.GET['organization'].strip()
        print 'organization %s' % organization
        datasets = get_datasets_for_organization(organization, only_contains_distributions=False)
        #print 'datasets: '
        #print datasets
        return JsonResponse({'datasets': datasets})
    else:
        print 'not in organization'
        return JsonResponse({'error': 'organization is not passed'})


def get_datasets_for_organization(organization, only_contains_distributions=False):
    url = os.path.join(ckan_base_url, 'action','organization_show')
    url += '?id=%s&include_datasets=true' % organization.strip()
    response = requests.get(url)
    print 'get url: '
    print url
    if response.status_code == 200:
        print 'status code is success'
        json_response = json.loads(response.content)
        if "success" in json_response and json_response["success"]:
            print "success ckan"
            datasets_elements = json_response["result"]['packages']
            if only_contains_distributions:
                datasets = [d['title'] for d in datasets_elements if len(get_distributions_for_dataset(d['title'], only_original=True))>0]
            else:
                datasets = [d['title'] for d in datasets_elements]
            return datasets
        else:
            print "response: " + str(response.content)
    else:
        print 'status code is wrong'
    return []


def get_distributions(request):
    if 'dataset' in request.GET:
        distributions = get_distributions_for_dataset(request.GET['dataset'], only_original=True)
        # originals = [d for d in distributions if d['format'].upper() in ['XML', 'JSON', 'CSV']]
        return JsonResponse({'distributions': distributions})
    else:
        return JsonResponse({'error': 'dataset is not passed'})


def get_distributions_for_dataset(dataset_id, only_original=False):
    url = os.path.join(ckan_base_url, 'action', 'package_show?id='+dataset_id)
    response = requests.get(url)
    if response.status_code == 200:
        print 'status code is success'
        json_response = json.loads(response.content)
        if "success" in json_response and json_response["success"]:
            distributions = json_response['result']['resources']
            if only_original:
                distributions = [d for d in distributions if d['format'].upper() in ['XML', 'JSON', 'CSV']]
            return distributions
        else:
            print "not success"
    else:
        print "not a success status code"
    return []


def get_mappings(request):
    if 'dataset' in request.GET:
        dataset = request.GET['dataset']
        mappings = get_mappings_for_dataset(dataset)
        return JsonResponse({'mappings': mappings})
    return JsonResponse({'error': 'distribution is not passed'})


def get_mappings_for_dataset(dataset):
    url = os.path.join(mappingpedia_engine_base_url, 'mappings?dataset_id='+dataset.strip())
    print 'get_mappings_for_dataset> url: '+url
    response = requests.get(url)
    if response.status_code == 200:
        json_response = json.loads(response.content)
        print 'get mappings result:'
        print response.content
        mappings = json_response['results']
    else:
        print 'get mapping status code error'
        mappings = []
    return mappings


def autocomplete(request):
    return render(request, 'autocomplete.html')


def editor_csv(request, download_url, file_name, dataset):
    response = requests.get(download_url)
    if response.status_code == 200:
        line = response.content.split('\n')[0]
        headers = line.split(',')
        return render(request, 'editor.html', {'headers': headers, 'file_name': file_name, 'dataset': dataset})
    else:
        return render(request, 'msg.html', {'error': 'can not download file: ' + download_url})


def editor(request):
    if 'dataset' in request.GET and 'distribution' in request.GET:
        dataset = request.GET['dataset']
        distribution = request.GET['distribution']
        url = os.path.join(ckan_base_url, 'action', 'resource_show?id='+distribution)
        print 'resource_show url: '+url
        response = requests.get(url)
        if response.status_code == 200:
            json_response = json.loads(response.content)
            print json_response
            if 'success' in json_response and json_response['success'] is True:
                print json_response
                download_url = json_response['result']['url'].strip()
                if download_url[-1] == '/':
                    download_url = download_url[0:-1]
                file_name = download_url.split('/')[-1]
                file_name_no_ext = ".".join(file_name.split('.')[:-1])
                if file_name_no_ext.strip() == '':
                    print 'filename stored in ckan has to contain an extension: '+file_name
                    file_name_no_ext = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
                if json_response['result']['format'].upper() == 'CSV':
                    return editor_csv(request, download_url, file_name_no_ext, dataset)
                else:
                    return render(request, 'msg.html', {'msg': 'format: '+json_response['result']['format'].upper()})
            else:
                print ' not a success in the ckan reply'
                return render(request, 'msg.html', {'msg': 'ckan API does not return success'})
        else:
            print 'status code is not 200 for getting distribution details'
            return render(request, 'msg.html', {'msg': 'status code is not 200 for getting distritbution details'})
    return render(request, 'msg.html', {'msg': 'dataset and distribution should be passed'})


def get_properties(request):
    if 'concept' in request.GET:
        concept = request.GET['concept'].strip()
        f = open('utils/schema-prop.json')
        properties_j = json.loads(f.read())
        if concept in properties_j:
            properties = list(set(properties_j[concept]))
            return JsonResponse({'properties': properties})
    return JsonResponse({'properties': []})


def generate_r2rml_mappings(file_name, entity_class, entity_column, mappings):
    from settings import BASE_DIR
    mapping_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
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
    mapping_file_path = os.path.join(BASE_DIR, 'local', mapping_id+'.r2rml.ttl')
    print 'mapping file path:'
    print mapping_file_path
    f = open(mapping_file_path, 'w')
    f.write(mapping_file)
    f.close()
    return mapping_file_path


def generate_mappings(request):
    print request.POST
    mappings = []
    if 'file_name' not in request.POST:
        return JsonResponse({'error': 'file_name is not passed'})
    if 'entity_class'  not in request.POST:
        return JsonResponse({'error': 'entity_class is not passed'})
    if 'entity_column' not in request.POST:
        return JsonResponse({'error': 'entity_column is not passed'})
    if 'dataset' not in request.POST:
        return JsonResponse({'error': 'dataset is not passed'})
    file_name = request.POST['file_name'].strip()
    entity_class = request.POST['entity_class'].strip()
    entity_column = request.POST['entity_column'].strip()
    dataset = request.POST['dataset'].strip()
    url = os.path.join(ckan_base_url, 'action', 'package_show?id='+dataset)
    response = requests.get(url)
    if response.status_code == 200:
        json_response = json.loads(response.content)
        organization = json_response["result"]["organization"]["id"]

    for i in range(len(request.POST)):
        key = 'form_key_'+str(i)
        val = 'form_val_'+str(i)
        if key in request.POST and val in request.POST:
            if request.POST[val].strip() != '':
                element = {"key": request.POST[key], "val": request.POST[val]}
                mappings.append(element)
        else:
            break
    if '.' in file_name and file_name.split('.')[-1].upper() in ['JSON', 'XML']:
        return render(request, 'msg.html', {'msg': 'RML is not supported yet'})
    else:
        mapping_file = generate_r2rml_mappings(file_name, entity_class, entity_column, mappings)
        mapping_file = open(mapping_file)
        print mapping_file
        url = os.path.join(mappingpedia_engine_base_url, 'mappings', organization, dataset)
        print "the url to upload mapping"
        print url
        response = requests.post(url, files=[('mappingFile', mapping_file)])
        if response.status_code == 200:
            print response.content
            download_url = json.loads(response.content)['mapping_document_download_url']
            return render(request, 'msg.html', {'msg': 'mappings has been registered with download_url: ' + download_url})
        else:
            return render(request, 'msg.html', {'msg': 'error: ' + response.content})

    return JsonResponse({'status': 'Ok'})


def get_distribution(distribution_id):
    url = os.path.join(ckan_base_url, 'action/resource_show?id='+distribution_id)
    print 'get distribution url: '+url
    response = requests.get(url)
    if response.status_code == 200:
        json_response = json.loads(response.content)
        return json_response['result']
    else:
        return None
