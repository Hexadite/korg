import sys
import regex
import glob
import os

here = lambda x: os.path.abspath(os.path.join(os.path.dirname(__file__), x))

class PatternRepo(object):
    def __init__(self, folders, import_korg_patterns=True, pattern_dict={}):
        if import_korg_patterns:
            folders.append(here('../patterns'))
        self.pattern_dict = self._load_patterns(folders, pattern_dict)

    def compile_regex(self, pattern, flags=0):
        """Compile regex from pattern and pattern_dict"""
        pattern_graph = PatternGraph(self.pattern_dict)
        if pattern_graph.has_cycles():
            raise Exception("Cycle found in pattern dictionary for pattern '%s'" % pattern_graph.cycle_key)
        pattern_re = regex.compile("(?P<substr>%\{(?P<fullname>(?P<patname>\w+)(?::(?P<subname>\w+))?)\})")
        while 1:
            matches = [md.groupdict() for md in pattern_re.finditer(pattern)]
            if len(matches) == 0:
                break
            for md in matches:
                if self.pattern_dict.has_key(md['patname']):
                    if md['subname']:
                        # TODO error if more than one occurance
                        if '(?P<' in self.pattern_dict[md['patname']]:
                            # this is not part of the original logstash implementation 
                            # but it might be usefull to be able to replace the 
                            # group name used in the pattern
                            repl = regex.sub('\(\?P<(\w+)>', '(?P<%s>' % md['subname'],
                                self.pattern_dict[md['patname']], 1)
                        else:
                            repl = '(?P<%s>%s)' % (md['subname'], 
                                self.pattern_dict[md['patname']])
                    else:
                        repl = self.pattern_dict[md['patname']]
                    # print "Replacing %s with %s"  %(md['substr'], repl)
                    pattern = pattern.replace(md['substr'],repl)
                else:
                    raise KeyError("Pattern '%s' not in pattern dictionary" % md['patname'])
        # print 'pattern: %s' % pattern
        return regex.compile(pattern, flags)


    def _load_pattern_file(self, filename, pattern_dict):
        pattern_re = regex.compile("^(?P<patname>\w+) (?P<pattern>.+)$")
        with open(filename) as f:
            lines = f.read().splitlines()
        for line in lines:
            m = pattern_re.search(line)
            if m:
                md = m.groupdict()
                pattern_dict[md['patname']] = md['pattern']


    def _load_patterns(self, folders, pattern_dict={}):
        """Load all pattern from all the files in folders"""
        # print 'folders: %s' % folders
        for folder in folders:
            for file in os.listdir(folder):
                if regex.match(r'^[\w-]+$', file):
                    self._load_pattern_file(os.path.join(folder, file), pattern_dict)
        return pattern_dict


class PatternGraph(object):
    """ Create a graph from a pattern dict to check for cyclic patterns """

    def __init__(self, pattern_dict):
        self.build_nodes(pattern_dict)

    def build_nodes(self, pattern_dict):
        """ Build adjancency map """
        pattern_re = regex.compile("(?P<substr>%\{(?P<fullname>(?P<patname>\w+)(?::(?P<subname>\w+))?)\})")
        self.nodes = {}
        for patname in pattern_dict:
            matches = [md.groupdict() for md in pattern_re.finditer(pattern_dict[patname])]
            if len(matches) == 0:
                continue
            if not self.nodes.has_key(patname):
                    self.nodes[patname] = {"in": [], "out": []}
            for md in matches:
                if not pattern_dict.has_key(md['patname']):
                    continue
                if not self.nodes.has_key(md['patname']):
                    self.nodes[md['patname']] = {"in": [], "out": []}
                self.nodes[patname]["out"].append(md['patname'])
                self.nodes[md['patname']]["in"].append(patname)
        return self.nodes

    def has_cycles(self):
        leaf_nodes = []
        # collect leaf nodes (no incoming edge)
        for n in self.nodes:
            if not len(self.nodes[n]["in"]):
                leaf_nodes.append(n)
        # Remove empty leaf nodes
        while len(leaf_nodes):
            n = leaf_nodes.pop(0)
            for m in self.nodes[n]["out"]:
                self.nodes[m]["in"] = [v for v in self.nodes[m]["in"] if v != n]
                if not len(self.nodes[m]["in"]):
                    leaf_nodes.append(m)
            self.nodes[n]["out"] = []
        # If any node connection is left, we have a circular graph
        for n in self.nodes:
            if len(self.nodes[n]["in"]) or len(self.nodes[n]["out"]):
                self.cycle_key = n
                return True
        return False

if __name__ == '__main__':
    print load_patterns(['../patterns'])
