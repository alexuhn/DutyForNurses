# Q&A

# Q1. 왜 완전탐색 안 하고 DP + 그리디? 최적해는 DFS 등으로 완전탐색해야 나오지 않나?

## 답1 : 알고리즘상의 최적해 != 실제 최적해 

**최적해**는 `알고리즘적으로 ` 가장 적절한 해가 아니라 `사용자==간호사` 가 만족하는 근무표.

우리의 역할은 `적절한` 근무표들을 `알고리즘`을 통해 '사용자가 만족할 때까지' 제공하는 것.  물론 처음 생성된 시간표도 당연히 만족스럽겠지만.

## 답2: 사용자 성향

사용자들은 조금이라도 홈페이지가 느린 것 같으면 `새로고침`을 연타한다. 너희들도 그렇게 하듯이..

## 답3: 신뢰성 확보

**사람들은 보통 안 쓰던걸 쓰면 신기해서라도 이상한 짓(ex: 새로고침 아주 많이 눌러보기)** 을 하게 된다. 처음 눌러볼 때도 '매우 빠른 시간 안에 좋은 시간표를 계속 주네?' 하는 느낌을 주고, 이들을 고객으로 만들기 위함. 



# Q2. 왜 `랜덤토큰`을 쓰냐?

## 답1: 브루트포스 검사(전수조사)가 불가능하기 때문

### 브루트포스(전수조사)

* 1명당 4개의 근무 타입 

* 18명의 간호사
* 31일
* (4**18) 의 31제곱???

### 그리디(표본조사)

* `불가능한 경우들` 을 배제한 후 
* 적당히 괜찮은 `경우의 수들` 을 조사. 
* 실제로 아래와 같은 단순 난수로도 '멀쩡한' 시간표를 쉽게 얻을 수 있음(현재 규모에서는)

```python
priority_token = randrange(1, 100)
```



## 꼬리 질문 - 그럼 왜 구태여 '가중치'를 부여하냐?

### 답 2: 우수한 표본들을 선정하기 위함 + 코드 확장성.

ex): 24인 팀 3개, 한 팀에서 각 근무(day, evening, night)별 6인 근무하는 기준으로 시간표를 작성해봄.

성공 평균 실행시간 0.7초

ex2) : 8인 팀 3개, 한 팀에서 각 근무별 2인 근무 -> 성공률 99.9% (1000번 시도 중 약 10회 실패)

평균 실행시간 50ms



## 꼬리질문 - 그래도 잘 이해가 안 된다..

### 답3: 내가 시간표를 짜본다면...

일단 '좋아보이는' 대로 시간표를 짜다가 `이거 안 된다` 싶으면

1. 이전 시간표를 지우고
2. 예전과는 `다른` 방식으로 시간표를 작성하기 시작할 것. 

**다르게 시도해보는** 것을 구현.



# Q3. 왜 5일씩 백트랙하냐?

시간표 생성 실패의 원인은 나비효과. 분명히 과거에 했던 근무 조합때문에 현재 근무표가 나오지 않는 것. 프로그램 내부에서 **'왜'를 찾아내서 제거할 수 있겠으**나, 언제 어디서부터 왜 잘못되었는지를 추적하고 **검출해내는 것은 그 자체만으로 시간**이 든다. 찾아서 고치는게 아니라 `문제 발생의 시작점`으로 추정되는 곳부터 다시 만드는게 연산량을 줄이는 방법이다. 

중요한 것: `왜 이런 문제가 발생했는가?` 가 아니라 `어떻게 하면 가장 빨리 좋은 시간표를 제시할 수 있는가?`

