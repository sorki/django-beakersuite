from django.conf import settings
from django.conf.urls.defaults import patterns, url

from views import list_results

urlpatterns = patterns('',
    url(r'latest/$',
        list_results,
        {'data_path': settings.BEAKERSUITE_DATA_PATH,
        'num_latest': 2,
        'template_name':'beakersuite/list.html'},
        name='beakersuite_latest'),

    url(r'list/$',
        list_results,
        {'data_path': settings.BEAKERSUITE_DATA_PATH,
        'template_name':'beakersuite/block_list.html'},
        name='beakersuite_list'),
    )
