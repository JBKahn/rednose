import unittest

from nose.plugins import PluginTester, testid

from rednose import RedNose


class TestRedNose(PluginTester, unittest.TestCase):
    activate = '--rednose'
    plugins = [RedNose(), testid.TestId()]
    args = ['--force-color', '--with-id']
    env = {}

    def test_colored_result(self):
        expected_lines = [
            '\x1b[33mE\x1b[0m',
            '\x1b[33m======================================================================\x1b[0m',
            '\x1b[33m1) ERROR: runTest (new_tests.TC)\x1b[0m',
            '\x1b[33m----------------------------------------------------------------------\x1b[0m',
            '\x1b[0m   Traceback (most recent call last):\x1b[0m',
            '    \x1b[34mtest/new_tests.py\x1b[0m line \x1b[1m\x1b[36m36\x1b[0m\x1b[0m in \x1b[36mrunTest\x1b[0m',
            '      raise ValueError("I hate fancy stuff")',
            '\x1b[33m   \x1b[33m\x1b[1m\x1b[33mValueError\x1b[0m\x1b[0m\x1b[33m: \x1b[0m\x1b[33mI hate fancy stuff\x1b[0m',
            '',
            '\x1b[30m-----------------------------------------------------------------------------\x1b[0m',
            '1 test run in',
            '\x1b[33m1 error\x1b[0m\x1b[32m (0 tests passed)\x1b[0m',
            '',
        ]
        for expected_line, actual_line in zip(expected_lines, str(self.output).split("\n")):
            self.assertIn(expected_line, actual_line)

    def makeSuite(self):  # noqa
        class TC(unittest.TestCase):
            def runTest(self):  # noqa
                raise ValueError("I hate fancy stuff")
        return [TC('runTest')]
