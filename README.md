# Jieba Dict Builder

## About the Project
jieba内置字典有三十多万词, 语料来源于1998年人民日报, 数据比较陈旧, 而且和实际应用的语境可能也不匹配。
所有需要一个工具能够稳定高效的用自己的语料来生成字典。

### 黑名单
定义了几个高频单字:的,了,我,是

可以在config/config.yaml中修改

### 成词规则
仅考虑2-4字的中文组合,不考虑英文和数字

可以在config/config.yaml中修改

## Installation

## Usage

## Description

input - 存放所有的csv格式语料文本

output - 存放所有语料对应的前缀树

data - 存放聚合后的前缀树和最终生成的字典

config - 存放配置文件config.yaml

scanner - 扫描单个文本文件生成前缀树
