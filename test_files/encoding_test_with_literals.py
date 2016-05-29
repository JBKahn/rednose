# vim: fileencoding=utf-8:
from __future__ import unicode_literals

import unittest


class EncodingTest(unittest.TestCase):
    def test_utf8(self):
        self.assertEqual('café', 'abc')
