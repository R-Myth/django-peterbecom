from django.conf.urls.defaults import patterns, include, url
#from feeds import BustFeed

import views
urlpatterns = patterns('',
    url('^$', views.plog_index, name='plog_index'),
    url('^add/$', views.add, name='plog_add'),
    url('^add/preview$', views.preview_post, name='plog_preview_post'),
    url('^new-comments$', views.new_comments, name='new_comments'),
    url('^prepare.json$', views.prepare_json, name='prepare'),
    url('^preview.json$', views.preview_json, name='preview'),
    url('^(.*)/submit$', views.submit_json, name='submit'),
    url('^(.*)/approve/(.*)', views.approve_comment, name='approve_comment'),
    url('^(.*)/delete/(.*)', views.delete_comment, name='delete_comment'),
    url('^(.*)', views.blog_post, name='blog_post'),
)
