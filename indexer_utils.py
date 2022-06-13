

# External import 
from warcio.archiveiterator import ArchiveIterator
import os
import resource
import argparse
import time





def test(path_to_corpus):
  url = []
  text = []
  files = os.listdir(path_to_corpus)
  #for file in files:
    # print(file)

  file = files[0]
  i = 0
  while True:
    print(i)
    i += 1
    with open(path_to_corpus+file, 'rb') as stream:
      for record in ArchiveIterator(stream):

        if record.rec_type == 'response':

          url.append(record.rec_headers.get_header('WARC-Target-URI'))
          text.append(record.content_stream().read())
  print(len(url))
