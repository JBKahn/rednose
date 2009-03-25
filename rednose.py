import nose
import sys
from termstyle import *
from nose.inspector import inspect_traceback

failure = 'fail'
error = 'error'
line_length = 77

class DevNull(object):
	def write(self, msg): pass
	def writeln(self, msg=''): pass
	
class RedNose(nose.plugins.Plugin):
	def __init__(self, *a, **k):
		self.reports = []
		self.error = self.success = self.failure = 0
		self.total = 0
		self.stream = None
		super(self.__class__, self).__init__(*a, **k)
		
	def _fmt(self, test, exc_info, c1, c2, c3):
		error_cls, error, trace = exc_info
		this_trace = trace
		# while this_trace is not None:
		# 	this_trace.tb_frame.f_code.co_filename = yellow(this_trace.tb_frame.f_code.co_filename)
		# 	this_trace = this_trace.tb_next
		
		return (c1(error_cls.__name__), c2(error.message), trace)
		
	def formatFailure(self, test, exc_info):
		return self._fmt(test, exc_info, red, yellow, white)
	
	def formatError(self, test, exc_info):
		return self._fmt(test, exc_info, blue, yellow, white)

	def print_test(self, char, color):
		self.total += 1
		self.out(color(char))
		if self.total % line_length == 0:
			self.outln()
		
	def addFailure(self, test, err):
		self.failure += 1
		self.reports.append((failure, test, err))
		self.print_test('F', red)
	
	def addError(self, test, err):
		self.error += 1
		self.reports.append((error, test, err))
		self.print_test('X', yellow)
		
	def addSuccess(self, test):
		self.success += 1
		self.print_test('.', green)
	
	def out(self, msg='', newline=False):
		self.stream.write(msg)
		if newline:
			self.stream.write('\n')

	def outln(self, msg=''):
		self.out(msg, True)
	
	def plural(self, num):
		return '' if num == 1 else 's'
	
	def line(self, color=reset, char='-'):
		self.outln(color(char * line_length))
	
	def report(self, stream):
		self.outln()
		if len(self.reports) > 0:
			self.line(black, char='=')
			self.outln("REPORTY!")
			self.outln()
		
		self.line(black)
		self.out("%s reports run" % self.total)
		if self.total == self.success:
			self.out(" successfully")
		else:
			self.outln(". ")
			if self.error > 0:
				self.out(red("%s error%s" % (self.error, self.plural(self.error))))
				if self.failure > 0:
					self.out(", ")
			if self.failure > 0:
				self.out(yellow("%s failure%s" % (self.failure, self.plural(self.error))))
			self.out(green(" (%s passed)" % (self.success,)))
		self.outln()
		return False
		
	def setOutputStream(self, stream):
		if not isinstance(stream, DevNull):
			self.stream = stream
		return DevNull()


# useful: http://somethingaboutorange.com/mrl/projects/nose/doc/plugin_interface.html
