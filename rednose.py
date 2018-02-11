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

from __future__ import print_function
import os
import sys
import linecache
import re

import nose
import termstyle

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


failure = 'FAILED'
error = 'ERROR'
success = 'passed'
skip = 'skipped'
expected_failure = 'expected failure'
unexpected_success = 'unexpected success'
line_length = 77


class RedNose(nose.plugins.Plugin):
    # In order to color multiprocess output it has to have a higher score.
    score = 1001
    env_opt = 'NOSE_REDNOSE'
    env_opt_color = 'NOSE_REDNOSE_COLOR'
    env_opt_hide_skips = 'NOSE_REDNOSE_HIDE_SKIPS'

    def __init__(self, *args):
        super(RedNose, self).__init__(*args)
        self.enabled = False

    def options(self, parser, env=os.environ):
        rednose_on_env_value = env.get(self.env_opt, False)
        rednose_hide_skips_env_value = env.get(self.env_opt_hide_skips, False)

        rednose_on = bool(rednose_on_env_value) if rednose_on_env_value not in ['false', '0'] else False
        rednose_hide_skips = bool(rednose_hide_skips_env_value) if rednose_hide_skips_env_value not in ['false', '0'] else False
        rednose_color = env.get(self.env_opt_color, 'auto')

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
        parser.add_option(
            "--full-file-path",
            action="store_true",
            default=False,
            help="print the full file path as opposed to the one relative to your directory (default)"
        )
        parser.add_option(
            "--hide-skips",
            action="store_true",
            default=rednose_hide_skips,
            help="Hide the error printing for skip cases (default is to show them)"
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
            self.full_file_path = options.full_file_path
            self.hide_skips = options.hide_skips

    def prepareTestResult(self, result):  # noqa
        """Required to prevent others from monkey patching the add methods."""
        return result

    def prepareTestRunner(self, runner):  # noqa
        stream = runner.stream
        if os.name == 'nt':
            import colorama
            stream = colorama.initialise.wrap_stream(stream, convert=True, strip=False, autoreset=False, wrap=True)
        return ColourTestRunner(stream=stream, descriptions=runner.descriptions, verbosity=runner.verbosity, config=runner.config, immediate=self.immediate, use_relative_path=not self.full_file_path, hide_skips=self.hide_skips)


class ColourTestRunner(nose.core.TextTestRunner):

    def __init__(self, stream, descriptions, verbosity, config, immediate, use_relative_path, hide_skips):
        super(ColourTestRunner, self).__init__(stream=stream, descriptions=descriptions, verbosity=verbosity, config=config)
        self.immediate = immediate
        self.use_relative_path = use_relative_path
        self.hide_skips = hide_skips

    def _makeResult(self):  # noqa
        return ColourTextTestResult(self.stream, self.descriptions, self.verbosity, self.config, immediate=self.immediate, use_relative_path=self.use_relative_path, hide_skips=self.hide_skips)


class ColourTextTestResult(nose.result.TextTestResult):
    """
    A test result class that prints colour formatted text results to the stream.
    """

    def __init__(self, stream, descriptions, verbosity, config, errorClasses=None, immediate=False, use_relative_path=False, hide_skips=False):  # noqa
        super(ColourTextTestResult, self).__init__(stream=stream, descriptions=descriptions, verbosity=verbosity, config=config, errorClasses=errorClasses)
        self.has_test_ids = getattr(config.options, "enable_plugin_id", False)
        if self.has_test_ids:
            self.ids = self.get_test_ids(self.config.options.testIdFile)
        self.total = 0
        self.immediate = immediate
        self.use_relative_path = use_relative_path
        self.hide_skips = hide_skips
        self.test_failures_and_exceptions = []
        self.error = self.success = self.failure = self.skip = self.expected_failure = self.unexpected_success = 0
        self.verbose = config.verbosity >= 2
        self.short_status_map = {
            failure: 'F',
            error: 'E',
            skip: '-',
            expected_failure: "X",
            unexpected_success: "U",
            success: '.',
        }
        self.skips = []

    def get_test_ids(self, test_id_file):
        """Returns a mapping of test to id if one exists, else an empty dictionary."""
        try:
            with open(test_id_file, 'rb') as fh:
                try:
                    from cPickle import load
                except ImportError:
                    from pickle import load
                data = load(fh)

            return dict((address, _id) for _id, address in data["ids"].items())
        except (IOError, ValueError):
            return {}

    def printSummary(self, start, stop):  # noqa
        """Summarize all tests - the number of failures, errors and successes."""
        self._line(termstyle.black)
        self._out("%s test%s run in %0.3f seconds" % (self.total, self._plural(self.total), stop - start))
        if self.total > self.success:
            self._outln(". ")

            additionals = [
                {"color": termstyle.red, "count": self.failure, "message": "%s FAILED"},
                {"color": termstyle.yellow, "count": self.error, "message": "%s error%s" % ("%s", self._plural(self.error))},
                {"color": termstyle.blue, "count": self.skip, "message": "%s skipped"},
                {"color": termstyle.green, "count": self.expected_failure, "message": "%s expected_failures"},
                {"color": termstyle.cyan, "count": self.unexpected_success, "message": "%s unexpected_successes"},
            ]

            additionals_to_print = [
                additional["color"](additional["message"] % (additional["count"])) for additional in additionals if additional["count"] > 0
            ]

            self._out(', '.join(additionals_to_print))

        self._out(termstyle.green(" (%s test%s passed)" % (self.success, self._plural(self.success))))
        self._outln()

    def _plural(self, num):
        return '' if num == 1 else 's'

    def _line(self, color=termstyle.reset, char='-'):
        """
        Print a line of separator characters (default '-') in the given colour (default black).
        """
        self._outln(color(char * line_length))

    def _print_test(self, test, type_, color):
        self.total += 1
        if self.verbose:
            self._outln(color(type_))
        else:
            short_ = self.short_status_map.get(type_, ".")
            self._out(color(short_))
            if self.total % line_length == 0:
                self._outln()

    def _out(self, msg='', newline=False):
        try:
            self.stream.write(msg)
            self.stream.flush()
        except UnicodeEncodeError:
            self.stream.write(msg.encode('utf-8'))
            self.stream.flush()
        if newline:
            self.stream.write('\n')

    def _outln(self, msg=''):
        self._out(msg=msg, newline=True)

    def _generate_and_add_test_report(self, type_, test, err):
        report = self._report_test(len(self.test_failures_and_exceptions), type_, test, err)
        self.test_failures_and_exceptions.append(report)

    def addFailure(self, test, err):  # noqa
        self.failure += 1
        self._print_test(test, failure, termstyle.red)
        self._generate_and_add_test_report(failure, test, err)

    def addError(self, test, err):  # noqa
        if err[0].__name__ == 'SkipTest':
            self.addSkip(test, err)
            return
        self.error += 1
        self._print_test(test, error, termstyle.yellow)
        self._generate_and_add_test_report(error, test, err)

    def addSuccess(self, test):  # noqa
        self.success += 1
        self._print_test(test, success, termstyle.green)

    def addSkip(self, test, err):  # noqa
        if isinstance(err, Exception):
            err = (err.__class__, err, None)
        elif self.verbose:
            skip_message = "#{test_id} {test_location} ... ".format(
                test_id=self._get_id(test),
                test_location=getattr(test.context, "__file__", getattr(test.context, "__module__", None))
            )
            self._out(termstyle.reset(skip_message))
        self.skip += 1
        self._print_test(test, skip, termstyle.blue)
        if not self.hide_skips:
            self._generate_and_add_test_report(skip, test, err)

    def addExpectedFailure(self, test, err):  # noqa
        self.expected_failure += 1
        self._print_test(test, expected_failure, termstyle.green)

    def addUnexpectedSuccess(self, test):  # noqa
        self.unexpected_success += 1
        self._print_test(test, unexpected_success, termstyle.cyan)

    def _report_test(self, report_index_num, type_, test, err):  # noqa
        """report the results of a single (failing or errored) test"""
        exc_type, exc_instance, exc_trace = err

        if type_ == failure:
            color = termstyle.red
        elif type_ == skip:
            color = termstyle.blue
            exc_type = nose.SkipTest
        else:
            color = termstyle.yellow

        colored_error_text = [
            ''.join(self.format_traceback(exc_trace)),
            self._format_exception_message(exc_type, exc_instance, color)
        ]

        if type_ == failure:
            self.failures.append((test, colored_error_text))
            flavour = "FAIL"
        elif type_ == skip:
            self.skips.append((test, colored_error_text))
            flavour = "SKIP"
        else:
            self.errors.append((test, colored_error_text))
            flavour = "ERROR"

        test_id = self._get_id(test)

        if self.immediate:
            self._outln()
            self._printError(flavour, test, colored_error_text, test_id, True)

        return (test_id, flavour, test, colored_error_text)

    def _get_id(self, test):
        report_index_num = len(self.test_failures_and_exceptions)
        if self.has_test_ids:
            try:
                test_id = self.ids.get(test.address(), self.total)
            except AttributeError:
                test_id = report_index_num + 1
        else:
            test_id = report_index_num + 1
        return test_id

    def format_traceback(self, tb):
        if tb is not None:
            ret = [termstyle.default("   Traceback (most recent call last):")]
        else:
            ret = [termstyle.default("   No Traceback")]

        current_trace = tb
        while current_trace is not None:
            line = self._format_traceback_line(current_trace)
            if line is not None:
                ret.append(line)
            current_trace = current_trace.tb_next
        return '\n'.join(ret)

    def _format_traceback_line(self, tb):
        """
        Formats the file / lineno / function line of a traceback element.

        Returns None is the line is not relevent to the user i.e. inside the test runner.
        """
        if self._is_relevant_tb_level(tb):
            return None

        f = tb.tb_frame
        filename = f.f_code.co_filename
        lineno = tb.tb_lineno
        linecache.checkcache(filename)
        function_name = f.f_code.co_name

        line_contents = linecache.getline(filename, lineno, f.f_globals).strip()

        return "    %s line %s in %s\n      %s" % (
            termstyle.blue(self._relative_path(filename) if self.use_relative_path else filename),
            termstyle.bold(termstyle.cyan(lineno)),
            termstyle.cyan(function_name),
            line_contents
        )

    def _format_exception_message(self, exception_type, exception_instance, message_color):
        """Returns a colorized formatted exception message."""
        orig_message_lines = to_unicode(exception_instance).splitlines()

        if len(orig_message_lines) == 0:
            return ''
        exception_message = orig_message_lines[0]

        message_lines = [message_color('   ', termstyle.bold(message_color(exception_type.__name__)), ": ") + message_color(exception_message)]
        for line in orig_message_lines[1:]:
            match = re.match('^---.* begin captured stdout.*----$', line)
            if match:
                message_color = termstyle.magenta
                message_lines.append('')
            line = '   ' + line
            message_lines.append(message_color(line))
        return '\n'.join(message_lines)

    def _relative_path(self, path):
        """
        Returns the relative path of a file to the current working directory.

        If path is a child of the current working directory, the relative
        path is returned surrounded.
        If path is not a child of the working directory, path is returned
        """
        try:
            here = os.path.abspath(os.path.realpath(os.getcwd()))
            fullpath = os.path.abspath(os.path.realpath(path))
        except OSError:
            return path
        if fullpath.startswith(here):
            return fullpath[len(here) + 1:]
        return path

    def printErrors(self):  # noqa
        if not self.verbose:
            self._outln()
        if self.immediate:
            self._outln()
            for x in range(0, 4):
                self._outln()

            self._outln(termstyle.green("TEST RESULT OUTPUT:"))

        for (test_id, flavour, test, coloured_output_lines) in (self.test_failures_and_exceptions):
            self._printError(flavour=flavour, test=test, coloured_output_lines=coloured_output_lines, test_id=test_id)

        # Copied from the parent function.
        self._outln()
        for cls in self.errorClasses.keys():
            storage, label, isfail = self.errorClasses[cls]
            if isfail:
                self.printErrorList(label, storage)
        # Might get patched into a result with no config
        if hasattr(self, 'config'):
            self.config.plugins.report(self.stream)

    def _printError(self, flavour, test, coloured_output_lines, test_id, is_mid_test=False):  # noqa
        if flavour == "FAIL":
            color = termstyle.red
        elif flavour == "SKIP":
            color = termstyle.blue

        else:
            color = termstyle.yellow

        self._outln(color(self.separator1))
        self._outln(color("%s) %s: %s" % (test_id, flavour, self.getDescription(test))))
        self._outln(color(self.separator2))

        for err_line in coloured_output_lines:
            self._outln("%s" % err_line)

        if is_mid_test:
            self._outln(color(self.separator2))
