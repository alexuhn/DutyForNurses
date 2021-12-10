# DFN 진행 상황 (21.11.09)

1. 휴무를 신청하고, 조회하고, 듀티를 생성할 때 이를 반영할 수 있게 되었다.

<br>

## 휴무 신청 기능 추가

듀티 생성 알고리즘에 휴무를 반영하는 기능이 포함되어 있어 이를 사용자에게 보여줄 수 있는 여러 페이지를 생성하였다. 중요하게 생각한 부분은 스태프 권한이 있는 간호사가 듀티를 생성할 때 같은 화면에서 휴무 신청 기록을 조회할 수 있는 것이었다. 

휴무 요청은 요청하는 날을 포함한 달의 듀티를 생성할 때 고려되어야 하므로 듀티를 생성하는 시점에서 가장 큰 의미가 있다 생각했다. 휴무만을 관리하는 페이지를 만들 수 있지만 듀티를 생성하기 전에 휴무를 미리 승인한다면 이후 듀티를 생성하는 시점에서 자신이 승인했던 휴무를 인식하기 어려울 수 있어서 사용자가 듀티를 생성할 때 어떠한 휴무가 반영되는지 즉각적으로 알려주고 싶었다.

따라서 전체 휴무 신청 목록을 볼 수 있는 페이지에서 휴무를 승인하고 그 이후 듀티 생성 페이지로 이동해 듀티를 생성할 수도 있지만, 사용자가 실제 이 기능을 이용할 때 하나의 화면에서 본인이 승인한 내역을 직접 선택, 승인하고 듀티를 생성한다면 그 과정이 더 눈에 명확하게 보이고, 요청이 반영된 응답을 즉각 받을 수 있으리라 생각했다. 이를 위해 새로운 듀티를 만들기 위해 날짜를 선택하는 과정에서 휴무 요청 내역이 보이고 승인까지 할 수 있도록 하였다.

간호사의 휴무 기록은 신청 시 DB에 저장되며 선택된 날짜에 맞춰 템플릿에 출력된다. `models.py`의 주요 수정 내용은 다음과 같다. 

```python
class ScheduleModification(models.Model):
    MODIFICATION_CATEGORY = [
        ('PTO', '연차 사용'),
        ('VAC', '휴가 신청'),
    ]
    nurse = models.ForeignKey(settings.AUTH_USER_MODEL, 
                              on_delete=models.DO_NOTHING)
    category = models.CharField(max_length=50, choices=MODIFICATION_CATEGORY)
    from_date = models.DateField()  # 휴무 시작일
    to_date = models.DateField()  # 휴무 종료일
    note = models.TextField()  # 비고
    approval = models.BooleanField(default=False)  # 승인 여부

    def __str__(self):
        return f'{self.pk}-N{self.nurse.pk}'
```

휴무를 승인하고 이를 듀티 생성에 반영하는 과정은 듀티 생성 과정과 비슷하다. 사용자가 승인한 휴무는 JS 객체에 담겨 JSON 파일에 따로 저장된다. 이 JSON 파일을 장고에서 가져와 원하는 형태로 가공하고 이를 듀티 생성 알고리즘에 넘겨주게 되는 것이다.

`views.py`의 주요 수정 내용은 다음과 같다.

```python
    # 간호사의 휴가, 연차 신청 반영
    with open('modify_schedule.json') as json_file:
        modifications = json.load(json_file)

    modification_dict = {}  # 알고리즘 인자로 들어갈 휴무 정보 딕셔너리
    for schedule_modification_pk, modify in modifications.items():
        # modify == True, 즉 휴무가 승인된 경우에만 딕셔너리에 추가
        if modify:
            schedule_modification = ScheduleModification
            						.objects.get(pk=schedule_modification_pk)
            # 휴무 시작일
            from_day = int(schedule_modification.from_date.strftime('%d'))  
            # 휴무 종료일
            to_day = int(schedule_modification.to_date.strftime('%d'))  
            # 시작 날에서부터 종료 날까지 모두 담은 튜플
            day_tuple = tuple(range(from_day, to_day + 1)) 
            # 딕셔너리의 key는 간호사의 pk 값이고 value는 날짜를 담은 튜플
            modification_dict[schedule_modification.nurse.pk] = day_tuple
```

<br>

1) 개인 휴무 신청 내역 조회

![](DFN 진행 상황 (21.11.08).assets/127.0.0.1_8000_schedule_modify_7_.png)

2. 휴무 신청

![127.0.0.1_8000_schedule_modify_create_](DFN 진행 상황 (21.11.08).assets/127.0.0.1_8000_schedule_modify_create_.png)

3. 전체 휴무 신청 내역 조회

![127.0.0.1_8000_schedule_modify_all_](DFN 진행 상황 (21.11.08).assets/127.0.0.1_8000_schedule_modify_all_.png)

4. 듀티 생성시 휴무 내역 자동 조회, 승인

![127.0.0.1_8000_schedule_create_ (2)](DFN 진행 상황 (21.11.08).assets/127.0.0.1_8000_schedule_create_ (2).png)

5. 승인된 휴무가 반영된 듀티 생성

![127.0.0.1_8000_schedule_create_2021-12_](DFN 진행 상황 (21.11.08).assets/127.0.0.1_8000_schedule_create_2021-12_.png)