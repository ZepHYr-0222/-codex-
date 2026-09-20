# 作业提交报告

## 课程作业：新浪财经历史分红数据获取与预处理

---

## 一、项目概述

本项目使用 Python + Playwright 自动化技术，从新浪财经个股历史分红页面获取股票分红数据，通过 Pandas 完成数据清洗与标准化处理，并开发前端 Web 页面实现数据可视化展示。项目覆盖了数据获取、数据处理、界面展示和版本管理完整链路。

---

## 二、需求规划（plan模式）

### 2.1 需求确认

| 需求项 | 说明 |
|--------|------|
| 数据源 | 新浪财经个股历史分红页面 |
| 爬取字段 | 分红年度、分红方案、每股送转、每股派息、股权登记日、除权除息日 |
| 预处理要求 | 清洗空值、重复行、异常字符；统一日期格式；计算分红率 |
| 前端要求 | 项目说明区 + 股票输入框 + 抓取按钮 + 原始/清洗数据表格 + 统计卡片 |
| 版本管理 | Git 全程管理代码 |

### 2.2 技术选型

- 爬虫框架：Playwright（Python异步API）
- 数据处理：Pandas + NumPy
- 前端技术：原生 HTML + CSS + JavaScript
- 版本控制：Git

### 2.3 项目规划方案

项目分为六个阶段实施：

| 阶段 | 内容 | 状态 |
|------|------|------|
| 阶段一 | 需求确认与环境搭建 | 已完成 |
| 阶段二 | Playwright爬虫开发 | 已完成 |
| 阶段三 | 数据预处理开发 | 已完成 |
| 阶段四 | 前端UI界面开发 | 已完成 |
| 阶段五 | 系统集成与测试 | 已完成 |
| 阶段六 | 文档编写与交付 | 已完成 |

---

## 三、UI设计说明

### 3.1 设计理念

采用简洁商务风格，主色调为深蓝色（#1d3557）搭配红色（#e63946）作为强调色，整体视觉风格专业、清爽，适合数据展示类应用。

### 3.2 页面布局

页面采用垂直流式布局，从上到下分为5个区块：

1. **头部区域**：渐变背景 + 项目标题 + 副标题说明
2. **项目说明区**：3个功能卡片（数据获取、数据预处理、可视化展示）
3. **数据控制区**：股票代码输入框 + 抓取按钮 + 预处理按钮 + 状态提示
4. **数据统计区**：4个统计卡片（总记录数、清洗后记录数、平均每股派息、平均分红率）
5. **数据表格区**：原始数据表格 + 清洗后数据表格

### 3.3 交互设计

- 输入框支持回车键快捷抓取
- 按钮点击后有禁用态防止重复操作
- 状态提示分3种类型：info（进行中）、success（成功）、error（失败）
- 表格支持悬停高亮和斑马纹背景
- 响应式设计，适配手机和桌面端

---

## 四、Playwright爬虫代码

### 4.1 核心实现

```python
async def scrape_dividend_data(self, stock_code, max_retries=3):
    url = self.base_url.format(stock_code)
    
    for attempt in range(max_retries):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.set_extra_http_headers(self.headers)
                await page.goto(url, timeout=30000)
                await page.wait_for_timeout(random.uniform(2000, 5000))
                content = await page.content()
                await browser.close()
                
                dividend_data = self._parse_dividend_data(content, stock_code)
                if dividend_data is not None and not dividend_data.empty:
                    return dividend_data
        except Exception as e:
            logger.error(f"爬取失败（尝试 {attempt + 1}/{max_retries}）: {str(e)}")
            await asyncio.sleep(random.uniform(5, 10))
    
    return pd.DataFrame()
```

### 4.2 爬虫特性

| 特性 | 说明 |
|------|------|
| 无头浏览器 | headless=True，不弹出窗口 |
| User-Agent | 模拟Chrome浏览器请求 |
| 随机延迟 | 2-5秒随机等待，降低被拦截风险 |
| 重试机制 | 最多重试3次 |
| 超时控制 | 页面加载超时30秒 |
| 日志记录 | 使用logging模块记录运行状态 |

---

## 五、爬虫结果截图说明

### 5.1 运行流程

1. 运行 `python get_dividend.py`
2. 脚本输出日志显示爬取进度
3. 成功后保存到 `data/raw_data.csv`
4. 运行 `python data_preprocess.py` 生成 `data/processed_data.csv`

### 5.2 截图说明

**建议截图位置：**

1. **终端运行截图**：展示 `python get_dividend.py` 的运行日志输出
2. **前端页面截图**：打开 `index.html` 展示完整UI界面
3. **数据文件截图**：用Excel打开 `data/raw_data.csv` 和 `data/processed_data.csv` 展示数据内容
4. **对比截图**：原始数据 vs 清洗后数据的差异对比

### 5.3 结果示例（字段说明）

| 字段 | 含义 | 示例值 |
|------|------|--------|
| stock_code | 股票代码 | 000001 |
| dividend_year | 分红年度 | 2023年度 |
| dividend_plan | 分红方案 | 10派3.50元(含税) |
| shares_distribution | 每股送转 | 0.0000 |
| dividend_per_share | 每股派息 | 0.3500 |
| record_date | 股权登记日 | 2024-06-14 |
| ex_dividend_date | 除权除息日 | 2024-06-17 |

---

## 六、数据预处理说明

### 6.1 清洗规则

| 规则 | 实现方式 |
|------|----------|
| 去除空值 | `df.dropna(how='all')` 去除全空行 |
| 去除重复行 | `df.drop_duplicates()` |
| 清洗字符串 | `.str.strip()` 去除空格，空字符串替换为NaN |
| 统一日期格式 | `pd.to_datetime(errors='coerce')` 标准化 |
| 计算分红率 | 每股派息 / 每股送转 x 100% |

### 6.2 输出结果

- 输出文件：`data/processed_data.csv`
- 编码格式：UTF-8 with BOM（兼容Excel直接打开）
- 保留字段：原始全部字段 + dividend_rate（分红率）

---

## 七、全部项目文件清单

| 文件路径 | 文件类型 | 说明 |
|----------|----------|------|
| `plan.md` | 文档 | 项目规划方案（需求确认 + 技术方案） |
| `README.md` | 文档 | 项目说明文档（介绍 + 运行步骤 + Git指引） |
| `report.md` | 文档 | 本作业提交报告 |
| `app.py` | Python脚本 | Playwright自动化爬虫 |
| `get_dividend.py` | Python脚本 | Playwright自动化爬虫 |
| `data_preprocess.py` | Python脚本 | 数据预处理与清洗 |
| `index.html` | 前端页面 | UI主页面 |
| `static/css/style.css` | 前端样式 | 页面样式表 |
| `static/js/script.js` | 前端脚本 | 页面交互逻辑 |
| `data/raw_data.csv` | 数据文件 | 爬虫抓取的原始数据 |
| `data/processed_data.csv` | 数据文件 | 清洗后的标准数据 |

---

## 八、Git提交说明

### 完整Git提交命令

```bash
# 进入项目目录
cd sina_finance_dividend_project

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 创建首次提交
git commit -m "feat: 新浪财经历史分红数据获取与预处理系统

- Playwright自动化爬取新浪财经股票历史分红数据
- Pandas数据预处理（清洗/标准化/分红率计算）
- 前端UI展示（数据获取控制/数据预览/统计卡片）
- 完整项目文档（plan.md/README.md/report.md）"

# 关联远程仓库（替换为你的实际仓库地址）
git remote add origin https://gitee.com/Zephyr-zhy/codex-word.git

# 推送到远程仓库
git push -u origin main
```

---

## 九、技术要点总结

1. **Playwright优势**：相比传统Requests爬虫，Playwright能处理JavaScript动态渲染内容，更接近真实浏览器行为。
2. **数据清洗策略**：分步处理（空值→重复→格式→计算），每步独立可控。
3. **UI设计原则**：信息层级清晰，操作流程简单，状态反馈及时。
4. **版本管理**：每个功能模块独立文件，Git commit message 遵循规范格式。

---

## 十、学习收获

通过本项目实战，掌握了：

- Playwright浏览器自动化爬虫的开发流程
- 异步编程（async/await）在爬虫中的应用
- Pandas数据清洗的标准流程
- 前端HTML/CSS/JS的数据可视化展示
- Git版本管理的基本操作
- 项目文档的规范编写

---

**报告结束**

