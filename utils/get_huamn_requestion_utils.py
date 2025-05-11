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
            'Cookie':'BAIDUID=34CB65A4C9458D3BBB52E00A0D69A789:FG=1; BIDUPSID=34CB65A4C9458D3BBB52E00A0D69A789; PSTM=1744952492; BAIDUID_BFESS=34CB65A4C9458D3BBB52E00A0D69A789:FG=1; ZFY=ATeXDuugsZG50THi:B:BkA0Z9mWQgq:Bbx2GM8qlA2im0s:C; newlogin=1; BDUSS=dVZmJtcXZ1NjdNSTdOYk93OVFUbWxVam9rOFppc1RPNkppVWtHMjhWY1AzRGRvSVFBQUFBJCQAAAAAAQAAAAEAAAAVucsnQW1kb27YvEN5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA9PEGgPTxBoRl; H_PS_PSSID=61027_62484_62327_62891_62928_62967_63019_63042_63046_63034_63146_63091; BA_HECTOR=242h2k85200g04a1al840g2k8m98if1k1ivth22; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; PSINO=6; delPer=0; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BCLID=10336332024730948513; BCLID_BFESS=10336332024730948513; BDSFRCVID=q4_OJexroGWgCqbsyqHzT92lNQpWxY5TDYrELPfiaimDVu-VvXWoEG0Pts1-dEu-S2EwogKKXgOTHw0F_2uxOjjg8UtVJeC6EG0Ptf8g0M5; BDSFRCVID_BFESS=q4_OJexroGWgCqbsyqHzT92lNQpWxY5TDYrELPfiaimDVu-VvXWoEG0Pts1-dEu-S2EwogKKXgOTHw0F_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF=tRAOoC8-fIvDqTrP-trf5DCShUFsbt6iB2Q-XPoO3M3JEPjPKnray5t7eH5QWqojQ5bk_xbgy4op8P3y0bb2DUA1y4vp-qvUa2TxoUJ2-KDVeh5Gqq-KQJ-ebPRiXPb9QgbfopQ7tt5W8ncFbT7l5hKpbt-q0x-jLTnhVn0MBCK0hD89Dj-Ke5PthxO-hI6aKC5bL6rJabC3qDb3XU6q2bDeQnJM3boa-55DaPcmfCoS8xjx3n7Zjq0vWq54WpOh2C60WlbCb664fxn5hUonDh83KNLLKUQtHGAHK43O5hvvob3O3M7bDMKmDloOW-TB5bbPLUQF5l8-sq0x0bOte-bQXH_E5bj2qRuDoK8K3f; H_BDCLCKID_SF_BFESS=tRAOoC8-fIvDqTrP-trf5DCShUFsbt6iB2Q-XPoO3M3JEPjPKnray5t7eH5QWqojQ5bk_xbgy4op8P3y0bb2DUA1y4vp-qvUa2TxoUJ2-KDVeh5Gqq-KQJ-ebPRiXPb9QgbfopQ7tt5W8ncFbT7l5hKpbt-q0x-jLTnhVn0MBCK0hD89Dj-Ke5PthxO-hI6aKC5bL6rJabC3qDb3XU6q2bDeQnJM3boa-55DaPcmfCoS8xjx3n7Zjq0vWq54WpOh2C60WlbCb664fxn5hUonDh83KNLLKUQtHGAHK43O5hvvob3O3M7bDMKmDloOW-TB5bbPLUQF5l8-sq0x0bOte-bQXH_E5bj2qRuDoK8K3f; Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc=1745899248,1746501632; HMACCOUNT=7B93E42C07B9C9DD; bdindexid=pgdnfg3640mbfrou4hue1q5eg5; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a049651408668FCr%2Bmjh%2BAk9bI%2Ft6kgzdGY1IOGUFaPKpA%2BYhjGy3yqCK2Z6tdylLhBciOWODCzleUqB2rtRYCXdZ8h1b3vjbioV30JY7eHTM2lDrolosHQGewxb%2BUZFeyTALzi9LY9Uk1oR9GRoxHQwmsGVumRwfCtNTKVcPwGH3USm7T9dlTqvfUvRIPSCZvU2%2FPyabb%2Bvic%2BZMoc9T15HraZCt624nyiKYAE5xoZRvvHlnwW2%2B%2FVHWiYrgJeUjngZCWrWb0r6cS76jubYQlnwU0LZafsYMzvnKudh%2FvXv2S4xzFZkX%2Fg%3D33179532768309692389450509778821; __cas__rn__=496514086; __cas__st__212=bdab102f0e0580291917d7b79726d13836fbf11e124d7913546801e155ae1c33147c8e1f6da59533fd96a932; __cas__id__212=60952149; CPTK_212=2088851321; CPID_212=60952149; RT="z=1&dm=baidu.com&si=db374730-829b-477c-bc2f-a2f0aa2cced9&ss=mabxz79e&sl=h&tt=dne&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf"; Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc=1746502360; BDUSS_BFESS=dVZmJtcXZ1NjdNSTdOYk93OVFUbWxVam9rOFppc1RPNkppVWtHMjhWY1AzRGRvSVFBQUFBJCQAAAAAAQAAAAEAAAAVucsnQW1kb27YvEN5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA9PEGgPTxBoRl; ab_sr=1.0.1_ZGVhOTkxM2VlZTQ5MmUzYTRjYTBiMmRhZmQ2NDA3OWUyMmU1MjFhMzc5OWMzM2YyMzMwNTBkZmRkYjgwZjU4Yzc3ZDhmMDIxM2E1MmJlODBhOTkzNDdiNGYyNjlmMjEzNjk1MTE5YTE5YTJlMDBmNTYzYmVkOTQ1OGVjZThhMDdkMmFmZGFmMmE0M2FjMzQ2MDljY2QyYzFmNzRiM2IzYg==',
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