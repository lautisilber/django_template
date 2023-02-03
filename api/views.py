from django.shortcuts import render
from django.http import JsonResponse, HttpRequest, HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.apps import apps
import json
from django.db.models import Model

from datetime import datetime
from django.contrib.auth.models import User
from django.db.models import DateTimeField, ForeignKey

def test(request: HttpRequest):
    return JsonResponse({'test': 'OK'})


hidden_models = [
    'logentry', 'permission', 'session', 'contenttype'
]


def _get_models() -> dict[str, Model]:
    models = { model.__name__.lower():model for model in apps.get_models() }
    models = { k:v for k, v in models.items() if k not in hidden_models }
    return models


def get_all(request: HttpRequest, model_name: str):
    models = _get_models()

    if model_name not in models:
        return HttpResponseNotFound('Model name was not found')
    
    model_abstract = models[model_name]
    query_params = request.GET.dict()
    fields = [f.name for f in model_abstract._meta.get_fields()]

    models = []

    if not query_params:
        models = model_abstract.objects
    else:
        queries = request.GET.dict()
        filter_kwargs = { k:v for k, v in queries.items() if k in fields }
        models = model_abstract.objects.filter(**filter_kwargs)

    res_obj = []
    for model in models.all():
        res_obj.append(dict())
        for field in fields:
            attr = getattr(model, field)
            # type transformation
            if isinstance(attr, datetime):
                attr = attr.strftime('%Y-%m-%d %H-%M-%S')
            elif isinstance(attr, User):
                attr = attr.id
            res_obj[-1][field] = attr
    return JsonResponse(res_obj, safe=False)


def get_first(request: HttpRequest, model_name: str):
    models = _get_models()

    if model_name not in models:
        return HttpResponseNotFound('Model name was not found')
    
    model_abstract = models[model_name]
    query_params = request.GET.dict()
    fields = [f.name for f in model_abstract._meta.get_fields()]

    models = []

    if not query_params:
        models = model_abstract.objects
    else:
        queries = request.GET.dict()
        filter_kwargs = { k:v for k, v in queries.items() if k in fields }
        models = model_abstract.objects.filter(**filter_kwargs)

    model = models.first()
    res_obj = {}
    for field in fields:
        attr = getattr(model, field)
        # type transformation
        if isinstance(attr, datetime):
            attr = attr.strftime('%Y-%m-%d_%H-%M-%S')
        elif isinstance(attr, User):
            attr = attr.id
        res_obj[field] = attr
    return JsonResponse(res_obj)


def post(request: HttpRequest, model_name: str):
    models = _get_models()

    if model_name not in models:
        return HttpResponseNotFound('Model name was not found')
    
    model_abstract = models[model_name]
    fields = { f.name:f for f in model_abstract._meta.get_fields() }

    if request.method == 'GET':
        data = request.GET.dict()
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
        except:
            return HttpResponseBadRequest(f"Couldn't parse JSON")
        
    kwargs = { k:v for k, v in data.items() if k in fields }

    fields_to_remove = []
    for k in kwargs:
        if isinstance(fields[k], DateTimeField):
            kwargs[k] = datetime.strptime(kwargs[k], '%Y-%m-%d_%H-%M-%S')
        elif isinstance(fields[k], ForeignKey):
            try:
                kwargs[k] = fields[k].related_model.objects.filter(id=kwargs[k]).first()
            except:
                fields_to_remove.append(k)
    print(kwargs)
    kwargs = { k:v for k, v in kwargs.items() if k not in fields_to_remove }

    try:
        model = model_abstract(**kwargs)
    except:
        return HttpResponseBadRequest(f"Couldn't create '{model_name}' with provided parameters\n\n{data}")
    model.save()
    return HttpResponse('OK')


def delete(request: HttpRequest, model_name: str, id: int):
    models = _get_models()

    if model_name not in models:
        return HttpResponseNotFound('Model name was not found')
    
    model = models[model_name].objects.filter(id=id).first()

    if not model:
        return HttpResponseNotFound(f"Didn't delete because model '{model_name}' of id '{id}' wasn't found")

    model.delete()
    return HttpResponse('OK')