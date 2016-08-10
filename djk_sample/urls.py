"""djk_sample URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url, patterns
# from django.contrib import admin
from club_app.views import ClubCreate, ManufacturerFkWidgetGrid


urlpatterns = [
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'club_app.views.main_page', name='club_main_page',
        kwargs={'view_title': 'Main page', 'allow_anonymous': True}),
    url(r'^accounts/', include('django_jinja_knockout._allauth.urls')),
    url(r'^club-create/$', ClubCreate.as_view(), name='club_create',
        kwargs={'view_title': 'Add new club'}),
    url(r'^manufacturer-fk-widget-grid(?P<action>/?\w*)/$', ManufacturerFkWidgetGrid.as_view(),
        name='manufacturer_fk_widget_grid',
        # kwargs={'ajax': True, 'permission_required': 'club_app.change_manufacturer'}),
        kwargs={'ajax': True}),
]

js_info_dict = {
    'domain': 'djangojs',
    'packages': ('djk_sample',),
}

urlpatterns += patterns('',
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
)

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns, static
    urlpatterns += staticfiles_urlpatterns()
    # media_static = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # urlpatterns += media_static
