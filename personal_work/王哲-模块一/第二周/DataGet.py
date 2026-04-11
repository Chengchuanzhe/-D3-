# 2组-王哲-第二周-数据整合和清洗
import requests
import pandas as pd
import xarray as xr
import json
import time
import os

# 1. 核心配置区
START_DATE = "2021-01-01"
END_DATE = "2023-09-27"

# 挑选中国沿海的 5 个典型海域坐标 (5点 * 1000天 ≈ 5000条数据)
TARGET_POINTS = [
    {"name": "台湾海峡", "lat": 25.0, "lon": 122.0},
    {"name": "东海中部", "lat": 28.0, "lon": 125.0},
    {"name": "舟山外海", "lat": 30.0, "lon": 123.0},
    {"name": "钓鱼岛海域", "lat": 25.5, "lon": 123.5},
    {"name": "南海北部", "lat": 22.0, "lon": 118.0},
]

# 读取三个从网页上下载的.nc文件
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
NC_FILES = [
    os.path.join(CURRENT_DIR, "ocean_temp.nc"),
    os.path.join(CURRENT_DIR, "ocean_salinity.nc"),
    os.path.join(CURRENT_DIR, "ocean_zos.nc"),
]

print("开始执行清洗...")


# 2. 定义处理单个坐标点的核心函数
def process_single_point(point_info, ds_ocean):
    lat = point_info["lat"]
    lon = point_info["lon"]
    name = point_info["name"]
    print(f"\n正在处理 [{name}] (Lat: {lat}, Lon: {lon})")

    # ---- 通过API获取该点的大气数据 (API) ----
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&"
        f"start_date={START_DATE}&end_date={END_DATE}&"
        f"daily=temperature_2m_mean,pressure_msl_mean,relative_humidity_2m_mean,"
        f"precipitation_sum,shortwave_radiation_sum,cloud_cover_mean,wind_speed_10m_max&"
        f"timezone=GMT"
    )

    response = requests.get(url)
    api_result = response.json()

    if "error" in api_result:
        print(f"{name} 大气数据获取失败: ", api_result.get("reason"))
        return None

    # 梳理从API获取的数据
    data = api_result["daily"]
    df_atmos = pd.DataFrame(
        {
            "date": data["time"],
            "air_temp": data["temperature_2m_mean"],
            "pressure": data["pressure_msl_mean"],
            "humidity": data["relative_humidity_2m_mean"],
            "precipitation": data["precipitation_sum"],
            "radiation": data["shortwave_radiation_sum"],
            "cloud_cover": data["cloud_cover_mean"],
            "wind_speed": data["wind_speed_10m_max"],
        }
    )

    # 从庞大的 3D 区域数据中，精准抽取离这个经纬度最近的一组时间序列
    point_data = ds_ocean.sel(longitude=lon, latitude=lat, method="nearest")
    df_ocean = point_data.to_dataframe().reset_index()
    df_ocean["date"] = df_ocean["time"].dt.strftime("%Y-%m-%d")

    # 清洗变量名
    df_clean_ocean = df_ocean[["date", "thetao", "so", "zos"]].copy()
    df_clean_ocean.rename(
        columns={"thetao": "sea_temp", "so": "salinity", "zos": "sea_level"},
        inplace=True,
    )

    # 按照日期将大气数据和海洋数据严格对齐合并
    df_merged = pd.merge(df_atmos, df_clean_ocean, on="date", how="inner")
    df_merged["longitude"] = lon
    df_merged["latitude"] = lat
    df_merged["region_name"] = name 

    numeric_cols = df_merged.select_dtypes(
        include=["float32", "float16", "float64"]
    ).columns
    df_merged[numeric_cols] = df_merged[numeric_cols].astype("float64")

    # 填充可能存在的空值，并严格保留 3 位小数
    df_merged = df_merged.fillna(method="ffill").round(3)
    print(f"[{name}] 处理完成，成功对齐 {len(df_merged)} 条数据。")
    return df_merged


# 3. 主流程：多文件合并与循环调度
all_data_frames = []

try:
    # 检查文件是否齐全
    for f in NC_FILES:
        if not os.path.exists(f):
            raise FileNotFoundError(f"未找到数据文件：{f}")

    ds_ocean = xr.open_mfdataset(NC_FILES, combine="by_coords")

    # 循环遍历 5 个海域坐标
    for point in TARGET_POINTS:
        df_point = process_single_point(point, ds_ocean)
        if df_point is not None:
            all_data_frames.append(df_point)
       
        time.sleep(1)

    # 将 5 个海域的数据纵向拼接成一个 5000 行的大表
    final_big_df = pd.concat(all_data_frames, ignore_index=True)

    # 输出为 JSON
    output_json = final_big_df.to_dict(orient="records")
    output_filename = "coupled_data_5000.json"

    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(output_json, f, indent=4, ensure_ascii=False)

    print(
        f"\n成功生成包含 {len(output_json)} 条记录的多时空维度数据文件：{output_filename}"
    )

except Exception as e:
    print(f"\n 出现未知错误：{e}")
