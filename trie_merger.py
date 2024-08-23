import json
import os
import time
from trie import Trie
import utils

INPUT_FOLDER = 'output'
OUTPUT_FOLDER = 'data'
CONFIG_FILE = 'config/config.yaml'


class TreeMerger:
    def __init__(self):
        config = utils.load_config(CONFIG_FILE)

        self.blacklist = config['BLACKLIST']
        self.word_length_min = config['WORD_LENGTH']['min_len']
        self.word_length_max = config['WORD_LENGTH']['max_len']
        self.trie = Trie(self.blacklist, self.word_length_min, self.word_length_max)

    # def merge_dicts(self, dict1, dict2):
    #     result = {}
    #     for key in set(dict1) | set(dict2):
    #         if key in dict1 and key in dict2:
    #             result[key] = {k: dict1[key].get(k, 0) + dict2[key].get(k, 0) for k in
    #                            set(dict1[key]) | set(dict2[key])}
    #         elif key in dict1:
    #             result[key] = dict1[key]
    #         else:
    #             result[key] = dict2[key]
    #     return result
    #
    # def load_and_merge_json_files(self):
    #     merged_dict = {}
    #     for filename in os.listdir(OUTPUT_FOLDER):
    #         if filename.endswith('.json'):
    #             file_path = os.path.join(OUTPUT_FOLDER, filename)
    #             with open(file_path, 'r') as f:
    #                 current_dict = json.load(f)
    #                 merged_dict = self.merge_dicts(merged_dict, current_dict)
    #     self.save_to_json(merged_dict, 'merged_{time}')
    #     return merged_dict
    #
    # @staticmethod
    # def save_to_json(result, filename):
    #     output_file = os.path.join(OUTPUT_FOLDER, f'{filename}.json')
    #     with open(output_file, 'w', encoding='utf-8') as f:
    #         json.dump(result, f, ensure_ascii=False, indent=4)
    def merge_all_tries(self, directory_path):
        final_trie = Trie(self.blacklist, self.word_length_min, self.word_length_max)
        for filename in os.listdir(directory_path):
            if filename.endswith('.json'):
                file_path = os.path.join(directory_path, filename)
                trie = final_trie.load_from_file(file_path)
                final_trie.merge_trie(trie)
        # final_trie.prune_trie()
        return final_trie

    @staticmethod
    def save_to_file(trie, file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(trie.trie_dict, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    merger = TreeMerger()
    final_trie = merger.merge_all_tries(INPUT_FOLDER)
    merger.save_to_file(final_trie, f'{OUTPUT_FOLDER}/final_trie.json')
