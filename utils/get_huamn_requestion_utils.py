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

        # 追踪插入和更新的数量
        inserted_count = 0
        updated_count = 0
        skipped_count = 0

        # 处理每条数据
        for item in data_list:
            word = item.get('word', '')[:255]  # 限制字段长度
            pv = int(item.get('pv', 0))
            ratio = int(item.get('ratio', 0))
            sim = int(item.get('sim', 0))
            
            # 检查数据是否已存在
            check_sql = """
            SELECT id, pv, ratio, sim FROM human_request_data 
            WHERE word = %s AND keyword = %s AND date = %s
            """
            cursor.execute(check_sql, (
                word,
                keyword[:100],
                date.strftime('%Y-%m-%d')
            ))
            
            existing = cursor.fetchone()
            if not existing:
                # 不存在，插入新数据
                insert_sql = """
                INSERT INTO human_request_data (word, pv, ratio, sim, keyword, date)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (
                    word,
                    pv,
                    ratio,
                    sim,
                    keyword[:100],
                    date.strftime('%Y-%m-%d')
                ))
                inserted_count += 1
            elif existing[1] != pv or existing[2] != ratio or existing[3] != sim:
                # 数据存在但有变化，更新数据
                update_sql = """
                UPDATE human_request_data 
                SET pv = %s, ratio = %s, sim = %s, created_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """
                cursor.execute(update_sql, (pv, ratio, sim, existing[0]))
                updated_count += 1
            else:
                # 数据完全相同，跳过
                skipped_count += 1

        # 提交事务
        db.connection.commit()
        print(f"数据处理完成: 插入 {inserted_count} 条, 更新 {updated_count} 条, 跳过 {skipped_count} 条")
        return inserted_count > 0 or updated_count > 0

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
            'Cookie':'BAIDUID=16E5CCC1192556FEE10159406A018509:FG=1; BIDUPSID=16E5CCC1192556FEE10159406A018509; PSTM=1739958453; H_WISE_SIDS_BFESS=62035_62112_62184_62186_62181_62196_62283_62326; MAWEBCUID=web_KXhXVnlpLhbQQSRCKRRisqqVaKJnMgKZIetEZOUCvCGytOiTJG; H_WISE_SIDS=61027_61674_62342_62426_62473_62500_62457_62455_62452_62451_62327_62644_62673_62704_62618_62520_62330_62773; BAIDUID_BFESS=16E5CCC1192556FEE10159406A018509:FG=1; ZFY=j3Dsz2JVStj8D7DQauQBTBbdC:BZ4rAe8jEh1w:BLfZCo:C; H_PS_PSSID=61027_61674_62342_62327_62646_62704_62520_62330_62827_62842_62869; BA_HECTOR=008181a000a08l8la1858021a6iujd1jv6nj523; PSINO=1; delPer=0; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BRAND_LANDING_FROM_PAGE=2231_0_1744002666; BCLID=9555134227461541508; BCLID_BFESS=9555134227461541508; BDSFRCVID=MJFOJexroGWUYtoJPnJ9uxWAWcpWxY5TDYrELPfiaimDVu-Vd6BEEG0Pts1-dEu-S2EwogKKXgOTHwtF_2uxOjjg8UtVJeC6EG0Ptf8g0M5; BDSFRCVID_BFESS=MJFOJexroGWUYtoJPnJ9uxWAWcpWxY5TDYrELPfiaimDVu-Vd6BEEG0Pts1-dEu-S2EwogKKXgOTHwtF_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF=tRAOoC8-fIvEDRbN2KTD-tFO5eT22-usBmQl2hcHMPoosU3aWJOoyl8HyGrthpbCQK7j--nwJxbUotoHXh3tMt_thtOp-Crp5ncGKl5TtUJMqIDzbMohqqJXQqJyKMniyIv9-pn5bpQrh459XP68bTkA5bjZKxtq3mkjbPbDfn028DKu-n5jHj3-jN-H3f; H_BDCLCKID_SF_BFESS=tRAOoC8-fIvEDRbN2KTD-tFO5eT22-usBmQl2hcHMPoosU3aWJOoyl8HyGrthpbCQK7j--nwJxbUotoHXh3tMt_thtOp-Crp5ncGKl5TtUJMqIDzbMohqqJXQqJyKMniyIv9-pn5bpQrh459XP68bTkA5bjZKxtq3mkjbPbDfn028DKu-n5jHj3-jN-H3f; Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc=1743211135,1743406925,1743486520,1744002667; HMACCOUNT=2B879FD6031C4D2D; ppfuid=FOCoIC3q5fKa8fgJnwzbE67EJ49BGJeplOzf+4l4EOvDuu2RXBRv6R3A1AZMa49I27C0gDDLrJyxcIIeAeEhD8JYsoLTpBiaCXhLqvzbzmvy3SeAW17tKgNq/Xx+RgOdb8TWCFe62MVrDTY6lMf2GrfqL8c87KLF2qFER3obJGm51EODDlnqgz44AdUN5VVLGEimjy3MrXEpSuItnI4KD46xh6KcipCBP3WBNo1ZhULgwNSQKKIDdXA6eDfuiw2FJ3ZBF1sLBqLP1Lik2nWCKk4sXpnMWzrlcw817brPPlfGgLbz7OSojK1zRbqBESR5Pdk2R9IA3lxxOVzA+Iw1TWLSgWjlFVG9Xmh1+20oPSbrzvDjYtVPmZ+9/6evcXmhcO1Y58MgLozKnaQIaLfWRHYJbniad6MOTaDR3XV1dTLxUSUZS0ReZYJMPG6nCsxNJlhI2UyeJA6QroZFMelR7tnTNS/pLMWceus0e757/UMPmrThfasmhDJrMFcBfoSrAAv3LCf1Y7/fHL3PTSf9vid/u2VLX4h1nBtx8EF07eCMhWVv+2qjbPV7ZhXk3reaWRFEeso3s/Kc9n/UXtUfNU1sHiCdbrCW5yYsuSM9SPGDZsl7FhTAKw7qIu38vFZiq+DRc8Vbf7jOiN9xPe0lOdZHUhGHZ82rL5jTCsILwcRVCndrarbwmu7G154MpYiKmTXZkqV7Alo4QZzicdyMbWvwvmR2/m//YVTM8qeZWgDSHjDmtehgLWM45zARbPujeqU0T92Gmgs89l2htrSKIVfEFzbtyzdes2f7rMR3DsT9s7hrTTo9fvI0eb7EXkrl28iVHWejeTfeu67KQzKLYpdImdyxYIjA1uSy2hfTFv/d3cnXH4nh+maaicAPllDg7JjsxZAfQoVAycJHizlQ5d34k8SzMID0x3kxnXwHfxXvz6DS3RnKydYTBUIWPYKJAEFefnSer1pU55Mw3PEJuMbPGO6Per4Y9UBohIIx5FdrGRChHnhPuJeIKACPXiVuli9ItRLEkdb1mLxNHAk3uJy88YX/Rf/sKUjR12zxRTDxxJNDJS+Dlsbqu3n4I65ujli/3rQ8Zk1MjmTOsz9+kTqOM4upsnQ6IWq/zeZTItMCgHpQhuhr4ip73honuzoJgge1cqWBFYvpabAPTOERTOP1kmx5SXPARX5uxyJzAiNILBC8zh7fGfNXOWV37O9gPNcivn6S9fB2Uhzqxb280Sz1OqOlLYK4Zd6grclXRmzd7jwWSX9V/ksh8wlbKD1hqmFU2Ekb/vTs/YZwJiVxHg==; BDUSS=h-Z1BVaDB-fmdRSUNudk1acUZrV25xdEcwVndTcUtPZGRyRFU5di1zZHc2eHBvSVFBQUFBJCQAAAAAAQAAAAEAAAAVucsnQW1kb27YvEN5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHBe82dwXvNnZU; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a049401512229aeUGBW7uO3sKds%2BnEQFkaYrBwOLd4jkEUzW03xTHj4wfP5o0yLjHUwD5yLQS7ieWKVBFOpAla%2FkWVUqx%2FvXrPZNKZQeRN93Xo9rWj2eYDaKskJdFKnDfhfeYrGqDJNM95JMzxnDL%2FJ4v%2BjMkZz9Q1kTgD4Vq%2BWRqHon04wNtqIZjWYMKbRLIgfFnoIs%2FU5IusEz08eFrWauSNOn5NOQ8SkYfjEu%2FyFdDKscZOEf%2FMgBbiT4ghV5saGRaDOFp%2BBEVmHnfNO9Hr%2Fxp4x0NYFpYPqhhOfklrEpYGkeNsBVbrQ%3D32729740383291200009764587538236; __cas__rn__=494015122; __cas__st__212=c9292e7efe55d9da1b4ded910007f2b87558a15406c925e6102dd599f239519fe8274c3d24f2081a8825e8db; __cas__id__212=60952149; CPTK_212=1818205581; CPID_212=60952149; bdindexid=i2p7bu7uec6fkv2nst7ghbmbv2; ab_sr=1.0.1_Yjk4MTJmOTIzYTYwZTcwOTdhMjc2MDVlM2FkMDlhZmM4OGQwZGE5ZjY0OTdhZDVhMWM4NTNlYzRhNzhlMDhhODkzNzBmYzQ4ZDFhZGJjOTg2OTYzMTg5ODZkODk5N2NhOWNmNWJhMTNjNWVhMGRkMjEzMWE4YWFiMTNiMTRkN2E4YTczYTRjZWUwMjY3YjgyNjEyZjNjYWQ4MjYxNjY5Yg==; RT="z=1&dm=baidu.com&si=902398b9-828b-4416-824b-28e4efb8592f&ss=m96m5pqh&sl=4&tt=6l2&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf"; Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc=1744002683',
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