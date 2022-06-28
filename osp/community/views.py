from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import Board, Article
from datetime import datetime, timedelta
from django.views.generic import TemplateView
import hashlib
import math

# Create your views here.

@login_required
def main(request):
    board_list = []
    for board in Board.objects.all():
        week_ago = datetime.now() - timedelta(days=7)
        print(week_ago)
        print(datetime.now())
        article_list = Article.objects.filter(board_id=board, 
                                              pub_date__range=[
                                                  week_ago.strftime('%Y-%m-%d %H:%M:%S-09:00'),
                                                  datetime.now().strftime('%Y-%m-%d %H:%M:%S-09:00')
                                              ]
                                              )
        print(article_list)
        if len(article_list) > 0:
            article_list = article_list.order_by('-view_cnt')
            board.article_list = article_list[:min(3, len(article_list))]
        else:
            board.article_list = []
        board.board_color = hashlib.md5(board.name.encode()).hexdigest()[:6]
        board_list.append(board)
    return render(request, 'community/main.html', {'boards': board_list})

def board(request, board_name):
    try:
        board = Board.objects.get(name=board_name)
    except Board.DoesNotExist:
        return redirect('/community')
    board_color = hashlib.md5(board.name.encode()).hexdigest()[:6]
    if board.board_type == 'QnA':
        return render(request, 'community/qna-board.html', {'board': board, 'board_name':board_name, 'board_color': board_color})
    if board.board_type == 'Normal':
        return render(request, 'community/board.html', {'board': '', 'board_name':board_name, 'board_color': board_color})
    if board.board_type == 'Team':
        return render(request, 'community/team-board.html', {'board': '', 'board_name':board_name, 'board_color': board_color})

def article_list(request, board_name):
    PAGE_SIZE = 5
    try:
        board = Board.objects.get(name=board_name)
    except Board.DoesNotExist:
        result = {'html': '', 'max-page': 0}
        return JsonResponse(result)
    context = {}
    context['bartype'] = 'normal'
    context['board_color'] = hashlib.md5(board.name.encode()).hexdigest()[:6]
    sort_field = request.GET.get('sort', ('-pub_date', 'title'))
    page = int(request.GET.get('page', 1))
    total_len = len(Article.objects.all())
    article_list = Article.objects.filter(board_id=board
                    ).order_by(*sort_field
                    )[PAGE_SIZE * (page - 1):]
    article_list = article_list[:PAGE_SIZE]
    context['article_list'] = article_list
    result = {}
    result['html'] = render_to_string('community/article-bar.html', context)
    result['max-page'] = math.ceil(total_len / PAGE_SIZE)
    return JsonResponse(result)