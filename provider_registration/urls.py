from django.conf.urls import patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from provider_registration import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^register', views.register_provider, name='register'),
    url(r'^contact_information', views.get_contact_info, name='contact_information'),
    url(r'^provider_detail/(?P<provider_long_name>.*)/$', views.detail, name='detail'),
    url(r'^provider_information', views.save_metadata_render_provider, name='provider_information'),
    url(r'^simple_oai_registration', views.redirect_to_simple_oai, name='simple_oai_registration')
)

urlpatterns += staticfiles_urlpatterns()
