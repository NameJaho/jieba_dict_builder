import os
import unicodedata
import time

import pkg_resources
import yaml


def is_chinese(char):
    """
    判断一个字符是否是中文
    """
    # 获取字符的 Unicode 名称
    name = unicodedata.name(char, '')

    # 只检查是否为 CJK 统一表意文字（中日韩象形文字）
    return 'CJK UNIFIED IDEOGRAPH' in name


def get_root_path():
    package_path = pkg_resources.resource_filename(__name__, "")
    parent_path = os.path.dirname(package_path)
    return parent_path


def split_into_phrases(text, blacklist):
    """
    将文本切割成短语，以非中文字符为分隔符
    """
    phrases = []
    current_phrase = ""

    for char in text:
        if is_chinese(char) and char not in blacklist:
            current_phrase += char
        else:
            # if len(current_phrase) > 1:

            phrases.append(current_phrase)
            current_phrase = ""

    # 添加最后一个短语（如果存在）
    if current_phrase:
        phrases.append(current_phrase)

    return [i for i in phrases if len(i) > 0]


def load_config(file_path):
    # 加载 YAML 配置
    with open(file_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config


def cost_time(func):
    def fun(*args, **kwargs):
        t = time.perf_counter()
        result = func(*args, **kwargs)
        print(f'func {func.__name__} cost time:{time.perf_counter() - t:.8f} s')
        return result

    return fun


if __name__ == '__main__':
    s = '开榴莲;15.8一斤，60块的小榴莲，最终开出来924克的肉'
    s = '北动小公主萌兰“太子妃” ，白天有多调皮;北动小公主，萌兰“太子妃” ，熊猫白天有多调皮！'
    print(split_into_phrases(s,
                             ['的', '一', '了', '是', '我', '不', '在', '人', '们', '有', '来', '他', '这', '上', '着',
                              '个', '到', '啦', '呢', '说', '就', '去', '得', '也', '和', '那', '要', '下', '看', '时',
                              '过', '出', '啊', '么', '起', '你', '都', '把', '好', '还', '没', '为', '又', '可', '只',
                              '以', '会', '样', '年', '想', '能', '中', '十', '从', '自', '前', '它', '后', '然', '走',
                              '很', '像', '见', '两', '用', '她', '国', '进', '成', '回', '什', '边', '作', '对', '而',
                              '己', '些', '现', '候', '向', '给', '才', '与']
                             ))
