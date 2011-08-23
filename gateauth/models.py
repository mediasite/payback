# -*- coding: UTF-8 -*-

from django.db import models
from django.contrib.auth.models import User
import string
import random
import hashlib
from datetime import datetime
import time

def randstring_creator(count):
    def _randstring():
        a =  string.ascii_letters + string.digits
        return ''.join([random.choice(a) for _ in xrange(count)])

    return _randstring


class HashKey(models.Model):
    user = models.OneToOneField(User, max_length=20, verbose_name=u'Пользователь', unique=True)
    signature = models.CharField(max_length=20, unique=True, default=randstring_creator(20))

    @staticmethod
    def date2utc2str(date):
        return u''.join((unicode(date.year), unicode(date.month), unicode(date.day), unicode(date.hour)))

    @staticmethod
    def get_token(params, salt, date=u''):
        items = sorted(params.iteritems())
        hash = u'&'.join([u'='.join((unicode(k), unicode(v))) for k, v in items])
        date = date or HashKey.date2utc2str(datetime.now())

        #прибаляем дату в формате UTC2 и применяем sha1
        hash = hashlib.sha1(u''.join((hash, date))).hexdigest()
        #добавляем ключ и применяем sha1
        hash = hashlib.sha1(u''.join((hash, salt))).hexdigest()

        return unicode(hash)

    @staticmethod
    def tokens_range(start, stop, params, salt):



        if not isinstance(start, int) \
            or not isinstance(stop, int) \
            or not isinstance(params, dict) \
            or not isinstance(salt, basestring):

            raise TypeError

        fromtimestamp = datetime.fromtimestamp
        timestamp = time.time()

        utc2_dates = [HashKey.date2utc2str(fromtimestamp(timestamp + 3600*i))  for i in xrange(start, stop+1)]
        tokens = [HashKey.get_token(params, salt, date) for date in utc2_dates]

        return tokens

    def __unicode__(self):
        return u'%s (partner)' % self.name

class IPRange(models.Model):
    ip_from = models.IPAddressField()
    ip_to = models.IPAddressField(blank=True, null=True)
<<<<<<< HEAD
    hash_key = models.ForeignKey(HashKey, db_index=True, related_name='ips_allowed')
=======
    user = models.ForeignKey(User, db_index=True, related_name='ips_allowed')
>>>>>>> ea3426dd617b050d74ce6818d4566382d50c2f47

    @staticmethod
    def _ipv4_to_int(ip):
        hexn = ''.join(["%02X" % long(i) for i in ip.split('.')])
        return long(hexn, 16)

    def in_range(self, ip_str):
        if self.ip_to:
            return IPRange._ipv4_to_int(self.ip_from) <= IPRange._ipv4_to_int(ip_str) <= IPRange._ipv4_to_int(
                self.ip_to)

        return ip_str == self.ip_from