import datetime
import math
import random
import string
from datetime import timedelta
from math import floor

from django.db import models
from django.db.models import Manager
from django.utils import timezone

def create_short_code():
    charset = string.digits + string.ascii_letters
    return "".join(random.choice(charset) for _i in range(8))

# Create your models here.
class Session(models.Model):
    short_code = models.CharField(max_length=8, default=create_short_code)
    title = models.CharField(max_length=300)
    round = models.IntegerField(default=1)

    objects = Manager().select_related("timer")

    def __str__(self):
        return f"{self.short_code} - {self.title}"

    @property
    def available_tables(self) -> list[int]:
        tables = set()
        for range_ in self.tableranges_set.all():
            tables.update(range(range_.start, range_.end+1))
        return list(sorted(tables))


class Timer(models.Model):
    session = models.OneToOneField(Session, on_delete=models.CASCADE)

    start_time = models.DateTimeField()
    running = models.BooleanField(default=False)
    duration = models.DurationField()
    remaining_duration = models.DurationField(
        help_text="The duration remaining on the timer, calculated from start_time"
    )
    
    def pause(self):
        if self.running:
            self.running = False
            self.remaining_duration = (
                (self.start_time + self.remaining_duration) - timezone.now()
            )
            self.save()
    
    def start(self):
        if not self.running:
            self.running = True
            self.start_time = timezone.now()
            self.save()

    def reset(self):
        self.running = False
        self.remaining_duration = self.duration
        self.save()

    @property
    def display(self) -> str:
        if self.running:
            duration = (self.start_time + self.remaining_duration) - timezone.now()
        else:
            duration = self.remaining_duration
        MINS = 60
        HRS = MINS * 60
        tsecs = abs(int(floor(duration.total_seconds())))
        sgn = int(math.copysign(1, duration.total_seconds()))
        secs = tsecs % MINS
        mins = (tsecs % HRS) // MINS
        hrs = int(tsecs // HRS)
        if hrs > 0:
            return f"{sgn*hrs}:{mins:02d}:{secs:02d}"
        else:
            return f"{sgn*mins:02d}:{secs:02d}"

    @property
    def fraction_complete(self) -> float:
        if self.running:
            duration = (self.start_time + self.remaining_duration) - timezone.now()

        else:
            duration = self.remaining_duration
        return duration / self.duration


class TableRanges(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    start = models.IntegerField()
    end = models.IntegerField()

    class Meta:
        ordering = ["start"]


class TableOffset(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    table = models.IntegerField()
    offset = models.DurationField()

    class Meta:
        ordering = ["table"]

    @property
    def remaining_duration(self):
        return self.session.timer.remaining_duration + self.offset

    @property
    def display(self) -> str:
        timer = self.session.timer
        if timer.running:
            duration = (timer.start_time + self.remaining_duration) - timezone.now()
        else:
            duration = self.remaining_duration
        MINS = 60
        HRS = MINS * 60
        tsecs = abs(int(floor(duration.total_seconds())))
        sgn = int(math.copysign(1, duration.total_seconds()))
        secs = tsecs % MINS
        mins = (tsecs % HRS) // MINS
        hrs = int(tsecs // HRS)
        if hrs > 0:
            return f"{sgn * hrs}:{mins:02d}:{secs:02d}"
        else:
            return f"{sgn * mins:02d}:{secs:02d}"

    @property
    def fraction_complete(self) -> float:
        timer = self.session.timer

        if timer.running:
            duration = (timer.start_time + self.remaining_duration) - timezone.now()

        else:
            duration = self.remaining_duration
        return duration / timer.duration
