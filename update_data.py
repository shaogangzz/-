# 由 GitHub Actions 在云端运行
# 说明：本脚本优先尝试使用 AKShare 获取公开行情/行业数据。
# 不要求用户本地安装 Python；GitHub Actions 会自动安装依赖并运行。
#
# 由于不同数据源接口会发生调整，本脚本采用“接口候选 + 保底空序列”的方式，
# 避免某一个接口变化导致整个网页更新失败。首次运行后可在 Actions 日志查看状态。

import json, os, sys
from datetime import datetime, timedelta

try:
    import akshare as ak
except Exception as e:
    print("AKShare import failed:", e)
    sys.exit(1)

OUT = "data/data.json"
START = "2024-01-01"

def empty():
    return {"updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"), "series": {
        "sows": [], "piglet": [], "hog": [], "weight": [], "futures": [], "profit": []
    }}

def pick_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

def rows(df, date_col, value_col):
    if df is None or len(df) == 0 or not date_col or not value_col:
        return []
    x = df[[date_col, value_col]].copy()
    x[date_col] = x[date_col].astype(str).str[:10]
    x[value_col] = __import__("pandas").to_numeric(x[value_col], errors="coerce")
    x = x.dropna().drop_duplicates(subset=[date_col]).sort_values(date_col)
    x = x[x[date_col] >= START]
    return [{"date": d, "value": float(v)} for d, v in zip(x[date_col], x[value_col])]

data = empty()
# 商品猪价格：AKShare 生猪现货价格接口
try:
    df = ak.index_hog_spot_price()
    dc = pick_col(df, ["日期","date","Date"])
    vc = pick_col(df, ["价格","price","生猪价格"])
    data["series"]["hog"] = rows(df, dc, vc)
except Exception as e:
    print("hog failed:", repr(e))

# 生猪期货：主力合约/核心合约接口
try:
    df = ak.futures_hog_core()
    dc = pick_col(df, ["日期","date","Date"])
    vc = pick_col(df, ["收盘","收盘价","close","Close"])
    data["series"]["futures"] = rows(df, dc, vc)
except Exception as e:
    print("futures failed:", repr(e))

# 养殖成本/利润：若接口可用则抓取；否则保留空序列
for func_name in ["futures_hog_cost", "futures_hog_supply"]:
    try:
        df = getattr(ak, func_name)()
        print(func_name, "columns:", list(df.columns))
    except Exception as e:
        print(func_name, "failed:", repr(e))

# 仔猪、能繁母猪、均重、利润的公开数据接口在不同版本 AKShare 中字段/函数可能变化。
# 不猜字段：保留为空，并在 Actions 日志提示，后续可针对当前 AKShare 版本补齐。
# 这样不会把错误字段当成真实数据。

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("Wrote", OUT)
for k,v in data["series"].items():
    print(k, len(v))
