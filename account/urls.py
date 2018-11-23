from django.conf.urls import url
from account import views

app_name = 'account'

urlpatterns = [
    url(r'^signup', views.signup, name='signup'),
    url(r'^user_logout', views.user_logout, name='user_logout'),
    url(r'^user_login', views.user_login, name='user_login'),
    url(r'^active_bets', views.active_bets, name='active_bets'),
    url(r'^$', views.account_home, name='account_home'),
    url(r'^password/$', views.change_password, name='change_password'),
]