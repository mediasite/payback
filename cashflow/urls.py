# -*- coding: UTF-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'currencies/$', 'cashflow.views.currs_list', name='currs_list'),
    url(r'payments/add/', 'cashflow.views.create_payment', name='create_payment'),
    url(r'payments/(?P<id>\d+)/$', 'cashflow.views.status', name='payment_status'),
    url(r'payments/(?P<backend_slug>\w+)/success/$', 'cashflow.views.success', name='payment_success'),
    url(r'payments/(?P<backend_slug>\w+)/fail/$', 'cashflow.views.fail', name='payment_fail'),
)