from django import template

register = template.Library()

@register.filter(name='has_event_option')
def has_event_option(regdetail, eventoption):
    for regoption in regdetail.regeventoptions_set.all():
        if regoption.option == eventoption:
            return True
    return False
