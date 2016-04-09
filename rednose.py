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
#            this software without specific prior written permission.
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

from __future__ import print_function
import os
import sys
import linecache
import re
import time
from unittest.util import strclass


colorama = None
if os.name == 'nt':
    import colorama
import nose
import termstyle

failure = 'FAILED'
error = 'ERROR'
success = 'passed'
skip = 'skipped'
expected_failure = 'expected failure'
unexpected_success = 'unexpected success'
line_length = 77

PY3 = sys.version_info[0] >= 3
if PY3:
    to_unicode = str
else:
    def to_unicode(s):
        try:
            return unicode(s)
        except UnicodeDecodeError:
            s = str(s)
            try:
                # try utf-8, the most likely case
                return unicode(s, 'UTF-8')
            except UnicodeDecodeError:
                # Can't decode, just use `repr`
                return unicode(repr(s))


REDNOSE_DEBUG = False


class RedNose(nose.plugins.Plugin):
    env_opt = 'NOSE_REDNOSE'
    env_opt_color = 'NOSE_REDNOSE_COLOR'
    score = 199  # just under the `coverage` module

    def __init__(self, *args):
        super(RedNose, self).__init__(*args)
        self.reports = []
        self.error = self.success = self.failure = self.skip = 0
        self.total = 0
        self.stream = None
        self.verbose = False
        self.enabled = False
        self.tree = False

    def options(self, parser, env=os.environ):
        global REDNOSE_DEBUG
        rednose_on = bool(env.get(self.env_opt, False))
        rednose_color = env.get(self.env_opt_color, 'auto')
        REDNOSE_DEBUG = bool(env.get('REDNOSE_DEBUG', False))

        parser.add_option(
            "--rednose",
            action="store_true",
            default=rednose_on,
            dest="rednose",
            help="enable colour output (alternatively, set $%s=1)" % (self.env_opt,)
        )
        parser.add_option(
            "--no-color",
            action="store_false",
            dest="rednose",
            help="disable colour output"
        )
        parser.add_option(
            "--force-color",
            action="store_const",
            dest='rednose_color',
            default=rednose_color,
            const='force',
            help="force colour output when not using a TTY (alternatively, set $%s=force)" % (self.env_opt_color,)
        )
        parser.add_option(
            "--immediate",
            action="store_true",
            default=False,
            help="print errors and failures as they happen, as well as at the end"
        )

    def configure(self, options, conf):
        if options.rednose:
            self.enabled = True
            termstyle_init = {
                'force': termstyle.enable,
                'off': termstyle.disable
            }.get(options.rednose_color, termstyle.auto)
            termstyle_init()

            self.immediate = options.immediate
            self.verbose = options.verbosity >= 2

    def prepareTestResult(self, result):
        """Required to prevent others from monkey patching the add methods."""
        return result

    def prepareTestRunner(self, runner):
        runner.immediate = self.immediate

        def _makeResult(self):
            return ColourTextTestResult(self.stream, self.descriptions, self.verbosity, self.config, immediate=self.immediate)

        import types
        runner._makeResult = types.MethodType(_makeResult, runner)
        return runner

    def setOutputStream(self, stream):
        self.stream = stream
        return self.stream


class ColourTextTestResult(nose.result.TextTestResult):
    """
    A test result class that prints colour formatted text results to the stream.
    """

    def __init__(self, stream, descriptions, verbosity, config, errorClasses=None, immediate=False):
        super(ColourTextTestResult, self).__init__(stream=stream, descriptions=descriptions, verbosity=verbosity, config=config, errorClasses=errorClasses)
        self.total = 0
        self.immediate = immediate
        self.reports = []
        self.error = self.success = self.failure = self.skip = 0
        self.verbose = config.verbosity >= 2

    def printSummary(self, start, stop):
        self._summarize(start, stop)

    def _summarize(self, start, stop):
        """Summarize all tests - the number of failures, errors and successes."""
        self._line(termstyle.black)
        self._out("%s test%s run in %0.3f seconds" % (
            self.total,
            self._plural(self.total),
            stop - start))
        if self.total > self.success:
            self._outln(". ")
            additionals = []
            if self.failure > 0:
                additionals.append(
                    termstyle.red("%s FAILED" % (self.failure,))
                )
            if self.error > 0:
                additionals.append(
                    termstyle.yellow("%s error%s" % (self.error, self._plural(self.error)))
                )
            if self.skip > 0:
                additionals.append(
                    termstyle.blue("%s skipped" % (self.skip))
                )
            self._out(', '.join(additionals))

        self._out(
            termstyle.green(
                " (%s test%s passed)" % (self.success, self._plural(self.success))
            )
        )
        self._outln()

    def _plural(self, num):
        return '' if num == 1 else 's'

    def _line(self, color=termstyle.reset, char='-'):
        """
        Print a line of separator characters (default '-') in the given colour (default black).
        """
        self._outln(color(char * line_length))

    def getShortDescription(self, test):
        doc_first_line = test.test.shortDescription()
        if self.descriptions and doc_first_line:
            return self.indent + doc_first_line
        return self.indent + test.test._testMethodName

    def getLongDescription(self, test):
        doc_first_line = test.test.shortDescription()
        if self.descriptions and doc_first_line:
            return '\n'.join((str(test), doc_first_line))
        return str(test)

    def getClassDescription(self, test):
        test_class = test.test.__class__
        doc = test_class.__doc__
        if self.descriptions and doc:
            return doc.split('\n')[0].strip()
        return strclass(test_class)

    def _print_test(self, type_, color):
        self.total += 1
        if self.verbose:
            self._outln(color(type_))
        else:
            if type_ == failure:
                short_ = 'F'
            elif type_ == error:
                short_ = 'E'
            elif type_ == skip:
                short_ = '-'
            elif type_ == expected_failure:
                short_ = "X"
            elif type_ == unexpected_success:
                short_ = "U"
            else:
                short_ = '.'

            self._out(color(short_))
            if self.total % line_length == 0:
                self._outln()

    def _out(self, msg='', newline=False):
        self.stream.write(msg)
        if newline:
            self.stream.write('\n')

    def _outln(self, msg=''):
        self._out(msg, True)

    def _add_report(self, report):
        failure_type, test, err = report
        self.reports.append(report)
        if self.immediate:
            self._outln()
        self._report_test(len(self.reports), *report)

    def addFailure(self, test, err):
        self.failure += 1
        self._print_test(failure, termstyle.red)
        self._add_report((failure, test, err))

    def addError(self, test, err):
        if err[0].__name__ == 'SkipTest':
            self.addSkip(test, err)
            return
        self.error += 1
        self._print_test(error, termstyle.yellow)
        self._add_report((error, test, err))

    def addSuccess(self, test):
        self.success += 1
        self._print_test(success, termstyle.green)

    def addSkip(self, test=None, err=None):
        self.skip += 1
        self._print_test(skip, termstyle.blue)

    def addExpectedFailure(self, test, err):
        self.expected_failure += 1
        self._print_test(expected_failure, termstyle.magenta)

    def addUnexpectedSuccess(self, test):
        self.unexpected_success += 1
        self._print_test(unexpected_success, termstyle.cyan)

    def _report_test(self, report_num, type_, test, err):
        """report the results of a single (failing or errored) test"""
        if type_ == failure:
            color = termstyle.red
        else:
            color = termstyle.yellow
        exc_type, exc_instance, exc_trace = err

        example = (
            self._fmt_traceback(exc_trace) +
            "\n" +
            color('   ', termstyle.bold(color(exc_type.__name__)), ": ") +
            self._fmt_message(exc_instance, color)
        )

        if type_ == failure:
            self.failures.append((test, example))
            flavour = "FAIL"
        else:
            self.errors.append((test, example))
            flavour = "ERROR"

        if self.immediate:
            self.printErrorList(flavour, [(test, example)])

    def _file_line(self, tb):
        """formats the file / lineno / function line of a traceback element"""
        prefix = "file://"
        prefix = ""

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
            termstyle.blue(prefix, self._relative_path(filename)),
            termstyle.bold(termstyle.cyan(lineno)),
            termstyle.cyan(function_name),
            line_contents)

    def _fmt_traceback(self, trace):
        """format a traceback"""
        ret = []
        ret.append(termstyle.default("   Traceback (most recent call last):"))
        current_trace = trace
        while current_trace is not None:
            line = self._file_line(current_trace)
            if line is not None:
                ret.append(line)
            current_trace = current_trace.tb_next
        return '\n'.join(ret)

    def _fmt_message(self, exception, color):
        orig_message_lines = to_unicode(exception).splitlines()

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

    def _relative_path(self, path):
        """
        If path is a child of the current working directory, the relative
        path is returned surrounded by bold xterm escape sequences.
        If path is not a child of the working directory, path is returned
        """
        try:
            here = os.path.abspath(os.path.realpath(os.getcwd()))
            fullpath = os.path.abspath(os.path.realpath(path))
        except OSError:
            return path
        if fullpath.startswith(here):
            return termstyle.bold(fullpath[len(here) + 1:])
        return path

    def printErrors(self):
        if self.immediate:
            for x in range(0, 5):
                self._outln()
        super(ColourTextTestResult, self).printErrors()

    def printErrorList(self, flavour, errors, is_mid_test=False):
        if not self.verbose:
            self._outln()
        if flavour == "FAIL":
            color = termstyle.red
        else:
            color = termstyle.yellow

        for test, err in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln(color("%s: %s" % (flavour, self.getDescription(test))))
            self.stream.writeln(self.separator2)
            self.stream.writeln("%s" % err)
