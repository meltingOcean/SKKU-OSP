from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.db.models import Avg, Sum, Subquery
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView, DeleteView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.files.images import get_image_dimensions

from home.models import DistFactor, DistScore
from tag.models import Tag, DomainLayer
from team.models import TeamMember
from repository.models import GithubRepoStats, GithubRepoCommits

from user.models import GitHubScoreTable, StudentTab, GithubScore, Account, AccountInterest, GithubStatsYymm, DevType, AccountPrivacy
from user.forms import ProfileImgUploadForm
from user.templatetags.gbti import get_type_test, get_type_analysis
from user import update_act

import time, datetime
import json
import os
import math


# Create your views here.
class ProfileView(TemplateView):
    '''
    유저 프로필
    url        : /user/<username>
    template   : profile/profile.html 

    Returns :
        GET     : redirect, render
    '''
    
    template_name = 'profile/profile.html'
    start_year = 2019

    # 새로 고침 시 GET 요청으로 처리됨.
    def get_context_data(self, request, *args, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            user = User.objects.get(username=context["username"])
            account = Account.objects.get(user=user)
            context['account'] = account
            student_data = account.student_data
            github_id = student_data.github_id
        except Exception as e:
            print(e)
            return None
            
        chartdata = {}
        context["user_type"] = 'user'
        context["student_id"] = student_data.id

        score_data_list = []
        score_detail_data = GithubScore.objects.filter(github_id=github_id).order_by("year")
        for row in score_detail_data:
            score_data_list.append(row.to_json())
        
        # GitHub data가 존재하지 않는 경우 더미데이터 리턴하고 
        # 데이터 관련 부분 프로필페이지에서 제거
        try:
            end_year = score_data_list[len(score_data_list)-1]["year"]
            num_year = end_year-self.start_year+1
            context["end_year"] = end_year
            context["year_list"] = [year for year in range(end_year, self.start_year-1, -1)]
            chartdata["score_data"] = score_data_list
        except Exception as e:
            print("[profile view] There are no score_data", e)
            context["end_year"] = datetime.datetime.now().year
            context["score_data"] = None
            context["chart_data"] = []
            context["type_data"] = []
            context["success"] = False
            return context
        
        student = StudentTab.objects.all()
        star_data = GithubRepoStats.objects.filter(github_id__in=Subquery(student.values('github_id'))).extra(tables=['github_repo_contributor'], where=["github_repo_contributor.repo_name=github_repo_stats.repo_name", "github_repo_contributor.owner_id=github_repo_stats.github_id", "github_repo_stats.github_id = github_repo_contributor.github_id"]).values('github_id').annotate(star=Sum("stargazers_count"))
        
        own_star = {"star" : 0}
        star_temp_dist = []
        for row in star_data:
            star_temp_dist.append(row["star"])
            if row["github_id"] == github_id:
                own_star["star"] = row["star"]
        star_temp_dist.sort()

        mean = sum(star_temp_dist)/len(star_temp_dist)
        own_star["avg"] = mean
        sigma = math.sqrt(sum((val - mean)**2 for val in star_temp_dist)/len(star_temp_dist))
        own_star["std"] = sigma
        star_dist = [star_temp_dist for _ in range(num_year)]
        
        annual_dist = {}
        dist_score_total = DistScore.objects.filter(case_num=0)
        for row in dist_score_total:
            row_json = row.to_json()
            annual_dist[row_json["year"]] = row_json
            
        dist_factor_total = DistFactor.objects.filter(case_num=0)
        for row in dist_factor_total:
            row_json = row.to_json()
            factor = row_json["factor"]
            row_json[factor] = row_json.pop("value")
            row_json[factor+"_sid"] = row_json.pop("value_sid")
            row_json[factor+"_sid_pct"] = row_json.pop("value_sid_pct")
            row_json[factor+"_dept"] = row_json.pop("value_dept")
            row_json[factor+"_dept_pct"] = row_json.pop("value_dept_pct")
            annual_dist[row_json["year"]].update(row_json)
        for annual_key in annual_dist.keys():
            key_name = "year"+str(annual_key)
            chartdata[key_name] = json.dumps([annual_dist[annual_key]])

        # 유저 점수를 모두 가져와서 각 요소별로 분포 데이터를 만든다.
        # 연도를 인덱스로 하여 저장한다.
        score_data = GitHubScoreTable.objects.all()
        user_data_list = []
        score_dist = [[] for _ in range(num_year)]
        commit_dist = [[] for _ in range(num_year)]
        pr_dist = [[] for _ in range(num_year)]
        issue_dist = [[] for _ in range(num_year)]
        repo_dist = [[] for _ in range(num_year)]
        for row in score_data:
            score_json = row.to_json()

            if score_json["year"] >= self.start_year :
                yid = score_json["year"] - self.start_year
                score_dist[yid].append(score_json["total_score"])
                commit_dist[yid].append(score_json["commit_cnt"])
                pr_dist[yid].append(score_json["pr_cnt"])
                issue_dist[yid].append(score_json["issue_cnt"])
                repo_dist[yid].append(score_json["repo_cnt"])
            if row.github_id == github_id:
                user_data_list.append(score_json)
        
        chartdata["user_data"] = json.dumps(user_data_list)
        
        # 연도별로 각 요소별 평균, 표준편차를 구해 확률밀도함수를 구할 수 있도록 한다.
        annual_dist_data = {"score":[], "commit": [], "pr": [], "issue": [], "repo": [], "score_std":[], "commit_std":[], "pr_std":[], "issue_std":[], "repo_std":[]}
        for sub_dist in score_dist:
            sub_dist.sort()
            mean = sum(sub_dist)/len(sub_dist)
            annual_dist_data["score"].append(mean)
            sigma = math.sqrt(sum((val - mean)**2 for val in sub_dist)/len(sub_dist))
            annual_dist_data["score_std"].append(sigma)
        for sub_dist in commit_dist:
            sub_dist.sort()
            mean = sum(sub_dist)/len(sub_dist)
            annual_dist_data["commit"].append(mean)
            sigma = math.sqrt(sum((val - mean)**2 for val in sub_dist)/len(sub_dist))
            annual_dist_data["commit_std"].append(sigma)
        for sub_dist in pr_dist:
            sub_dist.sort()
            mean = sum(sub_dist)/len(sub_dist)
            annual_dist_data["pr"].append(mean)
            sigma = math.sqrt(sum((val - mean)**2 for val in sub_dist)/len(sub_dist))
            annual_dist_data["pr_std"].append(sigma)
        for sub_dist in issue_dist:
            sub_dist.sort()
            mean = sum(sub_dist)/len(sub_dist)
            annual_dist_data["issue"].append(mean)
            sigma = math.sqrt(sum((val - mean)**2 for val in sub_dist)/len(sub_dist))
            annual_dist_data["issue_std"].append(sigma)
        for sub_dist in repo_dist:
            sub_dist.sort()
            mean = sum(sub_dist)/len(sub_dist)
            annual_dist_data["repo"].append(mean)
            sigma = math.sqrt(sum((val - mean)**2 for val in sub_dist)/len(sub_dist))
            annual_dist_data["repo_std"].append(sigma)
        chartdata["annual_overview"] = json.dumps([annual_dist_data])
        chartdata["score_dist"] = score_dist
        chartdata["star_dist"] = star_dist
        chartdata["commit_dist"] = commit_dist
        chartdata["pr_dist"] = pr_dist
        chartdata["issue_dist"] = issue_dist
        chartdata["repo_dist"] = repo_dist
        
        monthly_contr = [ [] for _ in range(num_year)]
        gitstat_year = GithubStatsYymm.objects.filter(github_id=github_id)
        for row in gitstat_year:
            row_json = row.to_json()
            row_json['star'] = own_star["star"]
            if row_json["year"] >= self.start_year and row_json["year"] <= end_year:
                monthly_contr[row_json["year"] - self.start_year].append(row_json)
        total_avg_queryset = GithubStatsYymm.objects.exclude(num_of_cr_repos=0, num_of_co_repos=0, num_of_commits=0, num_of_prs=0, num_of_issues=0).values('start_yymm').annotate(commit=Avg("num_of_commits"), pr=Avg("num_of_prs"), issue=Avg("num_of_issues"), repo_cr=Avg("num_of_cr_repos"), repo_co=Avg("num_of_co_repos")).order_by('start_yymm')
        
        monthly_avg = [ [] for _ in range(num_year)]
        for avg in total_avg_queryset:
            yid = avg["start_yymm"].year - self.start_year
            if avg["start_yymm"].year >= self.start_year and avg["start_yymm"].year <= end_year :
                avg["year"] = avg["start_yymm"].year
                avg["month"] =  avg["start_yymm"].month
                avg.pop('start_yymm', None)
                monthly_avg[yid].append(avg)
        chartdata["monthly_contr"] = monthly_contr
        chartdata["own_star"] = own_star
        chartdata["monthly_avg"] = monthly_avg
        chartdata["username"] = github_id
        context["star"] = own_star["star"]
        context["chart_data"] = json.dumps(chartdata)
        
        #GBTI test
        hour_dist, time_circmean, daytime, night, daytime_min, daytime_max = update_act.read_commit_time(context['username'])
        
        major_act, indi_num, group_num = update_act.read_major_act(context['username'])
        
        commit_freq, commit_freq_dist = update_act.read_frequency(context['username'])
        try:
            type_data = {}
            type_data["typeE_data"] = hour_dist
            type_data["typeE_sector"] = [int(daytime_min/3600), int(daytime_max/3600)]
            type_data["typeF_data"] = commit_freq_dist
            type_data["typeG_data"] = [indi_num, group_num]
            context["type_data"] = json.dumps(type_data)
        except Exception as e:
            print("Get Type data error", e)

        try:
            devtype_data = DevType.objects.get(account=account)
            try:
                devtype_data.typeE = -1 if daytime > night else 1
                devtype_data.typeF = commit_freq
                devtype_data.typeG = 1 if major_act == 'individual' else -1
                devtype_data.save()
                gbti_data = {"typeE":devtype_data.typeE, "typeF": devtype_data.typeF, "typeG": devtype_data.typeG}

                gbti_desc, gbti_descKR, gbti_icon = get_type_analysis(list(gbti_data.values()))
                gbti_data["zip"]=list(zip(gbti_desc, gbti_descKR, gbti_icon))
                context["gbti"] = gbti_data
            except Exception as e:
                print("Calculate dev type error", e)
                context["gbti"] = None
            test_data = {"typeA":devtype_data.typeA, "typeB": devtype_data.typeB, "typeC": devtype_data.typeC, "typeD": devtype_data.typeD}
            test_data.update(get_type_test(devtype_data.typeA, devtype_data.typeB, devtype_data.typeC, devtype_data.typeD))
            def get_type_len(type_val):
                return (int((100 - type_val)/2) - 3, int((100 + type_val)/2) + (100 + type_val)%2 - 3)

            test_data["typeAl"], test_data["typeAr"] = get_type_len(test_data["typeA"])
            test_data["typeBl"], test_data["typeBr"] = get_type_len(test_data["typeB"])
            test_data["typeCl"], test_data["typeCr"] = get_type_len(test_data["typeC"])
            test_data["typeDl"], test_data["typeDr"] = get_type_len(test_data["typeD"])
        except Exception as e:
            print("Get DevType object error", e)
            test_data = None
            typeE = -1 if daytime > night else 1
            typeF = commit_freq
            typeG = 1 if major_act == 'individual' else -1
            gbti_data = {"typeE":typeE, "typeF": typeF, "typeG": typeG}
            gbti_desc, gbti_descKR, gbti_icon = get_type_analysis(list(gbti_data.values()))
            gbti_data["zip"]=list(zip(gbti_desc, gbti_descKR, gbti_icon))
            context["gbti"] = gbti_data
        context["test"] = test_data
        context["success"] = True

        tags_domain = Tag.objects.filter(type='domain') # 분야 태그
        ints = AccountInterest.objects.filter(account=account).filter(tag__in=tags_domain)
        student_id = account.student_data.id
        domain_layer = DomainLayer.objects
        lang_tags = Tag.objects.filter(name__in = AccountInterest.objects.filter(account=account).exclude(tag__type="domain").values("tag")).order_by("name")
        account_lang = AccountInterest.objects.filter(account=account, tag__in=lang_tags).exclude(tag__type="domain").order_by("tag__name")
        level_list = [ al.level for al in account_lang ]

        lang = []

        for tag in lang_tags:
            lang_tag_dict = {"name":tag.name, "type":tag.type}
            lang_tag_dict["level"] = level_list[len(lang)]
            lang.append(lang_tag_dict)
        ints_parent_layer = domain_layer.filter(parent_tag__in=ints.values('tag')).values('parent_tag').order_by('parent_tag').distinct()
        ints_child_layer = domain_layer.filter(child_tag__in=ints.values('tag')).values('child_tag').order_by('child_tag').distinct()
        relation_origin = domain_layer.values('parent_tag', 'child_tag')
        relations = []
        remain_children = list(ints_child_layer)

        for par in ints_parent_layer:
            relation = {
                'parent' :par['parent_tag'],
                'children' : [],
            }
            for chi in ints_child_layer:
                if {'parent_tag':par['parent_tag'],'child_tag':chi['child_tag']} in relation_origin:
                    relation['children'].append(chi['child_tag'])
                    remain_children.remove({'child_tag' : chi['child_tag']})
            relations.append(relation)

        context["relations"] =  relations
        context["remains"] = remain_children
        context["account"] = Account.objects.get(user=user.id)
        context["info"] = StudentTab.objects.get(id=student_id)
        context["ints"] = ints
        context["lang"] = lang
        
        return context

    def get(self, request, *args, **kwargs):

        start = time.time()

        # 비 로그인 시 프로필 열람 불가
        if request.user.is_anonymous:
            return redirect('/community')

        context = self.get_context_data(request, *args, **kwargs)
        if not context:
            return redirect('/community')

        student_info = context['account'].student_data

        # student repository info
        context['cur_repo_type'] = 'owned'
        ## owned repository
        student_score = GitHubScoreTable.objects.filter(id=student_info.id).order_by('-year').first()

       

        student_account = context['account']
        acc_pp = AccountPrivacy.objects.get(account=student_account)
        print("acc_pp", acc_pp.open_lvl, acc_pp.is_write, acc_pp.is_open)
        
        is_own = request.user.username == context['username']
        # initialize
        is_redirect = True
        if 'privacy' in request.session:
            del request.session['privacy']
        if 'alert' in request.session:
            del request.session['alert']
        if not is_own and acc_pp.open_lvl == 0:
            target_team = TeamMember.objects.filter(member=context['account']).values('team')
            if target_team:
                # team check
                cowork = TeamMember.objects.filter(member=request.user.account, team__in=target_team)
                if cowork:
                    is_redirect = False
                    request.session['privacy'] = "팀원의 프로필페이지 입니다."
                    request.session['alert'] = True
                    acc_pp.open_lvl = 1
            if is_redirect:
                request.session['privacy'] = "해당 사용자는 정보 비공개 상태입니다."
                request.session['alert'] = True
                return redirect('../'+request.user.username+'/')
        data = {

        }

        context['score'] = student_score
        context['is_own'] = is_own
        context['open_lvl'] = acc_pp.open_lvl
        context['is_write'] = acc_pp.is_write
        context['is_open'] = acc_pp.is_open

        if 'alert' in request.session and request.session['alert']:
            print(request.session['privacy'])
            if 'privacy' in request.session and request.session['privacy']:
                data['privacy'] = request.session['privacy']
        context['data'] = data
        print("ProfileView get time :", time.time() - start)

        return render(request=request, template_name=self.template_name, context=context)

    


class ProfileEditView(TemplateView):
    '''
    유저 프로필 수정 페이지
    url        : /user/<username>
    template   : profile/profile.html 

    Returns :
        GET     : render, redirect
    '''

    def get_context_data(self, request, *args, **kwargs):
        # context 는 username과 view 인스턴스를 가진 딕셔너리
        context = super().get_context_data(**kwargs)
        if str(request.user) != context["username"] : # 타인이 edit페이지 접속 시도시 프로필 페이지로 돌려보냄
            print("허용되지 않는 접근 입니다.")
            context['valid'] = 0
            return context
        context['valid'] = 1
        username = context['username']
        user = User.objects.get(username=username)

        student_account = Account.objects.get(user=user.id)
        student_id = student_account.student_data.id

        tags_domain = Tag.objects.filter(type='domain')

        
        context["account"] = Account.objects.get(user=user.id)
        context["info"] = StudentTab.objects.get(id=student_id)
        context["ints"] = AccountInterest.objects.filter(account=student_account).filter(tag__in=tags_domain)
        context["lang"] = AccountInterest.objects.filter(account=student_account).exclude(tag__in=tags_domain)
        context["privacy"] = AccountPrivacy.objects.get(account=student_account)
        return context

    def get(self, request, *args, **kwargs):

        context = self.get_context_data(request, *args, **kwargs)
        if(context['valid'] == 0):
            return redirect(f'/user/{context["username"]}/')

        return render(request, 'profile/profile-edit.html', context)


def student_id_to_username(request, student_id):
    username = Account.objects.get(student_data=student_id).user.username
    return redirect(f'/user/{username}/')


@csrf_exempt
def compare_stat(request, username):
    if request.method == 'POST':
        start_year = 2019
        data = json.loads(request.body)
        #data에는 github_id 가 들어있어야한다.
        github_id = data["github_id"]
        latest_data = GithubScore.objects.filter(github_id=github_id).order_by("year").last()
        end_year = latest_data.year
        own_star = 0
        try:
            star_data = GithubRepoStats.objects.filter(github_id=github_id).extra(tables=['github_repo_contributor'], where=["github_repo_contributor.repo_name=github_repo_stats.repo_name", "github_repo_contributor.owner_id=github_repo_stats.github_id", "github_repo_stats.github_id = github_repo_contributor.github_id"]).values('github_id').annotate(star=Sum("stargazers_count"))
            for sd in star_data:
                own_star = sd['star']
        except Exception as e:
            print(e)
        
        monthly_contr = [ [] for _ in range(end_year-start_year+1)]
        gitstat_year = GithubStatsYymm.objects.filter(github_id=github_id)
        for row in gitstat_year:
            row_json = row.to_json()
            row_json['star'] = own_star
            if row_json["year"] >= start_year :
                monthly_contr[row_json["year"]-start_year].append(row_json)
                
        context = {
            "monthly_contr":monthly_contr,
            "github_id":github_id,
        }
        
        return JsonResponse(context)
    
    
class ProfileRepoView(TemplateView):
    
    template_name = 'profile/repo.html'
    def get_context_data(self, *args, **kwargs):
        
        start = time.time()
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username=context["username"])
        account = Account.objects.get(user=user)
        student_data = account.student_data
        github_id = student_data.github_id
        context['account'] = github_id
        repo_commits = GithubRepoCommits.objects.filter(committer_github=github_id).values("github_id", "repo_name", "committer_date").order_by("-committer_date")
        repos = {}
        id_reponame_pair_list = []
        for commit in repo_commits:
            commit_repo_name = commit['repo_name']
            if commit_repo_name not in repos:
                repos[commit_repo_name] = {'repo_name': commit_repo_name}
                repos[commit_repo_name]['github_id'] = commit['github_id']
                repos[commit_repo_name]['committer_date'] = commit['committer_date']
                id_reponame_pair_list.append((commit['github_id'], commit_repo_name))
        ctx_repo_stats = []
        contr_repo_queryset = GithubRepoStats.objects.extra(where=["(github_id, repo_name) in %s"], params=[tuple(id_reponame_pair_list)])
        for contr_repo in contr_repo_queryset:
            repo_stat = contr_repo.get_guideline()
            repo_stat['committer_date'] = repos[contr_repo.repo_name]['committer_date'] 
            ctx_repo_stats.append(repo_stat)
        ctx_repo_stats = sorted(ctx_repo_stats, key=lambda x:x['committer_date'], reverse=True)
        context["guideline"] = ctx_repo_stats
        print("ProfileRepoView time :", time.time() - start)
        
        return context


@csrf_exempt
def save_test_result(request, username):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            type_factors = data['factor']
            print("type_factors", type_factors)
            user = User.objects.get(username=username)
            try:
                account = Account.objects.get(user=user)
            except Exception as e:
                print("account error", e)
            devtype_objs = DevType.objects.filter(account=account).all()
            if len(devtype_objs) == 0:
                model_instance = DevType(account=account, typeA=type_factors[0], typeB=type_factors[1], typeC=type_factors[2], typeD=type_factors[3], typeE=0, typeF=0, typeG=0)
                model_instance.save()
            else:
                for devtype in devtype_objs:
                    devtype.typeA = type_factors[0]
                    devtype.typeB = type_factors[1]
                    devtype.typeC = type_factors[2]
                    devtype.typeD = type_factors[3]
                    devtype.save()
            context = {"status": 200}
        except Exception as e:
            print("error save", e)
            context = {"status": 400}
        
        return JsonResponse(context)

@csrf_exempt
def load_repo_data(request, username):
    if request.method == 'POST':
        start = time.time()
        try:
            user = User.objects.get(username=username)
            try:
                account = Account.objects.get(user=user)
            except Exception as e:
                print("account error", e)
            # 리포지토리 목록
            github_id = account.student_data.github_id
            commit_repos = GithubRepoCommits.objects.filter(committer_github=github_id).values("github_id", "repo_name", "committer_date").order_by("-committer_date")
            recent_repos = {}
            id_reponame_pair_list = []
            # 리포지토리 목록 중, 중복하지 않는 가장 최근 4개의 리포지토리 목록을 생성함
            for commit in commit_repos:
                commit_repo_name = commit['repo_name']
                if len(recent_repos) == 4:
                    break
                if commit_repo_name not in recent_repos:
                    recent_repos[commit_repo_name] = {'repo_name': commit_repo_name}
                    recent_repos[commit_repo_name]['github_id'] = commit['github_id']
                    recent_repos[commit_repo_name]['committer_date'] = commit['committer_date']
                    id_reponame_pair_list.append((commit['github_id'], commit_repo_name))
            contr_repo_queryset = GithubRepoStats.objects.extra(where=["(github_id, repo_name) in %s"], params=[tuple(id_reponame_pair_list)])
            for contr_repo in contr_repo_queryset:
                recent_repos[contr_repo.repo_name]["desc"] = contr_repo.proj_short_desc
            recent_repos = sorted(recent_repos.values(), key=lambda x:x['committer_date'], reverse=True)
            context = {"status": 200, "repo":recent_repos}
        except Exception as e:
            print("error save", e)
            context = {"status": 400}
        print("ajax repo", time.time() - start)
        return JsonResponse(context)




class ProfileInterestsView(UpdateView):
    def post(self, request, username, *args, **kwargs):
        print(request.POST)
        print(request.POST['act'])
        user = User.objects.get(username=username)
        user_account = Account.objects.get(user=user.id)
        student_id = user_account.student_data.id
        tags_all = Tag.objects
        if request.POST['act'] == 'append':
            added_preferLanguage = request.POST.get('interestDomain') # 선택 된 태그
            added_tag = Tag.objects.get(name=added_preferLanguage)
            try:
                already_ints = AccountInterest.objects.get(account=user_account, tag=added_tag)
                already_ints.delete()
                AccountInterest.objects.create(account=user_account, tag=added_tag, level=0)
            except:
                AccountInterest.objects.create(account=user_account, tag=added_tag, level=0)

        else:
            delete_requested_tag = Tag.objects.get(name=request.POST['target'])
            tag_deleted = AccountInterest.objects.get(account=user_account, tag=delete_requested_tag).delete()
            print("Selected tag is successfully deleted")

        return JsonResponse({'data':'asdfas'})

class ProfileLanguagesView(UpdateView):
    def post(self, request, username, *args, **kwargs):
        print(request.POST)
        print(request.POST['act'])
        print(request.POST['target'])
        user = User.objects.get(username=username)
        user_account = Account.objects.get(user=user.id)
        student_id = user_account.student_data.id
        tags_all = Tag.objects
        tags_domain = tags_all.filter(type='domain')

        if request.POST['act'] == 'append':
            added_preferLanguage = request.POST.get('preferLanguage') # 선택 된 태그
            added_tag = Tag.objects.get(name=added_preferLanguage)
            try:
                already_ints = AccountInterest.objects.get(account=user_account, tag=added_tag)
            except:
                AccountInterest.objects.create(account=user_account, tag=added_tag, level=1)


            lang = AccountInterest.objects.filter(account=user_account).exclude(tag__in=tags_domain)
            for l in lang:
                if "tag_" + l.tag.name in request.POST:
                    added_tag = Tag.objects.get(name=l.tag.name)
                    AccountInterest.objects.filter(account=user_account, tag=added_tag).update(level=request.POST.get("tag_" + l.tag.name))
            return JsonResponse({'data':'asdfas'})
        else:
            delete_requested_tag = Tag.objects.get(name=request.POST['target'])
            tag_deleted = AccountInterest.objects.get(account=user_account, tag=delete_requested_tag).delete()
            print("Selected tag is successfully deleted")
            return JsonResponse({'data':'asdfas'})

class ProfileImageView(UpdateView):

    def post(self, request, username, *args, **kwargs):
        print("asdfds")
        print('img 상태dffffffffffffffffffffffffff')
        user = User.objects.get(username=username)
        
        user_account = Account.objects.get(user=user.id)

        pre_img = user_account.photo.path
        field_check_list = {}
        profile_img = request.FILES.get('photo', False)
        
        print(profile_img)
        is_valid = True
        print(request.POST.get('is_default'))
        if request.POST.get('is_default') == 'true':
            print("is true!!")


        if profile_img:
            img_width, img_height = get_image_dimensions(profile_img)
            print(img_width, img_height)
            if img_width > 500 or img_height > 500:
                is_valid = False
                field_check_list['photo'] = f'이미지 크기는 500px x 500px 이하입니다. 현재 {img_width}px X {img_height}px'
                print(f'이미지 크기는 500px x 500px 이하입니다. 현재 {img_width}px X {img_height}px')

        img_form = ProfileImgUploadForm(request.POST, request.FILES, instance=user_account)
        print(img_form)
        print(pre_img)
        if bool(img_form.is_valid()) and is_valid:
            if 'photo' in request.FILES: # 폼에 이미지가 있으면
                print('form에 이미지 존재')
                try:
                    print(" path of pre_image is "+ pre_img)
                    if(pre_img.split("/")[-1] == "default.jpg" or pre_img.split("\\")[-1] == "default.jpg"):
                        pass
                    else:
                        print(pre_img.split("/")[-1])
                        os.remove(pre_img) # 기존 이미지 삭제
                
                except:                # 기존 이미지가 없을 경우에 pass
                    pass    

            print('Image is valid form')
            img_form.save()

        else:
            print(field_check_list['photo'])
        return redirect(f'/user/{username}/')

class ProfileImageDefaultView(DeleteView):
    def post(self, request, username, *args, **kwargs):
        user = User.objects.get(username=username)
        
        user_account = Account.objects.get(user=user.id)
        user_account.photo = "img/profile_img/default.jpg"
        user_account.save()
        return redirect(f'/user/{username}/')



class ProfileEditSaveView(UpdateView):
    def post(self, request, username, *args, **kwargs):
        user = User.objects.get(username=username)
        user_account = Account.objects.get(user=user.id)
        student_id = user_account.student_data.id
        user_tab = StudentTab.objects.get(id=student_id)
        tags_all = Tag.objects
        tags_domain = tags_all.filter(type='domain')

        lang = AccountInterest.objects.filter(account=user_account).exclude(tag__in=tags_domain)
        user_privacy = AccountPrivacy.objects.get(account=user_account)
        print(user_privacy)
        for l in lang:
            if "tag_" + l.tag.name in request.POST:
                added_tag = Tag.objects.get(name=l.tag.name)
                AccountInterest.objects.filter(account=user_account, tag=added_tag).update(level=request.POST.get("tag_" + l.tag.name))

        user_tab.plural_major = request.POST['plural_major']
        user_tab.personal_email = request.POST['personal_email']
        user_tab.primary_email = request.POST['primary_email']
        user_tab.secondary_email = request.POST['secondary_email']
        user_tab.save()

        user_account.introduction = request.POST['introduction']
        user_account.portfolio = request.POST['portfolio']
        user_account.save()


        user_privacy.open_lvl = request.POST['profileprivacy']
        user_privacy.is_write = request.POST['articleprivacy']
        user_privacy.is_open = request.POST['teamprivacy']
        user_privacy.save()


        return redirect(f'/user/{username}/')

class ProfilePasswdView(UpdateView):
    def post(self, request, username, *args, **kwargs):
        user = User.objects.get(username=username)

        if(user.check_password(request.POST['inputOldPassword']) == False):
            return JsonResponse({"status" : "error"})

        if(request.POST['inputNewPassword'] != request.POST['inputValidPassword']):
            return JsonResponse({"status" : "error"})

        user.set_password(request.POST['inputNewPassword'])
        user.save()
        print("비밀번호가 변경되었습니다. ")
        return 1


class ProfileType(TemplateView):
    template_name = 'profile/profile-type.html'
    
    def get_context_data(self, *args, **kwargs):
        
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username=context["username"])
        context["username"] = user
        context["end_year"] = datetime.datetime.now().date().today().year
        
        return context

def consent_write(request, username=""):

    '''
    글쓰기/댓글쓰기 시 본인의 프로필 공개 동의서
    url     : /user/api/consent-write
    template: consent/consent_write.html
    '''

    if request.method == 'GET':
        account = Account.objects.get(user=request.user.id)
        acc_pp = AccountPrivacy.objects.get(account=account)

        context = {
            'is_write': acc_pp.is_write,
            'open_lvl': acc_pp.open_lvl,
            'user': username
        }

        return render(request, 'consent/consent_write.html',context)

    if request.method == 'POST':
        try:
            account = Account.objects.get(user=request.user.id)
            acc_pp = AccountPrivacy.objects.get(account=account)
            acc_pp.is_write = True
            acc_pp.open_lvl = 1
            acc_pp.save()
            return JsonResponse({'status': 'success', 'msg':'저장하였습니다.'})
        except Exception as e:
            print(e)
            return JsonResponse({'status': 'fail', 'msg':'저장에 실패하였습니다. 잠시후 다시 시도해주세요.'})
            

def consent_open(request, username=""):

    '''
    유저 추천시스템 사용에 대한 동의서
    url     : /user/api/consent-open
    template: consent/consent_open.html
    '''

    if request.method == 'GET':
        account = Account.objects.get(user=request.user.id)
        acc_pp = AccountPrivacy.objects.get(account=account)

        context = {
            'is_open': acc_pp.is_open,
            'open_lvl': acc_pp.open_lvl,
            'user': username
        }

        return render(request, 'consent/consent_open.html',context)
    
    if request.method == 'POST':
        try:
            account = Account.objects.get(user=request.user.id)
            acc_pp = AccountPrivacy.objects.get(account=account)
            acc_pp.is_open = True
            acc_pp.open_lvl = 1
            acc_pp.save()
            return JsonResponse({'status': 'success', 'msg':'저장하였습니다.'})
        except Exception as e:
            print(e)
            return JsonResponse({'status': 'fail', 'msg':'저장에 실패하였습니다. 잠시후 다시 시도해주세요.'})