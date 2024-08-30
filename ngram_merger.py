import csv
import pandas as pd
import json
from collections import Counter
from pandarallel import pandarallel
from utils import cost_time
import warnings
from config.config_loader import ConfigLoader

pandarallel.initialize()
warnings.filterwarnings("ignore")


class NgramMerger(ConfigLoader):
    def __init__(self):
        super().__init__()

    @cost_time
    def process_ngrams(self):
        df = pd.read_csv(self.output_file_path.ngrams)

        # 统计doc_freq
        doc_freq = df.groupby('term')['doc_id'].nunique().reset_index()
        doc_freq.columns = ['term', 'doc_freq']

        # 过滤doc_freq大于阈值的term
        filtered_terms = doc_freq[doc_freq['doc_freq'] > self.filter.doc_freq_threshold]['term'].tolist()
        print(len(filtered_terms))

        # 过滤后的数据
        filtered_df = df[df['term'].isin(filtered_terms)]
        print(len(filtered_df))

        # 统计term_freq
        term_freq = filtered_df['term'].value_counts().reset_index()
        term_freq.columns = ['term', 'term_freq']

        # 统计left_char和right_char的频次
        left_chars = filtered_df.groupby('term')['left_char'].apply(lambda x: x.value_counts().to_dict()).reset_index(
            name='left_chars')
        right_chars = filtered_df.groupby('term')['right_char'].apply(lambda x: x.value_counts().to_dict()).reset_index(
            name='right_chars')

        # 合并所有统计结果
        result = pd.merge(term_freq, doc_freq, on='term')
        result = pd.merge(result, left_chars, on='term')
        result = pd.merge(result, right_chars, on='term')

        return result

    def save_to_csv(self, df):
        df.to_csv(self.output_file_path.merged_ngrams, index=False, encoding='utf-8')


if __name__ == '__main__':
    ngram_merger = NgramMerger()
    _results = ngram_merger.process_ngrams()
    ngram_merger.save_to_csv(_results)


