# 全球海洋大气耦合时空可视化分析系统

## 项目结构 (Project Structure)

```text
├── .gitignore          # Git 忽略文件配置文件（已屏蔽 .venv, .DS_Store 等）
├── README.md           # 你正在阅读的项目说明书
├── ScreenShot/         # 实验屏幕截图
└── D3_Lab/             # 系统核心代码文件夹
    ├── index.html      # D3导入成功测试页面
    ├── line_chart.html # 特定的折线图测试页面（目前正在开发）
    ├── DataGet.py      # 用于处理/提取 NetCDF 数据的 Python 脚本
    └── ocean_data.nc   # 从网页下载未处理文件
    └── coupled_data.json #经过处理的50条13维度文件