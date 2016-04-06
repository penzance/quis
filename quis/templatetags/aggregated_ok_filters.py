from django import template
register = template.Library()


@register.filter
def services_ok(services):
    return all(s['ok'] for s in services)

@register.filter
def env_ok(env):
    return all(all(s['ok'] for s in services) for _, services in env)
