import polars as pl
from utils import cost_time

from entropy_calculator import EntropyCalculator
from mi_calculator import MICalculator

TERMS_FILE = 'output/terms_data.csv'
ENTROPY_RESULT_FILE = 'output/entropy_result.csv'
FINAL_RESULT_FILE = 'output/final_result.csv'


class WordDiscoverer:
    def __init__(self):
        self.entropy_calculator = EntropyCalculator()
        self.mi_calculator = MICalculator()

    @cost_time
    def filter_with_entropy(self):
        entropy_results = []
        df = pl.read_csv(TERMS_FILE)

        for row in df.iter_rows(named=True):
            term = row['term']
            term_freq = row['term_freq']
            doc_freq = row['doc_freq']
            left_chars = eval(row['left_chars'])
            right_chars = eval(row['right_chars'])

            entropy = self.entropy_calculator.calculate_entropy(left_chars, right_chars)

            if entropy >= 1.5 and len(term.strip()) > 1:
                entropy_results.append({'term': term, 'term_freq': term_freq, 'doc_freq': doc_freq})

        return entropy_results

    @cost_time
    def save_entropy_results(self):
        entropy_results = self.filter_with_entropy()
        df = pl.DataFrame(entropy_results)
        df.write_csv(ENTROPY_RESULT_FILE, separator=",")

    @cost_time
    def filter_with_mi(self):
        mi_results = []
        df = pl.read_csv(ENTROPY_RESULT_FILE)

        for row in df.iter_rows(named=True):
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
        df = pl.DataFrame(mi_results)
        df.write_csv(FINAL_RESULT_FILE, separator=",")


if __name__ == '__main__':
    word_discoverer = WordDiscoverer()
    word_discoverer.save_entropy_results()
    word_discoverer.save_mi_results()

