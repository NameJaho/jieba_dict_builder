import json
import os
import time

INPUT_FOLDER = 'input'
OUTPUT_FOLDER = 'output'


class TreeMerger:

    def merge_dicts(self, dict1, dict2):
        result = {}
        for key in set(dict1) | set(dict2):
            if key in dict1 and key in dict2:
                result[key] = {k: dict1[key].get(k, 0) + dict2[key].get(k, 0) for k in
                               set(dict1[key]) | set(dict2[key])}
            elif key in dict1:
                result[key] = dict1[key]
            else:
                result[key] = dict2[key]
        return result

    def load_and_merge_json_files(self):
        merged_dict = {}
        for filename in os.listdir(OUTPUT_FOLDER):
            if filename.endswith('.json'):
                file_path = os.path.join(OUTPUT_FOLDER, filename)
                with open(file_path, 'r') as f:
                    current_dict = json.load(f)
                    merged_dict = self.merge_dicts(merged_dict, current_dict)
        self.save_to_json(merged_dict, 'merged_{time}')
        return merged_dict

    @staticmethod
    def save_to_json(result, filename):
        output_file = os.path.join(OUTPUT_FOLDER, f'{filename}.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
