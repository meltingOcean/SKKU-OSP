from django import template
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import resolve_url
from django.utils.safestring import mark_safe

import math
from datetime import datetime, timedelta

from community.models import ArticleComment, ArticleLike, ArticleScrap, Board, ArticleCommentLike
from team.models import Team, TeamMember,TeamInviteMessage
from user.models import Account

register = template.Library()
@register.filter
def time_before(date):
    delta = datetime.now() - date
    repr_string = ''
    if delta < timedelta(seconds=60):
        repr_string = '방금'
    elif delta < timedelta(seconds=3600):
        repr_string = f'{delta.seconds // 60}분 전'
    elif delta < timedelta(hours=24):
        repr_string = f'{delta.seconds // 3600}시간 전'
    elif delta < timedelta(days=15):
        repr_string = f'{delta.days}일 전'
    else:
        repr_string = date.strftime('%y.%m.%d')
    return repr_string

@register.filter
def remain_datetime(date):
    delta = date - datetime.now()
    if delta < timedelta(seconds=3600):
        repr_string = f'{math.ceil(delta.seconds / 60) % 60}분 전'
    elif delta < timedelta(days=1):
        repr_string = f'{math.ceil(delta.seconds / 3600) % 24}시간 전'
    else:
        repr_string = f'{delta.days}일 {math.ceil(delta.seconds / 3600) % 24}시간 전'
    return repr_string
    
@register.filter
def article_like(article):
    return len(ArticleLike.objects.filter(article=article))

@register.filter
def article_comment(article):
    return len(ArticleComment.objects.filter(article=article))

@register.filter
def article_scrap(article):
    return len(ArticleScrap.objects.filter(article=article))

@register.filter
def comment_like(comment):
    return len(ArticleCommentLike.objects.filter(comment=comment))

#TODO: 사용안되는 함수, 명세서에 작성안함.
@register.filter
def anonymous_checked(a_writer):
    if a_writer:
        return mark_safe('checked')
    else:
        return ''
    

@register.simple_tag(takes_context=True)
def board_sidebar_normal_board(context, request):
    result = ''
    boards = Board.objects.filter(team_id=None).exclude(board_type__in=['User', 'Notice'])
    # 일반 게시판이 팀 게시판과 분리되어있지 않아 DB에 넣기 애매함 
    icons = {"QnA": "bi-question-circle-fill",
    "Recruit": "bi-person-fill-add",
    "Normal": "bi-info-circle-fill",
    "Promotion": "bi-megaphone-fill"}
    for board in boards:
        url = resolve_url('community:Board',board_name=board.name,board_id=board.id)
        if board == context['board']:
            result += '<div class="boardgroup-item link-board hover-opacity selected">'
        else:
            result += '<div class="boardgroup-item link-board hover-opacity">'
        result += f'''
            <a href="{url}">
                <i class="bi {icons[board.board_type]} fa-lg"></i>
                <span>{board.name.capitalize()}</span>
            </a>
        </div>
        '''
        
    return mark_safe(result)

@register.simple_tag(takes_context=True)
def board_sidebar_team_board(context, request):
    team_board_query = Q()
    result = ''
    if request.user and request.user.is_authenticated:
        account = Account.objects.get(user=request.user.id)
        team_list = [x.team.name for x in TeamMember.objects.filter(member=account).prefetch_related('team')]
        team_board_query = Q(name__in=team_list)
        team_objs = Team.objects.filter(team_board_query)

        for board in Board.objects.filter(team_board_query):
            board_team = team_objs.get(id=board.team_id)

            url = resolve_url('community:Board', board_name=board.name, board_id=board.id)
            if board == context['board']:
                result += f'<div class="boardgroup-item link-team-board hover-opacity selected">'
            else:
                result += f'<div class="boardgroup-item link-team-board hover-opacity">'
            result += f'''
                <a href="{url}">
                    <img width="20px" height="20px" src="{board_team.image.url}" alt="{board.name} image" class="rounded-1">
                    <span>{board.name}</span>
                </a>
            </div>
            '''
    return mark_safe(result)

# 검색에 사용될 일반 게시판 목록
@register.simple_tag(takes_context=True)
def searcher_normal_board(context, request):
    result = ''
    boards = Board.objects.filter(team_id=None).exclude(board_type='User')
    for board in boards:
        if board == context['board']:
            result += f'<option value="{board.name}_{board.id}" selected>{board.name}</option>'
        else:
            result += f'<option value="{board.name}_{board.id}">{board.name}</option>'
        
    return mark_safe(result)

# 검색에 사용될 팀 게시판 목록
@register.simple_tag(takes_context=True)
def searcher_team_board(context, request):
    team_board_query = Q()
    result = ''
    if request.user and request.user.is_authenticated:
        account = Account.objects.get(user=request.user.id)
        team_list = [x.team.name for x in TeamMember.objects.filter(member=account).prefetch_related('team')]
        team_board_query = Q(name__in=team_list)
        team_objs = Team.objects.filter(team_board_query)

        for board in Board.objects.filter(team_board_query):
            board_team = team_objs.get(id=board.team_id)
            if board == context['board']:
                result += f'<option value="{board.id}" selected>{board.name}</option>'
            else:
                result += f'<option value="{board.id}">{board.name}</option>'

    return mark_safe(result)

@register.simple_tag()
def is_period_end(date):
    if isinstance(date, datetime):
        return date < datetime.now()
    else:
        return True

@register.simple_tag
def is_teammember_admin(team, user):
    if not user.is_anonymous:
        tm =  TeamMember.objects.filter(team=team, member__user=user).first()
        if tm and tm.is_admin:
            return True
    return False

@register.simple_tag
def apply_messages(team):
    apply_messages = TeamInviteMessage.objects.filter(
        team=team,
        direction=False,
        status=0
    )
    return apply_messages



@register.simple_tag
def is_article_thumb_up(article, user):
    if user.is_anonymous:
        return False
    if ArticleLike.objects.filter(article=article, account__user=user):
        return True
    else:
        return False

@register.simple_tag
def is_article_scrap(article, user):
    if user.is_anonymous:
        return False
    if ArticleScrap.objects.filter(article=article, account__user=user):
        return True
    else:
        return False

@register.simple_tag
def is_comment_like(comment, user):
    if user.is_anonymous:
        return False
    if ArticleCommentLike.objects.filter(comment=comment, account__user_id=user):
        return True
    else:
        return False