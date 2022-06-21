# TODO list
# -0 TODO read args
# -1 OK Read Corpus
# -2 TODO natural language processing
# -3 TODO create index
# -4 TODO print json with information


# DETAILED TODO LIST
# 1.FUTURE TODO cluster webpages in corpus

# 2.1 OK create file at designated location
# 2.2 TODO not rely entirely on available memory to produce index
# 2.3 OK tokenize text
# 2.4 TODO stemming (portuguese)
# 2.5 TODO stopword removal (portuguese)
# 2.6 TODO parallelization policy
# 2.FUTURE compression policy
# 2.FUTURE other languages

# 3.1 OK save words
# 3.3 TODO save url 
# 3.3.1 OK encode url
# 3.3.2 OK decode url
# 3.2 OK save positions in which the words are
# 3.3 TODO save positions from different url
# 3.FUTURE better way to save url, integer to string takes more space than string


# Local import
import indexer_utils as ut
import static_defines as static

# External import
import sys
import resource
import argparse
import time





rsrc = resource.RLIMIT_AS
#rsrc = resource.RLIMIT_DATA
#rsrc = resource.RLIMIT_RSS
#rsrc = resource.RLIMIT_STACK

def memory_limit(value):
	limit = value * static.MEGABYTE
	print(limit)
	resource.setrlimit(rsrc, (limit, limit))


def main():
	start_time = time.time()
	print("------------ max memory:" + str(resource.getrlimit(rsrc)[0]/1024) + " Kbytes -----------")

	# create index file

	with open(args.index_file, 'w') as index: pass 
	aux_id = 0
	with open(static.RESULTS + 'index_aux_' + str(aux_id), 'w') as index_aux: index_aux.write("{}")

	ut.create_index(args.corpus_path)

	print("--- %s minutes ---" % (time.time() - start_time))
	pass


if __name__ == "__main__":
	# argument parser
	parser = argparse.ArgumentParser(description='Process some integers.')

	# Corpus File
	parser.add_argument(
		'-c',
		dest='corpus_path',
		action='store',
		required=True,
		type=str,
		help='path to corpus files'
	)
	# Index File
	parser.add_argument(
		'-i',
		dest='index_file',
		action='store',
		required=True,
		type=str,
		help='index file path'
	)
	# Memory
	parser.add_argument(
		'-m',
		dest='memory_limit',
		action='store',
		required=True,
		type=int,
		help='memory available'
	)
	args = parser.parse_args()
	memory_limit(args.memory_limit)
	try:
		main()
	except MemoryError:
		sys.stderr.write('\n\nERROR: Memory Exception\n')
		sys.exit(1)


# You CAN (and MUST) FREELY EDIT this file (add libraries, arguments, functions and calls) to implement your indexer
# However, you should respect the memory limitation mechanism and guarantee
# it works correctly with your implementation
