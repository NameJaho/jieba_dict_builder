import csv
import pandas as pd
from pandarallel import pandarallel
import warnings
from config.config_loader import ConfigLoader

warnings.filterwarnings("ignore")
#pandarallel.initialize()


class NgramExtractor(ConfigLoader):
    def __init__(self):
        super().__init__()

    @staticmethod
    def generate_ngrams(char, left_context, right_context):
        ngrams = []
        left_len = len(left_context)
        right_len = len(right_context)

        # 裁剪上下文，确保不超过5个字
        if left_len > 5:
            left_context = left_context[-5:]
            left_len = 5
        if right_len > 5:
            right_context = right_context[:5]
            right_len = 5

        # 生成ngrams
        for i in range(2, 5):  # 修改为最长4个字
            if i <= left_len + right_len + 1:  # 加上char的长度
                for j in range(max(0, i - right_len - 1), min(left_len, i - 1) + 1):
                    ngram = left_context[left_len - j:] + char + right_context[:i - j - 1]
                    if len(ngram) > 1:
                        if len(right_context) > i - j - 1:
                            right_char = right_context[i - j - 1]
                        else:
                            right_char = ''

                        if len(left_context) > j:
                            left_char = left_context[left_len - j - 1]
                        else:
                            left_char = ''

                        ngrams.append({'ngram': ngram, 'left_char': left_char, 'right_char': right_char})
        return ngrams

    def process_row(self, row):
        char = row['char']
        left_context = str(row['left_context'])  # 确保是字符串类型
        right_context = str(row['right_context'])  # 确保是字符串类型
        doc_id = row['doc_id']

        if left_context or right_context:
            ngrams = self.generate_ngrams(char, left_context, right_context)
            results = []
            for ngram in ngrams:
                #print(ngram)
                results.append([ngram['ngram'], ngram['left_char'], ngram['right_char'], doc_id])
            return results
        return []

    def build_ngrams(self):
        df = pd.read_csv(self.output_file_path.scan_result)
        df.fillna('', inplace=True)
        results = df.apply(self.process_row, axis=1)
        return results

    def save_to_csv(self, results):
        with open(self.output_file_path.ngrams, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(['term', 'left_char', 'right_char', 'doc_id'])

            for result in results:
                if result:
                    writer.writerows(result)


if __name__ == '__main__':
    ngram_extractor = NgramExtractor()
    _results = ngram_extractor.build_ngrams()
    ngram_extractor.save_to_csv(_results)

