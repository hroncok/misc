import codecs
import locale
import os
import sys
import time
import unittest


PY3 = (sys.version_info >= (3,))
FREEBSD = sys.platform.startswith('freebsd')
FEBRUARY = time.localtime(time.mktime((2018, 2, 1, 12, 0, 0, 0, 0, 0)))
AUGUST = time.localtime(time.mktime((2018, 8, 1, 12, 0, 0, 0, 0, 0)))


if not PY3:
    ascii = repr


class Tests(unittest.TestCase):
    def setUp(self):
        self.encoding = None
        self.loc = None

    def tearDown(self):
        self.encoding = None

    def set_locale(self, loc, encoding):
        self.loc = loc
        self.encoding = encoding
        try:
            locale.setlocale(locale.LC_ALL, loc)
        except locale.Error as err:
            self.skipTest("setlocale(LC_ALL, %r) failed: %s" % (loc, err))
        codeset = locale.nl_langinfo(locale.CODESET)
        self.assertEqual(codecs.lookup(codeset).name,
                         codecs.lookup(encoding).name)

    def assertLocaleEqual(self, value, expected):
        if isinstance(value, bytes):
            value = value.decode(self.encoding)
        self.assertEqual(value, expected, (ascii(value), ascii(expected), self.encoding))

    def test_fr_FR_iso8859_1(self):
        # Linux, Fedora 27, glibc 2.27
        loc = "fr_FR.ISO8859-1" if FREEBSD else "fr_FR"
        self.set_locale(loc, "ISO-8859-1")
        lc = locale.localeconv()
        if FREEBSD:
            self.assertLocaleEqual(lc['mon_thousands_sep'], u'\xa0')
            self.assertLocaleEqual(lc['thousands_sep'], u'\xa0')
            self.assertLocaleEqual(os.strerror(2), u'Fichier ou r\xe9pertoire inexistant')
        self.assertLocaleEqual(time.strftime('%B', FEBRUARY), u'f\xe9vrier')
        self.assertLocaleEqual(time.strftime('%B', AUGUST), u'ao\xfbt')

    def test_fr_FR_utf8(self):
        # Linux, Fedora 27, glibc 2.27
        loc = "fr_FR.UTF-8" if FREEBSD else "fr_FR.utf8"
        self.set_locale(loc, "UTF-8")
        self.assertLocaleEqual(locale.localeconv()['currency_symbol'], u'\u20ac')
        if FREEBSD:
            self.assertLocaleEqual(locale.localeconv()['mon_thousands_sep'], u'\xa0')
            self.assertLocaleEqual(locale.localeconv()['thousands_sep'], u'\xa0')
        self.assertLocaleEqual(time.strftime('%B', FEBRUARY), u'f\xe9vrier')
        self.assertLocaleEqual(time.strftime('%B', AUGUST), u'ao\xfbt')

    def test_ru_RU(self):
        if FREEBSD:
            # FreeBSD 11
            loc = "ru_RU.ISO8859-5"
            currency_symbol = u'\u0440\u0443\u0431.'
            february = u'\u0444\u0435\u0432\u0440\u0430\u043b\u044f'
        else:
            # Linux, Fedora 27, glibc 2.27
            loc = "ru_RU"
            currency_symbol = u'\u0440\u0443\u0431'
            february = u'\u0424\u0435\u0432\u0440\u0430\u043b\u044c'
        self.set_locale(loc, "ISO-8859-5")
        lc = locale.localeconv()
        self.assertLocaleEqual(lc['currency_symbol'], currency_symbol)
        self.assertLocaleEqual(lc['mon_thousands_sep'], u'\xa0')
        self.assertLocaleEqual(lc['thousands_sep'], u'\xa0')
        self.assertLocaleEqual(time.strftime('%B', FEBRUARY), february)

    def test_ru_RU_koi8r(self):
        if FREEBSD:
            # FreeBSD 11.0
            loc = "ru_RU.KOI8-R"
            currency_symbol = u'\u0440\u0443\u0431.'
            february = u'\u0444\u0435\u0432\u0440\u0430\u043b\u044f'
        else:
            # Linux, Fedora 27, glibc 2.27
            loc = "ru_RU.koi8r"
            currency_symbol = u'\u0440\u0443\u0431'
            february = u'\u0424\u0435\u0432\u0440\u0430\u043b\u044c'
        self.set_locale(loc, "KOI8-R")
        lc = locale.localeconv()
        self.assertLocaleEqual(lc['currency_symbol'], currency_symbol)
        self.assertLocaleEqual(lc['mon_thousands_sep'], u'\xa0')
        self.assertLocaleEqual(lc['thousands_sep'], u'\xa0')
        self.assertLocaleEqual(time.strftime('%B', FEBRUARY),
                               february)
        if FREEBSD:
            self.assertLocaleEqual(os.strerror(2),
                                   u'\u041d\u0435\u0442 \u0442\u0430\u043a\u043e\u0433\u043e '
                                   u'\u0444\u0430\u0439\u043b\u0430 \u0438\u043b\u0438 '
                                   u'\u043a\u0430\u0442\u0430\u043b\u043e\u0433\u0430')

    def test_ru_RU_utf8(self):
        if FREEBSD:
            # FreeBSD 11.0
            loc = "ru_RU.UTF-8"
            currency_symbol = u'\u0440\u0443\u0431.'
            february = u'\u0444\u0435\u0432\u0440\u0430\u043b\u044f'
        else:
            # Linux, Fedora 27, glibc 2.27
            loc = "ru_RU.utf8"
            currency_symbol = u'\u20bd'
            february = u'\u0424\u0435\u0432\u0440\u0430\u043b\u044c'

        self.set_locale(loc, "UTF-8")
        lc = locale.localeconv()
        self.assertLocaleEqual(lc['currency_symbol'], currency_symbol)
        self.assertLocaleEqual(lc['mon_thousands_sep'], u'\xa0')
        self.assertLocaleEqual(lc['thousands_sep'], u'\xa0')
        self.assertLocaleEqual(time.strftime('%B', FEBRUARY), february)


if __name__ == '__main__':
    unittest.main()
