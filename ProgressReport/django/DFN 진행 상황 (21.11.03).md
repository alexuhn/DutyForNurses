# DFN 진행 상황 (21.11.03)

1. Navbar를 개선하였다.
2. 전체 듀티를 조회할 수 있게 되었다.
3. 달의 마지막 날을 고려해 전체 함수를 수정하였다.

<br>

## Navbar 개선

사용자가 자신의 듀티를 확인할 때 이전 날짜의 듀티를 확인할 방법이 없어 이를 위한 버튼을 사용자 듀티 템플릿에 추가하려 했다. 하지만 이미 `navbar`에 사용자의 듀티를 확인할 수 있는 버튼이 존재하기 때문에 템플릿에 비슷한 역할을 하는 또 다른 버튼을 생성하는 것이 비효율적이라 생각했다.

이미 존재하는 `navbar`를 확장하기 위해 드랍다운 형식의 버튼을 사용하기로 하였고, 그 안에 `input` 태그를 넣어 날짜를 선택할 수 있게 했다. 새로 배운 자바스크립트를 이용하여 사용자가 `input`에 입력한 값을 가져와 이동할 URL을 구성할 수 있었고 만들어진 URL로 리다이렉트 되는 방식으로 구성하였다.

팀의 듀티 조회 버튼 또한 같은 방식으로 수정하였다. 

URL의 변수들은 각 `input` 태그에 `data-user-id="{{ user.pk }}"`, `data-user-team="{{ user.profile.team }}`와 같이 설정한 값을 통해 구할 수 있다.

작성한 `base.html`의 `script` 태그는 다음과 같다.

```html
<!-- templates/base.html -->

  <script>
    const pesonalInput = document.querySelector('#personal-date')

    const personalButton = document.querySelector('#personal-duty')
    personalButton.addEventListener('click', function (event) {
      if (pesonalInput.value) {
        window.location.href = `/schedule/personal/
								${pesonalInput.dataset.userId}/
								${pesonalInput.value}/`
      }
    })


    const teamInput = document.querySelector('#team-date')

    const teamButton = document.querySelector('#team-duty')
    teamButton.addEventListener('click', function (event) {
      if (teamInput.value) {
        window.location.href = `/schedule/team/
								${teamInput.dataset.userTeam}/
								${teamInput.value}/`
      }
    })

    const hospitalInput = document.querySelector('#hospital-date')

    const hospitalButton = document.querySelector('#hospital-duty')
    hospitalButton.addEventListener('click', function (event) {
      if (hospitalInput.value) {
        window.location.href = `/schedule/hospital/
								${hospitalInput.value}/`
      }
    })
  </script>
```

전반적으로 수정하며 계정에 대한 여러 `a tag` 또한 하나의 드랍다운 버튼으로 만들었다.

![127.0.0.1_8000_schedule_personal_2_ (2)](DFN 진행 상황 (21.11.03).assets/127.0.0.1_8000_schedule_personal_2_ (2).png)

![127.0.0.1_8000_schedule_personal_2_](DFN 진행 상황 (21.11.03).assets/127.0.0.1_8000_schedule_personal_2_-16359317075641.png)

![127.0.0.1_8000_schedule_personal_2_ (1)](DFN 진행 상황 (21.11.03).assets/127.0.0.1_8000_schedule_personal_2_ (1).png)

<br>

## 전체 듀티 조회

조회 방법은 팀의 듀티를 조회하는 방법과 동일하다. 추가된 URL은 다음과 같다.

```python
# duty_creater/urls.py

from django.urls import path
from . import views


app_name = 'schedule'
urlpatterns = [
	# 생략
    
    # 병동 일정(이번 달, 기본값)
    path('hospital/', views.hospital, name='hospital'),  
    # 병동 일정(달 선택 가능)
    path('hospital/<str:date>/', views.hospital, name='hospital'),  
]
```

![127.0.0.1_8000_schedule_hospital_](DFN 진행 상황 (21.11.03).assets/127.0.0.1_8000_schedule_hospital_.png)

<br>

## 달의 마지막 날 변수 추가

기존의 듀티 생성 관련 함수는 모두 한 달이 31일로 끝난다는 가정하에 작성되어 있었다. 파이썬의 `calendar` 라이브러리를 이용하여 달의 마지막 날을 따로 변수에 추가하여 달라지는 마지막 날에 대응해 전체 함수를 수정하였다. 

```python
# # duty_creater/views.py

def create_monthly(request, date):
    # date: 사용자가 선택한 날짜(YY-MM 형식. str)
    month = date[5: 7]  # 사용자가 선택한 달(MM 형식)
    year = date[: 4]  # 사용자가 선택한 연(YY 형식)
    
    # 해당 달의 마지막 날을 int 타입으로 받음
    last_day = calendar.monthrange(int(year), int(month))[1]  
    
    # 생략
    
# 수정된 다른 함수 생략
```



