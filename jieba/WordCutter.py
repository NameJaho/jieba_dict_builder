import os
import re
import jieba
import utils

class WordCutter:
    def __init__(self):
        white_dict_path = os.path.join(utils.get_root_path(), 'word_splitter', WHITE_DICT)
        jieba.load_userdict(white_dict_path)