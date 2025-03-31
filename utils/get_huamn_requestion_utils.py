import requests
import json
import pandas as pd
import os
from datetime import datetime, date, timedelta
from utils.db_utils import DatabaseConnection
from urllib.parse import quote


def save_data_to_db(data_list, keyword, date):
    """保存需求图谱数据到MySQL数据库"""
    db = None
    cursor = None
    try:
        db = DatabaseConnection()
        cursor = db.connection.cursor()

        # 创建表（如果不存在）
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS human_request_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            word VARCHAR(255) NOT NULL,
            pv INT NOT NULL,
            ratio INT NOT NULL,
            sim INT NOT NULL,
            keyword VARCHAR(100) NOT NULL,
            date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_request (word(200), keyword(50), date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        cursor.execute(create_table_sql)

        # 批量插入数据
        insert_sql = """
        INSERT INTO human_request_data (word, pv, ratio, sim, keyword, date)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        pv = VALUES(pv),
        ratio = VALUES(ratio),
        sim = VALUES(sim)
        """

        # 准备批量插入的数据
        values = []
        for item in data_list:
            values.append((
                item.get('word', '')[:255],  # 限制字段长度
                int(item.get('pv', 0)),
                int(item.get('ratio', 0)),
                int(item.get('sim', 0)),
                keyword[:100],  # 限制字段长度
                date.strftime('%Y-%m-%d')
            ))

        # 执行批量插入
        if values:
            cursor.executemany(insert_sql, values)
            db.connection.commit()
            print(f"成功保存 {len(values)} 条数据到MySQL数据库")
            return True

        return False

    except Exception as e:
        print(f"保存数据到MySQL数据库时出错: {str(e)}")
        if db and db.connection:
            try:
                db.connection.rollback()
            except Exception as rollback_e:
                print(f"回滚事务失败: {rollback_e}")
        return False

    finally:
        if cursor:
            try:
                cursor.close()
            except Exception as e:
                print(f"关闭cursor失败: {e}")

        if db:
            try:
                db.close()
            except Exception as e:
                print(f"关闭数据库连接失败: {e}")


def get_human_request_data(keyword, username):
    """
    获取需求图谱数据（最近一周）
    :param keyword: 关键词
    :param username: 用户名
    :return: 是否成功
    """
    try:
        # 创建保存目录
        save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'requisition')
        os.makedirs(save_dir, exist_ok=True)

        # 构建请求URL
        encoded_keyword = quote(keyword)
        url = "https://index.baidu.com/api/WordGraph/multi"

        # 获取当前日期和一周前的日期
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # 设置请求参数
        params = {
            'wordlist[]': keyword,
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d')
        }

        # 设置请求头
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': 'BAIDUID=16E5CCC1192556FEE10159406A018509:FG=1; BIDUPSID=16E5CCC1192556FEE10159406A018509; PSTM=1739958453; H_WISE_SIDS_BFESS=62035_62112_62184_62186_62181_62196_62283_62326; MAWEBCUID=web_KXhXVnlpLhbQQSRCKRRisqqVaKJnMgKZIetEZOUCvCGytOiTJG; BAIDUID_BFESS=16E5CCC1192556FEE10159406A018509:FG=1; ZFY=j3Dsz2JVStj8D7DQauQBTBbdC:BZ4rAe8jEh1w:BLfZCo:C; BDUSS=dsTS12TWlHYmZ4RXJOd2xJZ2lLc1hyejhpODR1anNsVEEzbWVTb1Q3Vkgyd1ZvSVFBQUFBJCQAAAAAAQAAAAEAAAAVucsnQW1kb27YvEN5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEdO3mdHTt5nME; H_WISE_SIDS=61027_61674_62342_62426_62473_62500_62457_62455_62452_62451_62327_62644_62673_62704_62618_62520_62330_62773; H_PS_PSSID=61027_61674_62342_62327_62644_62673_62704_62618_62520_62330_62773_62827; BA_HECTOR=0hal2l200h2ha58h8g0k818g018kja1jukhq522; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; PSINO=6; delPer=0; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BCLID=9939879626829125608; BCLID_BFESS=9939879626829125608; BDSFRCVID=P2FOJexroGWUYtoJg4T0vwn9YQpWxY5TDYrELPfiaimDVu-Vd6BEEG0Pts1-dEu-S2EwogKKXgOTHwtF_2uxOjjg8UtVJeC6EG0Ptf8g0M5; BDSFRCVID_BFESS=P2FOJexroGWUYtoJg4T0vwn9YQpWxY5TDYrELPfiaimDVu-Vd6BEEG0Pts1-dEu-S2EwogKKXgOTHwtF_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF=tRAOoC8-fIvEDRbN2KTD-tFO5eT22-usLnrl2hcHMPoosU3aWJOoy4b33a3q--C8yG6j--nwJxbUotoHXh3tMt_thtOp-Crp5ncGKl5TtUJMqIDzbMohqqJXQqJyKMniyIv9-pn5bpQrh459XP68bTkA5bjZKxtq3mkjbPbDfn028DKu-n5jHj3WeHOP; H_BDCLCKID_SF_BFESS=tRAOoC8-fIvEDRbN2KTD-tFO5eT22-usLnrl2hcHMPoosU3aWJOoy4b33a3q--C8yG6j--nwJxbUotoHXh3tMt_thtOp-Crp5ncGKl5TtUJMqIDzbMohqqJXQqJyKMniyIv9-pn5bpQrh459XP68bTkA5bjZKxtq3mkjbPbDfn028DKu-n5jHj3WeHOP; Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc=1742692411,1743142244,1743211135,1743406925; HMACCOUNT=2B879FD6031C4D2D; bdindexid=5sqracr4ehibesoq2bh5f0tdm2; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a04934193733LKbiz%2BmJpPyIUcsvrJ90a%2B%2FDeAWszo4F5HxfaLETAESuUpBKPxMQ3qKesSnrAlaLD3AUZOwtQws4EpDqRVXirR4q6DhUmmoLo6SmnQh%2B9YckJfKfRUoUuahF5tpUgzAFta%2BpzjF34X9WSOe51IMUAptRnty0f7y90FJ4EbeWpGjmUWPEV7ebol7tVw5M2LIysVmc7PXPN0KuekmxOTzQjwpGdnuliAtX1S4UYFXi6t1jE4z3YEpGlwBnJp%2B1BsbiBZNNT6J0lqHVOFFh4%2B5V3LXRKnd7ecYzo4QMdoeWud8%3D80006705074010718894150696033484; __cas__rn__=493419373; __cas__st__212=082eb47e574009aa7315e0a9602a42b5006c22435a0ff2b24deeebbcab26c710f3c0ea0b8028583d6afe4ac8; __cas__id__212=60952149; CPTK_212=1460652888; CPID_212=60952149; Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc=1743406929; ab_sr=1.0.1_M2ZlOWRjODVlNmFjNmYzODNkZmI0MjA0MGMxZDIyZmMxMDgxNmJhOWY1M2FkOGQ3ZjlmNGRkNGY1NTBmZGJiOGE1OTFiNWIzMGY4ZTNlOWIxNTk2MDg4NTY1YTNhMWZjMjFlMTNhNjBkNzE5MjM5OGY4Njc4Mzg4YjIxODVjOTgzYzY1MDQ5Y2Q5MGY1OTdjOTQ3NGQxNzUzNmJlMzhiNg==; BDUSS_BFESS=dsTS12TWlHYmZ4RXJOd2xJZ2lLc1hyejhpODR1anNsVEEzbWVTb1Q3Vkgyd1ZvSVFBQUFBJCQAAAAAAQAAAAEAAAAVucsnQW1kb27YvEN5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEdO3mdHTt5nME; RT="z=1&dm=baidu.com&si=2f2cd6e0-77ea-43c1-ab3b-30cb0a0c2feb&ss=m8wrgw95&sl=4&tt=4nn&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf"',
            'Host': 'index.baidu.com',
            'Referer': f'https://index.baidu.com/v2/main/index.html#/trend/{encoded_keyword}?words={encoded_keyword}',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }

        # 发送请求
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        # 打印响应内容以便调试
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text[:500]}...")  # 只打印前500个字符

        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {str(e)}")
            print(f"完整响应内容: {response.text}")
            return False

        if data.get('status') == 0:
            # 检查data字段是否为字典
            if isinstance(data.get('data'), dict):
                # 提取数据
                wordlist = data.get('data', {}).get('wordlist', [])
                if wordlist and len(wordlist) > 0:
                    human_request_data = wordlist[0].get('wordGraph', [])

                    # 保存到数据库
                    if human_request_data:
                        # 确保数据格式正确
                        formatted_data = []
                        for item in human_request_data:
                            formatted_item = {
                                'word': item.get('word', ''),
                                'pv': int(item.get('pv', 0)),
                                'ratio': int(item.get('ratio', 0)),
                                'sim': int(item.get('sim', 0)),
                                'keyword': keyword,
                                'date': end_date.strftime('%Y-%m-%d')
                            }
                            formatted_data.append(formatted_item)
                            print(f"处理数据: {formatted_item}")  # 打印每条数据

                        # 保存到MySQL数据库
                        success = save_data_to_db(formatted_data, keyword, end_date.date())
                        if success:
                            print(f"成功保存 {len(formatted_data)} 条数据到MySQL数据库")
                        else:
                            print("保存数据到MySQL数据库失败")

                        # 尝试保存Excel文件
                        try:
                            # 创建DataFrame并保存为Excel
                            df = pd.DataFrame(formatted_data)
                            excel_path = os.path.join(save_dir, f"{keyword}_{end_date.strftime('%Y%m%d')}.xlsx")
                            df.to_excel(excel_path, index=False)
                            print(f"数据已保存到: {excel_path}")
                        except PermissionError:
                            print(f"无法保存Excel文件（可能正在被其他程序使用）: {excel_path}")
                        except Exception as e:
                            print(f"保存Excel文件时出错: {str(e)}")
                    else:
                        print("未获取到数据")
                else:
                    print("未获取到数据")
            else:
                print("未获取到数据")
        else:
            print(f"获取数据失败: {data.get('message', '未知错误')}")

        return True

    except Exception as e:
        print(f"获取需求图谱数据时出错: {str(e)}")
        return False


# 测试代码
if __name__ == "__main__":
    keyword = "养老"
    username = "your_username"  # 替换为实际的用户名

    # 测试需求图谱数据采集
    result = get_human_request_data(keyword, username)
    if result:
        print("需求图谱数据采集成功")
    else:
        print("需求图谱数据采集失败")