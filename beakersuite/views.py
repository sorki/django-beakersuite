import os

from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response

default_datapath = settings.BEAKERSUITE_DATA_PATH

def render_error(request, msg):
    return render_to_response('beakersuite/error.html',
        dict(error=msg),
        RequestContext(request, {}))

def list_results(request,
    data_path=default_datapath,
    num_latest=None,
    template_name='beakersuite/list.html'):

    if not os.path.isdir(data_path):
        render_error(request, 'No such dir: %s' % data_path)

    rundata = list_dirs(data_path, None, num_latest)
    return render_to_response(template_name,
        dict(runs=rundata, data_path=data_path),
        RequestContext(request, {}))

def list_single(request,
    dirname,
    data_path=default_datapath,
    template_name='beakersuite/list.html'):

    if not os.path.isdir(os.path.join(data_path, dirname)):
        render_error(request, 'No such dir: %s' %
            os.path.join(data_path, dirname))

    rundata = list_dirs(data_path, [dirname], None)
    return render_to_response(template_name,
        dict(runs=rundata, data_path=data_path),
        RequestContext(request, {}))


def list_dirs(data_path, only_dirs, num_latest):
    test_count = 0
    rundata = []
    dirs = os.listdir(data_path)
    dirs.sort(reverse=True)
    if num_latest:
        dirs = dirs[0:num_latest]

    if only_dirs:
        dirs = filter(lambda x: x in only_dirs, dirs)

    for run in dirs:
        fname = os.path.join(data_path, run, 'results')
        if os.path.isfile(fname):
            with open(fname) as f:
                cont = map(lambda x: x.strip(), f.readlines())
        else:
            continue

        tests = []
        test_name = None
        test_fail = False
        overal_fail = False

        for l in cont:
            if 'Test name' in l:
                if test_name is None:
                    test_name = l.split('Test name')[1].split(':')[1].strip()
                else:
                    tests.append(dict(name=test_name, result=test_fail))
                    test_fail = False
                    test_name = l.split('Test name')[1].split(':')[1].strip()

            if 'FAIL' in l:
                test_fail = True
                overal_fail = True

        tests.append(dict(name=test_name, result=test_fail))
        test_count = max(test_count, len(tests))
        rundata.append(dict(name=run, result=overal_fail, tests=tests))
        rundata.sort(reverse=True)

    return rundata
