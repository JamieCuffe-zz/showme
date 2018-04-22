from django.conf.urls import include, url
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

import hello.views
import django_cas_ng.views

# Examples:
# url(r'^$', 'gettingstarted.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

#OLD
# urlpatterns = [
#     url(r'^$', hello.views.index, name='index'),
#     url(r'^db', hello.views.db, name='db'),
#     url(r'^testjson', hello.views.testjson, name='testjson'),
#     path('admin/', admin.site.urls),
# ]

#NEW
urlpatterns = [
    url(r'^accounts/login$', django_cas_ng.views.login, name='cas_ng_login'),
    url(r'^accounts/logout$', django_cas_ng.views.logout, name='cas_ng_logout'),
    url(r'^$', hello.views.index, name = 'login'),
    url(r'^index', hello.views.index, name = 'index'),
    url(r'^certificate', hello.views.certificate, name = 'certificate'),
    url(r'^getrequest', hello.views.getrequest, name = 'getrequest'),
    url(r'^testtranscript', hello.views.testtranscript, name='testtranscript'),
    url(r'^result*', hello.views.result, name='result'),
] + static('static', document_root='hello/templates')
