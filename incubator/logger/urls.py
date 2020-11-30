from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.main_page, name='main_page'),
    url(r'^active/$', views.active, name='active'),
    url(r'^active/timer/$', views.timer, name='timer'),
    url(r'^active/rh_step/$', views.rh_step, name='rh_step'),
    url(r'^active/on_off/$', views.on_off, name='on_off'),
    url(r'^image/$', views.capture_image, name='capture_image'),
    url(r'^start/$', views.start, name='start'),
    url(r'^start/timer/$', views.timer, name='timer'),
    url(r'^active/(?P<incubation_id>[0-9]+)/$', views.past_inc, name='past_inc'),
    ]
