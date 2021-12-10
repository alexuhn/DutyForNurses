from calendar import monthrange
import calendar
from heapq import heappop, heappush
from .PriorityManager import PriorityManager


class ScheduleManager:

    def __init__(self, team_number_list) -> None:
        """
        매개 변수: 팀 번호가 작성된 리스트
        """
        self.team_numbers = team_number_list
        self.priority_stack = []
        self.daily_schedule_stack = []
        self.ideal_schedule_counter = [0, 1, 1, 1]
        self.recursed_days = 0
        self.current_priorities = dict()
        self.whole_schedule = dict()
        self.nurses_team_dict = dict()
        self.team_nurse_dict = dict()
        
        for team_number in team_number_list:
            self.team_nurse_dict[team_number] = set()

    def __repr__(self) -> str:
        return 

    def set_needed_nurses_by_team(self, nurses_needed)  -> None:
        """
        *** shift 당 필요한 간호사의 인원 수를 설정***  
        1. 매개 변수: nurses_needed - 한 shift에 한 팀당 필요한 간호사
        2. 반환값: None
        """
        for grade in range(1, 4):
            self.ideal_schedule_counter[grade] = nurses_needed

    def push_nurse_info(self, nurse_personal_infos)  -> None:
        """
        # 간호사의 개인정보를 입력받음 #
        1. 매개변수: dict()
        2. 출력값: None
        3. 역할: 간호사의 근무별 우선도 계산을 위한 정보 입력. 
        * nurse_personal_info
        1) key: nurse_pk
        2) value: list. == [nurse_pk, grade, team_pk, off_count]
        """
        for nurse_pk, grade, team_pk, off_count in nurse_personal_infos.values():
            manager = PriorityManager(nurse_pk, grade, team_pk, off_count)
            
            self.current_priorities[nurse_pk] = manager
            self.team_nurse_dict[team_pk].add(nurse_pk)
            self.nurses_team_dict[nurse_pk] = team_pk
    
    def push_last_schedules(self, schedules) -> None:
        """
        # 간호사의 최근 근무 일정을 입력받음
        1. 매개변수: dict()
        2. 출력값: None
        3. 역할: nurse의 근무별 priority 계산을 위한 정보 입력. 
        
        * schedules
        1. key: nurse_pk
        2. value: [0, 1, 2, 3, 1.....] 형태로 된 리스트. 
        """
        for nurse_pk, schedule in schedules.items():
            self.current_priorities[nurse_pk].personalize(schedule)

    def push_vacation_info(self, vacation_dict) -> None:
        """
        
        """
        for nurse_pk, vacation_tuple in vacation_dict.items():
            for date in vacation_tuple:
                # 인덱스 처리를 위해 date-1
                self.current_priorities[nurse_pk].vacation_date.add(date - 1)


    def get_team_info(self, team_number) -> dict:
        """
        # 팀에 속한 간호사들의 PriorityManager값을 딕셔너리 형태로 반환
        1. 매개변수: int
        2. 출력값: team_info_dict -> dict()
        1) key: nurse_pk
        2) value: PrioritManager object 
        """
        team_info_dict = dict()
        for nurse_pk in self.team_nurse_dict[team_number]:
            team_info_dict[nurse_pk] = self.current_priorities[nurse_pk]
        return team_info_dict

    def create_monthly_schedule(self, date) -> None:

        year = int(date[:4])
        month = int(date[5:7])
        day = int(date[-2:])
        
        current_day = 0
        last_day = monthrange(year, month)[1]
        remade_same_date = 0

        while current_day < last_day and self.recursed_days < 40:
            validation_token = 1
            todays_schedule = [[] for _ in range(4)]

            for team_num in self.team_numbers:
            
                team_info = self.get_team_info(team_num)
                team = DailyManager(self.ideal_schedule_counter)
                
                team_schedule = team.build_schedule(team_info, current_day)
                if team_schedule is not None:
                    for shift in range(4):
                        for nurse_pk in team_schedule[shift]:
                            todays_schedule[shift].append(nurse_pk)
                    validation_token |= team.pop_grade_validation_token()

                else:   # validation 토큰을 무조건 틀린 값으로 설정. 
                    validation_token = 25

            if validation_token == 15:      # 1111
                self.priority_stack.append(self.current_priorities)
                self.daily_schedule_stack.append(todays_schedule)
                self.update_nurse_priority_manager(todays_schedule)
                remade_same_date = 0
                current_day += 1
            
            elif remade_same_date == 10:
                current_day -= self.recurse_schedule(current_day)
                remade_same_date = 0
                print(f'recursed_by {self.recursed_days}')
                
            else:
                remade_same_date += 1
        
        self.update_whole_schedule()

            

    def modify_monthly_schedule() -> None:
        return
    
    def is_validate():
        return

    def update_nurse_priority_manager(self, todays_schedule):
        """
        todays schedule 예상 형태
        [[7, 8, 10], [9], [11], [12]]
        """
        for shift in range(4):
            for nurse in todays_schedule[shift]:
                self.current_priorities[nurse].update_a_shift(shift)

    def update_whole_schedule(self) -> dict:
        schedule_dict = dict()
        LENGTH = len(self.daily_schedule_stack)
        for nurse_pk in self.nurses_team_dict.keys():
            schedule_dict[nurse_pk] = [0] * LENGTH
        
        for date in range(LENGTH):
            for shift in range(4):
                for nurse_pk in self.daily_schedule_stack[date][shift]:
                    schedule_dict[nurse_pk][date] = shift

        self.whole_schedule = schedule_dict

    def recurse_schedule(self, recurse_time) -> int:
        """
        매개변수:
        1. 현재 작성중인 날짜.
        반환값:
        1. 실제로 돌
        """
        self.recursed_days += 1

        if not recurse_time:
            return 0
        
        # 8번째 시도마다 '맨 처음'으로 돌아간다
        print(self.recursed_days)
        if self.recursed_days % 5 == 0:
            print(self.recursed_days)
            self.current_priorities = self.priority_stack[0]
            self.priority_stack.clear()
            self.daily_schedule_stack.clear()
            return recurse_time

        # 최대 6일 전까지 돌아간다. 
        if recurse_time > 6:
            recurse_time = 6

        for _ in range(recurse_time):
            self.current_priorities = self.priority_stack.pop()
            self.daily_schedule_stack.pop()

        return recurse_time

    def get_stack(self) -> list:
        return self.daily_schedule_stack

    def get_schedule(self) -> dict:
        return self.whole_schedule
    

    # 디버깅용 기능들
    def print_schedule_by_day(self) -> None:
        for day in range(len(self.daily_schedule_stack)):
            print(f'day{day+1}: {self.daily_schedule_stack[day]}')

    def print_schedule_by_nurse(self) -> None:
        for key, value in self.whole_schedule.items():
            print(key, value)




class DailyManager:

    def __init__(self, ideal_schedule) -> None:
        self.priority_que = []
        self.ideal_schedule = ideal_schedule
        self.grade_validation_token = 1

    def __repr__(self) -> str:
        return f'ideal_schedule: {self.ideal_schedule}, validation_token: {self.grade_validation_token}'

    def pop_grade_validation_token(self) -> int:
        return self.grade_validation_token    

    def update_validation_token(self, token) -> None:
        self.grade_validation_token |= token

    def build_priority_que(self, nurse_priority_infos, date) -> None:
        temp_que = []
        for nurse in nurse_priority_infos.values():
            for shift in range(4):
                priority = nurse.compute_priority(shift, date)
                if priority is not None:
                    heappush(temp_que, (priority, nurse.nurse_pk, nurse.nurse_grade, shift))

        self.priority_que = temp_que
        
    def place_shifts(self) -> list:
        schedule_table = [[] for _ in range(4)]
        current_schedule_counter = [0, 0, 0, 0]
        current_valdation_token = 1
        placed_nurses_set = set()

        while self.priority_que:
            priority, nurse_pk, grade, shift = heappop(self.priority_que)
            if shift and current_schedule_counter[shift] >= self.ideal_schedule[shift]:
                continue

            if nurse_pk in placed_nurses_set:
                continue

            current_schedule_counter[shift] += 1
            schedule_table[shift].append(nurse_pk)
            placed_nurses_set.add(nurse_pk)

            if grade:
                current_valdation_token |= (1 << shift)
        
        self.update_validation_token(current_valdation_token)
        return schedule_table


    def build_schedule(self, nurse_priority_infos, date) -> list:
        is_validate = False
        recursed_by = 0

        while not is_validate and recursed_by < 50:
            
            self.build_priority_que(nurse_priority_infos, date)
            completed_schedule = self.place_shifts()
            recursed_by += 1

            for shift in range(1, 4):
                if len(completed_schedule[shift]) != self.ideal_schedule[shift]:
                    break
            else:
                is_validate = True

        if recursed_by < 30:
            return completed_schedule
        else:
            return None