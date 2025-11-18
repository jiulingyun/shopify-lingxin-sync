#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具测试脚本
用于快速测试转换和配对功能
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.converter import ShopifyToLingxinConverter
from src.matcher import ProductMatcher


def test_converter():
    """测试转换功能"""
    print("="*60)
    print("测试转换功能")
    print("="*60)
    
    shopify_csv = r'file\shopify_products_export.csv'
    
    if not os.path.exists(shopify_csv):
        print(f"❌ 测试文件不存在: {shopify_csv}")
        return False
    
    try:
        converter = ShopifyToLingxinConverter()
        output_path = converter.convert(shopify_csv)
        print(f"\n✓ 转换测试成功！")
        print(f"输出文件: {output_path}")
        return True
    except Exception as e:
        print(f"\n✗ 转换测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_matcher():
    """测试配对功能"""
    print("\n" + "="*60)
    print("测试配对功能")
    print("="*60)
    
    # 这里需要准备测试文件
    platform_file = r'file\shopify_products_export.csv'
    erp_file = r'file\Product-V369.xlsx'
    
    if not os.path.exists(platform_file):
        print(f"⚠ 平台文件不存在: {platform_file}")
        print("跳过配对测试")
        return True
    
    if not os.path.exists(erp_file):
        print(f"⚠ ERP文件不存在: {erp_file}")
        print("跳过配对测试")
        return True
    
    try:
        matcher = ProductMatcher()
        output_path = matcher.match(
            platform_file=platform_file,
            erp_file=erp_file,
            match_method='sku'
        )
        print(f"\n✓ 配对测试成功！")
        print(f"输出文件: {output_path}")
        return True
    except Exception as e:
        print(f"\n✗ 配对测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "🔧 开始测试工具功能...\n")
    
    results = []
    
    # 测试转换功能
    results.append(("转换功能", test_converter()))
    
    # 测试配对功能
    results.append(("配对功能", test_matcher()))
    
    # 打印测试结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠ 部分测试失败，请检查错误信息")
        return 1


if __name__ == '__main__':
    sys.exit(main())
