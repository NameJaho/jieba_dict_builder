import pandas as pd
import warnings

warnings.filterwarnings("ignore")
from pandarallel import pandarallel

from utils import cost_time

pandarallel.initialize()

ENTROPY_RESULT_FILE = 'output/entropy_result.csv'


class NgramsFreqStat():
    def __init__(self):
        pass

    @cost_time
    def preprocess_data(self):
        df = pd.read_csv(ENTROPY_RESULT_FILE)
        df.dropna(inplace=True)
        return df

    def init_jieba_dict(self):
        with open('output/jieba_dict.txt', 'r') as f:
            jieba_dict = f.readlines()
        words = [word.strip().split(' ')[0] for word in jieba_dict]
        j_df = pd.DataFrame({'ngram': words})
        return j_df

    def calculate_freq_by_entropy(self, df, j_df):
        diff_in_jieba = df[~df['term'].isin(j_df['ngram'])]
        diff_in_jieba.to_csv('output/entropy_result_diff_jieba.csv', index=False)

        diff_in_jieba['single_char'] = diff_in_jieba['term'].parallel_apply(lambda x: list(x))
        diff_in_jieba['single_char'].explode().value_counts().to_csv('output/char_freq_entropy.csv')

    @cost_time
    def init_freq(self, df):
        df['ngram'] = df['ngrams'].parallel_apply(lambda x: x['word'])
        df['single_char'] = df['ngram'].parallel_apply(lambda x: list(x))

        return df

    @cost_time
    def save_freq(self, df):
        df['single_char'].explode().value_counts().to_csv('output/char_freq.csv')
        df['ngram'].explode().value_counts().to_csv('output/word_freq.csv')


if __name__ == '__main__':
    stat = NgramsFreqStat()
    j_df = stat.init_jieba_dict()
    df = stat.preprocess_data()
    stat.calculate_freq_by_entropy(df, j_df)
    # df = stat.init_freq(df)
    # stat.save_freq(df)
