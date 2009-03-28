import os
import sys
import traceback
import linecache
import re

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
		
	def _print_test(self, char, color):
		self.total += 1
		self._out(color(char))
		if self.total % line_length == 0:
			self._outln()
		
	def addFailure(self, test, err):
		self.failure += 1
		self.reports.append((failure, test, err))
		self._print_test('F', red)
	
	def addError(self, test, err):
		self.error += 1
		self.reports.append((error, test, err))
		self._print_test('X', yellow)
		
	def addSuccess(self, test):
		self.success += 1
		self._print_test('.', green)
	
	def _out(self, msg='', newline=False):
		self.stream.write(msg)
		if newline:
			self.stream.write('\n')

	def _outln(self, msg=''):
		self._out(msg, True)
	
	def _plural(self, num):
		return '' if num == 1 else 's'
	
	def _line(self, color=reset, char='-'):
		"""
		print a line of separator characters (default '-')
		in the given colour (default black)
		"""
		self._outln(color(char * line_length))
	
	def _relative_path(self, path):
		"""
		If path is a child of the current working directory, the relative
		path is returned surrounded by bold xterm escape sequences.
		If path is not a child of the working directory, path is returned
		"""
		here = os.path.abspath(os.path.realpath(os.getcwd()))
		fullpath = os.path.abspath(os.path.realpath(path))
		if fullpath.startswith(here):
			return bold(fullpath[len(here)+1:])
		return path
	
	def _file_line(self, tb):
		"""formats the file / lineno / function line of a traceback element"""
		prefix = "file://"
		prefix=""

		f = tb.tb_frame
		if '__unittest' in f.f_globals:
			# this is the magical flag that prevents unittest internal
			# code from junking up the stacktrace
			return None

		filename = f.f_code.co_filename
		lineno = tb.tb_lineno
		linecache.checkcache(filename)
		function_name = f.f_code.co_name
		
		line_contents = linecache.getline(filename, lineno, f.f_globals).strip()

		return "    %s line %s in %s\n      %s" % (
			blue(prefix, self._relative_path(filename)),
			lineno,
			cyan(function_name),
			line_contents)
	
	def _fmt_traceback(self, trace):
		"""format a traceback"""
		ret = []
		ret.append(black("   Traceback (most recent call last):"))
		current_trace = trace
		while current_trace is not None:
			line = self._file_line(current_trace)
			if line is not None:
				ret.append(line)
			current_trace = current_trace.tb_next
		return '\n'.join(ret)
	
	def _fmt_message(self, exception, color):
		orig_message_lines = str(exception).splitlines()

		message_lines = [color(orig_message_lines[0])]
		for line in orig_message_lines[1:]:
			match = re.match('^---.* begin captured stdout.*----$', line)
			if match:
				color = None
				message_lines.append('')
			line = '   ' + line
			message_lines.append(color(line) if color is not None else line)
		return '\n'.join(message_lines)

	
	def _report_test(self, report_num, type_, test, err):
		"""report the results of a single (failing or errored) test"""
		self._line(black)
		self._out("%s) " % (report_num))
		if type_ == failure:
			color = red
			self._outln(color('FAIL: %s' % (test,)))
		else:
			color = yellow
			self._outln(color('ERROR: %s' % (test,)))
		
		exc_type, exc_instance, exc_trace = err
		
			
		self._outln()
		self._outln(self._fmt_traceback(exc_trace))
		self._out(color('   ', bold(color(exc_type.__name__)), ": "))
		self._outln(self._fmt_message(exc_instance, color))
		self._outln()
	
	def report(self, stream):
		"""report on all registered failures and errors"""
		self._outln()
		report_num = 0
		if len(self.reports) > 0:
			for report in self.reports:
				report_num += 1
				self._report_test(report_num, *report)
			self._outln()
		
		self._summarize()
		return False
	
	def _summarize(self):
		"""summarize all tests - the number of failures, errors and successes"""
		self._line(black)
		self._out("%s reports run" % self.total)
		if self.total == self.success:
			self._out(" successfully")
		else:
			self._outln(". ")
			if self.failure > 0:
				self._out(red("%s FAILED%s" % (
					self.failure,
					self._plural(self.failure) )))
				if self.error > 0:
					self._out(", ")
			if self.error > 0:
				self._out(yellow("%s error%s" % (
					self.error,
					self._plural(self.error) )))
			self._out(green(" (%s test%s passed)" % (
				self.success,
				self._plural(self.success) )))
		self._outln()
		
	def setOutputStream(self, stream):
		if not isinstance(stream, DevNull):
			self.stream = stream
		return DevNull()


#TODO: care about verbose setting
# useful: http://somethingaboutorange.com/mrl/projects/nose/doc/plugin_interface.html
