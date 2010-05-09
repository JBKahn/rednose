# Copyright (c) 2009, Tim Cuthbertson # All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#     * Neither the name of the organisation nor the names of its
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
# WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import os
import sys
import traceback
import linecache
import re
import time

import nose

from termstyle import *

failure = 'FAILED'
error = 'ERROR'
success = 'passed'
skip = 'skipped'
line_length = 77

class DevNull(object):
	def write(self, msg): pass
	def writeln(self, msg=''): pass
	def flush(self): pass
	
class RedNose(nose.plugins.Plugin):
	env_opt = 'NOSE_REDNOSE'
	env_opt_color = 'NOSE_REDNOSE_COLOR'
	score = 600
	
	def __init__(self, *args):
		super(type(self), self).__init__(*args)
		self.reports = []
		self.error = self.success = self.failure = self.skip = 0
		self.total = 0
		self.stream = None
		self.verbose = False
		self.enabled = False
		
	
	def options(self, parser, env=os.environ):
		parser.add_option(
			"--rednose", action="store_true",
			default=env.get(self.env_opt), dest="rednose",
			help="More readable (and pretty!) coloured output")
		parser.add_option(
			"--rednose-color", action="store", type="string",
			default=env.get(self.env_opt_color), dest="rednose_color",
			help="enable/disable rednose colour (on|off|auto)")

	def configure(self, options, conf):
		if options.rednose:
			self.enabled = True
		else:
			return
		color_mode = options.rednose_color
		try:
			auto() # enable colours if stdout is a tty
		except TypeError: # happens when stdout is closed - rednose is not much good when that happens
			self.enabled = False
			return
		if color_mode:
			color_mode = color_mode.lower()
			if color_mode == 'on':
				enable()
			elif color_mode == 'off':
				disable()
		self.verbose = options.verbosity >= 2
	
	def begin(self):
		self.start_time = time.time()
		self._in_test = False
	
	def _format_test_name(self, test):
		return test.test.shortDescription() or str(test)
	
	def beforeTest(self, test):
		if self._in_test:
			self.addSkip()
		self._in_test = True
		if self.verbose:
			self._out(self._format_test_name(test) + ' ... ')

	def _print_test(self, type_, color):
		self.total += 1
		if self.verbose:
			self._outln(color(type_))
		else:
			if type_ == failure:
				short_ = 'F'
			elif type_ == error:
				short_ = 'X'
			elif type_ == skip:
				short_ = '-'
			else:
				short_ = '.'
			self._out(color(short_))
			if self.total % line_length == 0:
				self._outln()
		self._in_test = False
		
	def addFailure(self, test, err):
		self.failure += 1
		self.reports.append((failure, test, err))
		self._print_test(failure, red)
	
	def addError(self, test, err):
		if err[0].__name__ == 'SkipTest':
			self.addSkip(test, err)
			return
		self.error += 1
		self.reports.append((error, test, err))
		self._print_test(error, yellow)
		
	def addSuccess(self, test):
		self.success += 1
		self._print_test(success, green)
	
	def addSkip(self, test=None, err=None):
		self.skip += 1
		self._print_test(skip, blue)

	def setOutputStream(self, stream):
		if not isinstance(stream, DevNull):
			self.stream = stream
		return DevNull()
	
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
		self._out("%s test%s run in %0.1f seconds" % (
			self.total,
			self._plural(self.total),
			time.time() - self.start_time))
		if self.total > self.success:
			self._outln(". ")
			additionals = []
			if self.failure > 0:
				additionals.append(red("%s FAILED" % (
					self.failure,)))
			if self.error > 0:
				additionals.append(yellow("%s error%s" % (
					self.error,
					self._plural(self.error) )))
			if self.skip > 0:
				additionals.append(blue("%s skipped" % (
					self.skip)))
			self._out(', '.join(additionals))
				
		self._out(green(" (%s test%s passed)" % (
			self.success,
			self._plural(self.success) )))
		self._outln()
	
	def _report_test(self, report_num, type_, test, err):
		"""report the results of a single (failing or errored) test"""
		self._line(black)
		self._out("%s) " % (report_num))
		if type_ == failure:
			color = red
			self._outln(color('FAIL: %s' % (self._format_test_name(test),)))
		else:
			color = yellow
			self._outln(color('ERROR: %s' % (self._format_test_name(test),)))
		
		exc_type, exc_instance, exc_trace = err
		
			
		self._outln()
		self._outln(self._fmt_traceback(exc_trace))
		self._out(color('   ', bold(color(exc_type.__name__)), ": "))
		self._outln(self._fmt_message(exc_instance, color))
		self._outln()
		
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

		if len(orig_message_lines) == 0:
			return ''
		message_lines = [color(orig_message_lines[0])]
		for line in orig_message_lines[1:]:
			match = re.match('^---.* begin captured stdout.*----$', line)
			if match:
				color = None
				message_lines.append('')
			line = '   ' + line
			message_lines.append(color(line) if color is not None else line)
		return '\n'.join(message_lines)

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

