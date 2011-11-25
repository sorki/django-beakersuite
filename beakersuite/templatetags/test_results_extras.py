import os
from django import template
from django.utils.datastructures import SortedDict

register = template.Library()

@register.simple_tag(takes_context=True)
def get_details(context, data, run, test):
        data_dir = os.path.join(data, run, 'test', test)
        if not os.path.isdir(data_dir):
            return 'ERROR: No such directory: %s' % data_dir

        filelist = SortedDict([
            ('fail.log', 'fail'),
            ('protocol.log', 'beaker'),
            ('full.log', 'beaker'),
            ('messages', 'messages'),
            ('dmesg', 'dmesg'),
        ])

        contentlist = []

        for fname, pretty in filelist.items():
            var = fname.replace('.log', '')
            fpath = os.path.join(data_dir, fname)
            if os.path.isfile(fpath):
                d = dict(
                    name=var,
                    content=open(fpath).read(),
                    pretty=pretty)
                if d['content']:
                    contentlist.append(d)

            context['test_details'] = contentlist
        return ''
