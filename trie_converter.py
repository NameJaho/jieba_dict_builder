# scan a single text file to generate trie tree
import json
from pandarallel import pandarallel
from collections import defaultdict
import pandas as pd
import os
import utils
from trie import Trie

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
        self.trie = Trie(self.blacklist, self.word_length_min, self.word_length_max)

    def convert_file(self, file_content):
        trie_dict = self.trie.extract_words(file_content)
        return trie_dict

    @staticmethod
    def save_to_json(result, filename):
        output_file = os.path.join(OUTPUT_FOLDER, f'{filename}.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

    def convert_all(self, merged_all=True):
        directory = INPUT_FOLDER
        trie_list = []
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
                        df['trie_tree'] = df.parallel_apply(lambda x: self.convert_file(x['content']), axis=1)
                        print('Saving: ', filename)
                        trie_tree = df['trie_tree'].tolist()
                        trie_list.extend(trie_tree)
                        if not merged_all:
                            merged = self.trie.merge_trie(trie_tree)
                            self.save_to_json(merged, filename)
                    else:
                        print(f"Warning: {filename} missing 'content' column")
                except Exception as e:
                    print(f"Processing {filename} error: {str(e)}")

        if merged_all:
            # 合并所有的trie树
            merged = self.trie.merge_trie(trie_list)
            self.save_to_json(merged, 'all')


if __name__ == '__main__':
    tree_converter = TreeConverter()
    tree_converter.convert_all()
