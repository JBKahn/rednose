## Change Log

List of Rednose releases and changes, with the latest at the top:
  * v1.3.0
    * Add `NOSE_REDNOSE_HIDE_SKIPS` environment variable.
    * Fix `NOSE_REDNOSE` environment variable.
    * Added LICENCE file

  * v1.2.3
    * Fix bug when switching between python 2 and 3 using node ids.
    * Added stream flush after every write to make sure dots are printed right after a test is executed.

  * v1.2.2
    * Fix bug for skips raised in setUpClass (issue #9).

  * v1.2.1
    * In python 2.7+ label skips as skip tests.
    * Change skip test exception coloring to blue..

  * v1.1.1
    * Fix for immediate broken with recent release when I switched API usage and removed an function.

  * v1.1.0
    * Update tests for better reporting
    * fix for errors during module setup (issue #1)
    * Better support for skips
    * Introduce proper printing for skipped tests as well as the ability to suppress them using `--hide-skips`
    * Test with python 3.4

  * v1.0.0 - **[!] Major Changes [!]**
    * [!] This release completely changes the way in which color test results are printed. It now attempts to override the code which nose uses to print results rather than to suppress those results and print them separately.
    * [!] Package maintainer changes to JBKahn
    * Use travis for testing
