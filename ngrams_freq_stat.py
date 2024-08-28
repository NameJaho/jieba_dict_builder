import pandas as pd

from pandarallel import pandarallel

pandarallel.initialize(progress_bar=True, verbose=2)


class NgramsFreqStat():
    def __init__(self):
        pass

    def preprocess_data(self):
        df = pd.read_csv('output/ngrams_10w_0828.csv')
        df.dropna(inplace=True)
        return df

    def init_freq(self, df):
        df['ngram'] = df['ngrams'].parallel_apply(lambda x: x['word'])
        df['single_char'] = df['ngram'].parallel_apply(lambda x: list(x))

        return df

    def save_freq(self, df):
        df['single_char'].explode().value_counts().to_csv('output/single_char_freq.csv')
        df['ngram'].explode().value_counts().to_csv('output/ngram_freq.csv')


if __name__ == '__main__':
    stat = NgramsFreqStat()
    df = stat.preprocess_data()
    df = stat.init_freq(df)
    stat.save_freq(df)
