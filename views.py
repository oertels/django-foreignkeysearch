# -*- coding: utf-8 -*-
import re
from django.utils import simplejson
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from foreignkeysearch import registered_handlers

@staff_member_required
@csrf_exempt
def search(request, handler):
    h = registered_handlers.get(handler, None)
    if h is None:
        return HttpResponse(
             simplejson.dumps({}),
             mimetype='application/json'
        )

    related_field_name = h.db_field.name

    # Prepare handler vars
    params = {}
    for k,v in request.POST.iteritems():
        if k.startswith(related_field_name.lower()+'_'):
            params[k[len(related_field_name)+1:]] = v
       
    results = h.search(params)[:20]
    result_list = {}
    for r in results:
        tmp = h.item(r)
        tmp = re.sub(u'\[link\](.*)\[/link\]', '<a href="#" onClick="$(\'#id_%(field)s\').val(\'%(id)s\');$(\'#search_panel_%(field)s\').toggle(\'fast\');$(\'#remove_foreignkey_%(field)s\').show();get_foreignkey_value_%(field)s();return false;">\\1</a>' % ({'id': r.id, 'field':request.GET.get('field', '')}), tmp)
        result_list[r.id] = tmp
    

    ret_dict = {}
    ret_dict['pre'] = h.pre_results()
    ret_dict['post'] = h.post_results()
    ret_dict['results'] = result_list
    ret_dict['no_results'] = h.no_results()

    # Return serialized results
    ret = HttpResponse(
         simplejson.dumps(ret_dict),
         mimetype='application/json'
    )
    return ret

@staff_member_required
def get_item(request, handler):
    object_id = request.GET.get('object_id', 0)
    h = registered_handlers.get(handler, None)
    if h is None:
        return HttpResponse(
             simplejson.dumps({}),
             mimetype='application/json'
        )
    try:
        obj = h.model.objects.get(id=object_id)
        d = {'object_id': object_id, 'value': h.selected_item(obj)}
    except Exception, e:
        d = {'object_id': '', 'value': ''}
    
    # Return serialized result
    ret = HttpResponse(
         simplejson.dumps(d),
         mimetype='application/json'
    )
    return ret
