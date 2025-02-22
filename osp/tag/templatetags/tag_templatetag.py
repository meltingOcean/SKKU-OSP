from django import template

from django.utils.safestring import mark_safe
from tag.models import TagIndependent
from user.models import AccountInterest
from community.models import *

register = template.Library()

@register.simple_tag
def category_tag(request):
    pre_tags = request.GET.get('tag', "")
    pre_tags=pre_tags.split(",")
    result = ''
    tags = Tag.objects.all()
    
    type_list = list(tags.values_list("type", flat=True).distinct())

    for t in type_list:
        result += f'<optgroup label="{t}">'
        objects = TagIndependent.objects.filter(type=t)
        name_list = list(objects.values_list("name", flat=True).distinct())
        name_list.sort()
        for n in name_list:
            if n in  pre_tags:
                result += f'<option class="tag-{t}" value="{n}" selected>{n}</option>'
            else:
                result += f'<option class="tag-{t}" value="{n}">{n}</option>'
        result += '</optgroup>'

    return mark_safe(result)

@register.simple_tag
def get_account_tags(account):
    return AccountInterest.objects.filter(account=account)

@register.simple_tag
def category_tag_domain(request):
    result = ''

    tags = TagIndependent.objects.filter(type="domain")
    type_list = list(tags.values_list("type", flat=True).distinct())

    for t in type_list:
        result += f'<optgroup label="{t}">'
        objects = TagIndependent.objects.filter(type=t)
        name_list = list(objects.values_list("name", flat=True).distinct())
        name_list.sort()
        for n in name_list:
            result += f'<option class="tag-{t}" value="{n}">{n}</option>'
        result += '</optgroup>'

    return mark_safe(result)

@register.simple_tag
def category_tag_language(request):
    result = ''
    
    tags = TagIndependent.objects.exclude(type="domain")
    type_list = list(tags.values_list("type", flat=True).distinct())

    for t in type_list:
        result += f'<optgroup label="{t}">'
        objects = TagIndependent.objects.filter(type=t)
        name_list = list(objects.values_list("name", flat=True).distinct())
        name_list.sort()
        for n in name_list:
            result += f'<option class="tag-{t}" value="{n}">{n}</option>'
        result += '</optgroup>'

    return mark_safe(result)

@register.simple_tag
def email_domain_tag(request):
    result = ''
    result += '<option value="" selected>직접입력</option>'
    domain_list  = ["g.skku.edu", "skku.edu", "gmail.com", "naver.com", "kakao.com", "nate.com", "yahoo.com"]
    for d in domain_list:
        result += f'<option value="{d}">{d}</option>'
    result += '<span>V</span>'

    return mark_safe(result)
