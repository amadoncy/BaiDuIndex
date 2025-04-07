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

def get_province_codes():
    """从数据库获取省份代码映射"""
    db = None
    cursor = None
    try:
        db = DatabaseConnection()
        cursor = db.connection.cursor()
        
        # 先检查表结构
        cursor.execute("DESCRIBE area_codes")
        columns = [column[0] for column in cursor.fetchall()]
        print("area_codes表的列结构:", columns)
        
        # 获取所有省份映射数据并打印
        cursor.execute("SELECT * FROM area_codes WHERE city = 'NULL' OR city IS NULL")
        results = cursor.fetchall()
        print("\n当前数据库中的省份映射:")
        for row in results:
            print(f"ID: {row[0]}, Region: {row[1]}, Province: {row[2]}, City: {row[3]}, Code: {row[4]}")
        
        # 获取省份代码映射
        query = """
        SELECT code, province 
        FROM area_codes 
        WHERE city = 'NULL' OR city IS NULL
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        # 构建代码到省份名称的映射字典
        code_map = {str(code): name for code, name in results}
        print("\n最终生成的省份代码映射字典:")
        for code, name in code_map.items():
            print(f"代码 {code} -> 省份 {name}")
            
        return code_map
        
    except Exception as e:
        print(f"获取省份代码映射失败: {str(e)}")
        return {}
        
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

# 百度指数省份代码映射
CODE2PROVINCE = {
    "901": "山东",
    "902": "安徽",
    "903": "江西",
    "904": "重庆",
    "905": "内蒙古",
    "906": "海南",
    "907": "贵州",
    "908": "宁夏",
    "909": "福建",
    "910": "上海",
    "911": "北京",
    "912": "广西",
    "913": "广东",
    "914": "四川",
    "915": "山西",
    "916": "江苏",
    "917": "浙江",
    "918": "青海",
    "919": "黑龙江",
    "920": "河北",
    "921": "吉林",
    "922": "辽宁",
    "923": "天津",
    "924": "陕西",
    "925": "河南",
    "926": "新疆",
    "927": "湖南",
    "928": "湖北",
    "929": "云南",
    "930": "西藏",
    "931": "甘肃",
    "932": "青海",
    "933": "宁夏",
    "934": "西藏"
}

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
            'Cookie':'BAIDUID=16E5CCC1192556FEE10159406A018509:FG=1; BIDUPSID=16E5CCC1192556FEE10159406A018509; PSTM=1739958453; H_WISE_SIDS_BFESS=62035_62112_62184_62186_62181_62196_62283_62326; MAWEBCUID=web_KXhXVnlpLhbQQSRCKRRisqqVaKJnMgKZIetEZOUCvCGytOiTJG; H_WISE_SIDS=61027_61674_62342_62426_62473_62500_62457_62455_62452_62451_62327_62644_62673_62704_62618_62520_62330_62773; BAIDUID_BFESS=16E5CCC1192556FEE10159406A018509:FG=1; ZFY=j3Dsz2JVStj8D7DQauQBTBbdC:BZ4rAe8jEh1w:BLfZCo:C; H_PS_PSSID=61027_61674_62342_62327_62646_62704_62520_62330_62827_62842_62869; BA_HECTOR=008181a000a08l8la1858021a6iujd1jv6nj523; PSINO=1; delPer=0; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BRAND_LANDING_FROM_PAGE=2231_0_1744002666; BCLID=9555134227461541508; BCLID_BFESS=9555134227461541508; BDSFRCVID=MJFOJexroGWUYtoJPnJ9uxWAWcpWxY5TDYrELPfiaimDVu-Vd6BEEG0Pts1-dEu-S2EwogKKXgOTHwtF_2uxOjjg8UtVJeC6EG0Ptf8g0M5; BDSFRCVID_BFESS=MJFOJexroGWUYtoJPnJ9uxWAWcpWxY5TDYrELPfiaimDVu-Vd6BEEG0Pts1-dEu-S2EwogKKXgOTHwtF_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF=tRAOoC8-fIvEDRbN2KTD-tFO5eT22-usBmQl2hcHMPoosU3aWJOoyl8HyGrthpbCQK7j--nwJxbUotoHXh3tMt_thtOp-Crp5ncGKl5TtUJMqIDzbMohqqJXQqJyKMniyIv9-pn5bpQrh459XP68bTkA5bjZKxtq3mkjbPbDfn028DKu-n5jHj3-jN-H3f; H_BDCLCKID_SF_BFESS=tRAOoC8-fIvEDRbN2KTD-tFO5eT22-usBmQl2hcHMPoosU3aWJOoyl8HyGrthpbCQK7j--nwJxbUotoHXh3tMt_thtOp-Crp5ncGKl5TtUJMqIDzbMohqqJXQqJyKMniyIv9-pn5bpQrh459XP68bTkA5bjZKxtq3mkjbPbDfn028DKu-n5jHj3-jN-H3f; Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc=1743211135,1743406925,1743486520,1744002667; HMACCOUNT=2B879FD6031C4D2D; ppfuid=FOCoIC3q5fKa8fgJnwzbE67EJ49BGJeplOzf+4l4EOvDuu2RXBRv6R3A1AZMa49I27C0gDDLrJyxcIIeAeEhD8JYsoLTpBiaCXhLqvzbzmvy3SeAW17tKgNq/Xx+RgOdb8TWCFe62MVrDTY6lMf2GrfqL8c87KLF2qFER3obJGm51EODDlnqgz44AdUN5VVLGEimjy3MrXEpSuItnI4KD46xh6KcipCBP3WBNo1ZhULgwNSQKKIDdXA6eDfuiw2FJ3ZBF1sLBqLP1Lik2nWCKk4sXpnMWzrlcw817brPPlfGgLbz7OSojK1zRbqBESR5Pdk2R9IA3lxxOVzA+Iw1TWLSgWjlFVG9Xmh1+20oPSbrzvDjYtVPmZ+9/6evcXmhcO1Y58MgLozKnaQIaLfWRHYJbniad6MOTaDR3XV1dTLxUSUZS0ReZYJMPG6nCsxNJlhI2UyeJA6QroZFMelR7tnTNS/pLMWceus0e757/UMPmrThfasmhDJrMFcBfoSrAAv3LCf1Y7/fHL3PTSf9vid/u2VLX4h1nBtx8EF07eCMhWVv+2qjbPV7ZhXk3reaWRFEeso3s/Kc9n/UXtUfNU1sHiCdbrCW5yYsuSM9SPGDZsl7FhTAKw7qIu38vFZiq+DRc8Vbf7jOiN9xPe0lOdZHUhGHZ82rL5jTCsILwcRVCndrarbwmu7G154MpYiKmTXZkqV7Alo4QZzicdyMbWvwvmR2/m//YVTM8qeZWgDSHjDmtehgLWM45zARbPujeqU0T92Gmgs89l2htrSKIVfEFzbtyzdes2f7rMR3DsT9s7hrTTo9fvI0eb7EXkrl28iVHWejeTfeu67KQzKLYpdImdyxYIjA1uSy2hfTFv/d3cnXH4nh+maaicAPllDg7JjsxZAfQoVAycJHizlQ5d34k8SzMID0x3kxnXwHfxXvz6DS3RnKydYTBUIWPYKJAEFefnSer1pU55Mw3PEJuMbPGO6Per4Y9UBohIIx5FdrGRChHnhPuJeIKACPXiVuli9ItRLEkdb1mLxNHAk3uJy88YX/Rf/sKUjR12zxRTDxxJNDJS+Dlsbqu3n4I65ujli/3rQ8Zk1MjmTOsz9+kTqOM4upsnQ6IWq/zeZTItMCgHpQhuhr4ip73honuzoJgge1cqWBFYvpabAPTOERTOP1kmx5SXPARX5uxyJzAiNILBC8zh7fGfNXOWV37O9gPNcivn6S9fB2Uhzqxb280Sz1OqOlLYK4Zd6grclXRmzd7jwWSX9V/ksh8wlbKD1hqmFU2Ekb/vTs/YZwJiVxHg==; BDUSS=h-Z1BVaDB-fmdRSUNudk1acUZrV25xdEcwVndTcUtPZGRyRFU5di1zZHc2eHBvSVFBQUFBJCQAAAAAAQAAAAEAAAAVucsnQW1kb27YvEN5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHBe82dwXvNnZU; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a049401512229aeUGBW7uO3sKds%2BnEQFkaYrBwOLd4jkEUzW03xTHj4wfP5o0yLjHUwD5yLQS7ieWKVBFOpAla%2FkWVUqx%2FvXrPZNKZQeRN93Xo9rWj2eYDaKskJdFKnDfhfeYrGqDJNM95JMzxnDL%2FJ4v%2BjMkZz9Q1kTgD4Vq%2BWRqHon04wNtqIZjWYMKbRLIgfFnoIs%2FU5IusEz08eFrWauSNOn5NOQ8SkYfjEu%2FyFdDKscZOEf%2FMgBbiT4ghV5saGRaDOFp%2BBEVmHnfNO9Hr%2Fxp4x0NYFpYPqhhOfklrEpYGkeNsBVbrQ%3D32729740383291200009764587538236; __cas__rn__=494015122; __cas__st__212=c9292e7efe55d9da1b4ded910007f2b87558a15406c925e6102dd599f239519fe8274c3d24f2081a8825e8db; __cas__id__212=60952149; CPTK_212=1818205581; CPID_212=60952149; bdindexid=i2p7bu7uec6fkv2nst7ghbmbv2; ab_sr=1.0.1_Yjk4MTJmOTIzYTYwZTcwOTdhMjc2MDVlM2FkMDlhZmM4OGQwZGE5ZjY0OTdhZDVhMWM4NTNlYzRhNzhlMDhhODkzNzBmYzQ4ZDFhZGJjOTg2OTYzMTg5ODZkODk5N2NhOWNmNWJhMTNjNWVhMGRkMjEzMWE4YWFiMTNiMTRkN2E4YTczYTRjZWUwMjY3YjgyNjEyZjNjYWQ4MjYxNjY5Yg==; RT="z=1&dm=baidu.com&si=902398b9-828b-4416-824b-28e4efb8592f&ss=m96m5pqh&sl=4&tt=6l2&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf"; Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc=1744002683',
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
            
            region_url = f"https://index.baidu.com/api/SearchApi/region?region=0&word={quote(keyword)}&startDate={start_date.strftime('%Y-%m-%d')}&endDate={end_date.strftime('%Y-%m-%d')}"
            print(f"请求区域分布数据: {region_url}")

            for key, value in headers.items():
                if key.lower() != 'cookie':
                    print(f"{key}: {value}")
                else:
                    print(f"{key}: [已隐藏]")

            region_response = requests.get(region_url, headers=headers)
            region_data = region_response.json()

            
            if region_data.get('status') == 0 and region_data.get('data'):
                try:
                    region_info = region_data['data']['region'][0]
                    if region_info.get('prov_real') or region_info.get('city_real'):
                        # 处理省份数据
                        if region_info.get('prov_real'):
                            formatted_region_data = []
                            prov_real = region_info['prov_real']
                            for code, value in prov_real.items():
                                province_name = CODE2PROVINCE.get(str(code), '未知')
                                formatted_region_data.append({
                                    'province': province_name,
                                    'value': int(value)
                                })
                            
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