from django.contrib import admin

from .models import (
    User,
    Batch, UserBatch,
    Activity, UserActivity,
    Card, UserCard,
    Question, Option, Answer
)

# Register your models here.

admin.site.register(User)
# admin.site.register(Batch)
# admin.site.register(UserBatch)
# admin.site.register(Activity)
# admin.site.register(UserActivity)
# admin.site.register(Card)
# admin.site.register(UserCard)
# admin.site.register(Question)
admin.site.register(Option)
# admin.site.register(Answer)


class UserBatchInline(admin.TabularInline):
    model = UserBatch
    extra = 1

# @admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    inlines = [UserBatchInline]

admin.site.register(Batch, BatchAdmin)


class UserActivityInline(admin.TabularInline):
    model = UserActivity
    extra = 1

# @admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    inlines = [UserActivityInline]

admin.site.register(Activity, ActivityAdmin)


class UserCardInline(admin.TabularInline):
    model = UserCard
    extra = 1

# @admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    inlines = [UserCardInline]

admin.site.register(Card, CardAdmin)


class OptionInline(admin.TabularInline):
    model = Option
    extra = 1  

# @admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [OptionInline]

admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
