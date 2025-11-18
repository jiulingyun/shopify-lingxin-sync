#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
平台商品与领星ERP商品配对工具
"""

import pandas as pd
import os
from datetime import datetime
from difflib import SequenceMatcher


class ProductMatcher:
    """商品配对器"""
    
    def __init__(self):
        self.match_results = []
        self.unmatched_platform = []
        self.unmatched_erp = []
    
    def match(self, platform_file, erp_file, output_path=None, match_method='sku', shop_name=None):
        """
        执行商品配对
        
        Args:
            platform_file: 平台商品文件路径（CSV或Excel）
            erp_file: 领星ERP商品文件路径（CSV或Excel）
            output_path: 输出文件路径（可选）
            match_method: 配对方法 ('sku', 'title', 'barcode', 'fuzzy')
            shop_name: 店铺名称（必填），格式：店铺名称（不含平台前缀）
        
        Returns:
            输出文件路径
        """
        if not shop_name:
            raise ValueError(
                f"\n❌ 错误：缺少必填参数\n"
                f"   店铺名称是必填参数\n"
                f"   使用方法: python main.py match -p <平台文件> -e <ERP文件> -s <店铺名称>\n"
                f"   示例: python main.py match -p shopify.csv -e erp.xlsx -s MyStore"
            )
        
        # 检查文件是否存在
        if not os.path.exists(platform_file):
            raise FileNotFoundError(
                f"\n❌ 错误：找不到平台商品文件\n"
                f"   文件路径: {platform_file}\n"
                f"   请检查文件路径是否正确"
            )
        
        if not os.path.exists(erp_file):
            raise FileNotFoundError(
                f"\n❌ 错误：找不到ERP商品文件\n"
                f"   文件路径: {erp_file}\n"
                f"   请检查文件路径是否正确"
            )
        
        print(f"正在读取平台商品数据: {platform_file}")
        platform_df = self._read_file(platform_file)
        
        print(f"正在读取领星ERP商品数据: {erp_file}")
        erp_df = self._read_file(erp_file)
        
        print(f"平台商品数量: {len(platform_df)}")
        print(f"ERP商品数量: {len(erp_df)}")
        
        # 执行配对
        if match_method == 'sku':
            results_df = self._match_by_sku(platform_df, erp_df)
        elif match_method == 'title':
            results_df = self._match_by_title(platform_df, erp_df)
        elif match_method == 'barcode':
            results_df = self._match_by_barcode(platform_df, erp_df)
        elif match_method == 'fuzzy':
            results_df = self._match_fuzzy(platform_df, erp_df)
        else:
            raise ValueError(f"不支持的配对方法: {match_method}")
        
        # 生成输出路径
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = os.path.dirname(platform_file)
            output_path = os.path.join(output_dir, f'lingxin_msku_match_{timestamp}.xlsx')
        
        # 转换为领星MSKU配对格式
        lingxin_df = self._convert_to_lingxin_format(results_df, shop_name)
        
        # 写入结果
        self._write_lingxin_results(results_df, lingxin_df, output_path, shop_name)
        
        # 打印统计信息
        self._print_statistics(results_df)
        
        return output_path
    
    def _read_file(self, file_path):
        """读取文件（支持CSV和Excel）"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.csv':
            # 尝试多种编码
            encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']
            for encoding in encodings:
                try:
                    return pd.read_csv(file_path, encoding=encoding)
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    raise Exception(
                        f"\n❌ 错误：读取CSV文件失败\n"
                        f"   文件: {file_path}\n"
                        f"   原因: {str(e)}\n"
                        f"   请确保文件格式正确"
                    )
            raise Exception(
                f"\n❌ 错误：无法识别CSV文件编码\n"
                f"   文件: {file_path}\n"
                f"   已尝试编码: {', '.join(encodings)}\n"
                f"   建议：使用UTF-8编码保存CSV文件"
            )
        
        elif ext in ['.xlsx', '.xls']:
            try:
                return pd.read_excel(file_path)
            except Exception as e:
                raise Exception(
                    f"\n❌ 错误：读取Excel文件失败\n"
                    f"   文件: {file_path}\n"
                    f"   原因: {str(e)}\n"
                    f"   请确保文件格式正确且未被占用"
                )
        
        else:
            raise ValueError(
                f"\n❌ 错误：不支持的文件格式\n"
                f"   文件: {file_path}\n"
                f"   格式: {ext}\n"
                f"   支持的格式: .csv, .xlsx, .xls"
            )
    
    def _match_by_sku(self, platform_df, erp_df):
        """基于SKU配对"""
        print("\n使用SKU进行配对...")
        
        # 检测SKU列名
        platform_sku_col = self._detect_sku_column(platform_df)
        erp_sku_col = self._detect_sku_column(erp_df)
        
        if not platform_sku_col:
            raise ValueError(
                f"\n❌ 错误：无法检测到平台商品的SKU列\n"
                f"   请确保文件中包含以下列名之一:\n"
                f"   - SKU, sku, *SKU\n"
                f"   - Variant SKU, Product SKU\n"
                f"   - 商品SKU"
            )
        
        if not erp_sku_col:
            raise ValueError(
                f"\n❌ 错误：无法检测到ERP商品的SKU列\n"
                f"   请确保文件中包含以下列名之一:\n"
                f"   - SKU, sku, *SKU\n"
                f"   - Variant SKU, Product SKU\n"
                f"   - 商品SKU"
            )
        
        print(f"平台SKU列: {platform_sku_col}")
        print(f"ERP SKU列: {erp_sku_col}")
        
        # 创建ERP的SKU索引
        erp_dict = {}
        for idx, row in erp_df.iterrows():
            sku = str(row[erp_sku_col]).strip() if pd.notna(row[erp_sku_col]) else ''
            if sku:
                erp_dict[sku] = row
        
        # 配对
        results = []
        for idx, platform_row in platform_df.iterrows():
            platform_sku = str(platform_row[platform_sku_col]).strip() if pd.notna(platform_row[platform_sku_col]) else ''
            
            if platform_sku and platform_sku in erp_dict:
                erp_row = erp_dict[platform_sku]
                results.append({
                    '配对状态': '已配对',
                    '平台SKU': platform_sku,
                    'ERP SKU': platform_sku,
                    '平台品名': platform_row.get('Title', platform_row.get('品名', '')),
                    'ERP品名': erp_row.get('品名', erp_row.get('Title', '')),
                    '匹配度': '100%',
                    '配对方法': 'SKU精确匹配'
                })
            else:
                results.append({
                    '配对状态': '未配对',
                    '平台SKU': platform_sku,
                    'ERP SKU': '',
                    '平台品名': platform_row.get('Title', platform_row.get('品名', '')),
                    'ERP品名': '',
                    '匹配度': '0%',
                    '配对方法': ''
                })
        
        return pd.DataFrame(results)
    
    def _match_by_title(self, platform_df, erp_df):
        """基于品名配对"""
        print("\n使用品名进行配对...")
        
        # 检测品名列
        platform_title_col = self._detect_title_column(platform_df)
        erp_title_col = self._detect_title_column(erp_df)
        
        if not platform_title_col:
            raise ValueError(
                f"\n❌ 错误：无法检测到平台商品的品名列\n"
                f"   请确保文件中包含以下列名之一:\n"
                f"   - Title, title\n"
                f"   - 品名, 产品名称, 商品名称\n"
                f"   - Product Name"
            )
        
        if not erp_title_col:
            raise ValueError(
                f"\n❌ 错误：无法检测到ERP商品的品名列\n"
                f"   请确保文件中包含以下列名之一:\n"
                f"   - Title, title\n"
                f"   - 品名, 产品名称, 商品名称\n"
                f"   - Product Name"
            )
        
        print(f"平台品名列: {platform_title_col}")
        print(f"ERP品名列: {erp_title_col}")
        
        # 创建ERP的品名索引
        erp_dict = {}
        for idx, row in erp_df.iterrows():
            title = str(row[erp_title_col]).strip().lower() if pd.notna(row[erp_title_col]) else ''
            if title:
                erp_dict[title] = row
        
        # 配对
        results = []
        for idx, platform_row in platform_df.iterrows():
            platform_title = str(platform_row[platform_title_col]).strip().lower() if pd.notna(platform_row[platform_title_col]) else ''
            
            if platform_title and platform_title in erp_dict:
                erp_row = erp_dict[platform_title]
                results.append({
                    '配对状态': '已配对',
                    '平台SKU': platform_row.get('Variant SKU', platform_row.get('*SKU', '')),
                    'ERP SKU': erp_row.get('*SKU', erp_row.get('SKU', '')),
                    '平台品名': platform_row[platform_title_col],
                    'ERP品名': erp_row[erp_title_col],
                    '匹配度': '100%',
                    '配对方法': '品名精确匹配'
                })
            else:
                results.append({
                    '配对状态': '未配对',
                    '平台SKU': platform_row.get('Variant SKU', platform_row.get('*SKU', '')),
                    'ERP SKU': '',
                    '平台品名': platform_row[platform_title_col],
                    'ERP品名': '',
                    '匹配度': '0%',
                    '配对方法': ''
                })
        
        return pd.DataFrame(results)
    
    def _match_by_barcode(self, platform_df, erp_df):
        """基于条形码配对"""
        print("\n使用条形码进行配对...")
        
        # 检测条形码列
        platform_barcode_col = self._detect_barcode_column(platform_df)
        erp_barcode_col = self._detect_barcode_column(erp_df)
        
        if not platform_barcode_col:
            raise ValueError(
                f"\n❌ 错误：无法检测到平台商品的条形码列\n"
                f"   请确保文件中包含以下列名之一:\n"
                f"   - Barcode, barcode\n"
                f"   - Variant Barcode\n"
                f"   - 条形码, 识别码"
            )
        
        if not erp_barcode_col:
            raise ValueError(
                f"\n❌ 错误：无法检测到ERP商品的条形码列\n"
                f"   请确保文件中包含以下列名之一:\n"
                f"   - Barcode, barcode\n"
                f"   - Variant Barcode\n"
                f"   - 条形码, 识别码"
            )
        
        # 创建ERP的条形码索引
        erp_dict = {}
        for idx, row in erp_df.iterrows():
            barcode = str(row[erp_barcode_col]).strip() if pd.notna(row[erp_barcode_col]) else ''
            if barcode:
                erp_dict[barcode] = row
        
        # 配对
        results = []
        for idx, platform_row in platform_df.iterrows():
            platform_barcode = str(platform_row[platform_barcode_col]).strip() if pd.notna(platform_row[platform_barcode_col]) else ''
            
            if platform_barcode and platform_barcode in erp_dict:
                erp_row = erp_dict[platform_barcode]
                results.append({
                    '配对状态': '已配对',
                    '平台SKU': platform_row.get('Variant SKU', ''),
                    'ERP SKU': erp_row.get('*SKU', ''),
                    '平台品名': platform_row.get('Title', ''),
                    'ERP品名': erp_row.get('品名', ''),
                    '匹配度': '100%',
                    '配对方法': '条形码精确匹配'
                })
            else:
                results.append({
                    '配对状态': '未配对',
                    '平台SKU': platform_row.get('Variant SKU', ''),
                    'ERP SKU': '',
                    '平台品名': platform_row.get('Title', ''),
                    'ERP品名': '',
                    '匹配度': '0%',
                    '配对方法': ''
                })
        
        return pd.DataFrame(results)
    
    def _match_fuzzy(self, platform_df, erp_df, threshold=0.8):
        """模糊匹配（基于品名相似度）"""
        print(f"\n使用模糊匹配（相似度阈值: {threshold*100}%）...")
        
        platform_title_col = self._detect_title_column(platform_df)
        erp_title_col = self._detect_title_column(erp_df)
        
        if not platform_title_col:
            raise ValueError(
                f"\n❌ 错误：无法检测到平台商品的品名列\n"
                f"   模糊匹配需要品名字段\n"
                f"   请确保文件中包含以下列名之一:\n"
                f"   - Title, title\n"
                f"   - 品名, 产品名称, 商品名称"
            )
        
        if not erp_title_col:
            raise ValueError(
                f"\n❌ 错误：无法检测到ERP商品的品名列\n"
                f"   模糊匹配需要品名字段\n"
                f"   请确保文件中包含以下列名之一:\n"
                f"   - Title, title\n"
                f"   - 品名, 产品名称, 商品名称"
            )
        
        results = []
        for idx, platform_row in platform_df.iterrows():
            platform_title = str(platform_row[platform_title_col]).strip() if pd.notna(platform_row[platform_title_col]) else ''
            
            if not platform_title:
                results.append({
                    '配对状态': '未配对',
                    '平台SKU': platform_row.get('Variant SKU', ''),
                    'ERP SKU': '',
                    '平台品名': '',
                    'ERP品名': '',
                    '匹配度': '0%',
                    '配对方法': ''
                })
                continue
            
            # 查找最佳匹配
            best_match = None
            best_ratio = 0
            
            for erp_idx, erp_row in erp_df.iterrows():
                erp_title = str(erp_row[erp_title_col]).strip() if pd.notna(erp_row[erp_title_col]) else ''
                if not erp_title:
                    continue
                
                ratio = SequenceMatcher(None, platform_title.lower(), erp_title.lower()).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = erp_row
            
            if best_match is not None and best_ratio >= threshold:
                results.append({
                    '配对状态': '已配对',
                    '平台SKU': platform_row.get('Variant SKU', ''),
                    'ERP SKU': best_match.get('*SKU', ''),
                    '平台品名': platform_title,
                    'ERP品名': best_match[erp_title_col],
                    '匹配度': f'{best_ratio*100:.1f}%',
                    '配对方法': '模糊匹配'
                })
            else:
                results.append({
                    '配对状态': '未配对',
                    '平台SKU': platform_row.get('Variant SKU', ''),
                    'ERP SKU': '',
                    '平台品名': platform_title,
                    'ERP品名': '',
                    '匹配度': f'{best_ratio*100:.1f}%' if best_match else '0%',
                    '配对方法': ''
                })
        
        return pd.DataFrame(results)
    
    def _detect_sku_column(self, df):
        """检测SKU列名"""
        possible_names = ['SKU', 'sku', '*SKU', 'Variant SKU', 'Product SKU', '商品SKU']
        for col in df.columns:
            if col in possible_names or 'sku' in col.lower():
                return col
        return None
    
    def _detect_title_column(self, df):
        """检测品名列名"""
        possible_names = ['Title', 'title', '品名', 'Product Name', '商品名称', '产品名称']
        for col in df.columns:
            if col in possible_names:
                return col
        return None
    
    def _detect_barcode_column(self, df):
        """检测条形码列名"""
        possible_names = ['Barcode', 'barcode', '条形码', 'Variant Barcode', '识别码']
        for col in df.columns:
            if col in possible_names or 'barcode' in col.lower():
                return col
        return None
    
    def _convert_to_lingxin_format(self, df, shop_name):
        """
        转换为领星MSKU配对格式
        
        Args:
            df: 配对结果DataFrame
            shop_name: 店铺名称
        
        Returns:
            领星格式的DataFrame
        """
        lingxin_data = []
        
        # 只处理已配对的商品
        matched_df = df[df['配对状态'] == '已配对']
        
        for idx, row in matched_df.iterrows():
            lingxin_data.append({
                '*MSKU': row['平台SKU'],  # 平台SKU作为MSKU
                '*SKU': row['ERP SKU'],    # ERP SKU
                '店铺': f'[Shopify].{shop_name}'  # 店铺格式：[平台].店铺名
            })
        
        return pd.DataFrame(lingxin_data, columns=['*MSKU', '*SKU', '店铺'])
    
    def _write_lingxin_results(self, results_df, lingxin_df, output_path, shop_name):
        """
        写入领星MSKU配对结果
        
        Args:
            results_df: 原始配对结果
            lingxin_df: 领星格式的配对结果
            output_path: 输出文件路径
            shop_name: 店铺名称
        """
        print(f"\n正在写入领星MSKU配对文件: {output_path}")
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Sheet1: 领星MSKU配对导入格式（必须是第一个sheet）
            lingxin_df.to_excel(writer, index=False, sheet_name='Sheet1')
            
            # 配对详情（供参考）
            results_df.to_excel(writer, index=False, sheet_name='配对详情')
            
            # 已配对的商品
            matched_df = results_df[results_df['配对状态'] == '已配对']
            if len(matched_df) > 0:
                matched_df.to_excel(writer, index=False, sheet_name='已配对')
            
            # 未配对的商品
            unmatched_df = results_df[results_df['配对状态'] == '未配对']
            if len(unmatched_df) > 0:
                unmatched_df.to_excel(writer, index=False, sheet_name='未配对')
        
        print(f"✓ 领星MSKU配对格式已生成")
        print(f"  - Sheet1: 领星导入格式（{len(lingxin_df)} 条配对记录）")
        print(f"  - 店铺: [Shopify].{shop_name}")
    
    def _write_results(self, df, output_path):
        """写入配对结果（旧版方法，保留兼容）"""
        print(f"\n正在写入配对结果: {output_path}")
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 写入配对结果
            df.to_excel(writer, index=False, sheet_name='配对结果')
            
            # 写入已配对的商品
            matched_df = df[df['配对状态'] == '已配对']
            if len(matched_df) > 0:
                matched_df.to_excel(writer, index=False, sheet_name='已配对')
            
            # 写入未配对的商品
            unmatched_df = df[df['配对状态'] == '未配对']
            if len(unmatched_df) > 0:
                unmatched_df.to_excel(writer, index=False, sheet_name='未配对')
    
    def _print_statistics(self, df):
        """打印统计信息"""
        total = len(df)
        matched = len(df[df['配对状态'] == '已配对'])
        unmatched = total - matched
        match_rate = (matched / total * 100) if total > 0 else 0
        
        print(f"\n{'='*50}")
        print(f"配对统计")
        print(f"{'='*50}")
        print(f"总商品数: {total}")
        print(f"已配对: {matched} ({match_rate:.1f}%)")
        print(f"未配对: {unmatched} ({100-match_rate:.1f}%)")
        print(f"{'='*50}\n")
