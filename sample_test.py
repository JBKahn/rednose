# vim: set fileencoding=utf-8 :
from __future__ import print_function
import unittest

def delay_fail(f):
	f() # fail it!

class SomeTest(unittest.TestCase):
	def test_fail(self):
		print("oh noes, it's gonna blow!")
		delay_fail(lambda: self.fail('no dice'))
	
	def test_success(self):
		self.assertEqual(True, True)
	
	def test_error(self):
		raise RuntimeError("things went south\nand here's a second line!")

	def test_utf8(self):
		self.assertEqual(u'café', u'abc')
	
	def test_skip(self):
		import nose
		raise nose.SkipTest
	
	def test_with_long_description(self):
		"""It's got a long description, you see?"""
		self.fail()

