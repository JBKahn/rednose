# Copyright (c) 2009, Tim Cuthbertson 
# All rights reserved.
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

failure = 'fail'
error = 'error'
success = 'success'
line_length = 77

class DevNull(object):
	def write(self, msg): pass
	def writeln(self, msg=''): pass
	
class RedNose(nose.plugins.Plugin):
	env_opt = 'NOSE_REDNOSE'
	env_opt_color = 'NOSE_REDNOSE_COLOR'
	reports = []
	error = success = failure = 0
	total = 0
	stream = None
	verbose = False
	enabled = False
	score = 600
	
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
		color_mode = options.rednose_color
		auto() # enable colours if stdout is a tty
		if color_mode:
			color_mode = color_mode.lower()
			if color_mode == 'on':
				enable()
			elif color_mode == 'off':
				disable()
		self.verbose = options.verbosity >= 2
	
	def begin(self):
		self.start_time = time.time()
	
	def beforeTest(self, test):
		if self.verbose:
			self._out(str(test) + ' ... ')
	
	def _print_test(self, type_, color):
		self.total += 1
		if type_ == failure:
			short_ = 'F'
			long_ = 'FAILED'
		elif type_ == error:
			short_ = 'X'
			long_ = 'ERROR'
		else:
			short_ = '.'
			long_ = 'passed'

		if self.verbose:
			self._outln(color(long_))
		else:
			self._out(color(short_))
			if self.total % line_length == 0:
				self._outln()
		
	def addFailure(self, test, err):
		self.failure += 1
		self.reports.append((failure, test, err))
		self._print_test(failure, red)
	
	def addError(self, test, err):
		self.error += 1
		self.reports.append((error, test, err))
		self._print_test(error, yellow)
		
	def addSuccess(self, test):
		self.success += 1
		self._print_test(success, green)

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
		self._out("%s reports run (in %0.1f seconds)" % (self.total, time.time() - self.start_time))
		if self.total > self.success:
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

