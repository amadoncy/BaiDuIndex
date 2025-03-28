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
            'Cookie': 'BAIDUID=16E5CCC1192556FEE10159406A018509:FG=1; BIDUPSID=16E5CCC1192556FEE10159406A018509; PSTM=1739958453; H_WISE_SIDS_BFESS=62035_62112_62184_62186_62181_62196_62283_62326; MAWEBCUID=web_KXhXVnlpLhbQQSRCKRRisqqVaKJnMgKZIetEZOUCvCGytOiTJG; H_WISE_SIDS=61027_61674_62342_62345_62426_62473_62500_62457_62455_62452_62451_62327_62644_62673; H_PS_PSSID=61027_61674_62342_62345_62426_62473_62500_62457_62455_62452_62451_62327_62644_62646_62673; Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc=1742539344,1742560102,1742570202,1742619258; HMACCOUNT=2B879FD6031C4D2D; delPer=0; PSINO=1; BAIDUID_BFESS=16E5CCC1192556FEE10159406A018509:FG=1; BA_HECTOR=a48484al048424ag85208k8h0fbc891jtsh2o22; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; ZFY=j3Dsz2JVStj8D7DQauQBTBbdC:BZ4rAe8jEh1w:BLfZCo:C; ppfuid=FOCoIC3q5fKa8fgJnwzbE67EJ49BGJeplOzf+4l4EOvDuu2RXBRv6R3A1AZMa49I27C0gDDLrJyxcIIeAeEhD8JYsoLTpBiaCXhLqvzbzmvy3SeAW17tKgNq/Xx+RgOdb8TWCFe62MVrDTY6lMf2GrfqL8c87KLF2qFER3obJGkjS1Q+e/k7Rs6uiFpI37bSGEimjy3MrXEpSuItnI4KDzKu30suSE3sF8hPJkvLugjgwNSQKKIDdXA6eDfuiw2FJ3ZBF1sLBqLP1Lik2nWCKk4sXpnMWzrlcw817brPPlfGgLbz7OSojK1zRbqBESR5Pdk2R9IA3lxxOVzA+Iw1TWLSgWjlFVG9Xmh1+20oPSbrzvDjYtVPmZ+9/6evcXmhcO1Y58MgLozKnaQIaLfWRHYJbniad6MOTaDR3XV1dTLxUSUZS0ReZYJMPG6nCsxNJlhI2UyeJA6QroZFMelR7tnTNS/pLMWceus0e757/UMPmrThfasmhDJrMFcBfoSrAAv3LCf1Y7/fHL3PTSf9vid/u2VLX4h1nBtx8EF07eCMhWVv+2qjbPV7ZhXk3reaWRFEeso3s/Kc9n/UXtUfNU1sHiCdbrCW5yYsuSM9SPGDZsl7FhTAKw7qIu38vFZiq+DRc8Vbf7jOiN9xPe0lOdZHUhGHZ82rL5jTCsILwcRVCndrarbwmu7G154MpYiKmTXZkqV7Alo4QZzicdyMbWvwvmR2/m//YVTM8qeZWgDSHjDmtehgLWM45zARbPujeqU0T92Gmgs89l2htrSKIVfEFzbtyzdes2f7rMR3DsT9s7hrTTo9fvI0eb7EXkrl28iVHWejeTfeu67KQzKLYpdImdyxYIjA1uSy2hfTFv/d3cnXH4nh+maaicAPllDg7JjsxZAfQoVAycJHizlQ5d34k8SzMID0x3kxnXwHfxXvz6DS3RnKydYTBUIWPYKJAEFefnSer1pU55Mw3PEJuMbPGO6Per4Y9UBohIIx5FdrGRChHnhPuJeIKACPXiWuli9ItRLEkdb1mLxNHAk3uJy88YX/Rf/sKUjR12zxRTDxxJNDJS+Dlsbqu3n4I65ujli/3rQ8Zk1MjmTOsz9+kTqOM4upsnQ6IWq/zeZTItMCgHpQhuhr4ip73honuzoJgge1cqWBFYvpabAPTOERTOP1kmx5SXPARX5uxyJzAiNILBC8zh7fGfNXOWV37O9gPNcivn6S9fB2Uhzqxb280Sz1OqOlLYK4Zd6grclXRmzd7jwWSX9V/ksh8wlbKD1hqmFU2Ekb/vTs/YZwJiVxHg==; BDUSS=dsTS12TWlHYmZ4RXJOd2xJZ2lLc1hyejhpODR1anNsVEEzbWVTb1Q3Vkgyd1ZvSVFBQUFBJCQAAAAAAQAAAAEAAAAVucsnQW1kb27YvEN5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEdO3mdHTt5nME; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a04926347288A0yZGLhtgWP3F0%2BVJrwssokCsvoIef5R9SB2%2FZMAX2XZ8yO3QqjryiU%2BqljIZKahuEpvFZiZOwcgc9v7JIdaziz3vQ%2BGx1a6JmozHEIYv6FDKtOqf6pHE9i4vUDkN5Yc0sNEOqe92F%2Bu4lcabqgHrCLn5YNQBm5sv8rXVH6nloiJ%2FXtr%2FJj9KYysLPV5v%2FRLCjr%2BoEB3Q2qnduSEJtZ26Ml9Bw7Dk2iGnViPkv0VeSiiaErsfLk3HKB%2FJEs6qLqS6A6lWRzh2kRm6ZYmffwqhMbHUPOVk8pRwMlufQdEsKc%3D73380160201651270195479748822458; __cas__rn__=492634728; __cas__st__212=5001b5202c87b03b863cef48f02c4560a4a522239a059a898d1d8c6e01bacfb10dc8d418ca468a9f274e84cb; __cas__id__212=60952149; CPTK_212=438665508; CPID_212=60952149; bdindexid=12bnhfb2bps4r0uhep6e7m0t42; Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc=1742641786; ab_sr=1.0.1_OGQ4NGI2MmY5NTg1MzAxYjNhMjkxNjZjYWU1OTJlZjlhOTQ3MDY3NjFhMTMyNDlkYTUwYmU1YWVjMDIxZTI5MGUzNWI4NGZlYTdlNDkzODRlOTZhYzc5NGNkNzY2ZTJkYTgyMTE2ODJjMGE3YjFiNjkzNjlkYzM1MzQzZmU2OThhYzIxZTE1MGE3NGE5ZjUwNjhmYWRlZTU1MWJjMzhiNQ==; BDUSS_BFESS=dsTS12TWlHYmZ4RXJOd2xJZ2lLc1hyejhpODR1anNsVEEzbWVTb1Q3Vkgyd1ZvSVFBQUFBJCQAAAAAAQAAAAEAAAAVucsnQW1kb27YvEN5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEdO3mdHTt5nME; RT="z=1&dm=baidu.com&si=2f2cd6e0-77ea-43c1-ab3b-30cb0a0c2feb&ss=m8k3uxad&sl=b&tt=h71&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=58tx"',
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
