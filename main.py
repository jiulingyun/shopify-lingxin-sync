#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Shopify产品转领星ERP工具 - 命令行主入口
"""

import argparse
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.converter import ShopifyToLingxinConverter
from src.matcher import ProductMatcher


def convert_command(args):
    """转换命令"""
    converter = ShopifyToLingxinConverter()
    
    try:
        output_path = converter.convert(
            shopify_csv_path=args.input,
            output_path=args.output
        )
        print(f"\n✓ 转换成功！")
        print(f"输出文件: {output_path}")
        return 0
    except FileNotFoundError as e:
        print(str(e))
        return 1
    except Exception as e:
        error_msg = str(e)
        if error_msg.startswith('\n❌'):
            # 已经是友好的错误信息
            print(error_msg)
        else:
            # 未处理的错误，显示详细信息
            print(f"\n❌ 转换失败: {error_msg}")
            import traceback
            traceback.print_exc()
        return 1


def match_command(args):
    """配对命令"""
    matcher = ProductMatcher()
    
    try:
        output_path = matcher.match(
            platform_file=args.platform,
            erp_file=args.erp,
            output_path=args.output,
            match_method=args.method,
            shop_name=args.shop
        )
        print(f"\n✓ 配对成功！")
        print(f"输出文件: {output_path}")
        return 0
    except (FileNotFoundError, ValueError) as e:
        print(str(e))
        return 1
    except Exception as e:
        error_msg = str(e)
        if error_msg.startswith('\n❌'):
            # 已经是友好的错误信息
            print(error_msg)
        else:
            # 未处理的错误，显示详细信息
            print(f"\n❌ 配对失败: {error_msg}")
            import traceback
            traceback.print_exc()
        return 1


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Shopify产品转领星ERP工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 转换Shopify产品到领星ERP格式
  python main.py convert -i file/shopify_products_export.csv
  
  # 指定输出文件
  python main.py convert -i file/shopify_products_export.csv -o output.xlsx
  
  # 配对平台商品和ERP商品（基于SKU）
  python main.py match -p platform.csv -e erp.xlsx -s MyStore
  
  # 使用品名进行配对
  python main.py match -p platform.csv -e erp.xlsx -s MyStore -m title
  
  # 使用模糊匹配
  python main.py match -p platform.csv -e erp.xlsx -s MyStore -m fuzzy
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 转换命令
    convert_parser = subparsers.add_parser('convert', help='转换Shopify产品到领星ERP格式')
    convert_parser.add_argument('-i', '--input', required=True, help='Shopify导出的CSV文件路径')
    convert_parser.add_argument('-o', '--output', help='输出Excel文件路径（可选）')
    
    # 配对命令
    match_parser = subparsers.add_parser('match', help='配对平台商品和ERP商品，生成领星MSKU配对导入文件')
    match_parser.add_argument('-p', '--platform', required=True, help='平台商品文件路径（CSV或Excel）')
    match_parser.add_argument('-e', '--erp', required=True, help='领星ERP商品文件路径（CSV或Excel）')
    match_parser.add_argument('-s', '--shop', required=True, help='店铺名称（必填），如：MyStore')
    match_parser.add_argument('-o', '--output', help='输出Excel文件路径（可选）')
    match_parser.add_argument('-m', '--method', 
                             choices=['sku', 'title', 'barcode', 'fuzzy'],
                             default='sku',
                             help='配对方法：sku=SKU匹配, title=品名匹配, barcode=条形码匹配, fuzzy=模糊匹配（默认：sku）')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # 执行命令
    if args.command == 'convert':
        return convert_command(args)
    elif args.command == 'match':
        return match_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
