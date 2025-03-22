import requests
import logging
import json
import time

def get_location_by_ip():
    """
    通过IP地址获取地理位置
    返回: str 城市ID
    """
    try:
        # 使用太平洋网络的IP定位API获取IP地址信息
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        ip_response = requests.get('http://whois.pconline.com.cn/ipJson.jsp?json=true', headers=headers, timeout=5)
        ip_response.encoding = 'gbk'  # 设置正确的编码
        ip_data = ip_response.json()
        
        # 获取城市名称
        city_name = ip_data.get('city', '').replace('市', '')  # 移除"市"字
        if not city_name:
            logging.error("无法获取城市名称")
            return None
            
        # 使用和风天气的城市查询API
        key = 'f527040e397d4f95b39d4518a057702d'
        city_api = f'https://geoapi.qweather.com/v2/city/lookup?location={city_name}&key={key}'
        
        # 添加延时避免请求过快
        time.sleep(0.5)
        
        city_response = requests.get(city_api)
        city_response.raise_for_status()
        city_data = city_response.json()
        
        if city_data.get('code') == '200' and city_data.get('location'):
            # 返回第一个匹配城市的ID
            return city_data['location'][0]['id']
        else:
            logging.error(f"城市查询失败: {city_data.get('code')}")
            return None
            
    except requests.RequestException as e:
        logging.error(f"获取IP地址信息失败: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"解析IP地址信息失败: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"处理地理位置信息时发生错误: {str(e)}")
        return None

def get_weather_info():
    """
    获取本地天气信息
    返回: dict 包含温度和天气描述
    """
    try:
        key = 'f527040e397d4f95b39d4518a057702d'
        
        # 获取城市ID
        location = get_location_by_ip()
        if not location:
            logging.error("无法获取城市ID")
            return None
            
        # 获取天气信息
        HeFengApi = f'https://devapi.qweather.com/v7/weather/now?location={location}&key={key}'
        
        # 添加延时避免请求过快
        time.sleep(0.5)
        
        response = requests.get(HeFengApi)
        response.raise_for_status()
        HeFengApi_data = response.json()
        
        if 'now' in HeFengApi_data:
            return {
                'temp': HeFengApi_data['now']['temp'],
                'text': HeFengApi_data['now']['text'],
                'location': location
            }
        else:
            logging.error("天气API返回数据格式错误")
            return None
            
    except requests.RequestException as e:
        logging.error(f"获取天气信息失败: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"处理天气信息时发生错误: {str(e)}")
        return None

