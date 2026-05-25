from django.contrib import admin

from timers.models import Session, Timer, TableOffset, TableRanges

class TimerInline(admin.StackedInline):
    model = Timer

class TableOffsetInline(admin.StackedInline):
    model = TableOffset
    extra = 0

class TableRangesInline(admin.StackedInline):
    model = TableRanges
    extra = 0

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    model = Session
    inlines = [
        TimerInline,
        TableRangesInline,
        TableOffsetInline,
    ]
    list_display = ["short_code", "title"]
