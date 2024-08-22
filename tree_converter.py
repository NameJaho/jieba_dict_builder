# scan a single text file to generate trie tree
import json
from pandarallel import pandarallel
from collections import defaultdict
import pandas as pd
import utils

pandarallel.initialize(progress_bar=True)

INPUT_FOLDER = 'input'
OUTPUT_FOLDER = 'output'
CONFIG_FILE = 'config/config.yaml'


class TreeConverter:

    def __init__(self):
        config = utils.load_config(CONFIG_FILE)

        self.blacklist = config['BLACKLIST']
        word_length = config['WORD_LENGTH']
        self.word_length_min = word_length['min_len']
        self.word_length_max = word_length['max_len']

    def gen_trie_tree(self, csv_file):
        pass


if __name__ == '__main__':
    pass
