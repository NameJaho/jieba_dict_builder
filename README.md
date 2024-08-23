# Jieba Dict Builder

## About the Project
jieba内置字典有三十多万词, 语料来源于1998年人民日报, 数据比较陈旧, 而且和实际应用的语境可能也不匹配。
所有需要一个工具能够稳定高效的用自己的语料来生成字典。

### 黑名单
定义了几个高频单字:的,了,我,是

可以在config/config.yaml中修改

### 成词规则
仅考虑2-4字的中文组合,不考虑英文和数字

可以在config/config.yaml中修改成词长度

### 统计规则
所有的非中文字符包括标点，英文，数字，换行符作为分割符来断句

## Installation
1. Clone the repo
   ```sh
   git clone git@github.com:Jeru2023/jieba_dict_builder.git
   ```

2. Install packages
   ```sh
   install -r requirements.txt
   ```
   
3. Prepare your own corpus

Put csv files in input folder, only 'content' column required.

## Usage

## Description

input - 存放所有的csv格式语料文本

output - 存放所有语料对应的前缀树

data - 存放聚合后的前缀树和最终生成的字典

config - 存放配置文件config.yaml

trie_converter.py - 扫描input中单个文本文件生成前缀树保存到output

trie_merger.py - 合并所有的前缀树保存到data

trie.py - 前缀树的节点添加，合并等操作

dict_builder.py - 通过合并的前缀树生成最终字典
