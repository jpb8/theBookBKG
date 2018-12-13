from django.contrib import admin
from account.models import Account, AccountAdmin


# Register your models here.
admin.site.register(Account, AccountAdmin)
