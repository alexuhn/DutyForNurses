from collections import deque
from random import randrange

class PriorityManager:
    
    def __init__(self, nurse_pk, grade, team_pk, off_count):
        self.nurse_pk = nurse_pk
        self.team_pk = team_pk
        self.nurse_grade = grade
        self.monthly_shift = 0
        self.monthly_night_shift = 0
        self.offs = off_count
        self.last_shift = 0
        self.shift_streaks = 2
        self.weekly_shift = 0
        self.weekly_schedule = deque([0, 0, 0, 0, 0, 0, 0])
        self.vacation_date = set()

    def __repr__(self) -> str:
        basic_infos = f'pk:{self.nurse_pk}, team:{self.team_pk}, grade:{self.nurse_grade} monthly_shift:{self.monthly_night_shift}'
        last_weeks_schedule = f'last_weeks_schedule: {self.weekly_schedule}'
        return basic_infos + '\n' +  last_weeks_schedule
        
    def personalize(self, last_schedule):

        # 1. weekly_schedule 개인화.
        if last_schedule is not None:
            last_weeks_schedule = last_schedule[-8:]
            for shift in last_weeks_schedule:
                self.weekly_schedule.append(shift)
                self.weekly_schedule.popleft()

        # 2. last_shift, shift_streak, weekly_shift. 
        index = 6
        last_duty = self.weekly_schedule[-1]
        is_streak = True
        while index >= 0:
            
            shift = self.weekly_schedule[index]
            index -= 1

            if shift: self.weekly_shift += 1
            
            if shift != last_duty:
                is_streak = False
            
            if is_streak:
                self.shift_streaks += 1


    def update_a_shift(self, shift):
        # 1. 일주일 전 스케쥴 삭제.
        shift_week_ago = self.weekly_schedule.popleft()
        if shift_week_ago: self.weekly_shift -= 1
        
        # 2. 업데이트 작업
        # 1) 최근 근무 기입.
        self.weekly_schedule.append(shift)

        # (1) 예외 처리- 야간근무
        if shift == 3:  # 야간근무 시 
            self.monthly_night_shift += 1   # 월간 야근 횟수 1 추가.

        # (2) 근무를 했다면
        if shift:
            # a. 월간 근무일 수 1 증가
            self.monthly_shift += 1
            # b. 주간 근무일 수 1 증가
            self.weekly_shift += 1        

        # 3) STREAK 갱신
        # (1) 이전 근무 == 현재 근무일 경우
        if self.last_shift == shift:
            self.shift_streaks += 1 # 연속 근무 횟수 1 가산
        # (2) 이전 근무와 현재 근무가 다르다면
        else:
            self.shift_streaks = 1  # 연속 근무 횟수 초기화
            self.last_shift = shift # 마지막 근무 변경. 


    def compute_priority(self, shift, today):
        
        # 1. 예외 처리 -> 
        # 1) None 값 반환하는 경우
        # (1) 근무는 오름차순으로 해야 한다.
        if shift and shift < self.last_shift:
            return None
        
        # (2) 한 달에 야근을 8회 이상 하지 않는다.
        if shift == 3 and self.monthly_night_shift > 7:
            return None
        
        # (3) 휴가 관련
        # a. 휴가 전날에 night 근무를 하지 않는다. 
        if shift == 3 and today+1 in self.vacation_date:
            return None
        
        # b. 휴가날에는 근무를 하지 않는다.  
        if shift and today in self.vacation_date:
            return None
        
        priority_token = 0
        # 2) 최 우선 처리 (우선도 5000)
        # (1) 휴가 당일
        if not shift and today in self.vacation_date:
            priority_token += 5000
            return -priority_token
        
        priority_token = randrange(0, 1500)

        # 2. 우선도 연산 시작.
        # # 1) 연속 근무
        # (1) shift_streak 2 미만
        # 예상 값: 300 ~ 700
        if shift and shift == self.last_shift and self.shift_streaks < 2:
            priority_token += randrange(400, 800)
    
        # # 추가 주 5일 이상 일했을 때 
        # 근무 할 확률이 줄어듦. 
        if shift and self.weekly_shift >= 5:
            multipliyer = self.weekly_shift - 4
            priority_token -= randrange(200, 500) * multipliyer

        # # (2) shift_streak 2 이상
        # # 예상 값: 500 ~ 850
        if shift == self.last_shift and self.shift_streaks >= 2:
            priority_token -= randrange(300, 500)

        # # (3) 2연속 근무 후 근무하려고 
        if shift == self.last_shift + 1 and self.shift_streaks >= 2:
            priority_token += randrange(400, 800)

        if not shift:
            priority_token -= 600


        return -priority_token