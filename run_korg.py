from korg import korg
from korg import pattern

if __name__ == '__main__':
	# load the pattern map
	pm = pattern.load_patterns(['./patterns/'])
	lg = korg.LineGrokker('%{COMBINEDAPACHELOG}', pm)

	# now grok the apache access log
	with open("/home/mark/devel/aogaeru/korg/research/access_petsy_2013_php.log.1") as infile:
	    for line in infile:
	        lg.grok(line)
