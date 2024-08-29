import re
import sys
import time
from collections import defaultdict

import pandas as pd
import warnings
import utils
from ngram_statistics import NgramStatistics
from ngrams_freq_stat import NgramsFreqStat
from word_discoverer import WordDiscoverer
from word_splitter.word_cutter import WordCutter

warnings.filterwarnings("ignore")

CONFIG_FILE = 'config/config.yaml'
INPUT_FILE = 'input/random_user_20W_0829.csv'

from pandarallel import pandarallel

pandarallel.initialize()


class NgramScanner:
    def __init__(self):
        self.wc = WordCutter()
        config = utils.load_config(CONFIG_FILE)
        self.blacklist = config['BLACKLIST']
        self.word_length_max = config['WORD_LENGTH']['max_len']

    @staticmethod
    def preprocess():
        df = pd.read_csv(INPUT_FILE)
        df.dropna(subset=['content'], inplace=True)
        # df = df[:100]
        return df

    def cut_words(self, df):
        df['words'] = df['content'].apply(
            lambda x: self.wc.cut(''.join(utils.split_into_phrases(x, self.blacklist))))
        return df

    # 返回最长单词
    # def find_max_length_word(self, words, index, direction):
    def find_max_length_word(self, content, char_list, max_length=4):
        results = []
        occurrences = {}  # This dictionary will store the positions of each character to avoid duplicates

        for char in char_list:
            start_pos = 0
            while start_pos < len(content):
                found_pos = content.find(char, start_pos)
                if found_pos == -1:
                    break  # No more occurrences
                if found_pos not in occurrences:
                    # Calculate start and end indices for the substring
                    start_idx = max(0, found_pos - max_length)
                    end_idx = min(len(content), found_pos + max_length + 1)

                    # Extract the substring
                    substring = content[start_idx:end_idx]

                    # Calculate necessary padding
                    left_padding = ' ' * (max_length - (found_pos - start_idx))
                    right_padding = ' ' * ((found_pos + max_length + 1) - end_idx)

                    # Apply padding and store the result
                    padded_substring = left_padding + substring + right_padding
                    results.append((char, padded_substring))
                    occurrences[found_pos] = True

                start_pos = found_pos + 1  # Move start_pos forward to find next occurrence

        return results

    @staticmethod
    def generate_ngrams(word, index, note_id, direction='left', max_length=4):
        """
        Generate n-grams from a given index within a word.

        :param word: The word from which to generate n-grams.
        :param index: The starting index for n-gram generation.
        :param direction: The direction for n-gram generation ('left' or 'right').
        :param max_length: The maximum length of n-grams to generate.
        :return: A tuple containing lists of n-grams, left characters (if applicable), and right characters (if applicable).
        """
        results = []
        left_chars = []
        right_chars = []
        ngrams = []
        if len(word) == 2:
            return results, left_chars, right_chars, ngrams
        if direction == 'left':
            # Generate n-grams to the left of the index
            start = max(0, index - max_length)  # Ensure start is not negative
            end = index + 1  # Include the character at the index
            for i in range(end - 1, start - 1, -1):
                ngram = word[i:end].strip()
                if len(ngram) > 1 and len(
                        ngram) <= max_length:  # Only consider left/right chars if n-gram length is more than 1
                    left_char = word[i - 1] if i > 0 else ''  # No left character if at the beginning
                    right_char = word[end] if end < len(word) else ''  # Right character after the n-gram
                    left_chars.append(left_char)
                    right_chars.append(right_char)
                    results.append(ngram)
                    ngrams.append({'word': ngram, 'left_char': left_char, 'right_char': right_char, 'doc_id': note_id})
                else:
                    left_char = ''
                    right_char = ''
                # print(f'N-gram: "{ngram}", Left char: "{left_char}", Right char: "{right_char}"')
        elif direction == 'right':
            # Generate n-grams to the right of the index
            start = index  # Start from the index
            end = min(len(word), index + max_length)  # Ensure end is within bounds
            for i in range(start, end):
                ngram = word[start:i + 1].strip()
                if len(ngram) > 1:  # Only consider left/right chars if n-gram length is more than 1
                    left_char = word[start - 1] if start > 0 else ''  # Left character before the n-gram
                    right_char = word[i + 1] if i + 1 < len(word) else ''  # Right character after the n-gram
                    left_chars.append(left_char)
                    right_chars.append(right_char)
                    results.append(ngram)
                    ngrams.append({'word': ngram, 'left_char': left_char, 'right_char': right_char, 'doc_id': note_id})

                else:
                    left_char = ''
                    right_char = ''
                # print(f'N-gram: "{ngram}", Left char: "{left_char}", Right char: "{right_char}"')

        return results, left_chars, right_chars, ngrams

    @staticmethod
    def remove_punctuation(text):
        # 使用正则表达式去除所有非中文字符、非字母、非数字的字符
        cleaned_text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z\s]', ' ', text)
        return cleaned_text

    # extract ngrams from both side
    def extract_neighbor(self, row):
        content = self.remove_punctuation(row['content'])
        char_list = [i for i in row['words'] if len(i) == 1]
        neighbor_char = self.find_max_length_word(content, char_list)
        return neighbor_char

    def extract_ngrams(self, row):
        # words = [("开", "     开榴莲15"), ("开", " 榴莲最终开出来92"), ("小", " 60块的小榴莲最终")]
        words, note_id = row['words_neighbor'], row['note_id']
        ngrams = []
        for word in words:
            keyword = word[0]
            long_word = word[1]
            left = long_word[:6].strip()
            right = long_word[3:].strip()
            # print(f'word: {word} left: {left} right: {right}')

            if right.startswith(keyword):
                right_index = 0
            else:
                right_index = 1

            if left.startswith(keyword):
                left_index = 0
            else:
                left_index = 4
            results, left_chars, right_chars, ngram = self.generate_ngrams(left, left_index, note_id, 'left')
            # print(f'left {left} ngrams :{ngram}')
            if ngram:
                ngrams.extend(ngram)

            results, left_chars, right_chars, ngram = self.generate_ngrams(right, right_index, note_id, 'right')
            # print(f'right {right} ngrams :{ngram}')
            if ngram:
                ngrams.extend(ngram)

        return ngrams


if __name__ == '__main__':
    scanner = NgramScanner()
    s = time.time()
    start = time.time()
    df = scanner.preprocess()
    print('\npreprocess cost time:', time.time() - start)
    df = scanner.cut_words(df)
    df['words_neighbor'] = df.apply(
        lambda x: scanner.extract_neighbor(x), axis=1)
    print('\nextract_neighbor cost time:', time.time() - start)
    df['ngrams'] = df.parallel_apply(scanner.extract_ngrams, axis=1)
    print(f'\ninit ngrams cost time: {time.time() - start}')

    df['ngrams_len'] = df['ngrams'].apply(len)
    filter_df = df[df['ngrams_len'] > 0]
    ngrams = filter_df.explode('ngrams')[['ngrams']]

    ngrams.to_csv('output/ngrams_10w_0828.csv', index=False)
    print(f'\nsave ngrams_10w cost time: {time.time() - start}')

    df.to_csv('output/keywords_0828.csv', index=False)
    print(f'\nsave origin_file cost time: {time.time() - start}')

    start = time.time()
    ngram_stat = NgramStatistics()
    print(f'\nexplode cost time: {time.time() - start}')

    # # 统计 ngram 词频
    # ngram_freq = NgramsFreqStat()
    # df = ngram_freq.init_freq(ngrams)
    # ngram_freq.save_freq(df)
    # print(f'\nsave ngram_freq cost time: {time.time() - start}')

    ngram_dict = ngrams.to_dict(orient='records')

    print('\nexplode cost time:', time.time() - start)
    processed_data = [item['ngrams'] for item in ngram_dict]

    result = ngram_stat.aggregate_words(processed_data, 30)
    print('\naggregate_words cost time:', time.time() - start)
    ngram_stat.save_to_csv(result)
    print('\nsave_term_freq_csv cost time:', time.time() - start)

    word_discoverer = WordDiscoverer()

    stat = NgramsFreqStat()

    word_df = word_discoverer.save_entropy_results()
    stat.save_char_freq()

    word_discoverer.save_mi_results()

    print('total cost time:', time.time() - s)
