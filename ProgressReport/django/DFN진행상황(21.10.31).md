# DFN 진행 상황 (21.10.31)

1. DB 조회 함수를 제작하였다.
2. 세 팀의 듀티를 생성할 수 있다.
3. 전체 템플릿 스타일을 통일하였다.

<br>

## DB 조회 함수

간호사의 듀티 생성을 위해 필요한 정보를 딕셔너리로 반환하는 함수를 생성했다.

1. `get_nurse_info`
   1. 간호사의 `pk` 리스트를 매개변수로 받고 필요한 정보를 담은 딕셔너리로 반환한다.
   2. 각 `pk`를 key로 갖고 이와 일치하는 간호사의 `pk`, `level`, `team`, `OFF`의 리스트를 value로 갖는 딕셔너리를 생성한다.
2. `get_last_schedule`
   1. 간호사의 `pk` 리스트와 원하는 날짜의 문자열을 매개변수로 받고 필요한 정보를 담은 딕셔너리로 반환한다.
   2. 각 `pk`를 key로 갖고 간호사 `pk`와 `date`가 일치하는 근무 기록을 리스트로 변환해 value로 추가하여 딕셔너리를 생성한다.

```python
# duty_creater/views.py

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
        duties = list(Event.objects
                      .filter(date__startswith=date)
                      .filter(nurse_id=pk)
                      .values_list('duty', flat=True)
                     )
        nurse_schedule_dict[pk] = duties

    return nurse_schedule_dict
```

<br>

## 여러 팀의 듀티 생성

총 세 팀의 듀티를 한꺼번에 생성하고 이를 템플릿에 출력할 수 있게 되었다. 팀의 듀티 출력을 위해 세 개의 리스트를 원소로 갖는 `team_duties` 리스트를 생성하여 각 팀의 듀티 일정을 저장하였다. 출력의 용이를 위해 각 간호사의 듀티를 간호사의 이름을 key, 듀티 리스트를 value로 갖는 딕셔너리로 생성했다.

`create_monthly` 함수의 주요 수정 내용은 다음과 같다.

```python
# duty_creater/views.py

def create_monthly(request, date):
    # 생략
    
    team_duties = [[], [], []]
    for key, value in dict_duties.items():
        nurse_profile = Profile.objects.get(user_id=key)  # 간호사 프로필 객체
        team_duties[nurse_profile.team - 1].append({nurse_profile.name: value})

    days = list(range(1, 31 + 1))  # 템플릿 출력용 일(day) 리스트

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
```

<br>

## 템플릿 수정

전체 템플릿에 통일성을 부여하려 했다.

### 로그인

![127.0.0.1_8000_accounts_login_](DFN진행상황(21.10.31).assets/127.0.0.1_8000_accounts_login_-16356930031552.png)

### 회원가입

![127.0.0.1_8000_accounts_signup_](DFN진행상황(21.10.31).assets/127.0.0.1_8000_accounts_signup_-16356930247673.png)

### 계정 정보 수정

![127.0.0.1_8000_accounts_update_](DFN진행상황(21.10.31).assets/127.0.0.1_8000_accounts_update_-16356931159624.png)

### 비밀번호 변경

![127.0.0.1_8000_accounts_password_](DFN진행상황(21.10.31).assets/127.0.0.1_8000_accounts_password_-16356931370805.png)

### 프로필 생성

![127.0.0.1_8000_accounts_signup_(1)](DFN진행상황(21.10.31).assets/127.0.0.1_8000_accounts_signup_(1).png)

### 프로필

![127.0.0.1_8000_accounts_profile_15_](DFN진행상황(21.10.31).assets/127.0.0.1_8000_accounts_profile_15_.png)

### 프로필(작성되지 않은 경우)

![127.0.0.1_8000_accounts_profile_20_](DFN진행상황(21.10.31).assets/127.0.0.1_8000_accounts_profile_20_-16356932266447.png)

### 프로필 수정

![127.0.0.1_8000_accounts_profile_update](DFN진행상황(21.10.31).assets/127.0.0.1_8000_accounts_profile_update-16356932378358.png)

### 인덱스(사용 미정)

![127.0.0.1_8000_schedule_](DFN진행상황(21.10.31).assets/127.0.0.1_8000_schedule_-16356932484489.png)

### 개인 듀티

![127.0.0.1_8000_schedule_personal_15_](DFN진행상황(21.10.31).assets/127.0.0.1_8000_schedule_personal_15_.png)

### 팀 듀티

![127.0.0.1_8000_schedule_team_3_](DFN진행상황(21.10.31).assets/127.0.0.1_8000_schedule_team_3_.png)

### 듀티 생성(날짜 선택)

![127.0.0.1_8000_schedule_create_](DFN진행상황(21.10.31).assets/127.0.0.1_8000_schedule_create_.png)

### 듀티 생성

![127.0.0.1_8000_schedule_create_2021-11_](DFN진행상황(21.10.31).assets/127.0.0.1_8000_schedule_create_2021-11_.png)

