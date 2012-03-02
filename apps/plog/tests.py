import re
import datetime
from django.core.urlresolvers import reverse
from django.conf import settings
from django.test import TestCase
from apps.plog.models import BlogItem, BlogComment, Category
from apps.plog.utils import utc_now
from apps.redisutils import get_redis_connection


class PlogTestCase(TestCase):
    def setUp(self):
        redis = get_redis_connection()
        redis.flushdb()

    def test_blog_post_caching(self):
        blog = BlogItem.objects.create(
          oid='some-longish-test-post',
          title='TITLEX',
          text='BLABLABLA',
          display_format='structuredtext',
          pub_date=utc_now() - datetime.timedelta(seconds=10),
        )
        url = reverse('blog_post', args=[blog.oid])

        import apps.plog.views
        old_render = apps.plog.views.render
        from django.shortcuts import render as django_render
        render_counts = []
        def mocked_render(*a, **k):
            render_counts.append(1)
            return django_render(*a, **k)
        apps.plog.views.render = mocked_render
        try:
            response = self.client.get(url)
            self.assertTrue(blog.title in response.content)
            assert '0 comments' in response.content
            response = self.client.get(url)
            assert '0 comments' in response.content

            comment1 = BlogComment.objects.create(
              comment="textext",
              blogitem=blog,
              approved=True,
              add_date=utc_now() + datetime.timedelta(seconds=1),
            )
            response = self.client.get(url)
            assert '1 comment' in response.content
        finally:
            apps.plog.views.render = old_render

        assert len(render_counts) == 2

    def test_text_rendering_with_images(self):
        blog = BlogItem.objects.create(
          oid='myoid',
          title='TITLEX',
          text="""
          "image.png":/plog/myoid/image.png
          and *this*
          """,
          display_format='structuredtext',
          pub_date=utc_now() - datetime.timedelta(seconds=10),
        )
        url = reverse('blog_post', args=[blog.oid])
        response = self.client.get(url)
        content = response.content.split('id="post"')[1].split('</section')[0]
        self.assertTrue('<em>this</em>' in content)
        regex_str = ('%sCACHE-\d+%s' %
                     (settings.STATIC_URL, re.escape('/plog/myoid/image.png')))

        self.assertTrue(re.findall(regex_str, content))

        old = settings.STATIC_URL
        settings.STATIC_URL = '//some.cdn.com/'
        try:
            blog.text_rendered = ''
            blog.save()
            response = self.client.get(url)
            content = response.content.split('id="post"')[1].split('</section')[0]
            regex_str = ('%sCACHE-\d+%s' %
                     (settings.STATIC_URL, re.escape('/plog/myoid/image.png')))
            self.assertTrue(re.findall(regex_str, content))
        finally:
            settings.STATIC_URL = old
