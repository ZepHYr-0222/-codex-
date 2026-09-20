import pandas as pd
import numpy as np
import os

class DataPreprocessor:
    """数据预处理类"""
    def __init__(self):
        pass

    def clean_data(self, df):
        try:
            # 去除空行
            df = df.dropna(how='all')
            # 去除重复行
            df = df.drop_duplicates()
            # 清洗字符串字段
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].str.strip().replace('', pd.NA)
        except Exception as e:
            print(f"数据清洗失败:{e}")
        return df

    def standardize_dates(self, df):
        """标准化日期格式"""
        try:
            date_columns = ['record_date', 'ex_dividend_date', 'announcement_date', 'implementation_date']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
        except Exception as e:
            print(f"日期标准化失败:{e}")
        return df

    def calculate_dividend_rate(self, df):
        """计算分红率，修复NaN问题"""
        try:
            # 使用新浪原生中文列名
            df["dividend_per_share"] = df["派息(税前)(元)"] / 10
            df["shares_distribution"] = (df["送股(股)"] + df["转增(股)"]) / 10

            # 先全部默认赋值0，不会出现NaN
            df['dividend_rate'] = 0.0

            # 满足条件才计算分红率
            mask = (df['dividend_per_share'] > 0) & (df['shares_distribution'] > 0)
            df.loc[mask, 'dividend_rate'] = (df.loc[mask, 'dividend_per_share'] / df.loc[mask, 'shares_distribution']) * 100

            # ✅ 把所有NaN替换成None，Flask转JSON会变成null，前端可正常解析
            df = df.where(pd.notna(df), None)

        except Exception as e:
            print(f"分红率计算失败: {e}")
        return df


def main():
    preprocessor = DataPreprocessor()
    # 读取原始数据
    df = pd.read_csv('data/raw_data.csv')
    if not df.empty:
        # 清洗数据
        df = preprocessor.clean_data(df)
        # 标准化日期
        df = preprocessor.standardize_dates(df)
        df = preprocessor.calculate_dividend_rate(df)
        # 保存处理后的数据
        df.to_csv('data/processed_data.csv', index=False, encoding='utf-8-sig')
        print("数据预处理完成！")
        print(f"处理完成，共 {len(df)} 条记录")
        print(f"保存到 data/processed_data.csv")
    else:
        print("未找到原始数据文件")


if __name__ == "__main__":
    main()
