from dataclasses import dataclass
import yaml


@dataclass
class WordLength:
    min_len: int = 0
    max_len: int = 0


@dataclass
class Validation:
    doc_freq_threshold: int = 0
    term_freq_threshold: int = 0


@dataclass
class FileName:
    input_file: str = ''
    scan_result: str = ''


class ConfigLoader:
    def __init__(self):
        with open('config.yaml', 'r') as file:
            config_data = yaml.safe_load(file)

        self.blacklist = config_data.get('BLACKLIST', [])
        self.word_length = WordLength(**config_data.get('WORD_LENGTH', {}))
        self.validation = Validation(**config_data.get('VALIDATION', ''))
        self.filename = FileName(**config_data.get('FILENAME', ''))


# 使用例子
if __name__ == "__main__":
    config = ConfigLoader()
    print(config.blacklist)  # 访问黑名单列表
    print(config.word_length.min_len)  # 访问单词长度的最小值
    print(config.word_length.max_len)  # 访问单词长度的最大值
    print(config.validation.doc_freq_threshold)  # 访问文档频率阈值
    print(config.filename.input_file)
    print(config.filename.scan_result)
