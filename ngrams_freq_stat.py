import pandas as pd
import warnings

warnings.filterwarnings("ignore")
from pandarallel import pandarallel

from utils import cost_time

pandarallel.initialize()

ENTROPY_RESULT_FILE = 'output/terms_data.csv'

CHAR_FREQ_FILE = 'output/char_freq.csv'
WORD_FREQ_FILE = 'output/word_freq.csv'
JIEBA_DICT = 'word_splitter/dict.txt'

class NgramsFreqStat():
    def __init__(self):
        pass

    @cost_time
    def preprocess_data(self):
        df = pd.read_csv(ENTROPY_RESULT_FILE)
        df.dropna(inplace=True)
        return df

    def init_jieba_dict(self):
        with open(JIEBA_DICT, 'r') as f:
            jieba_dict = f.readlines()
        words = [word.strip().split(' ')[0] for word in jieba_dict]
        jieba_df = pd.DataFrame({'ngram': words})
        return jieba_df

    def calculate_freq_by_entropy(self, df, jieba_df):
        diff_in_jieba = df[~df['term'].isin(jieba_df['ngram'])]
        diff_in_jieba.to_csv(WORD_FREQ_FILE, index=False)

        diff_in_jieba[['term', 'term_freq']].to_csv(WORD_FREQ_FILE, index=False)

        diff_in_jieba['single_char'] = diff_in_jieba['term'].parallel_apply(lambda x: list(x))
        diff_in_jieba['single_char'].explode().value_counts().to_csv(CHAR_FREQ_FILE)

    def save_char_freq(self):
        df = self.preprocess_data()
        jieba_df = self.init_jieba_dict()
        self.calculate_freq_by_entropy(df, jieba_df)


if __name__ == '__main__':
    stat = NgramsFreqStat()
    j_df = stat.init_jieba_dict()
    df = stat.preprocess_data()
    stat.calculate_freq_by_entropy(df, j_df)
    # df = stat.init_freq(df)
    # stat.save_freq(df)
