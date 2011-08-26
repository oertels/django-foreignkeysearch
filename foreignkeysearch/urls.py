from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^search/(?P<handler>[a-zA-Z0-9_]+)$', 'foreignkeysearch.views.search', name='foreignkey_search'),
    url(r'^get/(?P<handler>[a-zA-Z0-9_]+)$', 'foreignkeysearch.views.get_item', name='foreignkey_get'),
)
