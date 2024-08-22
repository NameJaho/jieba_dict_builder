# scan a single text file to generate trie tree
import json
from pandarallel import pandarallel
from collections import defaultdict
import pandas as pd
import os
import utils

pandarallel.initialize(progress_bar=True)

INPUT_FOLDER = 'input'
OUTPUT_FOLDER = 'output'
CONFIG_FILE = 'config/config.yaml'


class TreeConverter:

    def __init__(self):
        config = utils.load_config(CONFIG_FILE)

        self.blacklist = config['BLACKLIST']
        self.word_length_min = config['WORD_LENGTH']['min_len']
        self.word_length_max = config['WORD_LENGTH']['max_len']

    def extract_words(self, content):
        # 使用正则表达式切割字符串
        # 初始化结果字典
        result = defaultdict(lambda: defaultdict(int))

        # 需要排除的字符
        exclude_chars = self.blacklist

        phrases = utils.split_into_phrases(content)
        # 遍历每个段落，提取词语并统计频率
        for phrase in phrases:
            for i in range(len(phrase)):
                for j in range(self.word_length_min, self.word_length_max):
                    if i + j <= len(phrase):
                        word = phrase[i:i + j]
                        first_char = word[0]
                        if first_char not in exclude_chars:
                            result[first_char][word] += 1

        # 将结果转换为普通字典
        return {k: dict(v) for k, v in result.items()}

    @staticmethod
    def save_to_json(result, filename):
        output_file = os.path.join(OUTPUT_FOLDER, f'{filename}.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

    def convert_all(self):
        directory = INPUT_FOLDER

        # 遍历目录中的所有文件
        for filename in os.listdir(directory):
            if filename.endswith('.csv'):
                file_path = os.path.join(directory, filename)
                print('Processing: ', file_path)
                try:
                    # 读取CSV文件
                    df = pd.read_csv(file_path)

                    # 检查是否存在 'content' 列
                    if 'content' in df.columns:
                        content = df['content'].values[0]
                        print('Converting: ', filename)
                        trie_tree = self.extract_words(content)
                        print('Saving: ', filename)
                        self.save_to_json(trie_tree, filename)
                    else:
                        print(f"Warning: {filename} missing 'content' column")
                except Exception as e:
                    print(f"Processing {filename} error: {str(e)}")


if __name__ == '__main__':
    tree_converter = TreeConverter()
    tree_converter.convert_all()
