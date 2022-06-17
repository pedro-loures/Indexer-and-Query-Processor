
# Local import
import static_defines as static

# External import 
from warcio.archiveiterator import ArchiveIterator
import nltk
nltk.download('punkt')
import os
import resource
import argparse
import time

# TODO
def _treat_words(word):
  return word



# CODE ADAPTED FROM 'https://github.com/CDA-EPCWeb/Twitter-palavras'
# Add words to a ordered list withou word repetition
def _add_alphabetical(complete_list, new_words, treatment=False):

    # Ordena as palavras em ordem de crescimento e, caso queira tratá-las, deixa tudo minusculo
    # Sort the two lists and (if needed) apply treatment
    complete_list = sorted([str(word) for word in complete_list])
    if treatment:
        new_words = sorted([_treat_words(word) for word in new_words])
    else:
        new_words = sorted([str(word) for word in new_words])
    
    # Adiciona palavras complete_list
    # Add words to complete_list
    len_complete_list = len(complete_list) - 1
    i, j = 0, 0
    while(j < len(new_words)): 
        if j > 0 and new_words[j] == new_words[j - 1]:
            j += 1
        elif i > len_complete_list:
            complete_list.append(new_words[j])
            j += 1
        elif complete_list[i] > new_words[j]:
            complete_list.append(new_words[j])
            j += 1
        elif complete_list[i] < new_words[j]:
            i += 1
        else: 
            i += 1
            j += 1
    return sorted(complete_list)

# Process page Text
def _process_text(text):
  
  # Read dict 
  with open(static.RESULTS + 'word_dict', 'r', encoding='utf-8') as word_dict:
    word_in_files = word_dict.readlines() 
    # print(word_in_files)
  
  # Add words do dict
  with open(static.RESULTS + 'word_dict', 'w', encoding='utf-8') as word_dict:
    text_lines = [word + '\n' for word in  nltk.word_tokenize(text)]
    word_dict.writelines(_add_alphabetical(word_in_files, text_lines))


# Extract text from Warc Files
def _read_Warc_file(file_path, limit):


  with open(file_path, 'rb') as stream:
    for counter, record in enumerate(ArchiveIterator(stream)):      
  
      if record.rec_type == 'response':
        url = record.rec_headers.get_header('WARC-Target-URI')
        text = record.content_stream().read().decode('utf-8')
        _process_text(text)
        # print(nltk.word_tokenize(text))
      else:
        print(counter, ' : ', record.http_headers.get("content-type"))

      if counter > 7:
        break
    return url, text


# Create Index
def create_index(path_to_corpus, limit = 10):
  files = os.listdir(path_to_corpus)
  # pass through files
  for file in files:

    # print("usage_" + i +  ": " + str(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))

    url, text = _read_Warc_file(path_to_corpus + file, limit)

    if file == files[0]:
      break
    
    
  