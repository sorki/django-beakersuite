import os

from django.template import RequestContext
from django.shortcuts import render_to_response

def render_error(request, msg):
    return render_to_response('beakersuite/error.html',
        dict(error=msg),
        RequestContext(request, {}))

def list_results(request, data_path,
    template_name='beakersuite/list.html'):

    if not os.path.isdir(data_path):
        render_error(request, 'No such dir: %s' % data_path)

    test_count = 0
    rundata = []
    for run in os.listdir(data_path):
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

    return render_to_response(template_name,
        dict(runs=rundata, test_count=range(1, test_count+1),
             data_path=data_path),
        RequestContext(request, {}))
