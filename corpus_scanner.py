import re

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
        df = df[:10000]
        return df

    def filter_by_pos(self, char_list):
        filtered_list = []
        for index, (word, pos) in enumerate(char_list):
            if pos in self.blacklist.pos or len(word) != 1:
                continue

            if any(pos.startswith(prefix[:-1]) for prefix in self.blacklist.pos if prefix.endswith('*')):
                continue
            filtered_list.append((index, word, pos))
        return filtered_list

    def is_valid_char(self, word, pos):
        is_valid = True
        if pos in self.blacklist.pos or len(word) != 1:
            is_valid = False

        if any(pos.startswith(prefix[:-1]) for prefix in self.blacklist.pos if prefix.endswith('*')):
            is_valid = False

        if word in self.blacklist.word:
            is_valid = False

        return is_valid

    @staticmethod
    def remove_invalid_chars(text):
        # 使用正则表达式去除所有非中文字符、非字母、非数字的字符
        cleaned_text = re.sub(r'[^\u4e00-\u9fa5a-z0-9A-Z\s]', ' ', text)
        return cleaned_text.strip()

    def cut_words(self, df):
        df['valid_content'] = df['content'].apply(self.remove_invalid_chars)
        df['words'] = df['valid_content'].apply(lambda x: self.wc.pos_seg(x))
        return df

    def build_scan_result(self, df):
        df = self.cut_words(df)
        scan_result = []

        for _, row in df.iterrows():
            doc_id = row['doc_id']

            for index, word_pos in enumerate(row['words']):
                word = word_pos[0]
                pos = word_pos[1]
                if not self.is_valid_char(word, pos):
                    continue

                right_context = ''
                for i in range(1, 6):
                    if index + i >= len(row['words']):
                        break

                    next_word = row['words'][index + i][0]
                    if next_word == ' ':
                        break
                    right_context += next_word
                    if len(right_context) >= 5:
                        break

                # print('right context:', right_context)

                left_context = ''
                for i in range(1, 6):
                    if index - i < 0:
                        break
                    next_word = row['words'][index - i][0]
                    if next_word == ' ':
                        break
                    left_context = next_word + left_context
                    if len(left_context) >= 5:
                        break

                # print('left context:', left_context)

                result_dict = {'word': word, 'pos': pos, 'left_context': left_context, 'right_context': right_context, 'doc_id': doc_id}
                scan_result.append(result_dict)

        return scan_result

    def save_to_csv(self, scan_result):
        df = pd.DataFrame(scan_result)
        df.to_csv(self.output_file_path.scan_result, index=False)


if __name__ == '__main__':
    scanner = CorpusScanner()
    _df = scanner.preprocess()
    _df = scanner.cut_words(_df)
    _scan_result = scanner.build_scan_result(_df)
    scanner.save_to_csv(_scan_result)
