from django.contrib import admin
from .models import OTP, Lock, PreRegistration, ShareHistory, API, History

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('id','time','source','content')

@admin.register(Lock)
class LockAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'otp')


@admin.register(PreRegistration)
class PreRegistrationAdmin(admin.ModelAdmin):
    list_display = ('email','registered')

@admin.register(ShareHistory)
class ShareHistoryAdmin(admin.ModelAdmin):
    list_display = ('time', 'category', 'source', 'destination')

@admin.register(API)
class APIAdmin(admin.ModelAdmin):
    list_display = ('time','content')

@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('time','state')