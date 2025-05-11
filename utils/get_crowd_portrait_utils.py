import requests
import json
import pandas as pd
import os
import time
from datetime import datetime, timedelta, date
from utils.db_utils import DatabaseConnection
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Tab

# 从数据库获取省份代码映射
def get_province_codes():
    """从数据库获取省份代码映射"""
    db = None
    cursor = None
    try:
        db = DatabaseConnection()
        cursor = db.connection.cursor()
        
        # 获取省份代码映射
        query = """
        SELECT code, province 
        FROM area_codes 
        WHERE city = 'NULL' OR city IS NULL
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        # 构建代码到省份名称的映射字典
        code_map = {}
        for code, province in results:
            # 处理省份名称
            province_name = province
            if '省' in province_name:
                province_name = province_name.replace('省', '')
            if '市' in province_name:
                province_name = province_name.replace('市', '')
            if '自治区' in province_name:
                province_name = province_name.replace('自治区', '')
            if '特别行政区' in province_name:
                province_name = province_name.replace('特别行政区', '')
            # 特殊处理西藏和台湾
            if province_name == '西藏自治区':
                province_name = '西藏'
            if province_name == '台湾省':
                province_name = '台湾'
            
            code_map[str(code)] = province_name
        
        print(f"获取到的省份代码映射: {code_map}")
        return code_map
        
    except Exception as e:
        print(f"获取省份代码映射失败: {str(e)}")
        return {}
        
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

# 使用数据库中的代码映射
CODE2PROVINCE = get_province_codes()

# 兴趣分类
INTEREST_CATEGORIES = [
    {"name": "影视音乐", "typeId": "24000000"},
    {"name": "资讯", "typeId": "18000000"},
    {"name": "医疗健康", "typeId": "14000000"},
    {"name": "教育培训", "typeId": "13000000"},
    {"name": "金融财经", "typeId": "19000000"},
    {"name": "书籍阅读", "typeId": "23000000"},
    {"name": "旅游出行", "typeId": "28000000"},
    {"name": "餐饮美食", "typeId": "11000000"},
    {"name": "家电数码", "typeId": "29000000"},
    {"name": "软件应用", "typeId": "15000000"}
]

def create_chart(data, title):
    """创建组合图表"""
    bar = Bar()
    bar.add_xaxis(data['name'].tolist())
    bar.add_yaxis(
        "示数",
        data['value'].tolist(),
        category_gap="50%",
        gap="30%",
        itemstyle_opts=opts.ItemStyleOpts(color="#45a1ff")
    )
    bar.add_yaxis(
        "全网分布",
        data['all_net_value'].tolist(),
        category_gap="50%",
        gap="30%",
        itemstyle_opts=opts.ItemStyleOpts(color="#a0a4aa")
    )

    # 添加TGI折线
    line = Line()
    line.add_xaxis(data['name'].tolist())
    line.add_yaxis(
        "TGI",
        data['tgi'].tolist(),
        yaxis_index=1,
        label_opts=opts.LabelOpts(is_show=True, position="right"),
        linestyle_opts=opts.LineStyleOpts(width=2, color="#5470c6"),
        symbol_size=8,
        itemstyle_opts=opts.ItemStyleOpts(color="#5470c6")
    )

    # 全局配置
    bar.set_global_opts(
        title_opts=opts.TitleOpts(
            title=title,
            title_textstyle_opts=opts.TextStyleOpts(
                font_size=16,
                color="#333"
            )
        ),
        tooltip_opts=opts.TooltipOpts(
            trigger="axis",
            axis_pointer_type="cross"
        ),
        xaxis_opts=opts.AxisOpts(
            type_="category",
            axislabel_opts=opts.LabelOpts(
                rotate=15,
                color="#666"
            )
        ),
        yaxis_opts=opts.AxisOpts(
            type_="value",
            name="人群占比",
            min_=0,
            max_=100,
            position="left",
            axislabel_opts=opts.LabelOpts(formatter="{value}%"),
            splitline_opts=opts.SplitLineOpts(is_show=True)
        ),
        legend_opts=opts.LegendOpts(pos_top="5%")
    )

    # 添加第二个y轴
    bar.extend_axis(
        yaxis=opts.AxisOpts(
            type_="value",
            name="TGI",
            min_=0,
            max_=400,
            position="right",
            axislabel_opts=opts.LabelOpts(formatter="{value}")
        )
    )

    # 组合图表
    bar.overlap(line)
    return bar

def save_region_data_to_db(data_list, keyword, date):
    """保存区域分布数据到MySQL数据库"""
    db = None
    cursor = None
    try:
        db = DatabaseConnection()
        cursor = db.connection.cursor()
        
        # 创建表（如果不存在）- 修改value字段类型为DECIMAL
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS crowd_region_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            province VARCHAR(50) NOT NULL,
            value DECIMAL(10,2) NOT NULL,
            keyword VARCHAR(100) NOT NULL,
            date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_region (province, keyword, date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        cursor.execute(create_table_sql)
        
        # 追踪插入和更新的数量
        inserted_count = 0
        updated_count = 0
        skipped_count = 0
        
        # 处理每条数据
        for item in data_list:
            province = item.get('province', '')
            
            # 确保value是有效的数值
            try:
                raw_value = item.get('value', 0)
                value = float(raw_value) if raw_value is not None else 0.0
            except (ValueError, TypeError):
                print(f"警告: 无效的数值 '{raw_value}' 已被转换为0.0")
                value = 0.0
                
            # 检查数据是否已存在
            check_sql = """
            SELECT id, value FROM crowd_region_data 
            WHERE province = %s AND keyword = %s AND date = %s
            """
            cursor.execute(check_sql, (
                province,
                keyword[:100],
                date.strftime('%Y-%m-%d')
            ))
            
            existing = cursor.fetchone()
            if not existing:
                # 不存在，插入新数据
                insert_sql = """
                INSERT INTO crowd_region_data (province, value, keyword, date)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (
                    province,
                    value,
                    keyword[:100],
                    date.strftime('%Y-%m-%d')
                ))
                inserted_count += 1
            elif abs(float(existing[1]) - value) > 0.01:  # 使用小误差范围比较浮点数
                # 数据存在但有变化，更新数据
                update_sql = """
                UPDATE crowd_region_data 
                SET value = %s, created_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """
                cursor.execute(update_sql, (value, existing[0]))
                updated_count += 1
            else:
                # 数据完全相同，跳过
                skipped_count += 1
        
        # 提交事务
        db.connection.commit()
        print(f"区域分布数据处理完成: 插入 {inserted_count} 条, 更新 {updated_count} 条, 跳过 {skipped_count} 条")
        return inserted_count > 0 or updated_count > 0
        
    except Exception as e:
        print(f"保存区域分布数据到MySQL数据库时出错: {str(e)}")
        if db and db.connection:
            db.connection.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def save_gender_data_to_db(data_list, keyword, date):
    """保存性别数据到MySQL数据库"""
    db = None
    cursor = None
    try:
        db = DatabaseConnection()
        cursor = db.connection.cursor()
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS crowd_gender_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            typeId INT NOT NULL,
            name VARCHAR(50) NOT NULL,
            tgi FLOAT NOT NULL,
            rate FLOAT NOT NULL,
            keyword VARCHAR(100) NOT NULL,
            date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_gender (name, keyword, date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        cursor.execute(create_table_sql)
        
        # 追踪插入和更新的数量
        inserted_count = 0
        updated_count = 0
        skipped_count = 0
        
        # 处理每条数据
        for item in data_list:
            if item.get('desc') in ['男', '女']:
                name = item.get('desc', '')
                typeId = int(item.get('typeId', 0))
                tgi = float(item.get('tgi', 0))
                rate = float(item.get('rate', 0))
                
                # 检查数据是否已存在
                check_sql = """
                SELECT id, typeId, tgi, rate FROM crowd_gender_data 
                WHERE name = %s AND keyword = %s AND date = %s
                """
                cursor.execute(check_sql, (
                    name,
                    keyword[:100],
                    date.strftime('%Y-%m-%d')
                ))
                
                existing = cursor.fetchone()
                if not existing:
                    # 不存在，插入新数据
                    insert_sql = """
                    INSERT INTO crowd_gender_data (typeId, name, tgi, rate, keyword, date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_sql, (
                        typeId,
                        name,
                        tgi,
                        rate,
                        keyword[:100],
                        date.strftime('%Y-%m-%d')
                    ))
                    inserted_count += 1
                elif existing[1] != typeId or abs(existing[2] - tgi) > 0.01 or abs(existing[3] - rate) > 0.01:
                    # 数据存在但有变化，更新数据
                    update_sql = """
                    UPDATE crowd_gender_data 
                    SET typeId = %s, tgi = %s, rate = %s, created_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """
                    cursor.execute(update_sql, (typeId, tgi, rate, existing[0]))
                    updated_count += 1
                else:
                    # 数据完全相同，跳过
                    skipped_count += 1
        
        # 提交事务
        db.connection.commit()
        print(f"性别数据处理完成: 插入 {inserted_count} 条, 更新 {updated_count} 条, 跳过 {skipped_count} 条")
        return inserted_count > 0 or updated_count > 0
        
    except Exception as e:
        print(f"保存性别数据到MySQL数据库时出错: {str(e)}")
        if db and db.connection:
            db.connection.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def save_age_data_to_db(data_list, keyword, date):
    """保存年龄数据到MySQL数据库"""
    db = None
    cursor = None
    try:
        db = DatabaseConnection()
        cursor = db.connection.cursor()
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS crowd_age_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            typeId INT NOT NULL,
            name VARCHAR(50) NOT NULL,
            tgi FLOAT NOT NULL,
            rate FLOAT NOT NULL,
            keyword VARCHAR(100) NOT NULL,
            date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_age (name, keyword, date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        cursor.execute(create_table_sql)
        
        # 追踪插入和更新的数量
        inserted_count = 0
        updated_count = 0
        skipped_count = 0
        
        # 处理每条数据
        for item in data_list:
            if item.get('desc') not in ['男', '女']:
                name = item.get('desc', '')
                typeId = int(item.get('typeId', 0))
                tgi = float(item.get('tgi', 0))
                rate = float(item.get('rate', 0))
                
                # 检查数据是否已存在
                check_sql = """
                SELECT id, typeId, tgi, rate FROM crowd_age_data 
                WHERE name = %s AND keyword = %s AND date = %s
                """
                cursor.execute(check_sql, (
                    name,
                    keyword[:100],
                    date.strftime('%Y-%m-%d')
                ))
                
                existing = cursor.fetchone()
                if not existing:
                    # 不存在，插入新数据
                    insert_sql = """
                    INSERT INTO crowd_age_data (typeId, name, tgi, rate, keyword, date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_sql, (
                        typeId,
                        name,
                        tgi,
                        rate,
                        keyword[:100],
                        date.strftime('%Y-%m-%d')
                    ))
                    inserted_count += 1
                elif existing[1] != typeId or abs(existing[2] - tgi) > 0.01 or abs(existing[3] - rate) > 0.01:
                    # 数据存在但有变化，更新数据
                    update_sql = """
                    UPDATE crowd_age_data 
                    SET typeId = %s, tgi = %s, rate = %s, created_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """
                    cursor.execute(update_sql, (typeId, tgi, rate, existing[0]))
                    updated_count += 1
                else:
                    # 数据完全相同，跳过
                    skipped_count += 1
        
        # 提交事务
        db.connection.commit()
        print(f"年龄数据处理完成: 插入 {inserted_count} 条, 更新 {updated_count} 条, 跳过 {skipped_count} 条")
        return inserted_count > 0 or updated_count > 0
        
    except Exception as e:
        print(f"保存年龄数据到MySQL数据库时出错: {str(e)}")
        if db and db.connection:
            db.connection.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def save_interest_data_to_db(data_list, keyword, date):
    """保存兴趣分布数据到MySQL数据库"""
    db = None
    cursor = None
    try:
        db = DatabaseConnection()
        cursor = db.connection.cursor()
        
        # 创建表（如果不存在）
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS crowd_interest_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            value INT NOT NULL,
            tgi INT NOT NULL,
            rate FLOAT NOT NULL,
            category VARCHAR(50) NOT NULL,
            keyword VARCHAR(100) NOT NULL,
            data_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_interest (name, keyword, data_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        cursor.execute(create_table_sql)
        
        # 追踪插入和更新的数量
        inserted_count = 0
        updated_count = 0
        skipped_count = 0
        
        # 处理每条数据
        for item in data_list:
            name = item.get('name', '')[:100]
            value = int(item.get('value', 0))
            tgi = int(item.get('tgi', 0))
            rate = float(item.get('rate', 0))
            category = item.get('category', '未知')
            
            # 检查数据是否已存在
            check_sql = """
            SELECT id, value, tgi, rate FROM crowd_interest_data 
            WHERE name = %s AND keyword = %s AND data_date = %s
            """
            cursor.execute(check_sql, (
                name,
                keyword[:100],
                date.strftime('%Y-%m-%d')
            ))
            
            existing = cursor.fetchone()
            if not existing:
                # 不存在，插入新数据
                insert_sql = """
                INSERT INTO crowd_interest_data (name, value, tgi, rate, category, keyword, data_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (
                    name,
                    value,
                    tgi,
                    rate,
                    category,
                    keyword[:100],
                    date.strftime('%Y-%m-%d')
                ))
                inserted_count += 1
            elif existing[1] != value or existing[2] != tgi or abs(existing[3] - rate) > 0.01:
                # 数据存在但有变化，更新数据
                update_sql = """
                UPDATE crowd_interest_data 
                SET value = %s, tgi = %s, rate = %s, created_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """
                cursor.execute(update_sql, (value, tgi, rate, existing[0]))
                updated_count += 1
            else:
                # 数据完全相同，跳过
                skipped_count += 1
        
        # 提交事务
        db.connection.commit()
        print(f"兴趣分布数据处理完成: 插入 {inserted_count} 条, 更新 {updated_count} 条, 跳过 {skipped_count} 条")
        return inserted_count > 0 or updated_count > 0
        
    except Exception as e:
        print(f"保存兴趣分布数据到MySQL数据库时出错: {str(e)}")
        if db and db.connection:
            db.connection.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def get_interest_data(word, category_id, category_name, headers):
    """获取特定分类的兴趣数据"""
    try:
        params = {
            'wordlist[]': word,
            'typeid': category_id
        }
        url = "https://index.baidu.com/api/SocialApi/interest"
        print(f"| 正在获取分类 {category_name} (ID: {category_id}) 的兴趣数据...")

        response = requests.get(url, params=params, headers=headers)
        time.sleep(1)

        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 0 and data.get('data'):
                result = data['data']['result']
                interest_data = []

                keyword_data = result[0].get('interest', [])
                all_net_data = result[1].get('interest', []) if len(result) > 1 else []

                for i, item in enumerate(keyword_data):
                    if isinstance(item, dict):
                        all_net_item = all_net_data[i] if i < len(all_net_data) else {}
                        try:
                            processed_item = {
                                'name': item.get('desc', '未知'),
                                'typeId': item.get('typeId', ''),
                                'value': round(float(item.get('rate', '0') or '0'), 2),
                                'tgi': round(float(item.get('tgi', '0') or '0'), 2),
                                'all_net_value': round(float(all_net_item.get('rate', '0') or '0'), 2) if all_net_item else 0,
                                'all_net_tgi': round(float(all_net_item.get('tgi', '0') or '0'), 2) if all_net_item else 0,
                                'category': category_name
                            }
                            interest_data.append(processed_item)
                        except (ValueError, TypeError) as e:
                            print(f"处理 {category_name} 的兴趣数据项时出错：{str(e)}")
                            continue

                return interest_data
            else:
                print(f"API返回错误: {json.dumps(data, ensure_ascii=False)}")
        else:
            print(f"请求失败，状态码: {response.status_code}")

    except Exception as e:
        print(f"获取兴趣数据出错: {str(e)}")
        import traceback
        print(f"错误详情: {traceback.format_exc()}")
    return []

def get_crowd_portrait_data(keyword, save_dir):
    """获取人群画像数据"""
    try:
        # 创建保存目录
        portrait_dir = os.path.join(save_dir, 'data', 'crowd_portrait')
        os.makedirs(portrait_dir, exist_ok=True)

        # 设置请求头
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie':'BAIDUID=34CB65A4C9458D3BBB52E00A0D69A789:FG=1; BIDUPSID=34CB65A4C9458D3BBB52E00A0D69A789; PSTM=1744952492; BAIDUID_BFESS=34CB65A4C9458D3BBB52E00A0D69A789:FG=1; ZFY=ATeXDuugsZG50THi:B:BkA0Z9mWQgq:Bbx2GM8qlA2im0s:C; newlogin=1; BDUSS=dVZmJtcXZ1NjdNSTdOYk93OVFUbWxVam9rOFppc1RPNkppVWtHMjhWY1AzRGRvSVFBQUFBJCQAAAAAAQAAAAEAAAAVucsnQW1kb27YvEN5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA9PEGgPTxBoRl; H_PS_PSSID=61027_62484_62327_62891_62928_62967_63019_63042_63046_63034_63146_63091; BA_HECTOR=242h2k85200g04a1al840g2k8m98if1k1ivth22; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; PSINO=6; delPer=0; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BCLID=10336332024730948513; BCLID_BFESS=10336332024730948513; BDSFRCVID=q4_OJexroGWgCqbsyqHzT92lNQpWxY5TDYrELPfiaimDVu-VvXWoEG0Pts1-dEu-S2EwogKKXgOTHw0F_2uxOjjg8UtVJeC6EG0Ptf8g0M5; BDSFRCVID_BFESS=q4_OJexroGWgCqbsyqHzT92lNQpWxY5TDYrELPfiaimDVu-VvXWoEG0Pts1-dEu-S2EwogKKXgOTHw0F_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF=tRAOoC8-fIvDqTrP-trf5DCShUFsbt6iB2Q-XPoO3M3JEPjPKnray5t7eH5QWqojQ5bk_xbgy4op8P3y0bb2DUA1y4vp-qvUa2TxoUJ2-KDVeh5Gqq-KQJ-ebPRiXPb9QgbfopQ7tt5W8ncFbT7l5hKpbt-q0x-jLTnhVn0MBCK0hD89Dj-Ke5PthxO-hI6aKC5bL6rJabC3qDb3XU6q2bDeQnJM3boa-55DaPcmfCoS8xjx3n7Zjq0vWq54WpOh2C60WlbCb664fxn5hUonDh83KNLLKUQtHGAHK43O5hvvob3O3M7bDMKmDloOW-TB5bbPLUQF5l8-sq0x0bOte-bQXH_E5bj2qRuDoK8K3f; H_BDCLCKID_SF_BFESS=tRAOoC8-fIvDqTrP-trf5DCShUFsbt6iB2Q-XPoO3M3JEPjPKnray5t7eH5QWqojQ5bk_xbgy4op8P3y0bb2DUA1y4vp-qvUa2TxoUJ2-KDVeh5Gqq-KQJ-ebPRiXPb9QgbfopQ7tt5W8ncFbT7l5hKpbt-q0x-jLTnhVn0MBCK0hD89Dj-Ke5PthxO-hI6aKC5bL6rJabC3qDb3XU6q2bDeQnJM3boa-55DaPcmfCoS8xjx3n7Zjq0vWq54WpOh2C60WlbCb664fxn5hUonDh83KNLLKUQtHGAHK43O5hvvob3O3M7bDMKmDloOW-TB5bbPLUQF5l8-sq0x0bOte-bQXH_E5bj2qRuDoK8K3f; Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc=1745899248,1746501632; HMACCOUNT=7B93E42C07B9C9DD; bdindexid=pgdnfg3640mbfrou4hue1q5eg5; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a049651408668FCr%2Bmjh%2BAk9bI%2Ft6kgzdGY1IOGUFaPKpA%2BYhjGy3yqCK2Z6tdylLhBciOWODCzleUqB2rtRYCXdZ8h1b3vjbioV30JY7eHTM2lDrolosHQGewxb%2BUZFeyTALzi9LY9Uk1oR9GRoxHQwmsGVumRwfCtNTKVcPwGH3USm7T9dlTqvfUvRIPSCZvU2%2FPyabb%2Bvic%2BZMoc9T15HraZCt624nyiKYAE5xoZRvvHlnwW2%2B%2FVHWiYrgJeUjngZCWrWb0r6cS76jubYQlnwU0LZafsYMzvnKudh%2FvXv2S4xzFZkX%2Fg%3D33179532768309692389450509778821; __cas__rn__=496514086; __cas__st__212=bdab102f0e0580291917d7b79726d13836fbf11e124d7913546801e155ae1c33147c8e1f6da59533fd96a932; __cas__id__212=60952149; CPTK_212=2088851321; CPID_212=60952149; RT="z=1&dm=baidu.com&si=db374730-829b-477c-bc2f-a2f0aa2cced9&ss=mabxz79e&sl=h&tt=dne&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf"; Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc=1746502360; BDUSS_BFESS=dVZmJtcXZ1NjdNSTdOYk93OVFUbWxVam9rOFppc1RPNkppVWtHMjhWY1AzRGRvSVFBQUFBJCQAAAAAAQAAAAEAAAAVucsnQW1kb27YvEN5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA9PEGgPTxBoRl; ab_sr=1.0.1_ZGVhOTkxM2VlZTQ5MmUzYTRjYTBiMmRhZmQ2NDA3OWUyMmU1MjFhMzc5OWMzM2YyMzMwNTBkZmRkYjgwZjU4Yzc3ZDhmMDIxM2E1MmJlODBhOTkzNDdiNGYyNjlmMjEzNjk1MTE5YTE5YTJlMDBmNTYzYmVkOTQ1OGVjZThhMDdkMmFmZGFmMmE0M2FjMzQ2MDljY2QyYzFmNzRiM2IzYg==',
            'Host': 'index.baidu.com',
            'Referer': 'https://index.baidu.com/v2/main/index.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }

        # 处理当前月份的数据
        current_time = datetime.now()
        print(f"\n处理月份: {current_time.strftime('%Y-%m')}")
        
        try:
            # 1. 获取区域分布数据
            # 获取最近一周的日期范围
            end_date = current_time - timedelta(days=1)  # 截止到昨天
            start_date = end_date - timedelta(days=6)    # 往前推6天，总共7天
            
            print(f"\n使用日期范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
            
            region_url = f"https://index.baidu.com/api/SearchApi/region?region=0&word={quote(keyword)}&startDate={start_date.strftime('%Y-%m-%d')}&endDate={end_date.strftime('%Y-%m-%d')}"
            print(f"请求区域分布数据: {region_url}")

            region_response = requests.get(region_url, headers=headers)
            print(f"\nAPI响应状态码: {region_response.status_code}")
            print(f"API响应头: {dict(region_response.headers)}")
            
            region_data = region_response.json()
            print(f"\n完整API响应: {json.dumps(region_data, ensure_ascii=False, indent=2)}")
            
            # 检查登录状态
            if region_data.get('status') == 10000:
                print("登录状态已失效，请更新Cookie")
                return False
                
            if region_data.get('status') == 0 and region_data.get('data'):
                try:
                    region_info = region_data['data']['region'][0]
                    # 使用prov字段，因为这是最原始的省份数据
                    if region_info.get('prov'):
                        formatted_region_data = []
                        prov_data = region_info['prov']
                        
                        # 打印原始数据用于调试
                        print("\nAPI返回的原始数据:")
                        for code, value in sorted(prov_data.items()):  # 按代码排序
                            print(f"代码 {code}: {value}")
                        
                        # 直接使用API返回的数据
                        for code, value in prov_data.items():
                            province_name = CODE2PROVINCE.get(str(code), '未知')
                            formatted_region_data.append({
                                'province': province_name,
                                'value': value  # 保持原始值，不进行任何转换
                            })
                        
                        # 按省份名称排序
                        formatted_region_data.sort(key=lambda x: x['province'])
                        
                        # 打印处理后的数据用于调试
                        print("\n处理后的数据:")
                        for item in formatted_region_data:
                            print(f"省份: {item['province']}, 值: {item['value']}")
                        
                        # 保存区域分布数据到数据库
                        if save_region_data_to_db(formatted_region_data, keyword, end_date):
                            print("区域分布数据已保存到数据库")
                        
                        # 保存到Excel
                        df = pd.DataFrame(formatted_region_data)
                        excel_path = os.path.join(portrait_dir, f"{keyword}_区域分布_{end_date.strftime('%Y%m')}.xlsx")
                        df.to_excel(excel_path, index=False)
                        print(f"区域分布数据已保存到Excel: {excel_path}")
                    else:
                        print("区域分布数据为空，跳过保存")
                except (KeyError, IndexError) as e:
                    print(f"处理区域分布数据时出错: {str(e)}")
                    print(f"API返回数据: {json.dumps(region_data, ensure_ascii=False, indent=2)}")
            else:
                print(f"获取区域分布数据失败: {region_data}")
                if region_data.get('status') == 401:
                    print("Cookie已失效，请更新Cookie")
                    return False
            
            # 2. 获取性别和年龄数据
            gender_age_url = f"https://index.baidu.com/api/SocialApi/baseAttributes?wordlist[]={quote(keyword)}"
            print(f"请求性别年龄数据: {gender_age_url}")
            gender_age_response = requests.get(gender_age_url, headers=headers)
            gender_age_data = gender_age_response.json()
            
            if gender_age_data.get('status') == 0 and gender_age_data.get('data'):
                try:
                    result = gender_age_data['data']['result'][0]
                    gender_data = result.get('gender', [])
                    age_data = result.get('age', [])
                    
                    # 保存性别数据
                    if gender_data:
                        if save_gender_data_to_db(gender_data, keyword, current_time):
                            print("性别数据已保存到数据库")
                        gender_df = pd.DataFrame(gender_data)
                        gender_excel_path = os.path.join(portrait_dir, f"{keyword}_性别分布_{current_time.strftime('%Y%m')}.xlsx")
                        gender_df.to_excel(gender_excel_path, index=False)
                        print(f"性别数据已保存到Excel: {gender_excel_path}")
                    
                    # 保存年龄数据
                    if age_data:
                        if save_age_data_to_db(age_data, keyword, current_time):
                            print("年龄数据已保存到数据库")
                        age_df = pd.DataFrame(age_data)
                        age_excel_path = os.path.join(portrait_dir, f"{keyword}_年龄分布_{current_time.strftime('%Y%m')}.xlsx")
                        age_df.to_excel(age_excel_path, index=False)
                        print(f"年龄数据已保存到Excel: {age_excel_path}")
                except (KeyError, IndexError) as e:
                    print(f"处理性别年龄数据时出错: {str(e)}")
                    print(f"API返回数据: {json.dumps(gender_age_data, ensure_ascii=False, indent=2)}")
            else:
                print(f"获取性别年龄数据失败: {gender_age_data}")
                if gender_age_data.get('status') == 401:
                    print("Cookie已失效，请更新Cookie")
                    return False
            
            # 3. 获取兴趣分布数据
            print("\n开始获取兴趣分布数据...")
            all_interest_data = []
            
            # 使用线程池并发获取数据
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_category = {}
                for category in INTEREST_CATEGORIES:
                    interest_url = f"https://index.baidu.com/api/SocialApi/interest?wordlist[]={quote(keyword)}&typeid={category['typeId']}"
                    print(f"请求分类 {category['name']} 的兴趣分布数据: {interest_url}")
                    future = executor.submit(requests.get, interest_url, headers=headers)
                    future_to_category[future] = category

                for future in as_completed(future_to_category):
                    category = future_to_category[future]
                    try:
                        response = future.result()
                        if response.status_code == 200:
                            interest_data = response.json()
                            if interest_data.get('status') == 0 and 'data' in interest_data:
                                result = interest_data['data']['result']
                                if len(result) >= 2:
                                    keyword_data = result[0].get('interest', [])
                                    all_net_data = result[1].get('interest', [])
                                    
                                    for i, item in enumerate(keyword_data):
                                        if isinstance(item, dict):
                                            all_net_item = all_net_data[i] if i < len(all_net_data) else {}
                                            try:
                                                processed_item = {
                                                    'name': item.get('desc', '未知'),
                                                    'typeId': item.get('typeId', ''),
                                                    'value': round(float(item.get('rate', '0') or '0'), 2),
                                                    'tgi': round(float(item.get('tgi', '0') or '0'), 2),
                                                    'all_net_value': round(float(all_net_item.get('rate', '0') or '0'), 2) if all_net_item else 0,
                                                    'all_net_tgi': round(float(all_net_item.get('tgi', '0') or '0'), 2) if all_net_item else 0,
                                                    'category': category['name']
                                                }
                                                all_interest_data.append(processed_item)
                                            except (ValueError, TypeError) as e:
                                                print(f"处理 {category['name']} 的兴趣数据项时出错：{str(e)}")
                                                continue
                                    print(f"成功获取 {category['name']} 的兴趣分布数据")
                                else:
                                    print(f"获取 {category['name']} 的兴趣分布数据失败：数据格式不正确")
                            else:
                                print(f"获取 {category['name']} 的兴趣分布数据失败：{interest_data.get('message', '未知错误')}")
                        else:
                            print(f"获取 {category['name']} 的兴趣分布数据失败：HTTP {response.status_code}")
                    except Exception as e:
                        print(f"处理 {category['name']} 的兴趣分布数据时出错：{str(e)}")

            if all_interest_data:
                # 保存到Excel
                df_interest = pd.DataFrame(all_interest_data)
                excel_path = os.path.join(portrait_dir, f"{keyword}_兴趣分布_{current_time.strftime('%Y%m')}.xlsx")
                df_interest.to_excel(excel_path, index=False)
                print(f"兴趣分布数据已保存到Excel: {excel_path}")
                
                # 保存到数据库
                save_interest_data_to_db(all_interest_data, keyword, current_time)
                
                # 创建可视化图表
                tab = Tab()
                
                # 添加总览图表
                main_data = df_interest.groupby('category').agg({
                    'name': 'first',
                    'value': lambda x: round(x.mean(), 2),
                    'tgi': lambda x: round(x.mean(), 2),
                    'all_net_value': lambda x: round(x.mean(), 2),
                    'all_net_tgi': lambda x: round(x.mean(), 2)
                }).reset_index()
                main_data['name'] = main_data['category']
                
                main_chart = create_chart(main_data, f"{keyword} - 兴趣分布总览")
                tab.add(main_chart, "整体分布")
                
                # 为每个分类创建详细图表
                for category in INTEREST_CATEGORIES:
                    category_data = df_interest[df_interest['category'] == category['name']]
                    if not category_data.empty:
                        category_chart = create_chart(category_data, f"{category['name']} - 详细分布")
                        tab.add(category_chart, category['name'])
                
                # 保存图表
                chart_path = os.path.join(portrait_dir, f"{keyword}_兴趣分布图表_{current_time.strftime('%Y%m')}.html")
                tab.render(chart_path)
                print(f"兴趣分布图表已保存: {chart_path}")
            else:
                print("未获取到任何兴趣分布数据")
            
        except Exception as e:
            print(f"处理月份 {current_time.strftime('%Y-%m')} 时出错: {str(e)}")
            import traceback
            print(f"错误详情: {traceback.format_exc()}")
            return False

        return True

    except Exception as e:
        print(f"获取人群画像数据时出错: {str(e)}")
        import traceback
        print(f"错误详情: {traceback.format_exc()}")
        return False

# 测试代码
if __name__ == "__main__":
    keyword = "养老"
    save_dir = os.path.dirname(os.path.dirname(__file__))

    # 测试数据采集
    result = get_crowd_portrait_data(keyword, save_dir)
    if result:
        print("人群画像数据采集成功")
    else:
        print("人群画像数据采集失败") 