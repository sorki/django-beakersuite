from django.conf.urls.defaults import patterns, url

from views import list_results, list_single

urlpatterns = patterns('',
    url(r'latest/$',
        list_results,
        {'num_latest': 2,
        'template_name':'beakersuite/list.html'},
        name='beakersuite_latest'),

    url(r'list/$',
        list_results,
        {'template_name':'beakersuite/block_list.html'},
        name='beakersuite_list'),

    url(r'(?P<dirname>.+)/$',
        list_single,
        name='beakersuite_single'),
    )
