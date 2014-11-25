import django
from django.conf import settings
from django.core.urlresolvers import reverse
if django.get_version() <= '1.4.0':
    ADMIN_IMG_PREFIX = '%simg/admin/' % getattr(settings, 'ADMIN_MEDIA_PREFIX')
else:
    ADMIN_IMG_PREFIX = '%sadmin/img/' % getattr(settings, 'STATIC_URL')
from django import forms
from django.utils.safestring import mark_safe
from django.template import loader, Context

class NoRelatedField(Exception):
    pass

def get_search_form(m, db_field, exclude):
    """
    Create search form dynamically, based on database-field and
    list of to-be-excluded fields. The form will be prefixes with
    the name of the source field to avoid name conflicts.
    """
    if not exclude:
        e = ()
    else:
        e = exclude
    class DynamicForm(forms.ModelForm):
        class Meta:
            model = m
            prefix = db_field.name
            exclude = e
        def add_prefix(self, field_name):
            return '%s_%s' % (db_field.name, field_name)
    return DynamicForm()
        
class ForeignKeySearchForm(forms.HiddenInput):
    """
    Widget. Transforms the normal foreign key hidden field into a search form.
    """
    def __init__(self, search_object=None, db_field=None, handler=None, attrs=None):
        self.db_field = db_field
        self.handler = handler(db_field=db_field)
        try:
            self.form = get_search_form(db_field.related.parent_model, db_field, self.handler.exclude)
        except Exception:
            raise NoRelatedField('%s is not a ForeignKey-field' % db_field.name)

        super(ForeignKeySearchForm, self).__init__(attrs)
        
    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
            
        glasses = '<img src="%sselector-search.gif" width="16" height="16" alt="Lookup">' % ADMIN_IMG_PREFIX
        if not value:
            ret = '-- no object selected --  %s' % glasses
           
        # Load widget template
        t = loader.get_template('foreignkeysearch/widget.html')

        handler_name = self.handler.__class__.__name__
        foreignkey_get_url = reverse('foreignkey_get', kwargs={'handler':handler_name})
        foreignkey_search_url = reverse('foreignkey_search', kwargs={'handler':handler_name})
       
        # Set template variables
        c = Context({
            'field_name': name.replace('-', '____'),
            'field_name_original': name,
            'field_value': value,
            'field': self.db_field,
            'app_name': self.db_field.model._meta.app_label,
            'model': self.db_field.model,
            'model_name': self.db_field.model.__name__,
            'model_name_verbose': getattr(self.db_field.model._meta, 'verbose_name', self.db_field.model.__name__),
            'related_app_name': self.db_field.related.parent_model._meta.app_label,
            'related_model': self.db_field.related.parent_model,
            'related_model_name': self.db_field.related.parent_model.__name__,
            'related_model_name_verbose': getattr(self.db_field.related.parent_model._meta, 'verbose_name', self.db_field.related.parent_model.__name__),
            'ADMIN_IMG_PREFIX': ADMIN_IMG_PREFIX,
            'form': self.form,
            'foreignkey_get_url' : foreignkey_get_url,
            'foreignkey_search_url' : foreignkey_search_url,
        })

        # Render widget
        content = t.render(c)
        return mark_safe(content)
