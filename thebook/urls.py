"""thebook URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.conf.urls import include
from sportsbook import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', views.index, name='index'),
    url(r'^sportsbook/', include('sportsbook.urls', namespace='sportsbook')),
    url(r'^account/', include('account.urls', namespace='account')),
    url(r'^betslip/', include('betslip.urls', namespace='betslip')),
    path('api/', include('api.urls')),
    path("players/", include('players.urls')),
    path("slate/", include('slate.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
