# Shopify Lingxin Sync

> 一套完整的Shopify产品数据处理工具集，包括格式转换和MSKU商品配对功能

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/badge/GitHub-shopify--lingxin--sync-blue)](https://github.com/jiulingyun/shopify-lingxin-sync)

## 📋 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [使用指南](#使用指南)
  - [产品转换](#产品转换)
  - [MSKU配对](#msku配对)
- [字段映射](#字段映射)
- [常见问题](#常见问题)
- [项目结构](#项目结构)

## ✨ 功能特性

### 1. 产品转换工具

将Shopify导出的CSV文件转换为领星ERP导入格式：

- ✅ 自动字段映射（15+个关键字段）
- ✅ 智能处理变体产品
- ✅ 自动编码检测（UTF-8/GBK/GB2312等）
- ✅ 字段长度自动截断和验证
- ✅ SKU去重和冲突处理
- ✅ SKU非法字符自动清理
- ✅ 品名空格清理
- ✅ HTML标签自动清除
- ✅ 重量单位自动转换
- ✅ 产品类型自动留空（默认普通产品）

### 2. MSKU配对工具

生成领星ERP的MSKU配对导入文件：

- ✅ 基于SKU精确匹配
- ✅ 基于品名精确匹配
- ✅ 基于条形码匹配
- ✅ 模糊匹配（相似度算法）
- ✅ 自动生成配对报告
- ✅ 符合领星MSKU导入格式

## 🚀 快速开始

### 安装

```bash
# 克隆或下载项目
cd shopifyProductToLingxin

# 安装依赖
pip install -r requirements.txt
```

### 基本使用

```bash
# 转换Shopify产品到领星ERP格式
python main.py convert -i file/shopify_products_export.csv

# 配对商品并生成MSKU导入文件
python main.py match -p file/shopify.csv -e file/erp.xlsx -s MyStore
```

## 📖 使用指南

### 产品转换

将Shopify产品转换为领星ERP导入格式。

#### 命令行方式

```bash
# 基本用法
python main.py convert -i file/shopify_products_export.csv

# 指定输出文件
python main.py convert -i file/shopify_products_export.csv -o output.xlsx

# 查看帮助
python main.py convert --help
```

#### Python代码方式

```python
from src.converter import ShopifyToLingxinConverter

converter = ShopifyToLingxinConverter()
output_path = converter.convert('file/shopify_products_export.csv')
print(f"转换完成: {output_path}")
```

#### 输出说明

- 文件名：`lingxin_import_YYYYMMDD_HHMMSS.xlsx`
- Sheet名称：`产品`（领星ERP要求）
- 自动显示SKU截断和去重警告

### MSKU配对

生成领星ERP的MSKU配对导入文件，关联平台商品和ERP商品。

#### 命令行方式

```bash
# 基于SKU配对（推荐）
python main.py match -p file/shopify.csv -e file/erp.xlsx -s MyStore

# 基于品名配对
python main.py match -p file/shopify.csv -e file/erp.xlsx -s MyStore -m title

# 基于条形码配对
python main.py match -p file/shopify.csv -e file/erp.xlsx -s MyStore -m barcode

# 模糊匹配（相似度匹配）
python main.py match -p file/shopify.csv -e file/erp.xlsx -s MyStore -m fuzzy

# 指定输出文件
python main.py match -p file/shopify.csv -e file/erp.xlsx -s MyStore -o result.xlsx
```

#### 参数说明

- `-p, --platform`: 平台商品文件（CSV或Excel）
- `-e, --erp`: 领星ERP商品文件（CSV或Excel）
- `-s, --shop`: 店铺名称（必填），如：MyStore
- `-m, --method`: 配对方法（可选）
  - `sku`: SKU精确匹配（默认）
  - `title`: 品名精确匹配
  - `barcode`: 条形码匹配
  - `fuzzy`: 模糊匹配
- `-o, --output`: 输出文件路径（可选）

#### 输出格式

生成的Excel文件包含以下sheet：

1. **Sheet1**（领星MSKU导入格式）
   - `*MSKU`: 平台SKU
   - `*SKU`: ERP SKU
   - `店铺`: `[Shopify].店铺名`

2. **配对详情**：完整的配对信息
3. **已配对**：成功配对的商品
4. **未配对**：未找到匹配的商品

#### Python代码方式

```python
from src.matcher import ProductMatcher

matcher = ProductMatcher()
output_path = matcher.match(
    platform_file='file/shopify.csv',
    erp_file='file/erp.xlsx',
    shop_name='MyStore',
    match_method='sku'
)
print(f"配对完成: {output_path}")
```

## 🔄 字段映射

### 转换工具字段映射

| Shopify字段 | 领星ERP字段 | 长度限制 | 说明 |
|------------|------------|---------|------|
| Variant SKU/Handle | *SKU | 50字符 | 必填，自动清理非法字符+截断+去重 |
| Title | 品名 | 200字符 | 自动清理空格 |
| Type | 产品类型 | - | 自动留空（默认普通产品） |
| Vendor | 品牌 | 50字符 | |
| Tags | 产品标签 | - | 默认留空避免冲突 |
| Body (HTML) | 产品描述 | 1000字符 | 自动清除HTML |
| Image Src | 图片链接 | 500字符 | |
| Cost per item | 采购成本(CNY) | 数值 | |
| Variant Grams | 单品净重 | 数值 | 自动转为kg |
| Variant Barcode | 识别码 | 50字符 | |
| Product Category | 一/二/三级分类 | 各50字符 | 自动拆分 |
| Status | 状态 | - | active→在售, draft→开发中, archived→停售 |

### 字段长度限制

| 字段 | 最大长度 | 处理方式 |
|-----|---------|----------|
| *SKU | 50字符 | 清理非法字符+自动截断+去重（显示警告） |
| 品名 | 200字符 | 自动截断 |
| 产品类型 | - | 留空（默认普通产品） |
| 品牌 | 50字符 | 自动截断 |
| 产品标签 | - | 默认留空 |
| 产品描述 | 1000字符 | 清除HTML后截断 |
| 图片链接 | 500字符 | 自动截断 |
| 识别码 | 50字符 | 自动截断 |
| 产品材质 | 50字符 | 自动截断 |
| 一级/二级/三级分类 | 50字符 | 自动截断 |

### 状态映射

| Shopify | 领星ERP |
|---------|--------|
| active | 在售 |
| draft | 开发中 |
| archived | 停售 |

## ❓ 常见问题

### 转换工具

**Q: SKU长度超过50字符或包含非法字符怎么办？**

A: 脚本会自动清理非法字符（只保留字母、数字、下划线、短划线、点、井号、斜杠），然后截断到50字符，并添加序号后缀避免重复（如`-01`, `-02`）。会显示警告信息。

**Q: 品名中有连续空格导致导入失败？**

A: 脚本会自动清理连续空格，替换为单个空格。

**Q: 产品标签导入时提示"系统中已存在此标签"？**

A: 脚本默认不导入标签字段，避免冲突。需要在领星ERP中手动添加。

**Q: Excel中已存在该SKU？**

A: 脚本会自动去重，保留首次出现的记录。

**Q: 如何处理变体产品？**

A: 脚本会自动识别变体产品（Title为空的行），并继承主产品的信息。

**Q: 产品类型导入时提示"产品类型非法"？**

A: 脚本会自动将产品类型留空，让领星ERP默认为普通产品。如需创建组合产品，请在导入后在ERP中手动设置。

### 配对工具

**Q: 店铺名称格式是什么？**

A: 使用 `-s` 参数指定店铺名称（不含平台前缀），如：`-s MyStore`。生成的格式为：`[Shopify].MyStore`

**Q: 配对工具支持哪些文件格式？**

A: 支持CSV和Excel（.xlsx, .xls）格式。

**Q: 模糊匹配的相似度阈值是多少？**

A: 默认80%，匹配度低于80%的商品会标记为未配对。

**Q: 配对结果可以直接导入ERP吗？**

A: 可以。Sheet1是标准的领星MSKU配对导入格式，可直接导入。

**Q: 如何查看哪些商品未配对？**

A: 查看生成Excel文件中的"未配对"sheet。

## 📁 项目结构

```
shopifyProductToLingxin/
├── src/                                # 源代码模块
│   ├── __init__.py
│   ├── utils.py                        # 工具函数
│   ├── converter.py                    # 转换器
│   └── matcher.py                      # 配对器
├── file/                               # 数据文件目录
│   ├── shopify_products_export.csv     # Shopify导出文件（输入）
│   ├── Product-V369.xlsx               # 领星ERP模板（参考）
│   └── *.xlsx                          # 生成的文件（输出）
├── main.py                             # 命令行入口
├── test_tools.py                       # 测试脚本
├── requirements.txt                    # Python依赖
└── README.md                           # 本文档
```

## 🔧 技术栈

- Python 3.8+
- pandas 2.0.3
- openpyxl 3.1.2

## 📝 使用示例

### 示例1：批量转换Shopify产品

```bash
# 1. 从Shopify导出产品CSV
# 2. 将CSV文件放入file目录
# 3. 运行转换命令
python main.py convert -i file/shopify_products_export.csv

# 4. 在file目录找到生成的lingxin_import_*.xlsx文件
# 5. 导入到领星ERP
```

### 示例2：配对平台商品和ERP商品

```bash
# 场景：需要知道哪些Shopify商品已经在领星ERP中

# 1. 准备两个文件：
#    - shopify.csv: Shopify导出的商品
#    - erp.xlsx: 从领星ERP导出的商品

# 2. 运行配对命令
python main.py match -p file/shopify.csv -e file/erp.xlsx -s MyStore

# 3. 查看生成的配对结果文件
#    - Sheet1: 领星MSKU导入格式
#    - 配对详情: 所有商品的配对情况
#    - 已配对: 成功配对的商品
#    - 未配对: 未找到匹配的商品

# 4. 将Sheet1导入到领星ERP建立MSKU关联
```

### 示例3：模糊匹配查找相似商品

```bash
# 场景：品名不完全一致，需要找到相似的商品

python main.py match -p file/shopify.csv -e file/erp.xlsx -s MyStore -m fuzzy

# 结果会显示匹配度（如85.5%），方便人工审核
```

## 🎯 最佳实践

1. **首次使用**：建议先用少量数据测试
2. **数据备份**：导入前请备份领星ERP数据
3. **配对审核**：模糊匹配结果建议人工审核
4. **文件保留**：保留原始Shopify导出文件
5. **命令行优先**：推荐使用`main.py`命令行方式

## 📄 许可

本项目采用 [MIT License](LICENSE) 开源协议。

## 🤝 贡献

欢迎提交Issue和Pull Request！

如果这个项目对你有帮助，请给个 ⭐️ Star 支持一下！

---

**版本**: v1.0.0  
**更新日期**: 2025-11-18  
**作者**: [@jiulingyun](https://github.com/jiulingyun)
