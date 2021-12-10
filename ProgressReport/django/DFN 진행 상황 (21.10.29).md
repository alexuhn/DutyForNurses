# DFN 진행 상황 (21.10.29)

1. 명시적이지 않은 URL을 수정하였다.
2. 듀티 생성 후 DB 저장 과정을 수정하였다.
3. 듀티를 DB에 저장할 때 OFF 수를 함께 기록할 수 있게 되었다.
4. 사용자의 한 달 듀티와 팀의 한 달 듀티를 확인할 수 있게 되었다.

<br>

## URL 수정

```python
# duty_creater/urls.py

from django.urls import path
from . import views


app_name = 'schedule'
urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),  # 새 듀티 생성을 위한 날짜 선택
    path('create/<str:date>/', views.create_monthly, name='create_monthly'), 
    path('update/<str:date>/', views.update, name='update'),  
    
    # 개인 일정, date를 입력하지 않으면 이번달이 기본값으로 views.py 함수에서 들어간다
    path('personal/<int:nurse_pk>/', views.personal, name='personal'),  
    path(
        'personal/<int:nurse_pk>/<str:date>/', 
        views.personal, name='personal'
        ),
    
    # 팀 일정, date를 입력하지 않으면 이번달이 기본값으로 views.py 함수에서 들어간다
    path('team/<int:team_id>/', views.team, name='team'),  
    path('team/<int:team_id>/<str:date>/', views.team, name='team'),  
]
```

사용자가 입력한 날짜를 url에 추가하자는 아이디어를 받아 이를 반영하였다. 

<br>

## 듀티 저장 과정 수정

기존의 듀티 저장 과정은 다음과 같다.

1. 사용자가 연월 선택
2. 생성된 듀티 일정을 사용자가 선택한 연월과 함께 DB에 저장

이는 사용자가 날짜를 선택하면 그 즉시 DB에 듀티가 기록이 되어 적절한 듀티가 생성되지 않았을 때 수정, 삭제가 어렵다는 문제가 있었다. 이에 `임시 JSON 파일을 이용`하여 생성과 동시에 DB에 저장하지 않고, 먼저 사용자에게 일정을 재생성할 수 있는 선택지를 준 뒤 사용자가 `확정을 원하는 경우에만 DB에 저장`하는 방법을 제안받아 듀티 저장 과정을 개선할 수 있었다. 수정된 듀티 저장 과정은 다음과 같다.

1. 사용자가 연월 선택
2. 생성된 듀티 일정을 `temp_schedule.json`에 저장
   1. 사용자가 확정하면 `temp_schedule.json`에 저장된 일정을 불러와 사용자가 선택한 연월과 함께 이를 DB에 저장
   2. 사용자가 재생성을 원하면 리다이렉트를 통해 함수를 다시 실행해 새로운 일정 생성

`create_monthly` 함수의 주요 수정 내용은 다음과 같다.

```python
# duty_creater/views.py

def create_monthly(request, date):
    if request.method == "POST":  # 사용자가 확정 버튼을 누른 경우
        
        # 사용자가 생성하기로 했다면 json 파일을 불러와 이를 DB에 저장
        with open('temp_schedule.json') as json_file:
            dict_duties = json.load(json_file)

        # 근무 기록 생성
        for nurse_pk, duties in dict_duties.items():  
            start_date = datetime.datetime.strptime(date, '%Y-%m')  

            for duty in duties:
                # Event 생성
                 Event.objects.create(
                    date=start_date, 
                    duty=duty, 
                    nurse_id=nurse_pk
                    ) 
                start_date = start_date + datetime.timedelta(days=1)  # 하루 추가

        return redirect('schedule:index')

    # 한달 일정 생성 과정 생략
    
    # 생성된 한달 일정을 json 파일로 임시 저장
    with open('temp_schedule.json', 'w') as json_file:
        json.dump(dict_duties, json_file)

    # context 생략
    return render(request, 'schedule/create_monthly.html', context)
```

![](DFN 진행 상황 (21.10.29).assets/127.0.0.1_8000_schedule_create_2021-10_.png)

<br>

## OFF 수 기록 과정 생성

생성된 일정을 사용자가 확정하면 해당 일과 요일을 대조해 OFF 수를 기록할 수 있도록 했다.

`create_monthly` 함수의 주요 수정 내용은 다음과 같다.

```python
# duty_creater/views.py

def create_monthly(request, date):
    # date: 사용자가 선택한 날짜(YY-MM 형식. str)
    month = date[5: 7]  # 사용자가 선택한 달(MM 형식)
    year = date[: 2]  # 사용자가 선택한 연(YY 형식)

    weekdays = []  # date-01 부터 date-31까지 요일 저장 리스트
    start_date = date + '-01'  # 시작일
    weekday = datetime.datetime.strptime(start_date, '%Y-%m-%d')  
    for _ in range(31):
        weekdays.append(weekday.strftime('%a'))
        weekday = weekday + datetime.timedelta(days=1)  # 하루 추가

    if request.method == "POST":
        # 근무 기록 생성
        for nurse_pk, duties in dict_duties.items():  
            start_date = datetime.datetime.strptime(date, '%Y-%m')  
            nurse_profile = Profile.objects.get(pk=nurse_pk)  # 간호사 프로필 객체
            nurse_profile.OFF = 0  # 임시로 OFF 초기화

            weekdays_idx = 0  # 현재 날짜(int)
            for duty in duties:
                # 일요일이나 토요일에 근무를 하는 경우
                if duty > 0 and (weekdays[weekdays_idx] == 'Sun' \
                    or weekdays[weekdays_idx] == 'Sat'):
                    nurse_profile.OFF += 1  # OFF 갱신
                    nurse_profile.save()
                weekdays_idx += 1

                # Event 생성
                Event.objects.create(
                    date=start_date, 
                    duty=duty, 
                    nurse_id=nurse_pk
                	) 
                start_date = start_date + datetime.timedelta(days=1)  # 하루 추가

        return redirect('schedule:index')

    # 이하 생략
```

<br>

## 사용자(간호사)의 한 달 듀티 출력

한 달 듀티 일정을 DB에서 가져와 이를 최대 7개씩 나누어 리스트에 저장한다. 이때 리스트는 2차원 리스트로 각 원소 리스트는 한 주를 뜻하기 때문에 `weeks[0][0]`에 해당하는 값은 일요일이어야 한다. 이를 위해 해당 달의 시작 요일을 구하고 요일에 따라 더미 값을 넣어 `weeks[0]` 리스트의 길이를 7로 만들어주고 만들어진 리스트를 그대로 출력한다.

```python
# duty_creater/views.py

today = datetime.datetime.today().strftime('%Y-%m')  # 현재 달

def personal(request, nurse_pk, date=today):
    # date의 기본값은 현재 달
    month = date[5: 7]  # 사용자가 선택한 달(MM 형식)
    year = date[: 4]  # 사용자가 선택한 연(YY 형식)
    
    # 현재 사용자(간호사) 이름
    nurse_name = Profile.objects\
                .filter(user_id=nurse_pk)\
                .values('name')[0]['name']
    
    # 현재 사용자(간호사)의 이번 달 듀티(리스트)
    duties = list(Event.objects\
                  .filter(date__startswith=date)\
                  .filter(nurse_id=nurse_pk)\
                  .values_list('duty', flat=True))
	
    # 시작일 설정 후 시작 요일 저장
    start_date = date + '-01'  # 시작일
    start_weekday = datetime.datetime.strptime(start_date, '%Y-%m-%d')\
    				.weekday() + 1  
    
    # 듀티를 요일에 맞춰 7개씩 나누어 weeks에 저장
    # 이때 -1은 한 달의 시작에 맞춰 리스트 길이를 7로 만들기 위해 채워지는 더미 값
    weeks = [[-1] * (start_weekday) + duties[: (7 - start_weekday)]]
    day_idx = 7 - start_weekday
    while day_idx < 31:
        if 31 - day_idx <= 7:
            weeks.append(duties[day_idx: ])
            break
        weeks.append(duties[day_idx: day_idx + 7 ])
        day_idx += 7
    
    # 템플릿에서 출력하기 위한 요일 리스트
    weekdays = ['일', '월', '화', '수', '목', '금', '토']

    context = {
        'month': month,
        'year': year,
        'nurse_name': nurse_name,
        'date': date,
        'weeks': weeks,
        'weekdays': weekdays,
    }
    return render(request, 'schedule/personal.html', context)
```

![](DFN 진행 상황 (21.10.29).assets/127.0.0.1_8000_schedule_personal_6_.png)

<br>

## 팀의 한 달 듀티 출력

팀의 한 달 듀티를 DB에서 가져와 이를 딕셔너리에 저장한다. `Key`는 간호사의 `pk`이고 `value`는 한 달 듀티 리스트이다. 즉 듀티를 만들 때 `create_monthly` 함수에서 만들어지는 듀티 딕셔너리 `dict_duties`와 구조가 같다. 따라서 출력을 포함한 나머지 과정은 듀티 생성과 동일하다.

```python
# duty_creater/views.py

def team(request, team_id, date=today):
    # date의 기본값은 현재 달
    month = date[5: 7]  # 사용자가 선택한 달(MM 형식)
    year = date[: 4]  # 사용자가 선택한 연(YY 형식)
	
    # 해당 team_id의 모든 간호사 pk를 리스트에 저장
    nurse_pks = Profile.objects\
    			.filter(team=team_id)\
        		.values_list('user_id', flat=True)
    
    # 간호사의 pk를 이용해 듀티를 찾아 딕셔너리로 저장
    dict_duties = {}
    for nurse_pk in nurse_pks:
        duties = list(Event.objects\
                      .filter(date__startswith=date)\
                      .filter(nurse_id=nurse_pk)\
                      .values_list('duty', flat=True))
        dict_duties[nurse_pk] = duties
    
    weekdays = []  # date-01 부터 date-31까지 요일 저장 리스트
    start_date = date + '-01'  # 시작일
    weekday = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    for _ in range(31):
        weekdays.append(weekday.strftime('%a'))
        weekday = weekday + datetime.timedelta(days=1)  # 하루 추가

    nurse_names = []  # 간호사 이름 저장 [(pk, 이름), ...]
    for nurse_pk in dict_duties:
        nurse_profile = Profile.objects.get(user_id=nurse_pk)  # 간호사 프로필 객체
        nurse_names.append((nurse_pk, nurse_profile.name))

    context = {
        'month': month,
        'year': year,
        'team_id': team_id,
        'nurse_names': nurse_names,
        'date': date,
        'weekdays': weekdays,
        'dict_duties': dict_duties,
    }
    return render(request, 'schedule/team.html', context)
```

![](DFN 진행 상황 (21.10.29).assets/127.0.0.1_8000_schedule_team_0_.png)

<br>

## 개선할 사항

1. 현재 `duty_creater/views.py`에서 함수는 달라도 그 내용에 중복되는 코드가 많아 이를 정리할 필요가 있을 것 같다.
2. 템플릿을 위해 출력해야 할 모든 요소를 따로 리스트에 담아 전달하는데 그 과정에서 DB를 여러 번 검색하게 된다. 기능이 모두 완성되면 반복되는 검색을 줄이기 위한 방법을 찾아 수정을 해야 할 것 같다.