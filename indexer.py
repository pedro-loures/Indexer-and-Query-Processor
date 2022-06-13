# TODO list
# -0 TODO read args
# -1 ok? Read Corpus
# -2 TODO natural language processing
# -3 TODO create index
# -4 TODO print json with information

 
# DETAILED TODO LIST    

# 2.1 OK create file at designated location
# 2.2 TODO not rely entirely on available memory to produce index
# 2.3 TODO stemming (portuguese)
# 2.4 TODO stopword removal (portuguese)
# 2.5 TODO parallelization policy
# 2.FUTURE compression policy



# Local import
import indexer_utils as ut


# External import 
import sys
import resource
import argparse
import time


MEGABYTE = 1024 * 1024
def memory_limit(value):
    limit = value * MEGABYTE
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))

def main():
    start_time = time.time()
    print("------------ max memory:" + str(args.memory_limit * 1024) + "-----------")

    open(args.index_file, 'w')

    ut.test(args.corpus_path)

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