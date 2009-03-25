import unittest

class SomeTest(unittest.TestCase):
	def test_fail(self):
		self.fail('no dice')
	
	def test_success(self):
		self.assertEqual(True, True)
	
	def test_error(self):
		raise RuntimeError("things went south")


