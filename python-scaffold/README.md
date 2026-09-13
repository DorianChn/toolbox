# python-scaffold

一个用 Python 写的项目脚手架。

## 环境要求

- Python 3.10 或更高版本

## 快速开始

```bash
# 创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 安装依赖
pip install -e .

# 运行
python main.py
```

## 项目结构

```
python-scaffold/
├── main.py          # 程序入口
├── pyproject.toml   # 项目元数据与依赖
├── .gitignore       # Git 忽略规则
└── README.md        # 本说明文件
```

## 说明

在 `main.py` 里开始写你的代码，需要第三方库时在 `pyproject.toml` 的
`dependencies` 中声明即可。
