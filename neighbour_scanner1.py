import pandas as pd
import re
from collections import defaultdict, Counter
from config.config_loader import ConfigLoader
import pickle
from utils import cost_time


class NgramScanner(ConfigLoader):
    def __init__(self):
        super().__init__()
        self.ngrams_dict = pickle.load(open('./ngrams.pkl', 'rb'))
        self.neighbour_dict = defaultdict(lambda: {'term_freq': 0, 'doc_freq': 0, 'left_chars': Counter(), 'right_chars': Counter()})

    @staticmethod
    def remove_invalid_chars(text):
        # 使用正则表达式去除所有非中文字符、非字母、非数字的字符
        cleaned_text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', ' ', text)
        return cleaned_text.strip()

    @staticmethod
    def extract_ngrams(text, n):
        ngrams = []
        for i in range(len(text) - n + 1):
            ngram = text[i:i+n]
            if len(ngram.replace(' ', '')) == n:
                ngrams.append((ngram, i))  # 记录ngram及其位置
        return ngrams

    def find_term_in_dict(self, term):
        # check if term is in ngrams.pkl, if yes return dict item
        item = None
        for item in self.ngrams_dict:
            if item['term'] == term:
                item = item
                break
        return item

    @cost_time
    def scan_to_dict(self):
        df = pd.read_csv(self.input_file_path.input_file)
        df = df.head(100000)  # 只处理前2行，可以根据需要调整

        for index, row in df.iterrows():
            content = row['content']
            cleaned_content = self.remove_invalid_chars(content)

            for n in range(2, 5):
                ngrams = self.extract_ngrams(cleaned_content, n)
                for ngram, pos in ngrams:
                    term_item = self.find_term_in_dict(ngram)
                    if term_item is not None:
                        self.neighbour_dict[ngram]['term_freq'] = term_item['term_freq']
                        self.neighbour_dict[ngram]['doc_freq'] = term_item['doc_freq']
                        # 获取左右邻字
                        if pos > 0 and cleaned_content[pos-1] != ' ':
                            left_char = cleaned_content[pos-1]
                            self.neighbour_dict[ngram]['left_chars'][left_char] += 1
                        if pos + n < len(cleaned_content) and cleaned_content[pos+n] != ' ':
                            right_char = cleaned_content[pos+n]
                            self.neighbour_dict[ngram]['right_chars'][right_char] += 1

        # 转换为最终的字典格式
        result_dict = []
        for term, data in self.neighbour_dict.items():
            left_chars = [{'char': char, 'freq': freq} for char, freq in data['left_chars'].items()]
            right_chars = [{'char': char, 'freq': freq} for char, freq in data['right_chars'].items()]
            result_dict.append({
                'term': term,
                'term_freq': data['term_freq'],
                'doc_freq': data['doc_freq'],
                'left_chars': left_chars,
                'right_chars': right_chars
            })

        return result_dict


if __name__ == '__main__':
    ngram_scanner = NgramScanner()
    text = '今天天气真好 明天也不错'

    result = ngram_scanner.scan_to_dict()
    pickle.dump(result, open('neighbour_dict.pkl', 'wb'))