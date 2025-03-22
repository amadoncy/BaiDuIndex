import pandas as pd
import requests
from urllib.parse import quote
import time,datetime

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Cookie': 'BAIDUID=16E5CCC1192556FEE10159406A018509:FG=1; BIDUPSID=16E5CCC1192556FEE10159406A018509; PSTM=1739958453; H_WISE_SIDS_BFESS=62035_62112_62184_62186_62181_62196_62283_62326; MAWEBCUID=web_KXhXVnlpLhbQQSRCKRRisqqVaKJnMgKZIetEZOUCvCGytOiTJG; H_WISE_SIDS=61027_61674_62342_62345_62426_62473_62500_62457_62455_62452_62451_62327_62644_62673; H_PS_PSSID=61027_61674_62342_62345_62426_62473_62500_62457_62455_62452_62451_62327_62644_62646_62673; Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc=1742539344,1742560102,1742570202,1742619258; HMACCOUNT=2B879FD6031C4D2D; delPer=0; PSINO=1; BAIDUID_BFESS=16E5CCC1192556FEE10159406A018509:FG=1; BA_HECTOR=a48484al048424ag85208k8h0fbc891jtsh2o22; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; ZFY=j3Dsz2JVStj8D7DQauQBTBbdC:BZ4rAe8jEh1w:BLfZCo:C; ppfuid=FOCoIC3q5fKa8fgJnwzbE67EJ49BGJeplOzf+4l4EOvDuu2RXBRv6R3A1AZMa49I27C0gDDLrJyxcIIeAeEhD8JYsoLTpBiaCXhLqvzbzmvy3SeAW17tKgNq/Xx+RgOdb8TWCFe62MVrDTY6lMf2GrfqL8c87KLF2qFER3obJGkjS1Q+e/k7Rs6uiFpI37bSGEimjy3MrXEpSuItnI4KDzKu30suSE3sF8hPJkvLugjgwNSQKKIDdXA6eDfuiw2FJ3ZBF1sLBqLP1Lik2nWCKk4sXpnMWzrlcw817brPPlfGgLbz7OSojK1zRbqBESR5Pdk2R9IA3lxxOVzA+Iw1TWLSgWjlFVG9Xmh1+20oPSbrzvDjYtVPmZ+9/6evcXmhcO1Y58MgLozKnaQIaLfWRHYJbniad6MOTaDR3XV1dTLxUSUZS0ReZYJMPG6nCsxNJlhI2UyeJA6QroZFMelR7tnTNS/pLMWceus0e757/UMPmrThfasmhDJrMFcBfoSrAAv3LCf1Y7/fHL3PTSf9vid/u2VLX4h1nBtx8EF07eCMhWVv+2qjbPV7ZhXk3reaWRFEeso3s/Kc9n/UXtUfNU1sHiCdbrCW5yYsuSM9SPGDZsl7FhTAKw7qIu38vFZiq+DRc8Vbf7jOiN9xPe0lOdZHUhGHZ82rL5jTCsILwcRVCndrarbwmu7G154MpYiKmTXZkqV7Alo4QZzicdyMbWvwvmR2/m//YVTM8qeZWgDSHjDmtehgLWM45zARbPujeqU0T92Gmgs89l2htrSKIVfEFzbtyzdes2f7rMR3DsT9s7hrTTo9fvI0eb7EXkrl28iVHWejeTfeu67KQzKLYpdImdyxYIjA1uSy2hfTFv/d3cnXH4nh+maaicAPllDg7JjsxZAfQoVAycJHizlQ5d34k8SzMID0x3kxnXwHfxXvz6DS3RnKydYTBUIWPYKJAEFefnSer1pU55Mw3PEJuMbPGO6Per4Y9UBohIIx5FdrGRChHnhPuJeIKACPXiVuli9ItRLEkdb1mLxNHAk3uJy88YX/Rf/sKUjR12zxRTDxxJNDJS+Dlsbqu3n4I65ujli/3rQ8Zk1MjmTOsz9+kTqOM4upsnQ6IWq/zeZTItMCgHpQhuhr4ip73honuzoJgge1cqWBFYvpabAPTOERTOP1kmx5SXPARX5uxyJzAiNILBC8zh7fGfNXOWV37O9gPNcivn6S9fB2Uhzqxb280Sz1OqOlLYK4Zd6grclXRmzd7jwWSX9V/ksh8wlbKD1hqmFU2Ekb/vTs/YZwJiVxHg==; BDUSS=dsTS12TWlHYmZ4RXJOd2xJZ2lLc1hyejhpODR1anNsVEEzbWVTb1Q3Vkgyd1ZvSVFBQUFBJCQAAAAAAQAAAAEAAAAVucsnQW1kb27YvEN5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEdO3mdHTt5nME; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a04926347288A0yZGLhtgWP3F0%2BVJrwssokCsvoIef5R9SB2%2FZMAX2XZ8yO3QqjryiU%2BqljIZKahuEpvFZiZOwcgc9v7JIdaziz3vQ%2BGx1a6JmozHEIYv6FDKtOqf6pHE9i4vUDkN5Yc0sNEOqe92F%2Bu4lcabqgHrCLn5YNQBm5sv8rXVH6nloiJ%2FXtr%2FJj9KYysLPV5v%2FRLCjr%2BoEB3Q2qnduSEJtZ26Ml9Bw7Dk2iGnViPkv0VeSiiaErsfLk3HKB%2FJEs6qLqS6A6lWRzh2kRm6ZYmffwqhMbHUPOVk8pRwMlufQdEsKc%3D73380160201651270195479748822458; __cas__rn__=492634728; __cas__st__212=5001b5202c87b03b863cef48f02c4560a4a522239a059a898d1d8c6e01bacfb10dc8d418ca468a9f274e84cb; __cas__id__212=60952149; CPTK_212=438665508; CPID_212=60952149; bdindexid=12bnhfb2bps4r0uhep6e7m0t42; Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc=1742641786; ab_sr=1.0.1_OGQ4NGI2MmY5NTg1MzAxYjNhMjkxNjZjYWU1OTJlZjlhOTQ3MDY3NjFhMTMyNDlkYTUwYmU1YWVjMDIxZTI5MGUzNWI4NGZlYTdlNDkzODRlOTZhYzc5NGNkNzY2ZTJkYTgyMTE2ODJjMGE3YjFiNjkzNjlkYzM1MzQzZmU2OThhYzIxZTE1MGE3NGE5ZjUwNjhmYWRlZTU1MWJjMzhiNQ==; BDUSS_BFESS=dsTS12TWlHYmZ4RXJOd2xJZ2lLc1hyejhpODR1anNsVEEzbWVTb1Q3Vkgyd1ZvSVFBQUFBJCQAAAAAAQAAAAEAAAAVucsnQW1kb27YvEN5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEdO3mdHTt5nME; RT="z=1&dm=baidu.com&si=2f2cd6e0-77ea-43c1-ab3b-30cb0a0c2feb&ss=m8k3uxad&sl=b&tt=h71&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=58tx"',
    'Host': 'index.baidu.com',
    'Referer': 'https://index.baidu.com/v2/main/index.html',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    'sec-ch-ua-mobile': '?0',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
}

url = 'https://index.baidu.com/api/WordGraph/multi'
search_word_str = '养老'
encode_data = quote(search_word_str)  # encode处理
start_time = datetime.date(2025, 2, 10)  # 设置开始爬取日期
stop_time = datetime.date(2025, 3, 16)  # 设置结束爬取日期
while stop_time >= start_time:
    params = {
        'wordlist[]': str(search_word_str),  # 设置搜索词
        'datelist': str(start_time.strftime('%Y%m%d'))  # 开始日期
    }
    res_index = requests.get(url, params=params, headers=headers)
    
    json_index = res_index.json()
    if json_index['data'] != "":
        list_index = json_index['data']['wordlist'][0]['wordGraph']  # 关联词数据列表
        for line in list_index:  # 写入日期
            line["日期"] = start_time
        data = pd.DataFrame.from_dict(list_index)  # 将字典列表转pandas格式
        filename = "E:\\BaiDuIndex\\data\\requisition\\" + str(search_word_str) + start_time.strftime(
            '%Y%m%d') + ".xlsx"  # 生成文件
        print("| 正在写入文件{}..........             ".format(filename))
        data.to_excel(filename, sheet_name="数量")  # 写入excel文件
        time.sleep(10)
        print("| 成功写入文件{}...........            * ".format(filename))
    else:
        print("|  {}这周数据为空，放弃采集......        ! ".format(start_time))
    start_time = start_time + datetime.timedelta(7)  # +一周
print("****** 已采集数据到{}，结束数据采集                   ******".format(start_time))