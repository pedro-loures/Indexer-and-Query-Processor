
# Local import
import static_defines as static

# External import
from warcio.archiveiterator import ArchiveIterator
from charset_normalizer import from_bytes
import nltk
nltk.download('rslp')
nltk.download('stopwords')
import os
import resource
import argparse
import time
import re

#stopword preparation
stemmer = nltk.stem.RSLPStemmer()
stopwords_list = nltk.corpus.stopwords.words('portuguese')
stopwords_list = [stemmer.stem(word) for word in stopwords_list]
STOPWORDS = {}
for word in stopwords_list:
  STOPWORDS[word] = ''

################################### read index
def merge_indexes(file, encoding='utf-8'):
  

# read index file and convert it to a dictionary
def read_dict(file, encoding='utf-8'):
  # return {} # skip_function
  dictionary = {}

  # read file
  with open(file, 'r', encoding=encoding) as dict_file:
    dict_entry_str = dict_file.readlines()

  if len(dict_entry_str[0]) < 3: #if empty dict return a dict
    return dictionary

  # asser it is in brackets
  assert dict_entry_str[0][0] == '{' and dict_entry_str[-1][-1] == '}', "FILE is not a dict"
  dict_entry_str[0] = '}' + dict_entry_str[0]
  dict_entry_str = dict_entry_str[:-1]

  # read dictionry BAD WAY, WILL BUG IF ':' IN ANY ENTRY
  for entry in dict_entry_str:
    # print('read_dict - entry', entry,end='')
    if entry[0] == '}': 
      _size, _url = entry[2:-2].split(', ')
      continue

    assert ': ' in entry,  entry + " Is not a correct dict entry"
    
    # Key and position extraction
    key_str, positions_str = entry.split(': ')
    position_list_str = positions_str[1:-3]
    position_list_str = position_list_str.split(', ')
    position_list = [_url, *[int(position) for position in position_list_str]]

    key = key_str[1:-1]
    if key not in dictionary:
      dictionary[key] = position_list
    else:     
      dictionary[key].append(position_list)  
  # print('read_dict - complete dict len:' , len(dictionary))

  return dictionary

def write_dict(file, dictionary):
  dictionary_string = dict_to_string(dictionary)
  with open(file, 'w') as written_file: written_file.writelines(dictionary_string)

######################## create index

# Rules for the word Treatment
def _treat_words(words, logfile = None):
  # return words # skip_function
  treated_words = []
  
  
  for _position, _word in enumerate(words):
    _accepted = True
    if not _word:
      continue

    # Stemming
    _word = stemmer.stem(_word.lower())
    
    # Stopword
    if _word in STOPWORDS:
      continue

    # ignore whats not alphanumeric THIS IS BAD. UPDATE THIS LATER
    if not _word.isalnum():
      if logfile: logfile.write(_word + '\n') 
      continue

    if _accepted: # add position + word
      treated_words.append(str(_position) + '-' + _word)

  return treated_words



def dict_to_string(dictionary, len_dictionary = None, url = None):
  if not len_dictionary:
    len_dictionary = len(dictionary)
  _words = sorted(dictionary.keys())
  # print("_add_alphabetical - _words:", _words)
      
  dictionary_string =  [('\'' + _word + '\': ' + str(dictionary[_word]) + ',\n') for _word in _words] # convert to list
  if url:
    dictionary_string[0] = '{' + str(len_dictionary) + ', ' + url + '\n' \
                              +  dictionary_string[0]
  else:
    dictionary_string[0] = '{' + dictionary_string[0]
  dictionary_string[-1] = dictionary_string[-1][:-2] + ',\n}'
  return dictionary_string



# Add words to a ordered list withou word repetition
def _add_alphabetical(complete_dict, new_words, url, treatment=True):
    # return "" # skip_function

    # create a auxiliary dict with new words
    _index = {}
    for _word in new_words: # wordformat : position-word ex: 123-palavra

      _position, _word = _word.split('-')
      _position = int(_position)
    
      if _word not in _index:
        _index[_word] = ([_position])
      else:
        _index[_word].append(_position)

    # # Merge dicts
    # _index = complete_dict
    # for _word in _index_aux.keys():
    #   if _word not in _index:
    #     _index[_word] = ([_index_aux[_word]])
    #   else:
    #     _index[_word].append(_index_aux[_word])

    dictionary_string = ''
    
    # Convert dict into a alphatically ordered string
    len_index = len(_index)
    if len_index > 0:
      dictionary_string = dict_to_string(_index, len_index, url)

    return dictionary_string



# Process page Text
def _process_text(raw_stream, url, index_aux_file, treatment=True, logfile=None):

  
  # return # skip_function
  _text = raw_stream.read().decode('utf-8', 'ignore')

  _text_lines = re.split(static.WORD_TREATMENT, _text) #looks worse BUT FASTER   # OLD -> _text_lines = nltk.word_tokenize(_text)

  # Apply treatment
  if treatment and _text_lines:
      new_words = _treat_words(_text_lines, logfile)
  else:
      new_words = [str(_word) for _word in _text_lines]
  
  # Read dict
  index_dict_base = {}
  # print("_process_text - index_aux:", index_aux)

  # Add words do dict
  index_aux_file.writelines(_add_alphabetical(index_dict_base, new_words, url))
  
  return



# Convert url to a unique integer that can be decoded later
def encode_url(url):
  # return url # skip_function
  _urllen = len(url)
  _biturl = url.encode('utf-8')
  _numeric = int.from_bytes(_biturl, byteorder='big')
  encoded_string = str(_urllen) + '-' + str(_numeric)
  return encoded_string


# Decode url encoded by encode_url()
def decode_url(encoded_string):
  # return encoded_string # skip_function
  _lenght, encoded_url= encoded_string.split('-', maxsplit=1)

  _lenght = int(_lenght)
  encoded_url = int(encoded_url)
  encoded_url = encoded_url.to_bytes(_lenght, 'big')
  return encoded_url.decode('utf-8')



# Extract text from Warc Files
def store_warc_file(corpus_file, limit, aux_file, logfile = None):
  # Create index_aux for this file
  index_aux_file = open(aux_file, 'w', encoding='utf-8')
  print(logfile)
  # Fill_index_aux
  with open(corpus_file, 'rb') as _stream:
    for _counter, record in enumerate(ArchiveIterator( _stream )):
      if record.rec_type == 'response':
        if _counter % 50 == 0:
          print(_counter)
        # Get url and  raw stream
        _url = record.rec_headers.get_header('WARC-Target-URI')
        raw_stream = record.content_stream()#.read().decode('utf-8')

        # Encode url and assert it can be decoded
        encoded_url = encode_url(_url)
        assert _url == decode_url(encoded_url), "URL <" + _url +"> DOES NOT MATCH DECODED URL <" + decode_url(encoded_url) + ">"

        # Write an read dict # TODO 3.4.3
        
        _process_text(raw_stream, encoded_url, index_aux_file, logfile=logfile)
        # os.remove(auxfile)

      # In case there is a limit, break on the limit of files
      if limit != None and _counter > limit:
        break

    
    return encoded_url, raw_stream



### File management 



def _remove_files(filepath):
  tmp_files = os.listdir(filepath)
  for file in tmp_files:
    os.remove(filepath + file)
  return



# 3- Create Index TODO
def create_index(path_to_corpus, limit = None):
  files = os.listdir(path_to_corpus)
  # Pass through files

  # refused_logfile = open(static.LOG + 'refused_words.txt' , 'w') 
  refused_logfile = None 
  for _counter, file in enumerate(files):
    aux_file = static.TMP + "index_aux_" + str(_counter)
    url, text = store_warc_file(path_to_corpus + file, limit, aux_file, refused_logfile)
    
    dictionary = read_dict(aux_file)
    write_dict(static.TMP + "teste2.txt", dictionary)
    # Merge auxiliary indexes
    # _merge_files(static.TMP)
    # Remove tmp_files
    # _remove_files(static.TMP)
    break
  # assert 1 == 2, Just so it doesnt save

  return      
