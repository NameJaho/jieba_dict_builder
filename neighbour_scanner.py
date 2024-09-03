import pandas as pd
import re
from collections import defaultdict, Counter
from config.config_loader import ConfigLoader
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import cost_time
import pickle


class NgramScanner(ConfigLoader):
    def __init__(self):
        super().__init__()
        ngrams_list = pickle.load(open('./output/ngrams_dict.pkl', 'rb'))
        ngrams_list = [ngram for ngram in ngrams_list if ngram['doc_freq'] > self.filter.doc_freq_threshold]

        self.ngrams_dict = {item['term']: {'term_freq': item['term_freq'], 'doc_freq': item['doc_freq']} for item in ngrams_list}
        self.neighbour_dict = defaultdict(
            lambda: {'term_freq': 0, 'doc_freq': 0, 'left_chars': Counter(), 'right_chars': Counter()})

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
        if term in self.ngrams_dict:
            return self.ngrams_dict[term]
        else:
            return None

    def process_row(self, row):
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
                    if pos > 0 and cleaned_content[pos - 1] != ' ':
                        left_char = cleaned_content[pos - 1]
                        self.neighbour_dict[ngram]['left_chars'][left_char] += 1
                    if pos + n < len(cleaned_content) and cleaned_content[pos + n] != ' ':
                        right_char = cleaned_content[pos + n]
                        self.neighbour_dict[ngram]['right_chars'][right_char] += 1

    @cost_time
    def scan_to_dict(self):
        df = pd.read_csv(self.input_file_path.input_file)

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.process_row, row) for _, row in df.iterrows()]
            for future in as_completed(futures):
                future.result()

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

    result = ngram_scanner.scan_to_dict()
    print(len(result))
    pickle.dump(result, open('./output/neighbour_dict.pkl', 'wb'))

    # neighbour_dict = pickle.load(open('./output/neighbour_dict.pkl', 'rb'))
    # print(neighbour_dict[10:20])