
# Local import
import static_defines as static

# External import
from warcio.archiveiterator import ArchiveIterator
# import nltk
# nltk.download('punkt')
from charset_normalizer import from_bytes
import os
import resource
import argparse
import time
import re

################################### read index

# convert values that are in string mode to int [[url0, p1, p2, ..., pn ], [url1, p1, p2...],...]
def _convert_position_to_int(position_list_str, timed=False):
  # return [[0,1,2]] # skip_function
  for _ix, _url_positions_i in enumerate(position_list_str):
    for _jx, _position_j in enumerate(_url_positions_i): # remove apostrophes
      # print("   _convert_position_to_int - _position_j(antes): " + _position_j)
      if _position_j[0] == '\'' and _position_j[-1] == '\'':
        _position_j = _position_j[1:-1]
        position_list_str[_ix][_jx] = _position_j

      if _jx == 0: # skip url
        continue

      # print("   _convert_position - len(position_i) : ", len(_position_j))
      assert _position_j.isnumeric(), "VALUE " + _position_j + " IN " + str(_url_positions_i) + "NOT A INTEGER"
      position_list_str[_ix][_jx] = int(position_list_str[_ix][_jx])
  return position_list_str


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
  dict_entry_str[0] = dict_entry_str[0][1:]
  dict_entry_str[-1] = dict_entry_str[-1][:-1]  + ",\n" # add those spaces so it follows the same pattern as other lines


  # read dictionry BAD WAY, WILL BUG IF ':' IN ANY ENTRY
  for entry in dict_entry_str:
    # print('read_dict - entry', entry,end='')
    assert ': ' in entry,  entry + " Is not a correct dict entry"

    # Key and position extraction
    key_str, positions_str = entry.split(': ')
    position_list_str = [position_list_str for position_list_str in re.split('\[(.*?)\]', positions_str[1:-3]) if position_list_str != '']
    # print( "read_dict:", position_list_str)
    position_list_str = [position.split(', ') for position in position_list_str if position != ', ']
    position_list = _convert_position_to_int(position_list_str)

    key = key_str[1:-1]
    dictionary[key] = position_list
  # print('read_dict - complete dict:' , dictionary)

  return dictionary



######################## create index

# Rules for the word Treatment
def _treat_words(words):
  # return words # skip_function
  treated_words = []
  
  
  for _word in words:
    _accepted = True

    # convert to lower case
    _word = _word.lower()

    # ignore whats not alphanumeric THIS IS BAD. UPDATE THIS LATER
    if not _word.isalnum():
      _accepted = False
    if _accepted: 
      treated_words.append(_word)
    return treated_words


# Add words to a ordered list withou word repetition
def _add_alphabetical(complete_dict, new_words, url, treatment=True):
    # return "{}" # skip_function
    # Apply treatment
    if treatment and new_words:
        new_words = _treat_words(new_words)
    else:
        new_words = [str(_word) for _word in new_words]

    # create a auxiliary dict with new words
    _index_aux = {}
    for _position, _word in enumerate(new_words):

      if _word not in _index_aux:
        _index_aux[_word] = ([url, _position])
      else:
        _index_aux[_word].append(_position)

    # Merge dicts
    _index = complete_dict
    for _word in _index_aux.keys():
      if _word not in _index:
        _index[_word] = ([_index_aux[_word]])
      else:
        _index[_word].append(_index_aux[_word])

    dictionary_string = '{}'
    
    # Convert dict into a alphatically ordered string
    # return "{'faW': [['1-432',43,5,4]]}" # dict_string
    len_index = len(_index)
    if len_index > 0:

      _words = sorted(_index.keys())
      # print("_add_alphabetical - _words:", _words)
          
      dictionary_string =  [('\'' + _word + '\': ' + str(_index[_word]) + ',\n') for _word in _words] # convert to list
      dictionary_string[0] = '{' + dictionary_string[0]
      dictionary_string[-1] = dictionary_string[-1][:-2] + '}'
    # print("\n\n_add_aphabetical - dictionary_string:", dictionary_string)

    # return "{'faW': [['1-432',43,5,4]]}" # dict_string
    return dictionary_string



# Process page Text
def _process_text(raw_stream, url, aux_id=0):
  # return # skip_function
  _text = raw_stream.read().decode('utf-8', 'ignore')

  #_text_lines = nltk.word_tokenize(_text)
  _text_lines = re.split(', |_|-|!|\+', _text)

  # Read dict
  index_aux = {}
  # print("_process_text - index_aux:", index_aux)

  # Add words do dict
  with open(static.TMP + 'index_aux_' + str(aux_id), 'w', encoding='utf-8') as word_dict:
    word_dict.writelines(_add_alphabetical(index_aux, _text_lines, url))
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
def store_warc_file(file_path, limit):
  # return 'a', 'a' # skip_function
  with open(file_path, 'rb') as _stream:
    for _counter, record in enumerate(ArchiveIterator( _stream )):
      if record.rec_type == 'response':

        # Get url and  raw stream
        _url = record.rec_headers.get_header('WARC-Target-URI')
        raw_stream = record.content_stream()#.read().decode('utf-8')

        # Encode url and assert it can be decoded
        encoded_url = encode_url(_url)
        assert _url == decode_url(encoded_url), "URL <" + _url +"> DOES NOT MATCH DECODED URL <" + decode_url(encoded_url) + ">"

        # Write an read dict # TODO 3.4.3
        auxfilename = static.TMP + "index_aux_" + str(_counter)
        _process_text(raw_stream, encoded_url, aux_id=_counter)
        read_dict(auxfilename)
        # os.remove(auxfilename)

      # In case there is a limit, break on the limit of files
      if limit != None and _counter > limit:
        break
    return encoded_url, raw_stream



# 3- Create Index TODO
def create_index(path_to_corpus, limit = None):
  files = os.listdir(path_to_corpus)
  # Pass through files
  for _counter, file in enumerate(files):
    url, text = store_warc_file(path_to_corpus + file, limit)

    # Remove tmp_files
    tmp_files = os.listdir(static.TMP)
    for file in tmp_files:
      os.remove(static.TMP + file)
    break


# merge files
# for file in files:
# open(file) as index:
# 
# filelines == []
# while(still_lines)
#   for file_id, file in enumerate(files):
#     filelines.append([])
#     while(comparar as palavras)
#       line = readline()
#       fileslines[file_id] = line
        
