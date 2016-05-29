from __future__ import print_function
import unittest


def setup_module():
    raise unittest.SkipTest('RESI specific Nonius libs not present')
    print(__name__, ': setup_module() ~~~~~~~~~~~~~~~~~~~~~~')


def teardown_module():
    print(__name__, ': teardown_module() ~~~~~~~~~~~~~~~~~~~')


class SomeSkippedTest(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        print(__name__, ': TestClass.setup_class() ----------')

    @classmethod
    def teardown_class(cls):
        print(__name__, ': TestClass.teardown_class() -------')

    def setup(self):
        print(__name__, ': TestClass.setup()  - - - - - - - -')

    def teardown(self):
        print(__name__, ': TestClass.teardown() - - - - - - -')

    def test_method_1(self):
        print(__name__, ': TestClass.test_method_1()')

    def test_method_2(self):
        print(__name__, ': TestClass.test_method_2()')
