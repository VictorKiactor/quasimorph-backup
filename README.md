# Quasimorph Backup Tool

Quasimorph 存档备份与还原工具

## 项目简介

本工具为Quasimorph提供一键备份与还原存档的能力，支持多版本管理，防止存档丢失或误操作。

- **支持平台**：Windows
- **主要特性**：
  - 一键备份当前存档，自动按时间归档
  - 备份列表可视化，支持还原与删除
  - 无需手动查找存档路径，自动定位

## 使用方法

### 1. 运行环境

- Python 3.8 及以上
- 依赖库：`tkinter`、`Pillow`

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动程序

```bash
python quasimorph_gui.py
```

### 4. 备份与还原说明

- 存档目录：`C:\Users\你的用户名\AppData\LocalLow\Magnum Scriptum Ltd\Quasimorph`
- 备份目录：`C:\Users\你的用户名\AppData\LocalLow\Magnum Scriptum Ltd\backups`
- 每次备份会自动生成时间戳文件夹，支持多版本管理
