from django.http import HttpResponsePermanentRedirect
from django.conf.urls.defaults import patterns, include, url
from django.views.decorators.cache import cache_page
from .feed import PlogFeed
import views


urlpatterns = patterns('',
    url('^$', views.home, name='home'),
    url('^rest/(?P<from_index>\d+)/(?P<to_index>\d+)/$', views.home_rest, name='home_rest'),
    url(r'(.*?)/?rss.xml$', cache_page(PlogFeed(), 60 * 60)),
    url('^search$', views.search, name='search'),
    url('^About$', lambda x: HttpResponsePermanentRedirect('/about/')),
    url('^about$', views.about, name='about'),
    url('^about2$', views.about2, name='about2'),
    url('^about3$', views.about3, name='about3'),
    url('^contact$', views.contact, name='contact'),
    url('^oc-(.*)', views.home, name='only_category'),
    url('^zitemap.xml$', views.sitemap, name='sitemap'),
    url('^humans.txt$', views.humans_txt, name='humans_txt'),
    url('^(.*)', views.blog_post_by_alias, name='blog_post_by_alias'),
)
