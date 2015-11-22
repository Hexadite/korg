import regex  # compared to re this implements the full regex spec like atomic grouping
from pattern import PatternRepo


class LineGrokker(object):

    # TODO: can't say if this is a useful interface. Please provide feedback on any thoughts.
    def __init__(self, pattern, pattern_repo, flags=regex.IGNORECASE):
        self.regex = pattern_repo.compile_regex(pattern, flags)
        if self.regex.groups == 0:
            raise ValueError("No groups are defined in specified pattern: \"%s\"" % pattern)

    def grok(self, data, find_all=False):
        """
        Extract groups from data, returns dict if find_all=False. Otherwise if find_all=True keep searching until end
        of data, a list of dicts is returned for multiple matches.

        :param data: The text data to extract from.
        :type data: str
        :param find_all: True to keep iterating the data until reached EOF, False to return first captures.
        :type find_all: bool
        :rtype: list or dict or None
        """
        m = self.regex.search(data)
        if not m:
            return None

        if not find_all:
            # return first matches
            return m.capturesdict()

        res = [m.capturesdict()]
        # keep iterating until end of data
        while m.endpos < len(data):
            m = self.regex.search(data, m.endpos)
            if not m:
                break
            res.append(m.capturesdict())

        return res

    def find_all(self, data):
        """
        List of all matches and their positions in the text.

        :param data: The text to iterate.
        :type data: str
        :rtype: list of dict
        """
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

    try:
        g2 = LineGrokker(".*|test", pr)
        print g2.grok("this is a test of will", True)
    except ValueError as exc:
        print("validation check: %s" % exc)
