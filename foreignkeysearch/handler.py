from django.db.models import Q
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

class BaseHandler(object):
    resultset = None
    exclude = ()

    def __init__(self, db_field=None):
        # Register instance globally
        from foreignkeysearch import registered_handlers
        self.db_field = db_field
        if not self.__class__.__name__ in registered_handlers:
            registered_handlers[self.__class__.__name__] = self

    def pre_results(self):
        """
        The return string will be inserted before the result list
        Example:
        return '<table>'
        """
        return '<h4>%s:</h4>' % _('Results')

    def post_results(self):
        """
        The return string will be inserted after the result list.
        Example:
        return '</table>'
        """
        return ''

    def no_results(self):
        """
        A "no results"-string
        """
        return '-- %s --' % _('no results')

    def search(self, params):
        """
        Performs a search via __icontains over all fields and returns the resultset
        """
        q = Q()
        field_list = [f.name for f in self.model._meta.fields]
        for k,v in params.iteritems():
            if k in field_list and v != '':
                q &= Q(**{('%s__icontains' % k).__str__(): v.__str__()})
        if not q:
            return []
        return self.model.objects.filter(q)

    def selected_item(self, obj):
        """
        Returns the HTML-Representation of a selected item
        """
        try:
           return obj.__unicode__()
        except:
            return obj.__repr__()

    def item(self, obj):
        """
        Returns the HTML-Representation of an item in the result list
        """
        return mark_safe(u'[link]%(title)s[/link]<br />' % ({
            'title': obj
        }))