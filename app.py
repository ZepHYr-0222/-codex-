from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
from get_data import SinaFinanceDividendScraper
# 导入你写好的预处理类
from data_p import DataPreprocessor
import os
import pandas as pd

app = Flask(__name__)
CORS(app)

# 抓取数据接口
@app.route("/api/fetch", methods=["POST"])
def api_fetch():
    data = request.get_json()
    stock_code = data.get("stock_code")
    if not stock_code:
        return jsonify({"msg": "股票代码不能为空"}), 400

    scraper = SinaFinanceDividendScraper()
    df = asyncio.run(scraper.scrape_dividend_data(stock_code))
    if df.empty:
        return jsonify({"msg": "抓取失败，无分红数据"}), 500

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/raw_data.csv", index=False, encoding="utf-8-sig")
    # 同时把原始数据返回给前端，供前端表格渲染
    return jsonify({
        "msg": "✅抓取成功，已保存 raw_data.csv",
        "rawData": df.to_dict(orient="records")
    })


@app.route("/api/preprocess", methods=["POST"])
def api_preprocess():
    try:
        req_json = request.get_json()
        input_data = req_json.get("data")
        if not input_data:
            return jsonify({"success":False,"msg":"没有传入原始数据"}),400

        import pandas as pd
        preprocessor = DataPreprocessor()
        df = pd.DataFrame(input_data)

        df = preprocessor.clean_data(df)
        df = preprocessor.standardize_dates(df)
        df = preprocessor.calculate_dividend_rate(df)

        os.makedirs("data", exist_ok=True)
        df.to_csv("data/processed_data.csv", index=False, encoding="utf-8-sig")

        return jsonify({
            "success": True,
            "data": df.to_dict(orient="records")
        })

    except Exception as e:
        print(f"预处理异常 {e}")
        return jsonify({"success":False,"msg":str(e)}),500




if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
