# DFN 진행 상황 (21.10.25)

중요 기능과 관련된 변경 사항만 기록하였다.

<br>

## 사용자 관리 시스템 개선

1. 간호사의 프로필에서 경력과 나이는 입력한 날짜를 기준으로 계산하여 정수로 반환하여 출력한다.
2. 로그인한 사용자만 프로필을 생성할 수 있고 이미 프로필이 있는 사용자는 프로필을 생성할 수 없다.
3. 프로필 작성 시 form 항목의 이름을 변경하였고 날짜를 선택할 때 1980년부터 선택할 수 있다.
4. 레벨, 사용한 연차 수, 팀, OFF 수는 각각의 최댓값과 최솟값을 설정하였다. 

```python
# accounts/views.py

def profile(request, nurse_pk):
    nurse = get_object_or_404(get_user_model(), pk=nurse_pk)
    does_exist = False  # 프로필이 존재하는가

    if Profile.objects.filter(user_id=nurse_pk).exists():
        does_exist = True
        profile = Profile.objects.get(user_id=nurse_pk)

        # 경력과 나이를 햇수로 계산
        WEX = datetime.date.today() - profile.WEX 
        WEX = int(WEX.days // 365.25)
        age = datetime.date.today() - profile.DOB
        age = int(age.days // 365.25)
 
        context = {
            'nurse': nurse,
            'profile': profile,
            'WEX': WEX,
            'age': age,
            'does_exist': does_exist,
        }
        return render(request, 'accounts/profile.html', context)
    context = {
        'nurse': nurse,
        'does_exist': does_exist,
    }
    return render(request, 'accounts/profile.html', context)
```

```python
# accounts/forms.py

year = datetime.datetime.today().year  # 올해 년도

class ProfileForm(forms.ModelForm):
    name = forms.CharField(
        label='이름',
        widget=forms.TextInput(attrs={'maxlength': 10,})
    	)
    WEX = forms.DateField(
        label='경력 시작일',
        widget=forms.SelectDateWidget(years=range(1980, year + 1))
        )
    DOB = forms.DateField(
        label='생년월일',
        widget=forms.SelectDateWidget(years=range(1980, year + 1))
        )
    level = forms.IntegerField(
        label='레벨',
        max_value = 3,
        min_value = 0
    )
    PTO = forms.IntegerField(label='사용한 연차 수', min_value = 0)
    team = forms.IntegerField(label='팀',min_value = 0)
    OFF = forms.IntegerField(label='OFF 수',min_value = 0)

    class Meta:
        model = Profile
        # fields = '__all__'
        exclude = ('user',)
```

### 프로필 생성

![](DFN 진행 상황 (21.10.25).assets/create_profile.png)

### 프로필이 없을 경우

![no_profile](DFN 진행 상황 (21.10.25).assets/no_profile.png)

### 프로필

![profile](DFN 진행 상황 (21.10.25).assets/profile.png)

<br>

## 듀티 저장 시스템 개선

1. 원하는 달을 선택하는 새로운 과정이 추가되었다. 
2. 듀티 일정이 간호사를 key, 듀티 리스트를 value로 갖는 딕셔너리로 주어질 경우 이를 통해 한 달 일정을 출력할 수 있다.

```python
# duty_creater/views.py

def new_main(request):  # 원하는 달을 선택하도록 한다
    return render(request, 'dfn/new_main.html') 


def new(request):
    # 생략
    
    # 만약 듀티가 딕셔너리로 주어진다면
    dict_duties = {
        'nurse1': [1, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 2, 0, 
                   0, 0, 2, 3, 0, 0, 0, 3, 0, 0, 0, 3, 0, 0, 0, 3], 
        'nurse2': [2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 
                   1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0], 
        'nurse3': [0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 1, 0, 0, 
                   0, 1, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0], 
        'nurse4': [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 
                   3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2], 
        'nurse5': [3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 
                   2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1], 
        'nurse6': [0, 0, 3, 0, 1, 0, 0, 0, 1, 0, 3, 0, 0, 0, 3, 
                   0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0]
    }


    # 간호사를 username으로 저장한 리스트
    nurses = []
    for id in range(2, 8):
        nurses.append(get_user_model().objects.filter(pk=id).values('username')[0]['username'])


    if request.method == 'POST':
        start_date = request.POST.get('start')  # 사용자가 선택한 날짜
        month = start_date[5: 7] 
		
        # new 함수를 실행할때마다 db에 추가되서 임시로 매번 다 삭제
        Event.objects.all().delete()  
        
        # 생략

        context = {
            'duties_of_month': duties_of_month,
            'duties_of_day': duties_of_day,
            'month': month,

            'nurses': nurses,
            'duties': duties,
            'dict_duties': dict_duties
        }
        return render(request, 'dfn/new.html', context)
```

```django
<!-- duty_creater/new.html -->

{% extends 'base.html' %}

{% block content %}
<h1>{{ month }}월의 듀티 스케쥴</h1>

<table class="table text-center">
  <thead>
    <tr>
        <th colspan="32">1팀의 한달 스케쥴</th>
    </tr>
    <tr>
        <td></td>
        {% for duty in duties.0 %}
        <td>{{ forloop.counter }}</td>
        {% endfor %}
    </tr>
  </thead>
  <tbody>
    {% for nurse, duties in dict_duties.items %}
    <tr>
      <td>{{ nurse }}</td>
      {% for duty in duties %}
      {% if duty == 0 %}
      <td>{{ duty }}</td>
      {% elif duty == 1 %}
      <td style="background-color:#66cc00;">{{ duty }}</td>
      {% elif duty == 2 %}
      <td style="background-color:#4d9900;">{{ duty }}</td>
      {% else %}
      <td style="background-color:#408000;">{{ duty }}</td>
      {% endif %}
      {% endfor %}
    </tr>
    {% endfor %}
  </tbody>
</table>

<button type="button" class="btn btn-outline-success" style="float: right;">수정</button>
<button type="button" class="btn btn-outline-success me-3" style="float: right;">삭제 후 재생성</button>
<br>

<!-- 생략 -->
```

### 원하는 달 선택

![](DFN 진행 상황 (21.10.25).assets/new_main.png)

### 만들어진 일정

실제 간호사들이 사용하는 듀티표는 가로로된 A4용지에 행은 간호사, 열은 날짜로 설정하고 듀티는 `/`, `D`, `N`, `E`와 같이 표시하고 있었다. 듀티를 조회할 때 기존에 간호사가 익숙하게 보던 것과 구성을 동일하게 만들어 사용하는 도구는 달라져도 경험에는 끊김이 없는 연속성을 주고 싶었다. 이를 위해 한 달 듀티를 조회할 때에는 종이 듀티표와 동일한 형태로, 행에 각 간호사를, 열에 각 날짜를 넣은 테이블이 보이도록 했다. 현재 듀티는 0에서 3까지의 숫자로 표시되며 이후 각 숫자는 `/`, `D`, `N`, `E`  기호로 변경될 예정이다.

![](DFN 진행 상황 (21.10.25).assets/new_new.png)

### 필요한 기능

1. 일정이 만들어진 후 이를 삭제하고 싶을 때 다시 원하는 달을 선택하지 않아도 되도록 `삭제 후 재생성`을 통해 만들어진 일정을 삭제 후 다시 생성하는 기능. 하지만 삭제가 필요할지는 좀 더 생각해봐야 한다.
2. 수정 기능. 수정을 위해 만들어진 일정을 어떻게 다시 출력할지 고민이 필요하다.
3. 선택한 달에 이미 듀티가 존재한다면 일정을 생성할 수 없도록 막아야 한다.

