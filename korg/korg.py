import sys
import regex  # compared to re this implements the full regex spec like atomic grouping
from pattern import PatternRepo

class LineGrokker(object):
    # TODO: can't say if this is a useful interface. Please provide feedback on any thoughts.
    def __init__(self, pattern, pattern_repo):
        self.regex = pattern_repo.compile_regex(pattern)

    def grok(self, data, find_all=False):
        m = self.regex.search(data)
        if m:
            if not find_all:
                return m.capturesdict()
            else:
                res = []
                res.append(m.capturesdict())
                pos = m.span()[1]
                x = self.regex.search(data[pos:])
                while x:
                    res.append(x.capturesdict())
                    pos += x.span()[1]
                    x = self.regex.search(data[pos:])
                return res

    def find_all(self, data):
        return map(lambda x: {"position": x.start(), "value": x.group()}, self.regex.finditer(data))

if __name__ == "__main__":
    GLOBALPM = {
        'HOST': '[\w+\._-]+',
        'PORT': '\d+',
        'PROG': '\w+',
        'USER': '\w+',
    }
    pr = PatternRepo([], False, GLOBALPM)
    g = LineGrokker('%{HOST} %{PROG:progi}\[\d+\]: error: PAM: authentication error for %{USER} from %{HOST:SRC}', pr)

    print g.grok('HOST PROG[1234]: error: PAM: authentication error for USER from SRC')
