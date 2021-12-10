from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST, require_safe
from django.http import JsonResponse, HttpResponse
from accounts.models import Profile
from .models import Event, ScheduleModification
from .forms import ScheduleModificationForm
from .custom_classes.ScheduleManager import ScheduleManager
import json
import datetime
import calendar
from django.core import serializers


WEEKDAYS_KO = '일월화수목금토'


def get_nurse_info(pk_list: list) -> dict:
    nurse_profile_dict = {}

    for pk in pk_list:
        nurse_profile = Profile.objects.get(user_id=pk)
        level = nurse_profile.level
        team = nurse_profile.team
        off_cnt = nurse_profile.OFF

        nurse_profile_dict[pk] = [pk, level, team, off_cnt]

    return nurse_profile_dict


def get_last_schedule(pk_list: list, date: str) -> dict:
    nurse_schedule_dict = {}

    for pk in pk_list:
        duties = list(Event.objects.filter(date__startswith=date).filter(nurse_id=pk).values_list('duty', flat=True))
        nurse_schedule_dict[pk] = duties

    return nurse_schedule_dict


@require_safe
def index(request):
    return render(request, 'schedule/index.html')


@require_http_methods(['GET', 'POST'])
def create(request):
    # 인증되지 않은 사용자
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    # 스태프 간호사만 일정 생성 가능
    if request.user.is_staff:
        modifications = ScheduleModification.objects.filter(approval=False).all()

        if request.method == "POST":
            start_date = request.POST.get('start')  # 사용자가 선택한 날짜(YY-MM 형식에 str type)
            return redirect('schedule:create_monthly', start_date)
        
        context = {
            'modifications': modifications,
        }
        return render(request, 'schedule/create.html', context)
    return redirect('schedule:personal', request.user.pk)


def get_schedule_modification(request, date):
    modifications = ScheduleModification.objects.filter(approval=False).filter(from_date__startswith=date).all()
    data = serializers.serialize('json', modifications)
    return HttpResponse(data, content_type='application/json')


def duty_exist(request, date):
    flag = False  # 가능
    if Event.objects.filter(date__startswith=date).exists():
        flag = True  # 불가능
    context = {
        'flag': flag,
    }
    return JsonResponse(context)


@require_http_methods(['GET', 'POST'])
def create_monthly(request, date):
    # 인증되지 않은 사용자
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    # 일정 생성 권한이 없는 사용자
    if not request.user.is_staff:
        return redirect('schedule:personal', request.user.pk)

    # date: 사용자가 선택한 날짜(YY-MM 형식. str)
    month = date[5: 7]  # 사용자가 선택한 달(MM 형식)
    year = date[: 4]  # 사용자가 선택한 연(YY 형식)
    last_day = calendar.monthrange(int(year), int(month))[1]  # 해당 달의 마지막 날

    weekdays = []  # date-01 부터 date-last_day까지 요일 저장 리스트
    start_date = date + '-01'  # 시작일
    weekday = datetime.datetime.strptime(start_date, '%Y-%m-%d')  # datetime 객체로 변환
    for _ in range(last_day):
        weekdays.append(WEEKDAYS_KO[int(weekday.strftime('%w'))])
        weekday = weekday + datetime.timedelta(days=1)  # 하루 추가

    if request.method == "POST":
        # 간호사의 휴가, 연차 신청 반영
        with open('modify_schedule.json') as json_file:
            modifications = json.load(json_file)

        for schedule_modification_pk, modify in modifications.items():
            # modify == True인 경우에만 반영
            if modify:
                schedule_modification = ScheduleModification.objects.get(pk=schedule_modification_pk)

                # DBd에 승인 수정
                schedule_modification.approval = True
                schedule_modification.save()

                # 사용 연차 수 증가
                if schedule_modification.category == 'PTO':
                    nurse_profile = Profile.objects.get(user_id=schedule_modification.nurse.pk)
                    print(nurse_profile.PTO)
                    print('add PTO')
                    nurse_profile.PTO += 1
                    nurse_profile.save()
                    print(nurse_profile.PTO)


        # 사용자가 생성하기로 했다면 json 파일을 불러와 이를 DB에 저장
        with open('temp_schedule.json') as json_file:
            dict_duties = json.load(json_file)


        # 사용자가 전달한 수정 사항 반영
        updates = json.loads(request.body)
        # print(updates["updates"])  # dict

        for key, value in updates["updates"].items():
            nurse_id, day = key.split('-')
            day = int(day)
            wanted_duty = value
            dict_duties[nurse_id][day - 1] = wanted_duty


        # 근무 기록 DB 저장
        for nurse_pk, duties in dict_duties.items():  
            start_date = datetime.datetime.strptime(date, '%Y-%m')  # datetime 객체로 변환
            nurse_profile = Profile.objects.get(user_id=nurse_pk)  # 간호사 프로필 객체
            
            OFF_cnt = 0

            weekdays_idx = 0  # 현재 날짜(int)
            for duty in duties:
                # OFF 갱신
                if duty > 0 and (weekdays[weekdays_idx] == '일' or weekdays[weekdays_idx] == '토'):
                    OFF_cnt += 1
                weekdays_idx += 1

                # Event 생성
                Event.objects.create(date=start_date, duty=duty, nurse_id=nurse_pk) 
                start_date = start_date + datetime.timedelta(days=1)  # 하루 추가

            nurse_profile.OFF = OFF_cnt
            nurse_profile.save()

        return redirect('schedule:hospital')


    # 한달 일정 생성
    nurse_pk_list = []
    all_nurse_pk_list = get_user_model().objects.filter(~Q(username='admin')).values('id')
    for i in range(len(all_nurse_pk_list)):
        nurse_pk_list.append(all_nurse_pk_list[i]['id'])

    # 현재 달의 지난 달 구하기
    last_month = int(month) - 1
    lasy_year = int(year)
    if last_month == 0:
        last_month = '12'
        lasy_year = str(lasy_year - 1)
    else:
        last_month = str(last_month)
        lasy_year = str(lasy_year)
    
    if len(last_month) == 1:
        last_month = '0' + last_month
    

    # 간호사의 휴가, 연차 신청 반영
    with open('modify_schedule.json') as json_file:
        modifications = json.load(json_file)

    modification_dict = {}
    for schedule_modification_pk, modify in modifications.items():
        # modify == True인 경우에만 반영
        if modify:
            schedule_modification = ScheduleModification.objects.get(pk=schedule_modification_pk)
            from_day = int(schedule_modification.from_date.strftime('%d'))  # 시작 날
            to_day = int(schedule_modification.to_date.strftime('%d'))  # 종료 날
            day_tuple = tuple(range(from_day, to_day + 1))  # 시작 날에서부터 종료 날까지 모두 담은 튜플
            modification_dict[schedule_modification.nurse.pk] = day_tuple


    nurse_profile_dict = get_nurse_info(nurse_pk_list)
    nurse_schedule_dict = get_last_schedule(nurse_pk_list, lasy_year + '-' + last_month)

    current_month = ScheduleManager(team_number_list=[1, 2, 3])
    current_month.push_nurse_info(nurse_profile_dict)
    current_month.push_last_schedules(nurse_schedule_dict)
    current_month.push_vacation_info(modification_dict) 
    current_month.create_monthly_schedule(date=date + '-01')
    dict_duties = current_month.get_schedule()


    # 한달 일정을 json 파일로 임시 저장
    with open('temp_schedule.json', 'w') as json_file:
        json.dump(dict_duties, json_file)

    nurse_names = []  # 간호사 이름 저장 [(pk, 이름), ...]
    for nurse_pk in dict_duties:
        nurse_profile = Profile.objects.get(user_id=nurse_pk)  # 간호사 프로필 객체
        nurse_names.append((nurse_pk, nurse_profile.name))

    team_duties = [[], [], []]
    for key, value in dict_duties.items():
        nurse_profile = Profile.objects.get(user_id=key)  # 간호사 프로필 객체
        team_duties[nurse_profile.team - 1].append({(key, nurse_profile.name): value})


    days = list(range(1, last_day + 1))  # 템플릿 출력용 일(day) 리스트

    context = {
        'days': days,
        'month': month,
        'year': year,
        'start_date': date,
        'weekdays': weekdays,
        'nurse_names': nurse_names,
        'dict_duties': dict_duties,
        'team_duties': team_duties,
    }
    return render(request, 'schedule/create_monthly.html', context)


@require_POST
def update(request, date):
    updates = json.loads(request.body)
    for key, value in updates["updates"].items():
        nurse_id, day = key.split('-')
        if len(day) == 1:
            day = '0' + day
        wanted_date = date + '-' + day
        wanted_duty = value
        duty = Event.objects.filter(date__startswith=wanted_date).filter(nurse_id=nurse_id).update(duty=wanted_duty)
    return redirect('schedule:hospital')


today = datetime.datetime.today().strftime('%Y-%m')  # 현재 달

def personal(request, nurse_pk, date=today):
    # date의 기본값은 현재 달
    month = date[5: 7]  # 사용자가 선택한 달(MM 형식)
    year = date[: 4]  # 사용자가 선택한 연(YY 형식)
    last_day = calendar.monthrange(int(year), int(month))[1]  # 해당 달의 마지막 날
    nurse_name = Profile.objects.filter(user_id=nurse_pk).values('name')[0]['name']
    duties = list(Event.objects.filter(date__startswith=date).filter(nurse_id=nurse_pk).values_list('duty', flat=True))
    
    # 해당 날짜에 듀티가 존재하는지 여부 검사
    existence = False
    if duties:
        existence = True  # 듀티가 존재한다

        start_date = date + '-01'  # 시작일
        start_weekday = datetime.datetime.strptime(start_date, '%Y-%m-%d').weekday() + 1  # 시작 요일
        duties_for_calendar = [[-1] * (start_weekday) + duties[: (7 - start_weekday)]]
        day_idx = 7 - start_weekday
        while day_idx < last_day:
            if last_day - day_idx <= 7:
                duties_for_calendar.append(duties[day_idx: ])
                break
            duties_for_calendar.append(duties[day_idx: day_idx + 7 ])
            day_idx += 7
        
        # 달력에 일과 함께 출력하기 위해 duties_for_calendar의 모든 원소를 일과 함께 튜플로 다시 만듦
        day = 1
        for week_idx in range(len(duties_for_calendar)):
            for day_idx in range(len(duties_for_calendar[week_idx])):
                if duties_for_calendar[week_idx][day_idx] == -1:
                    duties_for_calendar[week_idx][day_idx] = (0, duties_for_calendar[week_idx][day_idx])
                else:
                    duties_for_calendar[week_idx][day_idx] = (day, duties_for_calendar[week_idx][day_idx])
                    day += 1

        weekdays = ['일', '월', '화', '수', '목', '금', '토']

        context = {
            'existence': existence,
            'month': month,
            'year': year,
            'nurse_name': nurse_name,
            'date': date,
            'duties_for_calendar': duties_for_calendar,
            'weekdays': weekdays,
        }
        return render(request, 'schedule/personal.html', context)
    
    context = {
        'existence': existence,
    }
    return render(request, 'schedule/personal.html', context)


def team(request, team_id, date=today):
    # date의 기본값은 현재 달
    month = date[5: 7]  # 사용자가 선택한 달(MM 형식)
    year = date[: 4]  # 사용자가 선택한 연(YY 형식)
    last_day = calendar.monthrange(int(year), int(month))[1]  # 해당 달의 마지막 날

    nurse_pks = Profile.objects.filter(team=team_id).values_list('user_id', flat=True)
    dict_duties = get_last_schedule(nurse_pks, date)

    # 해당 날짜에 듀티가 존재하는지 여부 검사
    existence = False
    for value in dict_duties.values():
        if value:  # 듀티가 있음
            existence = True
            break

    if existence:
        weekdays = []  # date-01 부터 date-last_day까지 요일 저장 리스트
        start_date = date + '-01'  # 시작일
        weekday = datetime.datetime.strptime(start_date, '%Y-%m-%d')  # datetime 객체로 변환
        for _ in range(last_day):
            weekdays.append(WEEKDAYS_KO[int(weekday.strftime('%w'))])
            weekday = weekday + datetime.timedelta(days=1)  # 하루 추가

        nurse_names = []  # 간호사 이름 저장 [(pk, 이름), ...]
        for nurse_pk in dict_duties:
            nurse_profile = Profile.objects.get(user_id=nurse_pk)  # 간호사 프로필 객체
            nurse_names.append((nurse_pk, nurse_profile.name))

        days = list(range(1, last_day + 1))  # 템플릿 출력용 일(day) 리스트

        context = {
            'existence': existence,
            'days': days,
            'month': month,
            'year': year,
            'team_id': team_id,
            'nurse_names': nurse_names,
            'date': date,
            'weekdays': weekdays,
            'dict_duties': dict_duties,
        }
        return render(request, 'schedule/team.html', context)
    context = {
        'existence': existence,
    }
    return render(request, 'schedule/team.html', context)


def hospital(request, date=today):
    # date의 기본값은 현재 달
    month = date[5: 7]  # 사용자가 선택한 달(MM 형식)
    year = date[: 4]  # 사용자가 선택한 연(YY 형식)
    last_day = calendar.monthrange(int(year), int(month))[1]  # 해당 달의 마지막 날

    weekdays = []  # date-01 부터 date-last_day까지 요일 저장 리스트
    start_date = date + '-01'  # 시작일
    weekday = datetime.datetime.strptime(start_date, '%Y-%m-%d')  # datetime 객체로 변환
    for _ in range(last_day):
        weekdays.append(WEEKDAYS_KO[int(weekday.strftime('%w'))])
        weekday = weekday + datetime.timedelta(days=1)  # 하루 추가

    nurse_pks = Profile.objects.filter(team__gt=0).values_list('user_id', flat=True)
    dict_duties = get_last_schedule(nurse_pks, date)

    # 해당 날짜에 듀티가 존재하는지 여부 검사
    existence = False
    for value in dict_duties.values():
        if value:  # 듀티가 있음
            existence = True
            break

    if existence:
        nurse_names = []  # 간호사 이름 저장 [(pk, 이름), ...]
        for nurse_pk in dict_duties:
            nurse_profile = Profile.objects.get(user_id=nurse_pk)  # 간호사 프로필 객체
            nurse_names.append((nurse_pk, nurse_profile.name))

        team_duties = [[], [], []]
        for key, value in dict_duties.items():
            nurse_profile = Profile.objects.get(user_id=key)  # 간호사 프로필 객체
            team_duties[nurse_profile.team - 1].append({(key, nurse_profile.name): value})


        days = list(range(1, last_day + 1))  # 템플릿 출력용 일(day) 리스트

        context = {
            'existence': existence,
            'days': days,
            'month': month,
            'year': year,
            'start_date': date,
            'weekdays': weekdays,
            'nurse_names': nurse_names,
            'dict_duties': dict_duties,
            'team_duties': team_duties,
        }
        return render(request, 'schedule/hospital.html', context)
    context = {
        'existence': existence,
    }
    return render(request, 'schedule/hospital.html', context)


@require_http_methods(['GET', 'POST'])
def create_modification(request):
    if request.method == 'POST':
        form = ScheduleModificationForm(request.POST)
        if form.is_valid():
            modification_form = form.save(commit=False)
            modification_form.nurse = request.user
            modification_form.save()
            return redirect('schedule:modification', request.user.pk)
    form = ScheduleModificationForm()
    context = {
        'form': form,
    }
    return render(request, 'schedule/modify/create_modification.html', context)



def modification(request, nurse_pk):
    modifications = ScheduleModification.objects.filter(nurse_id=nurse_pk).all().order_by('-pk')
    context = {
        'modifications': modifications,
    }
    return render(request, 'schedule/modify/modification.html', context)



def confirm_modification(request):
    modifications = json.loads(request.body)

    with open('modify_schedule.json', 'w') as json_file:
        json.dump(modifications['modifications'], json_file)

    return JsonResponse(modifications['modifications'])



def all_modification(request):
    modifications = ScheduleModification.objects.all().order_by('-pk')
    context = {
        'modifications': modifications,
    }
    return render(request, 'schedule/modify/all_modification.html', context)