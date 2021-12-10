from django.db import models
from django.conf import settings


class Event(models.Model):
    # on_delete=DO_NOTHING: nurse user가 삭제되어도 db를 수정하거나 삭제하지 않는다
    nurse = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    date = models.DateField()
    duty = models.IntegerField()

    def __str__(self):
        return f'{self.date}-N{self.nurse.pk}-D{self.duty}'


class ScheduleModification(models.Model):
    MODIFICATION_CATEGORY = [
        ('PTO', '연차 사용'),
        ('VAC', '휴가 신청'),
    ]
    nurse = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    category = models.CharField(max_length=50, choices=MODIFICATION_CATEGORY)
    from_date = models.DateField()
    to_date = models.DateField()
    note = models.TextField()
    approval = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.pk}-N{self.nurse.pk}'