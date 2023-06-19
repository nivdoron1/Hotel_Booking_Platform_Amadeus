from django import template

register = template.Library()


@register.filter
def split(value, key):
    """
        Returns the value turned into a list where each string is delimited by key.
    """
    return value.split(key)
