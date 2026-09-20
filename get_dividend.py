import asyncio
import pandas as pd
import numpy as np
import random
from io import StringIO
from playwright.async_api import async_playwright
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SinaFinanceDividendScraper:
    """新浪分红爬虫 Playwright等待JS动态渲染"""
    def __init__(self):
        self.base_url = "https://vip.stock.finance.sina.com.cn/corp/go.php/vISSUE_ShareBonus/stockid/{stock_code}.phtml"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    async def scrape_dividend_data(self, stock_code):
        url = self.base_url.format(stock_code=stock_code)
        print(f"正在爬取股票 {stock_code} 的分红数据...")
        print(f"URL: {url}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
            )
            context = await browser.new_context(extra_http_headers=self.headers)
            await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            page = await context.new_page()
            try:
                resp = await page.goto(url, timeout=40000)
                if not resp.ok:
                    logger.warning(f"页面响应异常 status={resp.status}")
                    await browser.close()
                    return pd.DataFrame()

                # 加长等待
                await asyncio.sleep(random.uniform(5.0, 7.0))
                await page.wait_for_selector('text="公告"', timeout=30000)

                html = await page.content()
                table_list = pd.read_html(StringIO(html))
                print(f"一共找到 {len(table_list)} 个表格")
                for idx, tbl in enumerate(table_list):
                    print(f"【表格{idx}】列名：", tbl.columns.tolist())

                # 分红表是表格13
                df_raw = table_list[13]
                # 多层表头压扁，拿最内层名称
                df_raw.columns = [col[-1] for col in df_raw.columns]
                print("✅扁平化后的列名：", df_raw.columns.tolist())

                await browser.close()
                return df_raw

            except Exception as e:
                logger.error(f"爬取异常：{str(e)}")
                await browser.close()
                return pd.DataFrame()


async def main():
    scraper = SinaFinanceDividendScraper()
    os.makedirs("data", exist_ok=True)
    df = await scraper.scrape_dividend_data("000001")
    print(f"抓取行数:{len(df)}")
    if not df.empty:
        df.to_csv("data/raw_data.csv", index=False, encoding="utf-8-sig")
        print("✅保存成功 raw_data.csv")


if __name__ == "__main__":
    asyncio.run(main())
