# DFN 진행 상황 (21.10.26)

생성된 듀티 일정을 수정하는 기능이 추가되었다.

<br>

# 듀티 일정 수정 시스템 생성

원하는 연월을 통해 해당 날짜의 듀티 일정을 불러와 수정할 수 있다. 

1. 수정을 위한 url, `update/<str:date>/`에서 `date`는 `YYYY-MM` 형태로 입력해야 한다. 이는 사용자가 듀티 일정을 생성할 때 선택한 날짜가 저장되는 변수, `start_date = request.POST.get('start')`와 형태가 동일하다.
2. `EventFormSet`을 이용하여 여러 개의 `form`을 한꺼번에 출력할 수 있게 하였다. 
   1. 사용하고자 하는 `form`이 `modelform`이므로 `modelformset_factory`를 이용했다.
   2. 본래 `formset`은 빈 `form`이 하나 더 추가되기 때문에 `extra=0` 속성을 통해 이를 없앴다.
3. `Event`에서 간호사와 날짜는 `attrs={'readonly':'readonly',}` 속성을 통해 수정할 수 없도록 하였다.
4. `update.html` 출력은 [링크](https://stackoverflow.com/a/2234286)의 테이블을 사용하였다.

```python
# duty_creater/views.py

def update(request, date):
    wanted_events = Event.objects.filter(date__startswith=date).all().order_by('date')
    
    if request.method == 'POST':
        formset = EventFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('dfn:new_main')  # 임시

    else:
        formset = EventFormSet(queryset=wanted_events)
    context = {
        'formset': formset,
        'date': date
    }
    return render(request, 'dfn/update.html', context)
```

```python
# duty_creater/forms.py

from django import forms
from django.forms import modelformset_factory
from .models import Event


class EventForm(forms.ModelForm):
    nurse = forms.IntegerField(widget=forms.NumberInput(attrs={'readonly':'readonly',}))
    date = forms.DateField(widget=forms.DateInput(attrs={'readonly':'readonly'}))

    class Meta:
        model = Event
        fields = '__all__'

EventFormSet = modelformset_factory(Event, form=EventForm, extra=0)
```

```django
{% extends 'base.html' %}
{% load bootstrap5 %}

{% block content %}
<h1>일정 수정</h1>

<form action="{% url 'dfn:update' date %}" method="POST">
  {% csrf_token %}

  <table id="formset" class="form">
  {% for form in formset.forms %}
    {% if forloop.first %}
    <thead><tr>
      {% for field in form.visible_fields %}
      <th>{{ field.label|capfirst }}</th>
      {% endfor %}
    </tr></thead>
    {% endif %}
    <tr class="{% cycle row1 row2 %}">
      {% for field in form.visible_fields %}
      <td>{{ field }}</td>
      {% endfor %}
    </tr>
  {% endfor %}
  </table>

  <button class="btn btn-outline-success">수정</button>
</form>

{% endblock content %}
```

![](DFN 진행 상황 (21.10.26).assets/update.png)

### 개선해야 할 사항

필요한 정보 출력에는 문제가 없지만 템플릿이 매우 불친절해 실제 수정 기능에 사용되기에는 어렵다. `Form`을 날짜와 간호사에 맞춰 배치한뒤 듀티만 출력하는 것이 이상적이겠지만 현재로선 구현하기 어렵다. 

또 다른 방법은 자바스크립트를 배운뒤 url 이동 없이 수정이 가능하게 만드는 것인데 만약 이 또한 불가능하다면 전체 `Event`를 한꺼번에 `formset`에 넣어 수정하는 것이 아닌 단일 `Event`만 수정하도록 기능을 축소하거나 다른 기능을 전부 완성한 뒤 다시 `form` 출력을 공부해야 할 것 같다.