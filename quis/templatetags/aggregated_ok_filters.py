from django import template
register = template.Library()


@register.filter
def services_ok(services):
    # services = [{'ok': True, 'name': 'databases/default', details: {}}, ...]
    # treat empty services as a failure
    return all(s['ok'] for s in services) if services else False

@register.filter
def env_ok(watchmen):
    # watchmen = [{'env': 'dev', 'project': 'foo', 'services': [...]}, ...]
    # treat empty services as a failure
    return all(all(s['ok'] for s in w['services']) if w['services'] else False
                   for w in watchmen)
