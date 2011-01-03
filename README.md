## README


This django app closes a gap I found several times on handling foreign keys in the admin. There is a bunch of approaches how to select foreign keys comfortably, the best one might be [django-ajax-selects](http://code.google.com/p/django-ajax-selects/), which provides a very good and customizable autocompletion function. It has its limitations, though, since it's not possible to do complex queries with an autocompletion function.

So this app's purpose is to offer a complete search form, which basically contains a ModelForm of the related field's model and some ajax stuff.

When a related field selection looks like this before:

![Before](http://oertel.it/pub/fk-before.png)

this it how it looks after, in a simple version:

![After](http://oertel.it/pub/fk-after.png)

**NOTE:** This is a first draft of the app, and my first app on github ever, so use with care. Please note the attached MIT-LICENSE.

### INSTALLATION

First, add the application to your INSTALLED_APPS:

    INSTALLED_APPS = (
      [..]
      'foreignkeysearch',
    )

Then adjust your project's urls.py (for ajax calls):

    urlpatterns = patterns('',
      [..]
      (r'^foreignkeysearch/', include('foreignkeysearch.urls')),
    )

### WRITE HANDLERS

Inspired by django-ajax-selects, you may now write handlers. The basic process of adding foreign key search forms is:

1. Write a handler that takes care of searching for related records, displaying the result list and things like that
2. Change the widget of the desired field in the models' ModelForm

- you're done!

#### EXAMPLE 1

The easiest implementation of a handlers looks like this:

    from foreignkeysearch.handler import BaseHandler

    class MyModelSearchHandler(BaseHandler):
        model = MyModel

and in admin.py:

    class MyAdmin(admin.ModelAdmin):
        [..]
        def formfield_for_dbfield(self, db_field, **kwargs):
            field = super(MyAdmin, self).formfield_for_dbfield(db_field, **kwargs)
            if db_field.name == 'myrelatedfield':
                field.widget = ForeignKeySearchForm(
                    db_field=db_field, 
                    handler=MyModelSearchHandler,
                )
            return field
            
Everything should be fine. Since we did not define anything but the model in the handler (please note that the model is mandatory), it falls back to defaults:

* All fields are shown in the search form
* All fields are searched via __icontains
* The field's \_\_unicode\_\_() or \_\_repr\_\_()-methods are used to display the results and the selected item

You can overwrite all this stuff, of course.

#### EXAMPLE 2

A more complete example:

First, we add a "handlers.py" to an app directory of a model which shall be used as a related model. The model targets images, and therefore contains copyrights notes etc., which we want to search later.
Our handler looks like this:

    from django.utils.safestring import mark_safe
    from django.db.models import Q
    from foreignkeysearch.handler import BaseHandler
    from images.models import Image
    
    class ImageSearchHandler(BaseHandler):
        # The model we connect this handler to
        model = Image
        # Exclude these fields from the search form, since we don't want to search for
        #  width, height, the filename and things like this.
        # We could add support for "images with width greater than x" later, however.
        exclude = (
            'width','height', 'filename_original', 'url_source', 'source',
            'file',
        )
    
        # We overwrite the handler's search function here, because the image model contains tags,
        # and we have to construct a query for them manually.
        # At this place, you can define the search routine yourself
        def search(self, params):
            q = Q()
            if params['title']:
                q = q & Q(title__icontains=params['title'])
            if params['description']:
                q = q & Q(description__icontains=params['description'])
            if params['tags']:
                q = q & Q(tags__name__in=[t.strip() for t in params['tags'].split(',')])
            return Image.objects.filter(q)
    
        # Every item in the result list shall look like this.
        # Please note the [link]...[/link] pseudo-tags: The text/code within them will
        # be replaced with the appropriate link that sets the foreign key later.
        # It could be e.g.: 
        # 
        # return '[link]%s[/link]</div>' % obj
        
        def item(self, obj):
            return mark_safe('<div style="display:block;width:100%%;clear:both;">[link]<div style="float:left;margin-right:8px;">%(image_preview)s</div>%(title)s[/link]<br /></div>' % ({
                'title': obj,
                'image_preview': obj.preview(),
            }))
    
        # This is the representation of the selected item. It is the visible
        # replacement for django's foreignkey-widget.
        def selected_item(self, obj):
            return mark_safe('%(title)s<br />%(image_preview)s' % ({
                'title': obj,
                'image_preview': obj.preview(),
            }))

The initialization in the admin.py is the same as in example 1.

### ADDITION/TODO

The app is in early stage, but works fine for now. I know that tests are missing, they will follow. Don't hesitate to add feature requests and bug reports in the issues.
