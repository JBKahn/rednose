# -*- coding: utf-8 -*-

import os
import sys
import unittest

import nose
from nose.plugins import PluginTester, testid
from six import PY2, PY3

from rednose import RedNose


try:
    from unittest import skip, skipUnless
except ImportError:
    def skip(f):
        return lambda self: None

    def skipUnless(condition, reason):  # noqa
        if condition:
            return lambda x: x
        else:
            return lambda x: None


class TestRedNoseWithId(PluginTester, unittest.TestCase):
    activate = '--rednose'
    plugins = [RedNose(), testid.TestId()]
    args = ['--force-color', '--with-id']
    env = {}

    def test_colored_result(self):
        expected_lines = [
            '\x1b[33mE\x1b[0m',
            '\x1b[33m======================================================================\x1b[0m',
            '\x1b[33m1) ERROR: runTest (test_files.basic_test_suite.TC)\x1b[0m',
            '\x1b[33m----------------------------------------------------------------------\x1b[0m',
            '\x1b[0m   Traceback (most recent call last):\x1b[0m',
            '    \x1b[34mtest_files/basic_test_suite.py\x1b[0m line \x1b[1m\x1b[36m6\x1b[0m\x1b[0m in \x1b[36mrunTest\x1b[0m',
            '      raise ValueError("I hate fancy stuff")',
            '\x1b[33m   \x1b[33m\x1b[1m\x1b[33mValueError\x1b[0m\x1b[0m\x1b[33m: \x1b[0m\x1b[33mI hate fancy stuff\x1b[0m',
            '',
            '\x1b[30m-----------------------------------------------------------------------------\x1b[0m',
            '1 test run in',
            '\x1b[33m1 error\x1b[0m\x1b[32m (0 tests passed)\x1b[0m',
            '',
        ]
        for expected_line, actual_line in zip(expected_lines, str(self.output).split("\n")):
            if expected_line not in actual_line:
                print(expected_line)
                print(actual_line)
                print(self.output)
            self.assertTrue(expected_line in actual_line)

    def makeSuite(self):  # noqa
        from test_files.basic_test_suite import TC
        return [TC('runTest')]


class TestRedNose(PluginTester, unittest.TestCase):
    activate = '--rednose'
    plugins = [RedNose()]
    args = ['--force-color']
    env = {}

    def test_colored_result(self):
        expected_lines = [
            '\x1b[33mE\x1b[0m',
            '\x1b[33m======================================================================\x1b[0m',
            '\x1b[33m1) ERROR: runTest (test_files.basic_test_suite.TC)\x1b[0m',
            '\x1b[33m----------------------------------------------------------------------\x1b[0m',
            '\x1b[0m   Traceback (most recent call last):\x1b[0m',
            '    \x1b[34mtest_files/basic_test_suite.py\x1b[0m line \x1b[1m\x1b[36m6\x1b[0m\x1b[0m in \x1b[36mrunTest\x1b[0m',
            '      raise ValueError("I hate fancy stuff")',
            '\x1b[33m   \x1b[33m\x1b[1m\x1b[33mValueError\x1b[0m\x1b[0m\x1b[33m: \x1b[0m\x1b[33mI hate fancy stuff\x1b[0m',
            '',
            '\x1b[30m-----------------------------------------------------------------------------\x1b[0m',
            '1 test run in',
            '\x1b[33m1 error\x1b[0m\x1b[32m (0 tests passed)\x1b[0m',
            '',
        ]
        for expected_line, actual_line in zip(expected_lines, str(self.output).split("\n")):
            if expected_line not in actual_line:
                print(expected_line)
                print(actual_line)
                print(self.output)
            self.assertTrue(expected_line in actual_line)

    def makeSuite(self):  # noqa
        from test_files.basic_test_suite import TC
        return [TC('runTest')]


@skipUnless(sys.version_info >= (2, 7), "python 2.6 not supported")
class TestRedNoseSkipInClass(PluginTester, unittest.TestCase):
    activate = '--rednose'
    plugins = [RedNose()]
    args = ['--force-color']
    env = {}
    suitepath = os.path.join(os.getcwd(), 'test_files', 'class_test_failure.py')

    def test_colored_result(self):
        expected_lines = [
            '\x1b[34m-\x1b[0m',
            '\x1b[34m======================================================================\x1b[0m',
            "\x1b[34m1) SKIP: test suite for <module 'test_files.class_test_failure' from '{0}/test_files/class_test_failure.py".format(os.getcwd()),
            '\x1b[34m----------------------------------------------------------------------\x1b[0m',
            '\x1b[0m   Traceback (most recent call last):\x1b[0m',
            '    \x1b[34m{0}/suite.py\x1b[0m line \x1b[1m\x1b[36m'.format(nose.__path__[0]),
            '      self.setUp()',
            '    \x1b[34m{0}/suite.py\x1b[0m line \x1b[1m\x1b[36m'.format(nose.__path__[0]),
            '      self.setupContext(ancestor)',
            '    \x1b[34m{0}/suite.py\x1b[0m line \x1b[1m\x1b[36m'.format(nose.__path__[0]),
            '      try_run(context, names)',
            '    \x1b[34m{0}/util.py\x1b[0m line \x1b[1m\x1b[36m'.format(nose.__path__[0]),
            '      return func()',
            '    \x1b[34mtest_files/class_test_failure.py\x1b[0m line \x1b[1m\x1b[36m6\x1b[0m\x1b[0m in \x1b[36msetup_module\x1b[0m',
            "      raise unittest.SkipTest('RESI specific Nonius libs not present')",
            '\x1b[34m   \x1b[34m\x1b[1m\x1b[34mSkipTest\x1b[0m\x1b[0m\x1b[34m: \x1b[0m\x1b[34mRESI specific Nonius libs not present\x1b[0m',
            '',
            '\x1b[30m-----------------------------------------------------------------------------\x1b[0m',
            '1 test run in ',
            '\x1b[34m1 skipped\x1b[0m\x1b[32m (0 tests passed)\x1b[0m',
            '',
        ]
        for expected_line, actual_line in zip(expected_lines, str(self.output).split("\n")):
            if expected_line not in actual_line:
                print(expected_line)
                print(actual_line)
                print(self.output)
            self.assertTrue(expected_line in actual_line)


@skipUnless(sys.version_info >= (2, 7), "python 2.6 not supported")
class TestRedNoseSampleTests(PluginTester, unittest.TestCase):
    activate = '--rednose'
    plugins = [RedNose()]
    args = ['--force-color']
    env = {}
    suitepath = os.path.join(os.getcwd(), 'test_files', 'sample_test.py')

    def test_colored_result(self):
        expected_lines = [
            '\x1b[33mE\x1b[0m\x1b[31mF\x1b[0m\x1b[34m-\x1b[0m\x1b[34m-\x1b[0m\x1b[32m.\x1b[0m\x1b[31mF\x1b[0m',
            '\x1b[33m======================================================================\x1b[0m',
            '\x1b[33m1) ERROR: test_error (test_files.sample_test.SomeTest)\x1b[0m',
            '\x1b[33m----------------------------------------------------------------------\x1b[0m',
            '\x1b[0m   Traceback (most recent call last):\x1b[0m',
            '    \x1b[34mtest_files/sample_test.py\x1b[0m line \x1b[1m\x1b[36m20\x1b[0m\x1b[0m in \x1b[36mtest_error\x1b[0m',
            '      raise RuntimeError("things went south\\nand here\'s a second line!")',
            '\x1b[33m   \x1b[33m\x1b[1m\x1b[33mRuntimeError\x1b[0m\x1b[0m\x1b[33m: \x1b[0m\x1b[33mthings went south\x1b[0m',
            "\x1b[33m   and here's a second line!\x1b[0m",
            '\x1b[31m======================================================================\x1b[0m',
            '\x1b[31m2) FAIL: test_fail (test_files.sample_test.SomeTest)\x1b[0m',
            '\x1b[31m----------------------------------------------------------------------\x1b[0m',
            '\x1b[0m   Traceback (most recent call last):\x1b[0m',
            '    \x1b[34mtest_files/sample_test.py\x1b[0m line \x1b[1m\x1b[36m14\x1b[0m\x1b[0m in \x1b[36mtest_fail\x1b[0m',
            "      delay_fail(lambda: self.fail('no dice'))",
            '    \x1b[34mtest_files/sample_test.py\x1b[0m line \x1b[1m\x1b[36m8\x1b[0m\x1b[0m in \x1b[36mdelay_fail\x1b[0m',
            '      f()  # fail it!',
            '    \x1b[34mtest_files/sample_test.py\x1b[0m line \x1b[1m\x1b[36m14\x1b[0m\x1b[0m in \x1b[36m<lambda>\x1b[0m',
            "      delay_fail(lambda: self.fail('no dice'))",
            '\x1b[31m   \x1b[31m\x1b[1m\x1b[31mAssertionError\x1b[0m\x1b[0m\x1b[31m: \x1b[0m\x1b[31mno dice\x1b[0m',
            '\x1b[34m======================================================================\x1b[0m',
            '\x1b[34m3) SKIP: test_skip (test_files.sample_test.SomeTest)\x1b[0m',
            '\x1b[34m----------------------------------------------------------------------\x1b[0m',
            '\x1b[0m   No Traceback\x1b[0m',
            '',
            '\x1b[34m======================================================================\x1b[0m',
            '\x1b[34m4) SKIP: test_skip_with_reason (test_files.sample_test.SomeTest)\x1b[0m',
            '\x1b[34m----------------------------------------------------------------------\x1b[0m',
            '\x1b[0m   No Traceback\x1b[0m',
            "\x1b[34m   \x1b[34m\x1b[1m\x1b[34mSkipTest\x1b[0m\x1b[0m\x1b[34m: \x1b[0m\x1b[34mLook at me, I'm skipping for a reason!!\x1b[0m",
            '\x1b[31m======================================================================\x1b[0m',
            "\x1b[31m5) FAIL: It's got a long description, you see?.\x1b[0m",
            '\x1b[31m----------------------------------------------------------------------\x1b[0m',
            '\x1b[0m   Traceback (most recent call last):\x1b[0m',
            '    \x1b[34mtest_files/sample_test.py\x1b[0m line \x1b[1m\x1b[36m32\x1b[0m\x1b[0m in \x1b[36mtest_with_long_description\x1b[0m',
            '      self.fail()', '\x1b[31m   \x1b[31m\x1b[1m\x1b[31mAssertionError\x1b[0m\x1b[0m\x1b[31m: \x1b[0m\x1b[31mNone\x1b[0m',
            '',
            "\x1b[34m6) SKIP: test suite for <class 'test_files.sample_test.TestBug'>\x1b[0m",
            '\x1b[34m----------------------------------------------------------------------\x1b[0m',
            '\x1b[0m   Traceback (most recent call last):\x1b[0m',
            'nose/suite.py\x1b[0m line',
            '      self.setUp()',
            'nose/suite.py\x1b[0m line',
            '      self.setupContext(ancestor)',
            'nose/suite.py\x1b[0m line',
            '      try_run(context, names)',
            'nose/util.py\x1b[0m line',
            '      return func()',
            '    \x1b[34mtest_files/sample_test.py\x1b[0m line \x1b[1m\x1b[36m39\x1b[0m\x1b[0m in \x1b[36msetUpClass\x1b[0m',
            '      raise nose.SkipTest("SKIPPING!")',
            '\x1b[34m   \x1b[34m\x1b[1m\x1b[34mSkipTest\x1b[0m\x1b[0m\x1b[34m: \x1b[0m\x1b[34mSKIPPING!\x1b[0m',
            '',
            '\x1b[30m-----------------------------------------------------------------------------\x1b[0m',
            '7 tests run in ',
            '\x1b[31m2 FAILED\x1b[0m, \x1b[33m1 error\x1b[0m, \x1b[34m3 skipped\x1b[0m\x1b[32m (1 test passed)\x1b[0m',
            ''
        ]
        if PY2:
            import sys
            if sys.version_info[1] == 6:
                expected_lines = expected_lines[:8] + expected_lines[10:]

        for expected_line, actual_line in zip(expected_lines, str(self.output).split("\n")):
            if expected_line not in actual_line:
                print(expected_line)
                print(actual_line)
                print(self.output)
            self.assertTrue(expected_line in actual_line)


class TestRedNoseEncoding(PluginTester, unittest.TestCase):
    activate = '--rednose'
    plugins = [RedNose()]
    args = ['--force-color']
    env = {}
    suitepath = os.path.join(os.getcwd(), 'test_files', 'encoding_test.py')

    def setUp(self):
        import sys
        self.old_encoding = sys.getdefaultencoding()
        if PY2:
            reload(sys)
            sys.setdefaultencoding('utf8')
        super(TestRedNoseEncoding, self).setUp()

    def tearDown(self):
        import sys
        if PY2:
            reload(sys)
            sys.setdefaultencoding(self.old_encoding)
        super(TestRedNoseEncoding, self).tearDown()

    def test_colored_result(self):
        expected_lines = [
            '\x1b[31mF\x1b[0m',
            '\x1b[31m======================================================================\x1b[0m',
            '\x1b[31m1) FAIL: test_files.encoding_test.test\x1b[0m',
            '\x1b[31m----------------------------------------------------------------------\x1b[0m',
            '\x1b[0m   Traceback (most recent call last):\x1b[0m',
            '    \x1b[34m{0}/case.py\x1b[0m line \x1b[1m\x1b[36m'.format(nose.__path__[0]),
            '      self.test(*self.arg)',
            '    \x1b[34mtest_files/encoding_test.py\x1b[0m line \x1b[1m\x1b[36m8\x1b[0m\x1b[0m in \x1b[36mtest\x1b[0m',
            '      assert False, "\xc3\xa4"',
            '\x1b[31m   \x1b[31m\x1b[1m\x1b[31mAssertionError\x1b[0m\x1b[0m\x1b[31m: \x1b[0m\x1b[31m\xc3\xa4\x1b[0m',
            '',
            '\x1b[30m-----------------------------------------------------------------------------\x1b[0m',
            '1 test run in ',
            '\x1b[31m1 FAILED\x1b[0m\x1b[32m (0 tests passed)\x1b[0m',
            ''
        ]

        if PY3:
            pass
            expected_lines[8] = '      assert False, "ä"'
            expected_lines[9] = '\x1b[31m   \x1b[31m\x1b[1m\x1b[31mAssertionError\x1b[0m\x1b[0m\x1b[31m: \x1b[0m\x1b[31mä\x1b[0m'

        for expected_line, actual_line in zip(expected_lines, str(self.output).split("\n")):
            if expected_line not in actual_line:
                print(expected_line)
                print(actual_line)
                print(self.output)
            self.assertTrue(expected_line in actual_line)


class TestRedNoseEncodingWithLiterals(PluginTester, unittest.TestCase):
    activate = '--rednose'
    plugins = [RedNose()]
    args = ['--force-color']
    env = {}
    suitepath = os.path.join(os.getcwd(), 'test_files', 'encoding_test_with_literals.py')

    def setUp(self):
        import sys
        self.old_encoding = sys.getdefaultencoding()
        if PY2:
            reload(sys)
            sys.setdefaultencoding('utf8')
        super(TestRedNoseEncodingWithLiterals, self).setUp()

    def tearDown(self):
        import sys
        if PY2:
            reload(sys)
            sys.setdefaultencoding(self.old_encoding)
        super(TestRedNoseEncodingWithLiterals, self).tearDown()

    def test_colored_result(self):
        expected_lines = [
            '\x1b[31mF\x1b[0m',
            '\x1b[31m======================================================================\x1b[0m',
            '\x1b[31m1) FAIL: test_utf8 (test_files.encoding_test_with_literals.EncodingTest)\x1b[0m',
            '\x1b[31m----------------------------------------------------------------------\x1b[0m',
            '\x1b[0m   Traceback (most recent call last):\x1b[0m',
            '    \x1b[34mtest_files/encoding_test_with_literals.py\x1b[0m line \x1b[1m\x1b[36m9\x1b[0m\x1b[0m in \x1b[36mtest_utf8\x1b[0m',
            "      self.assertEqual('caf\xc3\xa9', 'abc')",
            "\x1b[31m   \x1b[31m\x1b[1m\x1b[31mAssertionError\x1b[0m\x1b[0m\x1b[31m: \x1b[0m\x1b[31mu'caf\\xe9' != u'abc'\x1b[0m",
            '\x1b[31m   - caf\xc3\xa9\x1b[0m',
            '\x1b[31m   + abc\x1b[0m',
            '',
            '\x1b[30m-----------------------------------------------------------------------------\x1b[0m',
            '1 test run in ',
            '\x1b[31m1 FAILED\x1b[0m\x1b[32m (0 tests passed)\x1b[0m',
            ''
        ]

        if PY3:
            expected_lines[6] = "      self.assertEqual('café', 'abc')"
            expected_lines[7] = "\x1b[31m   \x1b[31m\x1b[1m\x1b[31mAssertionError\x1b[0m\x1b[0m\x1b[31m: \x1b[0m\x1b[31m'café' != 'abc'\x1b[0m"
            expected_lines[8] = "\x1b[31m   - café\x1b[0m"
        elif PY2:
            import sys
            if sys.version_info[1] == 6:
                expected_lines = expected_lines[:8] + expected_lines[10:]

        for expected_line, actual_line in zip(expected_lines, str(self.output).split("\n")):
            if expected_line not in actual_line:
                print(expected_line)
                print(actual_line)
                print(self.output)
            self.assertTrue(expected_line in actual_line)
