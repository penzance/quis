import collections
import logging
import warnings
from concurrent import futures

import redis
import requests
import cachecontrol
from cachecontrol.caches import RedisCache
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


# TODO: mechanism to bubble up details from individual services?

# set up logger and requests session cache
logger = logging.getLogger(__name__)
pool = redis.ConnectionPool(host=settings.REDIS_HOST,
                            port=settings.REDIS_PORT)
cache = RedisCache(redis.Redis(connection_pool=pool))
session = cachecontrol.CacheControl(requests.Session(), cache)
session.verify = False


@require_http_methods(['GET'])
def index(request):
    config = settings.WATCHMEN
    watchmen = []
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_bucket = {}
        for env in config:
            for project, url in config[env].iteritems():
                future = executor.submit(get_watchman_data, url)
                future_to_bucket[future] = (env, project)

        for future in futures.as_completed(future_to_bucket):
            env, project = future_to_bucket[future]
            try:
                services = future.result()
            except Exception as e:
                logger.exception('unable to get status for %s, %s',
                                 env, project)
                services = []
            watchmen.append({'env': env, 'project': project, 'services': services})
    watchmen.sort(key=lambda x: (x['env'], x['project']))
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
            response = session.get(url, timeout=5)
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
