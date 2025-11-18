#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Shopify产品转换为领星ERP导入格式的核心模块
"""

import pandas as pd
import os
import re
from datetime import datetime
from .utils import clean_text, truncate_field


class ShopifyToLingxinConverter:
    """Shopify到领星ERP的转换器"""
    
    # 领星ERP字段长度限制
    FIELD_LIMITS = {
        '*SKU': 50,
        '品名': 200,
        '产品类型': 50,
        '品牌': 50,
        '产品标签': 200,
        '产品描述': 1000,
        '图片链接': 500,
        '识别码': 50,
        '产品材质': 50,
        '一级分类': 50,
        '二级分类': 50,
        '三级分类': 50,
    }
    
    # 状态映射
    STATUS_MAP = {
        'active': '在售',
        'draft': '开发中',
        'archived': '停售'
    }
    
    def __init__(self):
        self.sku_warnings = []
        self.duplicate_count = 0
        
    def convert(self, shopify_csv_path, output_path=None):
        """
        执行转换
        
        Args:
            shopify_csv_path: Shopify导出的CSV文件路径
            output_path: 输出文件路径（可选）
        
        Returns:
            输出文件路径
        """
        # 检查输入文件是否存在
        if not os.path.exists(shopify_csv_path):
            raise FileNotFoundError(
                f"\n❌ 错误：找不到Shopify导出文件\n"
                f"   文件路径: {shopify_csv_path}\n"
                f"   请检查文件路径是否正确"
            )
        
        print(f"正在读取Shopify产品数据: {shopify_csv_path}")
        
        # 读取CSV文件
        shopify_df = self._read_shopify_csv(shopify_csv_path)
        
        # 过滤空行
        shopify_df = shopify_df[shopify_df['Handle'].notna()]
        print(f"共读取 {len(shopify_df)} 条产品数据")
        
        # 转换数据
        lingxin_df = self._transform_data(shopify_df)
        
        # 去重
        lingxin_df = self._remove_duplicates(lingxin_df)
        
        # 生成输出路径
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = os.path.dirname(shopify_csv_path)
            output_path = os.path.join(output_dir, f'lingxin_import_{timestamp}.xlsx')
        
        # 写入Excel
        self._write_excel(lingxin_df, output_path)
        
        # 显示警告信息
        self._print_warnings()
        
        print(f"转换完成！共转换 {len(lingxin_df)} 条产品")
        print(f"输出文件: {output_path}")
        
        return output_path
    
    def _read_shopify_csv(self, file_path):
        """读取Shopify CSV文件，自动检测编码"""
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin1', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                print(f"成功使用 {encoding} 编码读取文件")
                return df
            except UnicodeDecodeError:
                continue
            except Exception as e:
                raise Exception(
                    f"\n❌ 错误：读取CSV文件失败\n"
                    f"   原因: {str(e)}\n"
                    f"   请确保文件格式正确"
                )
        
        raise Exception(
            f"\n❌ 错误：无法识别CSV文件编码\n"
            f"   已尝试编码: {', '.join(encodings)}\n"
            f"   建议：使用UTF-8编码保存CSV文件"
        )
    
    def _transform_data(self, shopify_df):
        """转换数据格式"""
        # 定义领星ERP的列头
        lingxin_columns = [
            '*SKU', '品名', '产品类型', '单品SKU1', '关联数量1', '单位加工费', '加工备注',
            '关联单品成本', '识别码', '状态', '型号', '单位', '产品材质', '一级分类',
            '二级分类', '三级分类', '品牌', '产品标签', '开发人', '产品负责人', '产品描述',
            '图片链接', '采购员', '采购交期', '采购成本(CNY)', '采购备注', '单品规格长',
            '单品规格宽', '单品规格高', '单品规格单位', '单品净重', '单品净重单位',
            '单品毛重', '单品毛重单位', '包装规格长', '包装规格宽', '包装规格高',
            '包装规格单位', '外箱规格长', '外箱规格宽', '外箱规格高', '外箱规格单位',
            '单箱数量(pcs)', '单箱重量', '单箱重量单位', '供应商名称', '币种', '含税',
            '税率', '最小采购量', '单价', '含税单价', '交期', '采购链接', '报价备注',
            '默认质检方式', '质检模板', '中文报关名', '英文报关名', '中文材质', '英文材质',
            '中文用途', '英文用途', '品牌类型', '出口享惠情况', '内部编码', '特殊属性',
            '报关单价', '报关单价币种', '报关HSCODE', '报关型号', '原产国(地区)',
            '境内货源地', '报关单位', '其他申报要素', '征免', '生产销售企业名称',
            '生产销售企业代码', '清关型号', '配货备注', '织造方式', '默认清关HSCODE',
            '默认清关单价', '默认清关单价币种', '默认清关税率', '默认清关备注',
            '全部国家头程费用(含税)', '全部国家头程费用币种'
        ]
        
        lingxin_data = []
        sku_set = set()
        
        # 用于记录上一个产品的信息（处理变体）
        last_title = ''
        last_vendor = ''
        last_type = ''
        last_category = ''
        
        for idx, row in shopify_df.iterrows():
            lingxin_row = self._transform_row(
                row, sku_set, last_title, last_vendor, last_type, last_category
            )
            
            # 更新last变量
            if pd.notna(row['Title']) and row['Title'] != '':
                last_title = row['Title']
            if pd.notna(row['Vendor']) and row['Vendor'] != '':
                last_vendor = row['Vendor']
            if pd.notna(row['Type']) and row['Type'] != '':
                last_type = row['Type']
            if pd.notna(row['Product Category']) and row['Product Category'] != '':
                last_category = row['Product Category']
            
            # 填充空字段
            for col in lingxin_columns:
                if col not in lingxin_row:
                    lingxin_row[col] = ''
            
            lingxin_data.append(lingxin_row)
        
        return pd.DataFrame(lingxin_data, columns=lingxin_columns)
    
    def _transform_row(self, row, sku_set, last_title, last_vendor, last_type, last_category):
        """转换单行数据"""
        lingxin_row = {}
        
        # SKU处理
        lingxin_row['*SKU'] = self._process_sku(row, sku_set)
        
        # 品名处理
        lingxin_row['品名'] = self._process_title(row, last_title)
        
        # 产品类型
        lingxin_row['产品类型'] = self._process_type(row, last_type)
        
        # 状态
        lingxin_row['状态'] = self.STATUS_MAP.get(row['Status'], '在售') if pd.notna(row['Status']) else '在售'
        
        # 品牌
        lingxin_row['品牌'] = self._process_vendor(row, last_vendor)
        
        # 产品标签（留空避免冲突）
        lingxin_row['产品标签'] = ''
        
        # 产品描述
        lingxin_row['产品描述'] = self._process_description(row)
        
        # 图片链接
        lingxin_row['图片链接'] = truncate_field(row['Image Src'], 500)
        
        # 采购成本
        lingxin_row['采购成本(CNY)'] = self._process_cost(row)
        
        # 单品净重
        self._process_weight(row, lingxin_row)
        
        # 识别码
        lingxin_row['识别码'] = truncate_field(row['Variant Barcode'], 50)
        
        # 产品材质
        lingxin_row['产品材质'] = self._process_material(row)
        
        # 分类
        self._process_category(row, lingxin_row, last_category)
        
        return lingxin_row
    
    def _process_sku(self, row, sku_set):
        """处理SKU字段"""
        sku = row['Variant SKU'] if pd.notna(row['Variant SKU']) and row['Variant SKU'] != '' else row['Handle']
        sku = str(sku) if pd.notna(sku) else ''
        
        # 清理非法字符：只保留字母、数字、下划线、短划线、点、井号、斜杠
        # 领星ERP要求：字母，数字，下划线（_），短划线（-），英文点（.），井号（#），斜杆（/）
        original_sku = sku
        sku = re.sub(r'[^a-zA-Z0-9_\-\.#/]', '', sku)
        
        if sku != original_sku and sku:
            self.sku_warnings.append(f"SKU包含非法字符已清理: '{original_sku}' -> '{sku}'")
        
        if len(sku) > 50:
            original_sku = sku
            sku = sku[:50]
            
            # 处理重复
            if sku in sku_set:
                counter = 1
                while f"{sku[:47]}-{counter:02d}" in sku_set and counter < 100:
                    counter += 1
                sku = f"{sku[:47]}-{counter:02d}"
            
            self.sku_warnings.append(f"SKU过长已截断: '{original_sku}' -> '{sku}'")
        
        sku_set.add(sku)
        return sku
    
    def _process_title(self, row, last_title):
        """处理品名字段"""
        if pd.notna(row['Title']) and row['Title'] != '':
            title = row['Title']
        else:
            title = last_title
        
        title_cleaned = clean_text(title)
        return truncate_field(title_cleaned, 200)
    
    def _process_type(self, row, last_type):
        """
        处理产品类型字段
        
        领星ERP要求：
        1、产品类型为组合产品时，支持填写右侧同底色字段及【包含单品】表格
        2、产品类型为普通产品时，填写无效自动过滤
        3、为空时，默认为普通产品
        
        因此，对于Shopify导入的普通产品，应该留空
        """
        # 留空，让领星ERP默认为普通产品
        return ''
    
    def _process_vendor(self, row, last_vendor):
        """处理品牌字段"""
        if pd.notna(row['Vendor']) and row['Vendor'] != '':
            return truncate_field(row['Vendor'], 50)
        return truncate_field(last_vendor, 50)
    
    def _process_description(self, row):
        """处理产品描述字段"""
        if pd.notna(row['Body (HTML)']):
            description = re.sub('<[^<]+?>', '', str(row['Body (HTML)']))
            return truncate_field(description.strip(), 1000)
        return ''
    
    def _process_cost(self, row):
        """处理采购成本字段"""
        if pd.notna(row['Cost per item']) and row['Cost per item'] != '':
            try:
                return float(row['Cost per item'])
            except:
                return ''
        return ''
    
    def _process_weight(self, row, lingxin_row):
        """处理重量字段"""
        if pd.notna(row['Variant Grams']) and row['Variant Grams'] != '':
            try:
                weight_grams = float(row['Variant Grams'])
                lingxin_row['单品净重'] = weight_grams / 1000
                lingxin_row['单品净重单位'] = 'kg'
            except:
                lingxin_row['单品净重'] = ''
                lingxin_row['单品净重单位'] = ''
        else:
            lingxin_row['单品净重'] = ''
            lingxin_row['单品净重单位'] = ''
    
    def _process_material(self, row):
        """处理产品材质字段"""
        material_col = '物品材质 (product.metafields.shopify.item-material)'
        if material_col in row and pd.notna(row[material_col]):
            return truncate_field(row[material_col], 50)
        return ''
    
    def _process_category(self, row, lingxin_row, last_category):
        """处理分类字段"""
        if pd.notna(row['Product Category']) and row['Product Category'] != '':
            category = row['Product Category']
        else:
            category = last_category
        
        if category:
            categories = str(category).split(' > ')
            lingxin_row['一级分类'] = truncate_field(categories[0] if len(categories) > 0 else '', 50)
            lingxin_row['二级分类'] = truncate_field(categories[1] if len(categories) > 1 else '', 50)
            lingxin_row['三级分类'] = truncate_field(categories[2] if len(categories) > 2 else '', 50)
        else:
            lingxin_row['一级分类'] = ''
            lingxin_row['二级分类'] = ''
            lingxin_row['三级分类'] = ''
    
    def _remove_duplicates(self, df):
        """去除重复的SKU"""
        original_count = len(df)
        df = df.drop_duplicates(subset=['*SKU'], keep='first')
        self.duplicate_count = original_count - len(df)
        return df
    
    def _write_excel(self, df, output_path):
        """写入Excel文件"""
        print(f"正在写入领星ERP导入文件: {output_path}")
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='产品')
    
    def _print_warnings(self):
        """打印警告信息"""
        if self.sku_warnings:
            print(f"\n⚠ 警告：发现 {len(self.sku_warnings)} 个SKU超过50字符限制，已自动截断：")
            for warning in self.sku_warnings:
                print(f"  - {warning}")
        
        if self.duplicate_count > 0:
            print(f"\n⚠ 警告：发现 {self.duplicate_count} 个重复的SKU，已自动去重（保留首次出现的记录）")
