import os
import sys
import traceback
import linecache

import nose

from termstyle import *

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
	
	def _fmt_traceback(self, trace):
		def relative(path):
			# self.out(path)
			_here = os.path.abspath(os.path.realpath(os.getcwd()))
			_path = os.path.abspath(os.path.realpath(path))
			if _path.startswith(_here):
				return bold(_path[len(_here)+1:])
			return path
		def file_line(tb):
			prefix = "file://"
			prefix=""

			f = tb.tb_frame
			filename = f.f_code.co_filename
			lineno = tb.tb_lineno
			linecache.checkcache(filename)
			function_name = f.f_code.co_name
			
			if '__unittest' in f.f_globals:
				return None
			
			line_contents = linecache.getline(filename, lineno, f.f_globals).strip()

			return "    %s line %s in %s\n      %s" % (
				blue(prefix, relative(filename)),
				bold(lineno),
				cyan(function_name),
				line_contents)

		ret = []
		ret.append(black("   Traceback (most recent call last):"))
		current_trace = trace
		while current_trace is not None:
			line = file_line(current_trace)
			if line is not None:
				ret.append(line)
			current_trace = current_trace.tb_next
		return '\n'.join(ret)
	
	def _report_test(self, type_, test, err):
		self.line(black)
		self._report_num += 1
		self.out("%s) " % (self._report_num))
		if type_ == failure:
			color = red
			self.outln(color('FAIL: %s' % (test,)))
		else:
			color = yellow
			self.outln(color('ERROR: %s' % (test,)))
		
		exc_type, exc_instance, exc_trace = err
		self.outln(color('   ', bold(color(exc_type.__name__)), ": ", exc_instance))
		self.outln()
		self.outln(self._fmt_traceback(exc_trace))
		
		self.outln
	
	def report(self, stream):
		self.outln()
		self._report_num = 0
		if len(self.reports) > 0:
			for report in self.reports:
				self._report_test(*report)
			self.outln()
		
		self.line(black)
		self.out("%s reports run" % self.total)
		if self.total == self.success:
			self.out(" successfully")
		else:
			self.outln(". ")
			if self.failure > 0:
				self.out(red("%s FAILED%s" % (
					self.failure,
					self.plural(self.failure),
				)))
				if self.error > 0:
					self.out(", ")
			if self.error > 0:
				self.out(yellow("%s error%s" % (self.error, self.plural(self.error))))
			self.out(green(" (%s test%s passed)" % (self.success, self.plural(self.success))))
		self.outln()
		return False
		
	def setOutputStream(self, stream):
		if not isinstance(stream, DevNull):
			self.stream = stream
		return DevNull()


# useful: http://somethingaboutorange.com/mrl/projects/nose/doc/plugin_interface.html
