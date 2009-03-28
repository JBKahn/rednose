import unittest

def delay_fail(f):
	f() # fail it!

class SomeTest(unittest.TestCase):
	def test_fail(self):
		print "oh noes, it's gonna blow!"
		delay_fail(lambda: self.fail('no dice'))
	
	def test_success(self):
		self.assertEqual(True, True)
	
	def test_error(self):
		raise RuntimeError("things went south\nand here's a second line!")


