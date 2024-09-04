import pandas as pd
import re
from collections import defaultdict
from config.config_loader import ConfigLoader
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import cost_time
import pickle


class NgramScanner(ConfigLoader):
    def __init__(self):
        super().__init__()
        self.ngram_dict = defaultdict(lambda: {'term_freq': 0, 'doc_freq': 0})

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

    def process_row(self, row):
        doc_id = row['doc_id']
        content = row['content']
        cleaned_content = self.remove_invalid_chars(content)

        doc_ngrams = set()
        for n in range(2, 5):
            ngrams = self.extract_ngrams(cleaned_content, n)
            for ngram, pos in ngrams:
                if ngram not in doc_ngrams:
                    doc_ngrams.add(ngram)
                    self.ngram_dict[ngram]['term_freq'] += 1
                    self.ngram_dict[ngram]['doc_freq'] += 1
                else:
                    self.ngram_dict[ngram]['term_freq'] += 1

    @cost_time
    def scan_to_dict(self):
        df = pd.read_csv(self.input_file_path.input_file)

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.process_row, row) for _, row in df.iterrows()]
            for future in as_completed(futures):
                future.result()

        # 转换为最终的字典格式
        result_dict = []
        for term, data in self.ngram_dict.items():
            result_dict.append({
                'term': term,
                'term_freq': data['term_freq'],
                'doc_freq': data['doc_freq'],
            })

        return result_dict


if __name__ == '__main__':
    ngram_scanner = NgramScanner()

    # result = ngram_scanner.scan_to_dict()
    # print(len(result))
    # pickle.dump(result, open('./output/ngrams_dict.pkl', 'wb'))

    ngrams_dict = pickle.load(open('./output/ngrams_dict.pkl', 'rb'))
    print(ngrams_dict[10:20])

    for item in ngrams_dict:
        if item['term'] == '麦卢卡':
            print(item)
