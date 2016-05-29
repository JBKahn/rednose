## Change Log

List of Rednose releases and changes, with the latest at the top:
  * v1.2.1
    * In python 2.7+ label skips as skip tests.
    * Change skip test exception coloring to blue..

  * v1.1.1
    * Fix for immediate broken with recent release when I switched API ussage and removed an function.

  * v1.1.0
    * Update tests for better reporting
    * fix for errors during module setup (issue #1)
    * Better support for skips
    * Introduce proper printing for skipped tests as well as the ability to supress them using `--hide-skips`
    * Test with python 3.4

  * v1.0.0 - **[!] Major Changes [!]**
    * [!] This release completely changes the way in which color test results are printed. It now attmepts to override the code which nose uses to print results rather than to supress those results and print them seperatly.
    * [!] Package maintainer changes to JBKahn
    * Use travis for testing

