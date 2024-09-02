import csv
import pandas as pd
import json
from collections import Counter, defaultdict
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

        # 读取ngrams列表
        ngrams = df['ngram'].apply(lambda x: eval(x)).tolist()

        # 统计doc_freq
        doc_freq_dict = defaultdict(set)
        for ngram in ngrams:
            term = ngram['term']
            doc_id = ngram['doc_id']
            doc_freq_dict[term].add(doc_id)

        doc_freq = [{'term': term, 'doc_freq': len(doc_ids)} for term, doc_ids in doc_freq_dict.items()]
        doc_freq_df = pd.DataFrame(doc_freq)

        # 过滤doc_freq大于阈值的term
        filtered_terms = doc_freq_df[doc_freq_df['doc_freq'] > self.filter.doc_freq_threshold]['term'].tolist()
        print(len(filtered_terms))

        # 过滤后的数据
        filtered_ngrams = [ngram for ngram in ngrams if ngram['term'] in filtered_terms]
        print(len(filtered_ngrams))

        # 统计term_freq
        term_freq_dict = Counter(ngram['term'] for ngram in filtered_ngrams)
        term_freq = [{'term': term, 'term_freq': freq} for term, freq in term_freq_dict.items()]
        term_freq_df = pd.DataFrame(term_freq)

        # 统计left_char和right_char的频次
        left_chars_dict = defaultdict(Counter)
        right_chars_dict = defaultdict(Counter)
        for ngram in filtered_ngrams:
            term = ngram['term']
            left_char = ngram['left_char']
            right_char = ngram['right_char']
            left_chars_dict[term][left_char] += 1
            right_chars_dict[term][right_char] += 1

        left_chars = [{'term': term, 'left_chars': dict(counter)} for term, counter in left_chars_dict.items()]
        right_chars = [{'term': term, 'right_chars': dict(counter)} for term, counter in right_chars_dict.items()]
        left_chars_df = pd.DataFrame(left_chars)
        right_chars_df = pd.DataFrame(right_chars)

        # 合并所有统计结果
        result = pd.merge(term_freq_df, doc_freq_df, on='term')
        result = pd.merge(result, left_chars_df, on='term')
        result = pd.merge(result, right_chars_df, on='term')

        return result

    def save_to_csv(self, df):
        df.to_csv(self.output_file_path.merged_ngrams, index=False, encoding='utf-8')


if __name__ == '__main__':
    ngram_merger = NgramMerger()
    _results = ngram_merger.process_ngrams()
    ngram_merger.save_to_csv(_results)
