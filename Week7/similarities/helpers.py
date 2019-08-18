from nltk.tokenize import sent_tokenize


def lines(a, b):
    """Return lines in both a and b"""

    return list({l.rstrip() for l in a.split('\n') if l in b.split('\n')})


def sentences(a, b):
    """Return sentences in both a and b"""

    return list({s for s in sent_tokenize(a) if s in sent_tokenize(b)})


def substrings(a, b, n):
    """Return substrings of length n in both a and b"""

    a_substrings = set()
    for i in range(0, len(a) - n + 1):
        a_substrings.add(a[i:i+n].rstrip())
    b_substrings = set()
    for i in range(0, len(b) - n + 1):
        b_substrings.add(b[i:i+n].rstrip())

    return list(a_substrings & b_substrings)

