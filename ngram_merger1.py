import polars as pl
import pandas as pd
import json
from collections import Counter
from pandarallel import pandarallel
from utils import cost_time
import warnings
from config.config_loader import ConfigLoader

warnings.filterwarnings("ignore")


class NgramMerger(ConfigLoader):
    def __init__(self):
        super().__init__()

    @cost_time
    def process_ngrams(self):
        df = pl.read_csv(self.output_file_path.ngrams)
        print(len(df))

        # 统计doc_freq
        doc_freq = df.group_by('term').agg([pl.col('doc_id').n_unique().alias('doc_freq')])

        # 过滤doc_freq大于阈值的term
        filtered_terms = doc_freq.filter(pl.col('doc_freq') > self.filter.doc_freq_threshold).select(
            'term').to_series().to_list()

        # 过滤后的数据
        filtered_df = df.filter(pl.col('term').is_in(filtered_terms))

        # 统计term_freq
        term_freq = filtered_df.group_by('term').agg([pl.count().alias('term_freq')])

        # 统计left_char和right_char的频次
        left_chars = filtered_df.group_by('term').agg(
            [pl.col('left_char').value_counts(sort=True).map_elements(lambda x: x.to_dict()).alias('left_chars')])
        right_chars = filtered_df.group_by('term').agg(
            [pl.col('right_char').value_counts(sort=True).map_elements(lambda x: x.to_dict()).alias('right_chars')])
        # left_chars = filtered_df.group_by('term')['left_char'].map_elements(lambda x: x.value_counts().to_dict()).alias('left_chars')
        # right_chars = filtered_df.group_by('term')['right_char'].map_elements(lambda x: x.value_counts().to_dict()).alias('right_chars')
        # 合并所有统计结果
        result = term_freq.join(doc_freq, on='term')
        result = result.join(left_chars, on='term')
        result = result.join(right_chars, on='term')

        return result

    def save_to_csv(self, df):
        df.write_csv(self.output_file_path.merged_ngrams, index=False, encoding='utf-8')


if __name__ == '__main__':
    ngram_merger = NgramMerger()
    _results = ngram_merger.process_ngrams()
    ngram_merger.save_to_csv(_results)


