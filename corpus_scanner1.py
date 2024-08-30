import re
import sys
import time

import pandas as pd
from pandarallel import pandarallel
import warnings
from config.config_loader import ConfigLoader
from word_splitter.word_cutter import WordCutter

warnings.filterwarnings("ignore")
pandarallel.initialize()


class CorpusScanner(ConfigLoader):
    def __init__(self):
        super().__init__()
        self.wc = WordCutter()

    def preprocess(self):
        df = pd.read_csv(self.intput_file_path.input_file)
        df.dropna(subset=['content'], inplace=True)
        df = df[:100]
        return df

    def cut_words(self, df):
        df['remove_punc_content'] = df['content'].apply(self.remove_punctuation)
        df['words'] = df['remove_punc_content'].apply(lambda x: self.wc.pseg(x))
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
        cleaned_text = re.sub(r'[^\u4e00-\u9fa5a-z0-9A-Z\s]', ' ', text)
        return cleaned_text.strip()

    def find_5_length_words(self, words, filter_pos_char_list, remove_punc_content):

        # 根据用户要求，将索引也加入到结果中
        results = []

        for index, word, pos in filter_pos_char_list:
            # 获取该词左侧最多5个词，遇到空格则截断
            left_context = []
            i = index - 1
            while i >= max(0, index - 5) and words[i][1] != 'x':
                left_context.insert(0, words[i][0])  # 从左向右插入，包括索引
                i -= 1

            # 获取该词右侧最多5个词，遇到空格则截断
            right_context = []
            i = index + 1
            while i < min(len(words), index + 6) and words[i][1] != 'x':
                right_context.append(words[i][0])
                i += 1

            # 存储结果，包括当前词的索引
            results.append((index, word, left_context, right_context, remove_punc_content[index - 5: index + 5]))

        return results

    def filter_by_pos(self, char_list):
        filtered_list = []
        for index, (word, pos) in enumerate(char_list):
            if pos in self.blacklist.pos or len(word) != 1:
                continue
            # 检查以 'u' 开头的词性
            if any(pos.startswith(prefix[:-1]) for prefix in self.blacklist.pos if prefix.endswith('*')):
                continue
            filtered_list.append((index, word, pos))
        return filtered_list

    # extract ngrams from both side
    def extract_neighbor(self, row):
        char_list = [i for i in row['words'] if len(i[0]) == 1]
        filter_pos_char_list = self.filter_by_pos(char_list)
        neighbor_char = self.find_5_length_words(row['words'], filter_pos_char_list, row['remove_punc_content'])

        return neighbor_char, filter_pos_char_list

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
    scanner = CorpusScanner()
    s = time.time()
    start = time.time()
    df = scanner.preprocess()
    print('\npreprocess cost time:', time.time() - start)
    df = scanner.cut_words(df)
    df[['words_neighbor', 'char_list']] = df.apply(scanner.extract_neighbor, axis=1, result_type='expand' )
    print('\nextract_neighbor cost time:', time.time() - start)
    df[['doc_id', 'remove_punc_content', 'char_list']].to_csv(scanner.output_file_path.scan_result, index=False)
    sys.exit()
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
