# vim: fileencoding=utf-8:

# NOTE: this file does *not* import unicode_literals,
# so the assertion message is actually just utf-8 bytes


def test():
    assert False, "ä"
