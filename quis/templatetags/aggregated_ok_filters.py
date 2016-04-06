from django import template
register = template.Library()


@register.filter
def services_ok(services):
    # treat empty services as a failure
    return all(s['ok'] for s in services) if services else False

@register.filter
def env_ok(env):
    # treat empty services as a failure
    return all(all(s['ok'] for s in services) if services else False
                   for _, services in env)
