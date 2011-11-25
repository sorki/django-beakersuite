from django.conf import settings
from django.conf.urls.defaults import patterns, url

from views import list_results

urlpatterns = patterns('',
    url(r'list/$',
        list_results,
        {'data_path': settings.BEAKERSUITE_DATA_PATH},
        name='beakersuite_list'),
    )
