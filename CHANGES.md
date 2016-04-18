## Change Log

List of Rednose releases and changes, with the latest at the top:

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

