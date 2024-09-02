# import polars as pl
import pandas as pd
import utils

from ngrams_freq_stat import NgramsFreqStat
from utils import cost_time

from entropy_calculator1 import EntropyCalculator
from mi_calculator import MICalculator

CONFIG_FILE = 'config/config.yaml'
TERMS_FILE = 'output/terms_data.csv'
ENTROPY_RESULT_FILE = 'output/entropy_result_diff_jieba.csv'
FINAL_RESULT_FILE = 'output/final_result.csv'
ENTROPY_CHAR_FREQ_FILE = 'output/char_freq.csv'


class WordDiscoverer:
    def __init__(self):
        config = utils.load_config(CONFIG_FILE)
        self.blacklist = config['BLACKLIST']
        self.entropy_calculator = EntropyCalculator()
        self.mi_calculator = MICalculator()

    def is_in_blacklist(self, term):
        return any(char in self.blacklist for char in term)

    @cost_time
    def filter_with_entropy(self):
        entropy_results = []
        df = pd.read_csv(TERMS_FILE)

        for index, row in df.iterrows():
            term = row['term']
            term_freq = row['term_freq']
            doc_freq = row['doc_freq']
            left_chars = eval(row['left_chars'])
            right_chars = eval(row['right_chars'])

            if self.is_in_blacklist(term):
                continue

            entropy = self.entropy_calculator.calculate_entropy(left_chars, right_chars)

            if entropy >= 1.5 and len(term.strip()) > 1:
                entropy_results.append({'term': term, 'term_freq': term_freq, 'doc_freq': doc_freq})

        return entropy_results

    @cost_time
    def save_entropy_results(self):
        entropy_results = self.filter_with_entropy()
        df = pd.DataFrame(entropy_results)
        df.to_csv(ENTROPY_RESULT_FILE)
        return df

    @cost_time
    def filter_with_mi(self):
        mi_results = []
        df = pd.read_csv(ENTROPY_RESULT_FILE)

        for index, row in df.iterrows():
            term = row['term']
            term_freq = row['term_freq']
            doc_freq = row['doc_freq']
            mi = self.mi_calculator.calculate_mutual_information(term)
            if mi > -4.5:
                mi_results.append({'term': term, 'term_freq': term_freq, 'doc_freq': doc_freq})

        return mi_results

    @cost_time
    def save_mi_results(self):
        mi_results = self.filter_with_mi()
        df = pd.DataFrame(mi_results)
        df.to_csv(FINAL_RESULT_FILE)


if __name__ == '__main__':
    word_discoverer = WordDiscoverer()
    stat = NgramsFreqStat()

    df = word_discoverer.save_entropy_results()
    stat.save_char_freq()

    word_discoverer.save_mi_results()
