from django.conf.urls import include, url
from django.urls import path

from django.contrib import admin
admin.autodiscover()

import hello.views

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
    url(r'^$', hello.views.login, name = 'login'),
    url(r'^index', hello.views.index, name = 'index'),
    url(r'^transcript', hello.views.transcript, name = 'transcript'),
    # added a period before '*'
    url(r'^result.*', hello.views.result, name = 'result')
]
