# DFN 진행 상황 (21.11.06)

1. 듀티 생성 과정 중 개별 듀티를 수정할 수 있게 되었다.
2. 듀티 생성 확정 이후 DB에 저장하는 대기 시간 동안 로딩 표시를 출력하게 되었다.
3. 초기 메인 화면을 생성하였다.
4. 기타 자잘한 수정을 진행했다.

<br>

## 듀티 생성 중 개별 듀티 수정 기능 추가

듀티 생성 알고리즘을 통해 조건에 맞는 전체 일정을 생성할 수 있지만 현재 만들어진 듀티를 수정하기 위해서는 관리 페이지에 직접 접속하는 방법밖에 없다. 듀티 일정을 생성하는 것이 가장 중요하지만 듀티를 짜면서 알고리즘이 고려할 수 없는 조건이 존재할 수 있기 때문에 사용자의 편의를 위해서는 쉬운 수정이 그다음으로 중요하다 생각해 이를 구현하기 위한 방법을 생각해 보았다. 

10월 26일 수정을 통해 이미 생성된 듀티를 조회해 이를 수정하는 기능을 만들었지만 간호사 pk와 날짜, 듀티를 하나의 행에 수직으로 출력하는 방법밖에 성공하지 못했고 이를 사용자가 직접 사용하기엔 보기에도, 사용하기에도 불편했다. 

듀티를 `table tag`로 출력하도록 코드를 짜며 가장 좋은 수정 방법은 듀티를 생성하고, 그 결과가 출력되었을 때 사용자가 수정하고 싶은 부분을 발견하면 해당 테이블 칸에 직접 원하는 듀티 값을 입력할 수 있는 것으로 생각했었다. 이를 구현하고 싶었지만 HTML과 CSS만 이용한 방법은 생각해내지 못했었다. 

이후 자바스크립트를 배우며 생각한 것과 비슷하게 수정 기능을 만들 수 있으리라 생각했다. 구현하고자 하는 수정 기능에서 가장 중요한 것은 사용자가 듀티 생성 화면에서 수정을 동시에 진행할 수 있도록 만드는 것이기 때문에 다음과 같은 방법을 생각해봤다.

1. 출력된 듀티에서 수정하고자 하는 듀티를 클릭하면 `OFF-DAY-EVENING-NIGHT` 순으로 듀티 번호가 `0-1-2-3`으로 변경되도록 한다. 이 번호는 출력 시 이용해 각 듀티에 맞는 배경색과 출력값(`/`, `D`, `E`, `N`) 변경에 함께 이용한다.
2. 듀티 번호를 간호사 pk 번호와 수정을 원하는 날짜와 함께 JS 객체에 저장하여 이를 장고에 전달한다. 객체에 저장할 때는 `{간호사 pk-날짜(일): 원하는 듀티}` 형식을 맞춘다.
3. 장고에 전달된 JS 객체는 분해해 원하는 값을 가져와 듀티를 저장하는 `dict_duties` 딕셔너리에 반영한다. 이후 DB에 저장한다.

이를 구현한 주요 `script tag`와 `create_monthly` 함수는 다음과 같다.

```django
<!-- create_monthly.html -->

<script>
  const updates = {}  // 장고에 전달될 객체
  const duties = document.querySelectorAll('.duty')  // 듀티를 출력하는 td tag
  
  // 모든 td tag에 클릭 이벤트를 붙임
  duties.forEach(duty => {
    duty.addEventListener('click', function (event) {
      // 수정을 원하는 날짜와 간호사 pk, 듀티 번호 
      const date = event.target.dataset.date
      const nursePk = event.target.dataset.nursePk
      const targetDuty = parseInt(event.target.dataset.targetDuty)
		
      // 듀티는 각각 0, 1, 2, 3으로 전달되기 때문에 이를 이용해 순서대로 듀티를 바뀌며
      // 원하는 듀티를 숫자로 객체에 저장
      if (updates[`${nursePk}-${date}`] === undefined) {
        updates[`${nursePk}-${date}`] = (targetDuty + 1) % 4
      } else {
        updates[`${nursePk}-${date}`] = (updates[`${nursePk}-${date}`] + 1) % 4
      }
		
      // 각 듀티에 따른 배경색과 출력값 갱신
      if (updates[`${nursePk}-${date}`] === 0) {
        duty.style.backgroundColor = '#ffffff'
        duty.innerText = '/'
      } else if (updates[`${nursePk}-${date}`] === 1) {
        duty.style.backgroundColor = '#2a9d8f'
        duty.innerText = 'D'
      } else if (updates[`${nursePk}-${date}`] === 2) {
        duty.style.backgroundColor = '#e9c46a'
        duty.innerText = 'E'
      } else if (updates[`${nursePk}-${date}`] === 3) {
        duty.style.backgroundColor = '#f4a261'
        duty.innerText = 'N'
      }
    })
  })
</script>
```

```javascript
// 생성된 JS 객체 예시
    
{
    "8-27": 1,  // pk 8번 간호사가 27일 듀티를 DAY로 바꾸기 원함
    "18-23": 3,  // pk 18번 간호사가 28일 듀티를 NIGHT로 바꾸기 원함
    "19-23": 2  // pk 19번 간호사가 28일 듀티를 EVENING으로 바꾸기 원함
}
```

```python
# views.py - create_monthly 함수

	if request.method == "POST":
        # 사용자가 전달한 JS 객체를 불러옴
        updates = json.loads(request.body)
   
		# 이를 이용해 dict_duties 딕셔너리에 반영
        for key, value in updates["updates"].items():
            nurse_id, day = key.split('-')  # 간호사 pk와 날짜
            day = int(day)  
            wanted_duty = value  # 원하는 듀티 번호
            dict_duties[nurse_id][day - 1] = wanted_duty
```

### 이전 수정 방법

![update](DFN 진행 상황 (21.11.06).assets/update.png)

### 현재 수정 방법

`수정 전`

![127.0.0.1_8000_schedule_create_2023-04_ (1)](DFN 진행 상황 (21.11.06).assets/127.0.0.1_8000_schedule_create_2023-04_ (1).png)

`수정 후`

![127.0.0.1_8000_schedule_create_2023-04_ (3)](DFN 진행 상황 (21.11.06).assets/127.0.0.1_8000_schedule_create_2023-04_ (3).png)

<br>

## DB저장 대기 시 로딩 표시

DB에 듀티를 저장할 때 약 3초의 대기시간이 존재한다. 사용자가 이 대기 시간 동안 듀티가 저장 중이라는걸 알 수 있도록 로딩 화면을 생성하였다.

로딩 화면을 위한 새 `div`를 생성하여 불투명한 흰 배경과 bootstrap spinner를 이용하였고 사용자가 `확정` 버튼을 누를 시 다음과 같은 화면이 출력된다.

![127.0.0.1_8000_schedule_create_2023-04_ (4)](DFN 진행 상황 (21.11.06).assets/127.0.0.1_8000_schedule_create_2023-04_ (4).png)

<br>

## 초기 화면 수정

`Duty For Nurses`의 모든 기능은 인증된 사용자만 이용할 수 있기에 다른 사용자도 접근할 수 있는 메인 페이지로 사용하기 위해 기존에 존재하던 `index` URL을 가져와 수정하였다.

![127.0.0.1_8000_schedule_ (1)](DFN 진행 상황 (21.11.06).assets/127.0.0.1_8000_schedule_ (1).png)

<br>

## 기타 수정

`views.py` 함수를 수정해 다음과 같은 변경사항이 생겼다.

1. 모든 기능에 대해 인증된 사용자만 이용할 수 있다.
2. 새로운 듀티 생성과 관련된 기능은 스태프 사용자만 이용할 수 있다.
3. 듀티를 생성할 시 이미 듀티가 존재하는 달을 선택하면 경고창을 띄우고 더는 진행할 수 없다.
4. 듀티를 조회할 시 듀티가 존재하지 않는 달을 선택하면 경고창을 띄우고 더는 진행할 수 없다.

또한 모든 템플릿을 수정해 디자인을 통일시켰다. 주요 기능의 템플릿은 다음과 같이 변경되었다.

![127.0.0.1_8000_schedule_personal_7_](DFN 진행 상황 (21.11.06).assets/127.0.0.1_8000_schedule_personal_7_.png)

![127.0.0.1_8000_schedule_team_1_](DFN 진행 상황 (21.11.06).assets/127.0.0.1_8000_schedule_team_1_-16362039279571.png)

> 현재 사용자의 이름은 색상을 변경하여 눈에 띄게 하였고 `table-hover` 속성을 추가해 간호사별 듀티를 더 잘 확인할 수 있게 하였다.

![127.0.0.1_8000_schedule_create_ (1)](DFN 진행 상황 (21.11.06).assets/127.0.0.1_8000_schedule_create_ (1).png)

![127.0.0.1_8000_accounts_profile_7_](DFN 진행 상황 (21.11.06).assets/127.0.0.1_8000_accounts_profile_7_.png)

