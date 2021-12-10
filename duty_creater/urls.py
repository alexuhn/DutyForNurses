from django.urls import path
from . import views


app_name = 'schedule'
urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),  # 새 듀티 생성을 위한 날짜 선택
    path('create/<str:date>/', views.create_monthly, name='create_monthly'),  # 한달 일정 생성

    path('duty-exist/<str:date>/', views.duty_exist, name='duty_exist'),  # 한달 일정 생성 가능 여부 판별

    path('update/<str:date>/', views.update, name='update'),  # 생성된 듀티 일정 수정

    path('personal/<int:nurse_pk>/', views.personal, name='personal'),  # 개인 일정(이번 달)
    path('personal/<int:nurse_pk>/<str:date>/', views.personal, name='personal'),  # 개인 일정(달 선택 가능)

    path('team/<int:team_id>/', views.team, name='team'),  # 팀 일정(이번 달)
    path('team/<int:team_id>/<str:date>/', views.team, name='team'),  # 팀 일정(달 선택 가능)

    path('hospital/', views.hospital, name='hospital'),  # 병동 일정(이번 달)
    path('hospital/<str:date>/', views.hospital, name='hospital'),  # 병동 일정(달 선택 가능)

    path('modify/all/', views.all_modification, name="all_modification"),
    path('modify/create/', views.create_modification, name="create_modification"),
    path('modify/confirm/', views.confirm_modification, name="confirm_modification"),
    path('modify/<int:nurse_pk>/', views.modification, name="modification"),
    path('modify/<str:date>/', views.get_schedule_modification, name="get_schedule_modification"),
]