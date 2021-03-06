from push_endpoint import views
from django.conf.urls import include, url


urlpatterns = [
    url(r'', include([
        url(r'^$', views.DataList.as_view()),
        url(r'^established/$', views.EstablishedDataList.as_view()),
        url(r'^provider_list/$', views.ProviderList.as_view()),
        url(r'^(?P<pk>[0-9]+)/$', views.DataDetail.as_view(), name='data-detail'),
        url(r'^get-api-key/$', views.render_api_form, name='get-api-key'),
        url(r'^help/$', views.render_api_help, name='help'),
        url(r'^provider_information/$', views.provider_information, name='provider_information'),
        url(r'^information/$', views.render_settings, name='render_settings'),
    ]))
]
