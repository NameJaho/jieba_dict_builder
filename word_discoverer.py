import polars as pl
from utils import cost_time

from entropy_calculator import EntropyCalculator
from mi_calculator import MICalculator

TERMS_FILE = 'output/terms_data.csv'
ENTROPY_RESULT_FILE = 'output/entropy_result.csv'


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

    def filter_with_mi(self):
        pass


if __name__ == '__main__':
    new_word_detector = NewWordDetector()
    new_word_detector.save_entropy_results()

