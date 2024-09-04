from dataclasses import dataclass
import yaml

import utils


@dataclass
class Blacklist:
    word: list
    pos: list


@dataclass
class WordLength:
    min_len: int = 0
    max_len: int = 0


@dataclass
class Filter:
    bad_words: list
    doc_freq_threshold: int = 0
    entropy_threshold: float = 0.0
    mi_threshold: float = 0.0
    ignore_words: list = None


@dataclass
class OutputFile:
    ngrams_dict: str = ''
    neighbours_dict: str = ''
    entropy_result: str = ''
    char_freq: str = ''
    mi_result: str = ''


@dataclass
class InputFile:
    input_file: str = ''


class ConfigLoader:
    def __init__(self):
        root = utils.get_root_path()
        with open(root + '/jieba_dict_builder/config/config.yaml', 'r') as file:
            config_data = yaml.safe_load(file)

        self.blacklist = Blacklist(**config_data.get('BLACKLIST', {}))
        self.word_length = WordLength(**config_data.get('WORD_LENGTH', {}))
        self.filter = Filter(**config_data.get('FILTER', ''))
        self.output_file_path = OutputFile(**config_data.get('OUTPUT_FILE_PATH', ''))
        self.input_file_path = InputFile(**config_data.get('INPUT_FILE_PATH', ''))


# 使用例子
if __name__ == "__main__":
    config = ConfigLoader()
    print(config.blacklist.word)  # 访问黑名单列表
    print(config.blacklist.pos)  # 访问黑名单列表
    print(config.word_length.min_len)  # 访问单词长度的最小值
    print(config.word_length.max_len)  # 访问单词长度的最大值
    print(config.filter.doc_freq_threshold)  # 访问文档频率阈值
    print(config.output_file_path.scan_result)
    print(config.input_file_path.input_file)
