# 全球海洋大气耦合时空可视化分析系统
！PS：要提交的时候记得先创建个分支,写代码的时候先pull一下同步

Week2(WZ): Data.json是最新的5000条数据一共14维，新加变量region_name表示不同区域名称

## 项目结构 (Project Structure)
```text
├── .gitignore          # Git 忽略文件配置文件
├── README.md           # 你正在阅读的项目说明书
├── ScreenShots/        # 实验屏幕截图
├── Doc/                # 文档文件含实验报告
├── personal_work/      # 独立成果文件夹
└── D3_Lab/             # 系统核心代码文件夹
    ├── index.html      # D3导入成功测试页面
    ├── line_chart.html # 特定的折线图测试页面（目前正在开发）
    ├── DataGet.py      # 用于处理/提取 NetCDF 数据的 Python 脚本
    └── ocean_data.nc   # 从网页下载未处理文件
    └── coupled_data.json #经过处理的50条13维度文件
