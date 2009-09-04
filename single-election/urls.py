# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from views import *

urlpatterns = patterns('',
  (r'^$', home),
  (r'^about$', about),
  (r'^cast$', cast),
  (r'^confirm$', cast_confirm),
  (r'^done$', cast_done),
)