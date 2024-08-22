import unicodedata
import re


def is_chinese(char):
    """
    判断一个字符是否是中文
    """
    # 获取字符的 Unicode 名称
    name = unicodedata.name(char, '')

    # 只检查是否为 CJK 统一表意文字（中日韩象形文字）
    return 'CJK UNIFIED IDEOGRAPH' in name


def split_into_phrases(text):
    """
    将文本切割成短语，以非中文字符为分隔符
    """
    phrases = []
    current_phrase = ""

    for char in text:
        if is_chinese(char):
            current_phrase += char
        else:
            if current_phrase:
                phrases.append(current_phrase)
                current_phrase = ""

    # 添加最后一个短语（如果存在）
    if current_phrase:
        phrases.append(current_phrase)

    return phrases


if __name__ == '__main__':
    s = '我是123中国人@汉子-三个人,还有%#和band也是。'
    print(split_into_phrases(s))
