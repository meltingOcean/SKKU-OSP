from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import connection
from django.contrib.auth.decorators import login_required

from user.models import Account, StudentTab
from .models import Challenge, ChallengeAchieve

# Create your views here.
@login_required
def challenge_list_view(request):
    try:
        achieve_list = ChallengeAchieve.objects.filter(account__user=request.user).select_related('challenge')
        my_acc = Account.objects.get(user=request.user.id)
        new_challenge = achieve_list.values_list('challenge', flat=True)
        for challenge in Challenge.objects.exclude(id__in=new_challenge):
            achievement_check(my_acc, challenge)
            achieve_list = ChallengeAchieve.objects.filter(account__user=request.user).select_related('challenge')
        context = {
            'achieved_list': [],
            'not_achieved_list': []
        }
        achieve_cnt_query = '''
            select challenge_id as id, Count(*) as achieve_cnt
            from challenge_challengeachieve 
            where acheive_date IS NOT NULL
            group by challenge_id;
        '''
        achieve_cnt = {}
        for x in ChallengeAchieve.objects.raw(achieve_cnt_query):
            achieve_cnt[x.id] = x.achieve_cnt
        account_cnt = len(Account.objects.all())
        context['account_cnt'] = account_cnt
        for achievement in achieve_list:
            achievement.width = achievement.progress / achievement.challenge.max_progress * 100
            achievement.total = achieve_cnt[achievement.challenge.id] if achievement.challenge.id in achieve_cnt else 0
            if achievement.challenge.max_progress > achievement.progress:
                context['not_achieved_list'].append(achievement)
            else:
                context['achieved_list'].append(achievement)
        context['total'] = len(context['not_achieved_list']) + len(context['achieved_list'])
        context['total_cnt'] = len(StudentTab.objects.all())
        return render(request, 'challenge/main.html', context)

    except:
        # 관리자 혹은 수집데이터가 없을 떄
        return redirect("./forbidden")

@login_required
def challenge_acheive_update(request):
    challenge_list = Challenge.objects.all()
    my_acc = Account.objects.get(user=request.user.id)
    acheive_list = ChallengeAchieve.objects.filter(account=my_acc)
    acheive_id_list = acheive_list.values_list('challenge__id', flat=True)
    print(acheive_id_list)
    for challenge in challenge_list:
        try:
            achievement_check(my_acc, challenge)
        except:
            return JsonResponse({'status': 'fail', 'message': 'DB Fail'})
    return JsonResponse({'status': 'success'})

def achievement_check(user: Account, challenge: Challenge):
    sql_with_format = challenge.sql.replace('{{github_id}}', user.student_data.github_id)
    sql_with_format = sql_with_format.replace('{{user_id}}', str(user.user_id))
    acheive_list = ChallengeAchieve.objects.filter(account=user)
    acheive_id_list = acheive_list.values_list('challenge__id', flat=True)
    try:
        cursor = connection.cursor()
        cursor.execute(sql_with_format)
        result = cursor.fetchall()[0]
        if challenge.id in acheive_id_list:
            acheive = acheive_list.get(challenge=challenge)
            acheive.progress = result[0]
            acheive.acheive_date = result[1]
        else:
            acheive = ChallengeAchieve.objects.create(
                account=user,
                challenge=challenge,
                progress=result[0],
                acheive_date=result[1]
            )
        acheive.save()
    except:
        connection.rollback()

def forbidden_page(request):
    return render(request, 'challenge/forbidden.html')