# 【2组-王哲-数据获取与清洗-第一周】2026-3-25
import requests
import pandas as pd
import xarray as xr
import json


# 1. 核心配置区：中国东海海域，2024年初
LATITUDE = 25.0  # 北纬 25度
LONGITUDE = 122.0  # 东经 122度
START_DATE = "2024-01-01"
END_DATE = "2024-02-20"  # 共 51 天的数据

print("开始执行海气耦合数据清洗 Pipeline...")


# 2. 获取大气数据 (通过 API)
def fetch_atmosphere_data():
    print("-> 正在调用 Open-Meteo API 获取大气数据...")
    # 已将 surface_pressure 替换为 pressure_msl_mean
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={LATITUDE}&longitude={LONGITUDE}&"
        f"start_date={START_DATE}&end_date={END_DATE}&"
        f"daily=temperature_2m_mean,pressure_msl_mean,relative_humidity_2m_mean,"
        f"precipitation_sum,shortwave_radiation_sum,cloud_cover_mean,wind_speed_10m_max&"
        f"timezone=GMT"
    )

    response = requests.get(url)
    api_result = response.json()

    data = api_result["daily"]

    # 转化为 DataFrame 方便后续操作
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
    return df_atmos


# 3. 获取海洋数据 (读取本地 .nc 文件)
def process_ocean_data(nc_file_path):
    print("-> 正在解析本地 Copernicus 海洋 NetCDF 数据...")
    try:
        ds = xr.open_dataset(nc_file_path)
        # 提取目标经纬度的点数据 (降维)
        point_data = ds.sel(longitude=LONGITUDE, latitude=LATITUDE, method="nearest")
        df_ocean = point_data.to_dataframe().reset_index()

        # 提取核心字段并标准化时间格式
        df_ocean["date"] = df_ocean["time"].dt.strftime("%Y-%m-%d")

        df_clean_ocean = df_ocean[["date", "thetao", "so", "zos"]].copy()
        df_clean_ocean.rename(
            columns={"thetao": "sea_temp", "so": "salinity", "zos": "sea_level"},
            inplace=True,
        )
        return df_clean_ocean
    except FileNotFoundError:
        print("找不到 ocean_data.nc 文件。")
        return None


# 4. 数据耦合、清洗与输出 (数据结构化)
df_atmos = fetch_atmosphere_data()
df_ocean = process_ocean_data(
    "/Users/wangzhe/Documents/Course- Experiment/Visual Tech/E1/ D3_Lab/ocean_data.nc"
)

if df_ocean is not None:
    print("-> 正在进行时空耦合 (Merge)...")
    # 以日期为基准，将大气和海洋数据强行对齐合并
    final_df = pd.merge(df_atmos, df_ocean, on="date", how="inner")

    # 加入基础空间维度
    final_df["longitude"] = LONGITUDE
    final_df["latitude"] = LATITUDE

    # 【数据清洗】：处理缺失值 (fillna 替换为空或者平均值)
    final_df = final_df.fillna(method="ffill").round(3)

    # 【字符标准化】：确保所有的 key 都是小写加下划线，符合 D3 的读取规范
    # 最终输出为 JSON
    output_json = final_df.to_dict(orient="records")

    with open("coupled_data.json", "w", encoding="utf-8") as f:
        json.dump(output_json, f, indent=4)

    print(
        f"已生成包含 {len(output_json)} 条记录、13 个维度的 coupled_data.json 文件。"
    )
else:
    print("-> 流程暂停：请先完成 Copernicus 海洋数据的下载。")
