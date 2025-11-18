# 数据文件目录

此目录用于存放输入和输出文件。

## 目录说明

### 输入文件

将以下文件放入此目录：

1. **Shopify导出文件**
   - 文件名：`shopify_products_export.csv`
   - 说明：从Shopify后台导出的产品CSV文件
   - 用途：作为转换工具的输入

2. **ERP商品文件**（可选，用于配对）
   - 文件名：任意Excel或CSV文件
   - 说明：从领星ERP导出的商品数据
   - 用途：作为配对工具的输入

### 输出文件

工具会自动生成以下文件：

1. **领星ERP导入文件**
   - 文件名格式：`lingxin_import_YYYYMMDD_HHMMSS.xlsx`
   - 说明：可直接导入到领星ERP的产品数据

2. **MSKU配对文件**
   - 文件名格式：`lingxin_msku_match_YYYYMMDD_HHMMSS.xlsx`
   - 说明：领星ERP的MSKU配对导入文件

### 参考文件（可选）

- `Product-V369.xlsx`：领星ERP的产品导入模板（仅供参考）

## 注意事项

⚠️ **重要提示**

- 此目录中的所有CSV和Excel文件都会被`.gitignore`忽略
- 请勿将包含商业敏感信息的文件提交到版本控制
- 建议定期备份重要的输出文件

## 文件示例

```
file/
├── shopify_products_export.csv          # Shopify导出（输入）
├── erp_products.xlsx                    # ERP商品（输入，可选）
├── lingxin_import_20251118_222209.xlsx  # 转换结果（输出）
└── lingxin_msku_match_20251118_223942.xlsx  # 配对结果（输出）
```

## 快速开始

1. 将Shopify导出的CSV文件放入此目录
2. 运行转换命令：
   ```bash
   python main.py convert -i file/shopify_products_export.csv
   ```
3. 查看生成的Excel文件
