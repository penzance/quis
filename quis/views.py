import warnings

import requests
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(['GET'])
def index(request):
    config = settings.WATCHMEN
    watchmen = {}
    for env in config:
        watchmen[env] = []
        for project, url in config[env].iteritems():
            watchmen[env].append((project, get_watchman_data(url)))
        watchmen[env].sort()

    return render(request, 'quis/index.html', {'watchmen': watchmen})


def get_watchman_data(url):
    """
    Retrieves a set of service statuses from a django-watchman endpoint, and
    flattens the responses into a list that looks like:

        [{'name': 'serviceX', 'ok': True, 'details': {}},
         {'name': 'serviceY', 'ok': False,
          'details': {'error': 'foo', 'stacktrace': 'bar'}},
         {'name': 'serviceZ', 'ok': True,
          'details': {'custom': 'field'}}]
    """
    try:
        with warnings.catch_warnings(
                requests.packages.urllib3.exceptions.InsecureRequestWarning):
            response = requests.get(url, verify=False)
        watchman = response.json()
    except requests.exceptions.RequestException:
        watchman = {}

    rv = []
    for service in watchman:
        if isinstance(watchman[service], dict):
            # here we expect to see:
            #     'storage': {'ok': True},
            ok = watchman[service].pop('ok')
            rv.append({'name': service, 'ok': ok, 'details': watchman[service]})
        else:
            # here we expect to see:
            #     'databases': [{'default': {'ok': True}},
            #                   {'other': {'ok': True}}],
            for instance in watchman[service]:
                for name, status in instance.iteritems():
                    ok = status.pop('ok')
                    rv.append({'name': service + '/' + name,
                               'ok': ok, 'details': status})
    return rv
