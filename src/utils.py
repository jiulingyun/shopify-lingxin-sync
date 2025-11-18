#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
通用工具函数模块
"""

import pandas as pd
import re


def clean_text(value):
    """
    清理文本：去除连续空格、首尾空格
    
    Args:
        value: 文本值
    
    Returns:
        清理后的文本
    """
    if not value or pd.isna(value):
        return ''
    
    value_str = str(value)
    # 将连续的空格替换为单个空格
    value_str = re.sub(r'\s+', ' ', value_str)
    # 去除首尾空格
    return value_str.strip()


def truncate_field(value, max_length, field_name=''):
    """
    截断字段到指定长度
    
    Args:
        value: 字段值
        max_length: 最大长度
        field_name: 字段名称（用于警告信息）
    
    Returns:
        截断后的字符串
    """
    if not value or pd.isna(value):
        return ''
    
    value_str = str(value)
    if len(value_str) > max_length:
        return value_str[:max_length]
    return value_str


def detect_encoding(file_path):
    """
    检测文件编码
    
    Args:
        file_path: 文件路径
    
    Returns:
        编码名称
    """
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin1', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read()
            return encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    return 'utf-8'  # 默认返回utf-8
