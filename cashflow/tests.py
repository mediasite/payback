#-*- coding: UTF-8 -*-
from decimal import Decimal
import json
from django.core.urlresolvers import reverse

from django.test import TestCase
from django.test.client import Client as InternetClient
from cashflow.models import *

class BaseRESTTest(TestCase):
    def setUp(self):
        user = User.objects.create_user('test', 'test', password='test')
        self.user = user

        client_user = Client(user=user)
        client_user.save()
        self.client_user = client_user

        self.payment_backend = PaymentBackend()
        self.payment_backend.save()
        self.cur = Currency(title='Ya money', code='YANDEX', payment_backend=self.payment_backend)
        self.cur.save()

        self.c = InternetClient()

    def post(self, params):
        return self.c.post(self.url, params)

    def tearDown(self):
        self.c.logout()
        self.client_user.delete()
        self.user.delete()
        self.payment_backend.delete()
        self.cur.delete()


class ListingTest(BaseRESTTest):
    def setUp(self):
        super(ListingTest, self).setUp()
        self.url = reverse('currs_list')

    def test_listing_in_model(self):
        listing = Currency.get_listing()
        self.assertTrue(self.cur.code in listing)

    def test_list_rest(self):
        annon_resp = self.post({})
        self.assertEqual(annon_resp.status_code, 403)

        self.c.login(username='test', password='test')
        logged_in_resp = self.c.post(self.url, {})
        o = json.loads(logged_in_resp.content)
        self.assertTrue(self.cur.code in o['currs_list'])


class CreatePaymentTest(BaseRESTTest):
    def setUp(self):
        super(CreatePaymentTest, self).setUp()
        self.url = reverse('create_payment')

    def test_create_payment_rest_annon403(self):
        annon_resp = self.c.post(self.url, {})
        self.assertEqual(annon_resp.status_code, 403)

    def login(self):
        self.c.login(username='test', password='test')

    def test_create_payment_rest_ok(self):
        self.login()
        # все четко
        params = {
            'amount': 42.50,
            'currency_code': self.cur.code,
            'comment': 'za gaz',
            'success_url': 'http://66.ru/success/',
            'fail_url': 'http://66.ru/fail/',
        }
        req = self.post(params)
        result = json.loads(req.content)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['payment_id'], 1)
        p = Payment.objects.get()
        self.assertEqual(p.amount, Decimal('42.5'))
        self.assertEqual(p.currency, self.cur)
        self.assertEqual(p.backend, self.payment_backend)
        self.assertEqual(p.client, self.client_user)


    def test_create_payment_rest_minimum(self):
        self.login()
        # все по минимуму
        params = {
            'amount': 42.50,
            'currency_code': self.cur.code,
        }
        req = self.post(params)
        result = json.loads(req.content)
        self.assertEqual(result['status'], 'ok')
        p = Payment.objects.get()
        self.assertEqual(p.amount, Decimal('42.5'))
        self.assertEqual(p.currency, self.cur)

        self.assertEqual(p.backend, self.payment_backend)
        self.assertEqual(p.client, self.client_user)
        self.assertEqual(p.comment, '')
        self.assertEqual(p.success_url, '')
        self.assertEqual(p.fail_url, '')

    def test_create_payment_rest_empty_form(self):
        self.login()
        # просто плохая форма
        params = {}
        req = self.post(params)
        result = json.loads(req.content)
        self.assertEqual(result['status'], 'invalid form')

    def test_create_payment_rest_silly_cur(self):
        self.login()
        # вариант со странной валютой
        params = {
            'amount': 42.50,
            'currency_code': 'PAPER',
        }
        req3 = self.post(params)
        result = json.loads(req3.content)
        self.assertEqual(result['status'], 'invalid form')

    def test_create_payment_negative_amount(self):
        self.login()
        # вариант с отрицательным числом
        params = {
            'amount': -200,
            'currency_code': self.cur.code,
        }
        req = self.post(params)
        result = json.loads(req.content)
        self.assertEqual(result['status'], 'invalid form')

    def test_create_payment_rest_str_price(self):
        self.login()
        # вариант со строкой вместо числа
        params = {
            'amount': 'yahrr!',
            'currency_code': self.cur.code,
        }
        req5 = self.post(params)
        result = json.loads(req5.content)
        self.assertEqual(result['status'], 'invalid form')
