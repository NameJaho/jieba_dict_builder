import pandas as pd
import re
from collections import Counter
import time
from pandarallel import pandarallel
from multiprocessing import Pool, Manager
import numpy as np

from config.config_loader import ConfigLoader
from utils import cost_time


class KeywordCounter(ConfigLoader):
    def __init__(self, num_partitions=4):
        super().__init__()
        self.input_csv = self.input_file_path.input_file
        self.target_csv = self.output_file_path.entropy_result
        self.output_csv = self.output_file_path.char_freq
        self.num_partitions = num_partitions

    def initialize_pandarallel(self):
        pandarallel.initialize()

    def load_data(self):
        self.df = pd.read_csv(self.input_csv)
        target_term = pd.read_csv(self.target_csv)
        target_term.dropna(inplace=True)
        self.keywords = target_term['term'].tolist()
        self.characters = set(''.join([i for i in self.keywords if i != ' ']))
        self.char_pattern = r'(' + '|'.join(map(re.escape, self.characters)) + r')'

    def count_keywords(self, content, pattern):
        words_found = re.findall(pattern, content, flags=re.IGNORECASE)
        return Counter(words_found)

    @cost_time
    def parallel_count(self):
        self.df['char_counts'] = self.df.parallel_apply(lambda x: self.count_keywords(x['content'], self.char_pattern),
                                                        axis=1)
    @cost_time
    def aggregate_counts(self):
        self.total_counter = Counter()
        for row in self.df['char_counts']:
            self.total_counter.update(row)
    @cost_time
    def save_results(self):
        result_df_char = pd.DataFrame(list(self.total_counter.items()), columns=['word', 'count'])
        result_df_char.to_csv(self.output_csv, index=False)

    def run(self):
        start_time = time.time()
        self.initialize_pandarallel()
        self.load_data()
        self.parallel_count()
        self.aggregate_counts()
        self.save_results()
        print(f"Total time taken: {time.time() - start_time} seconds")


if __name__ == "__main__":
    counter = KeywordCounter()
    counter.run()
