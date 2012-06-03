import datetime
from django.core.urlresolvers import reverse
from django.test import TestCase
from apps.plog.models import BlogItem, BlogComment, Category
from apps.plog.utils import utc_now
from django.test import TestCase
from django.conf import settings
from django.template.loader import render_to_string
from django.template import Context
from django.core.urlresolvers import reverse


class HomepageTestCase(TestCase):

    def test_homepage_cache_rendering(self):
        url = reverse('home')

        blog1 = BlogItem.objects.create(
          title='TITLE1',
          text='BLABLABLA',
          display_format='structuredtext',
          pub_date=utc_now() - datetime.timedelta(seconds=10),
        )
        comment1 = BlogComment.objects.create(
          comment="textext",
          blogitem=blog1,
          approved=True,
        )

        comment2 = BlogComment.objects.create(
          comment="tuxtuxt",
          blogitem=blog1,
          approved=True,
        )

        response = self.client.get(url)
        self.assertTrue('TITLE1' in response.content)
        self.assertTrue('2 comments' in response.content)

        blog1.title = 'TUTLE1'
        blog1.save()
        response = self.client.get(url)
        self.assertTrue('TUTLE1' in response.content)

        blog2 = BlogItem.objects.create(
          title='TATLE2',
          text='BLEBLE',
          display_format='structuredtext',
          pub_date=utc_now() - datetime.timedelta(seconds=1),
        )

        response = self.client.get(url)
        self.assertTrue('TATLE2' in response.content)
        self.assertTrue('0 comments' in response.content)
        self.assertTrue('TUTLE1' in response.content)
        self.assertTrue('2 comments' in response.content)

        # by categories only
        cat1 = Category.objects.create(
          name='CATEGORY1',
        )
        cat2 = Category.objects.create(
          name='CATEGORY2',
        )
        blog1.categories.add(cat1)
        blog1.save()
        blog2.categories.add(cat2)
        blog2.save()

        response = self.client.get(url)
        self.assertTrue('CATEGORY1' in response.content)
        self.assertTrue('CATEGORY2' in response.content)

        url = reverse('only_category', args=['CATEGORY2'])
        response = self.client.get(url)
        self.assertTrue('CATEGORY1' not in response.content)
        self.assertTrue('CATEGORY2' in response.content)

        url = reverse('only_category', args=['CATEGORY1'])
        response = self.client.get(url)
        self.assertTrue('CATEGORY1' in response.content)
        self.assertTrue('CATEGORY2' not in response.content)

        for i in range(2, 21):
            BlogItem.objects.create(
              title='TITLE-%s' % i,
              text='BLEBLE',
              display_format='structuredtext',
              pub_date=utc_now() - datetime.timedelta(seconds=20 + i),
            )

        url = reverse('home')
        response = self.client.get(url)
        assert '?page=2' in response.content
        visible_titles = []
        not_visible_titles = []
        for item in BlogItem.objects.all():
            if item.title in response.content:
                visible_titles.append(item.title)
            else:
                not_visible_titles.append(item.title)

        response = self.client.get(url, {'page': 2})
        for each in visible_titles[:10]:
            assert each not in response.content
        for each in not_visible_titles[:10]:
            assert each in response.content
        assert '?page=1' in response.content
        assert '?page=3' in response.content


    def test_render_to_string(self):
        assert not settings.DEBUG
        reverse('home')
        context = {'name': 'Peter'}
        html = render_to_string('homepage/test.html', context)
        assert 'Name:Peter' in html

        ccontext = Context(context)
        html = render_to_string('homepage/test.html', context_instance=ccontext)
        assert 'Name:Peter' in html
        assert 'main.css' not in html


class TestTView(TestCase):

    def test_sample_get(self):
        url = reverse('testview')
        r = self.client.get(url)
        assert r.status_code == 200
        assert 'hi!' in r.content
        assert 'text/html' in r['content-type']
        assert 'charset=utf-8' in r['content-type'].lower()

    def test_sample2_get(self):
        url = reverse('testview2')
        r = self.client.get(url)
        assert r.status_code == 200
        assert '<h1>hi!</h1>' in r.content
        assert 'text/html' in r['content-type']
        assert 'charset=utf-8' in r['content-type'].lower()

    def test_sample2_post(self):
        url = reverse('testview2')
        r = self.client.post(url, {'a': 10, 'b': 20})
        assert r.status_code == 200
        import json
        assert json.loads(r.content)['sum'] == 30
        assert 'text/html' in r['content-type']
        assert 'charset=utf-8' in r['content-type'].lower()

    def test_cached_view_get(self):
        url = reverse('cachedview')
        r = self.client.get(url)
        first = r.content
        from time import sleep
        sleep(0.01)
        r = self.client.get(url)
        second = r.content
        assert second == first

    def test_login_required_view_get(self):
        url = reverse('loginrequiredview')
        r = self.client.get(url)
        assert r.status_code == 302

        from django.contrib.auth.models import User
        user = User()
        user.username = 'peter'
        user.set_password('secret')
        user.save()

        assert self.client.login(username='peter', password='secret')
        r = self.client.get(url)
        assert r.status_code == 200
        assert 'Secret' in r.content

    def test_advanced_cached_view(self):
        url = reverse('advancedcachedview')
        r = self.client.get(url)
        first = r.content
        from time import sleep
        sleep(0.01)
        r = self.client.get(url)
        second = r.content
        assert second == first
