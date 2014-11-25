import django
if django.get_version() <= '1.6.0':
    from django.conf.urls.defaults import *  # @UnusedWildImport
else: # django version >= 1.6.0
    from django.conf.urls import url, patterns  # @Reimport

urlpatterns = patterns('',
    url(r'^search/(?P<handler>[a-zA-Z0-9_]+)$', 'foreignkeysearch.views.search', name='foreignkey_search'),
    url(r'^get/(?P<handler>[a-zA-Z0-9_]+)$', 'foreignkeysearch.views.get_item', name='foreignkey_get'),
)
