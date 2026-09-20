# 新浪财经历史分红数据获取与预处理系统

基于 **Playwright 自动化爬虫 + Pandas 数据处理 + Web 可视化** 的股票分红数据获取与预处理实战项目。

## 项目介绍

本项目实现了以下核心功能：

1. **数据自动获取**：使用 Playwright 自动化访问新浪财经个股历史分红页面，抓取分红年度、分红方案、每股送转、每股派息、股权登记日、除权除息日等字段。
2. **数据预处理**：清洗空值、去除重复行、清理异常字符、统一日期格式（YYYY-MM-DD）、计算分红率。
3. **前端可视化**：提供项目说明区、股票代码输入框、抓取按钮、原始数据表格预览、清洗后数据表格预览和数据统计卡片。
4. **版本管理**：使用 Git 管理全部代码，便于提交和追溯。

## 项目结构

```
sina_finance_dividend_project/
├── plan.md                  # 项目规划方案（plan模式文档）
├── README.md                # 项目说明文档
├── report.md                # 作业提交报告
├── app.py                   # 按钮运行脚本
├── get_dividend.py          # Playwright爬虫脚本
├── data_preprocess.py       # 数据预处理脚本
├── index.html               # 前端UI页面
├── static/
│   ├── css/
│   │   └── style.css        # 页面样式
│   └── js/
│       └── script.js        # 页面交互逻辑
└── data/
    ├── raw_data.csv         # 原始抓取数据
    └── processed_data.csv   # 清洗后数据
```

## 环境准备

### 系统要求

- Python 3.8 或更高版本
- Windows / macOS / Linux 均可运行

### 安装依赖

```bash
# 1. 进入项目目录
cd sina_finance_dividend_project

# 2. 安装Python依赖包
pip install playwright pandas numpy

# 3. 安装Playwright浏览器内核（首次运行必装）
playwright install chromium
```

## 运行步骤

### 步骤一：抓取分红数据

```bash
python get_dividend.py
```

运行后脚本会自动打开无头浏览器，访问新浪财经页面，抓取股票 `000001`（平安银行）的历史分红数据，并保存到 `data/raw_data.csv`。

> 如需抓取其他股票，可在 `get_dividend.py` 中修改 `test_stock_code` 变量的值。

### 步骤二：数据预处理

```bash
python data_preprocess.py
```

运行后脚本会读取 `data/raw_data.csv`，进行数据清洗和标准化处理，输出到 `data/processed_data.csv`。

### 步骤三：

```bash
python app.py
```
运行后脚本会可以进行按钮运行

### 步骤四：查看前端页面

直接双击打开 `index.html` 文件即可在浏览器中查看UI界面。前端页面会通过API接口调用后端数据。

## 核心代码说明

### get_dividend.py（Playwright爬虫）

| 方法 | 功能 |
|------|------|
| `scrape_dividend_data(stock_code)` | 主入口，异步启动Playwright浏览器抓取数据 |
| `_parse_dividend_data(content, stock_code)` | 解析页面JS数据块，提取分红字段 |
| `_clean_dividend_data(df)` | 内置基础数据清洗 |
| `_standardize_date(date_series)` | 日期格式标准化 |

爬虫特性：
- 无头模式运行，不弹出浏览器窗口
- 设置User-Agent模拟真实浏览器
- 随机延迟 2-5 秒，防止请求过快被拦截
- 最多重试3次，增强容错能力
- 完整的异常捕获和日志输出

### data_preprocess.py（数据预处理）

| 方法 | 功能 |
|------|------|
| `clean_data(df)` | 去空行、去重复、清洗字符串 |
| `standardize_dates(df)` | 统一日期为 YYYY-MM-DD 格式 |
| `calculate_dividend_rate(df)` | 计算分红率百分比 |

预处理规则：
- 去除全空行
- 去除完全重复的行
- 字符串字段去除首尾空格
- 空字符串替换为 NaN
- 数值字段强制转换为数值类型
- 日期字段统一为标准日期格式
- 分红率 = 每股派息 / 每股送转 x 100%

## 前端UI说明

页面包含以下模块：

1. **项目说明区**：三个功能卡片（数据获取、数据预处理、可视化展示）
2. **数据获取控制区**：股票代码输入框 + 抓取按钮 + 预处理按钮
3. **数据统计区**：4个统计卡片（总记录数、清洗后记录数、平均每股派息、平均分红率）
4. **原始数据表格**：展示抓取到的原始分红数据
5. **清洗后数据表格**：展示预处理后的数据（含分红率列）

UI特点：
- 响应式设计，支持手机和桌面端
- 简洁美观的卡片式布局
- 状态提示信息（info/success/error）
- 支持回车键快捷抓取

## Git 提交指引

### 首次初始化仓库

```bash
# 1. 进入项目目录
cd sina_finance_dividend_project

# 2. 初始化Git仓库
git init

# 3. 添加所有文件到暂存区
git add .

# 4. 首次提交
git commit -m "feat: 初始化新浪财经历史分红数据获取与预处理系统

- 使用Playwright自动化爬取新浪财经股票历史分红数据
- 使用Pandas进行数据预处理（清洗空值/重复行/异常字符/统一日期/计算分红率）
- 开发前端UI页面（项目说明/股票输入/数据表格预览/统计卡片）
- 添加完整的项目文档plan.md/README.md/report.md"

# 5. 关联远程仓库（替换为你的仓库地址）
git remote add origin https://gitee.com/Zephyr-zhy/codex-word.git

# 6. 推送到远程仓库
git push -u origin main
```

### 常用提交信息规范

```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 样式调整
refactor: 代码重构
test: 测试相关
chore: 其他杂项
```

## 注意事项

1. **网络环境**：确保网络连接正常，能够访问新浪财经网站
2. **反爬限制**：脚本已内置随机延迟和重试机制，但请合理使用，避免频繁请求
3. **股票代码**：仅支持6位数字的A股股票代码（如000001、600519）
4. **数据时效**：分红数据以新浪财经网站最新发布为准
5. **仅用于学习**：本项目数据仅用于课程作业和教学演示，请勿用于商业用途

## 技术栈

| 技术 | 用途 |
|------|------|
| Python 3.8+ | 开发语言 |
| Playwright | 浏览器自动化爬虫 |
| Pandas | 数据处理和分析 |
| NumPy | 数值计算 |
| HTML/CSS/JS | 前端界面 |
| Git | 版本控制 |

## 许可证

本项目仅用于学习交流，不设许可证限制。

---

如需了解项目详细设计方案，请查阅 [plan.md](plan.md)。
如需查看完整作业报告，请查阅 [report.md](report.md)。

