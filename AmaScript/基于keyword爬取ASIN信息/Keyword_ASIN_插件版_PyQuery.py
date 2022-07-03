# -*- coding: utf-8 -*-
"""

"""


from datetime import date
import time
import requests
import re
from PIL import Image
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
import openpyxl
from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import urllib.parse as urlparse
from texttable import Texttable
import pandas as pd
from pandas.plotting import  table
import matplotlib.pyplot as plt
import xlwt, time, xlrd
import random


#更换地址邮编
def change_address(postal):
    while True:
        try:
            driver.find_element_by_id('glow-ingress-line1').click()
            # driver.find_element_by_id('nav-global-location-slot').click()
            time.sleep(3)
        except Exception as e:
            driver.refresh()
            time.sleep(10)
            continue
        try:
            driver.find_element_by_id("GLUXChangePostalCodeLink").click()
            time.sleep(3)
        except:
            pass
        try:
            driver.find_element_by_id('GLUXZipUpdateInput').send_keys(postal)
            time.sleep(2)
            break
        except Exception as NoSuchElementException:
            try:
                driver.find_element_by_id('GLUXZipUpdateInput_0').send_keys(postal.split('-')[0])
                time.sleep(2)
                driver.find_element_by_id('GLUXZipUpdateInput_1').send_keys(postal.split('-')[1])
                time.sleep(2)
                break
            except Exception as NoSuchElementException:
                driver.refresh()
                time.sleep(10)
                continue
        print("重新选择地址")
    driver.find_element_by_id('GLUXZipUpdate').click()
    time.sleep(6)
    driver.refresh()
    time.sleep(6)


if __name__ == '__main__':    
    # 设置get直接返回，不再等待界面加载完成
    desired_capabilities = DesiredCapabilities.CHROME
    desired_capabilities["pageLoadStrategy"] = "none"
    options = webdriver.ChromeOptions()

    # 附带本地插件
    extension_path = r"D:\PycharmProjects\关键词抓ASIN\SellerSprite3.1.5_0.crx"
    options.add_extension(extension_path)   
    
    # 启用本地带插件的浏览器 chrome://version/  个人资料路径
    # options.add_argument("--user-data-dir="+r"D:/Program Files/GoogleCache/Chrome/UserData/")

    # 无窗口模式
    # options.add_argument('--headless')
    
    # 禁止硬件加速，避免严重占用cpu
    options.add_argument('--disable-gpu')
    # 关闭安全策略
    options.add_argument("disable-web-security")
    # 禁止图片加载
    # options.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2})
    # 隐藏Chrome正在受到自动软件的控制
    options.add_argument('disable-infobars')
    # 设置开发者模式启动，该模式下webdriver属性为正常值
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    #指定浏览器分辨率
    options.add_argument('window-size=1920x1080')
   
    # 模拟移动设备
    # options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"')
    
    #需要指定Google驱动的文件位置,chromedriver_Home     下载地址：http://npm.taobao.org/mirrors/chromedriver/
    # driver = webdriver.Chrome(chrome_options=options,executable_path="D:/Reports/Tools/chromedriver")
    driver = webdriver.Chrome(chrome_options=options)

    # 返回驱动等待的变量
    wait = WebDriverWait(driver, 60)
    # driver.maximize_window()



    SITE = 'https://www.amazon.com'
    
    #设置要查询的关键词
    KEYWORDS = ["magnetic floating light", "magnetic levitating lamp", "Floating suspended light", "Magnetic Levitating"]

    
    #设置US邮编
    postal = "17888"
    
    driver.get(SITE)
    time.sleep(7)
    change_address(postal)
    # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-result-list")))
    
    Now_Time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    record_sheet = pd.DataFrame()
    i = 0
    for keyword in KEYWORDS:
        #就抓每个关键词前1-5页      
        for page in range(1, 2):
            #生成搜素结果页面的url
            data = {
                "k": keyword,
                "page": page,
                "ref": "sr_pg_" + str(page)
            }
            search_page_url = SITE +'/s?' + urlparse.urlencode(data)
            print("当前Url：", search_page_url)
            
            driver.get(search_page_url)
            
            # css选择器，返回结果存在跳出，异常报错
            try:
                time.sleep(5)
                wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "div.s-result-list")))
            except:
                time.sleep(5)
                print("url: " + search_page_url.format(i) + "获取失败,尝试刷新")
                driver.refresh()
                pass

            time.sleep(random.randint(3,6))
            
            #下拉到底部
            js="var q=document.documentElement.scrollTop=5800"  
            driver.execute_script(js)     
            time.sleep(random.randint(3,7))
            js="var q=document.documentElement.scrollTop=15800"  
            driver.execute_script(js)     
            time.sleep(random.randint(3,7))
            js = "var q=document.documentElement.scrollTop=25800"
            driver.execute_script(js)
            time.sleep(random.randint(3, 7))
            
            Try_Count = 1
            while Try_Count <=10:
                time.sleep(1)
                IsSeller = driver.find_elements_by_xpath('//*[@class="s-main-slot s-result-list s-search-results sg-row"]/div//*[@class="quick-view-loading"]')
                if len(IsSeller)<=56:
                    print('加载未完成,仅%s个，等待第%s次'%(len(IsSeller),Try_Count))
                    time.sleep(10)
                    Try_Count += 1
                elif len(IsSeller)>=57 and len(IsSeller)<=60:
                    time.sleep(16)
                    break
                else:
                    break
            
            time.sleep(10)
            #PyQuery
            doc = pq(driver.page_source,parser="html")

            MainList = doc('.s-main-slot.s-result-list.s-search-results.sg-row')
            AsinList = MainList.children().items()
            for child in AsinList:
                ASIN_TEXT = child.attr('data-asin').strip()  
                if ASIN_TEXT == "":
                    continue

                # 排位
                Pagerank =  child.attr('data-index').strip()
   
                # 标题
                title = child('.a-size-base-plus.a-color-base.a-text-normal').text()


                # 首图
                # img = re.findall('src="(.*?)"', str(child))[0]
          
                # 是否为广告
                sponsor = child('.s-label-popover-default .a-size-mini.a-color-secondary').text()  
    
                # 价格，但是会有打折价格，所以多个价格只选第一个
                price_list = child('.a-price .a-offscreen').text().split(" ")
                price = price_list[0]
           
                # 评论数
                review_num = child('.a-section.a-spacing-none.a-spacing-top-micro .a-row.a-size-small .a-size-base').text()
     
                # 评分
                Rating = child('.a-icon-alt').text().replace('out of 5 stars','').split(" ")[0]


                # 配送地址
                # adds = child('.a-row.a-size-base.a-color-secondary.s-align-children-center .a-size-small.a-color-secondary').text()
                

                # 卖家精灵插件提数
                SellerSpriteList = child('.quick-view-loading').children().items()                   
                # 卖家精灵 常规 存储列表
                Items_List = []
                # 卖家精灵 卖家 存储列表
                Seller_List = []
                # 卖家精灵 详细 存储列表
                Plus_Items_List = []
                ListCount = 1
                #获取常规信息(卖家精灵这段页面是有默认顺序的1-7为常规,8为详细，需要区分列表方便取数)
                for SpriteChild in SellerSpriteList:    
                    #第2个是存储卖家相关信息,单独列表方便提取
                    if ListCount ==2: 
                        ListCount += 1
                        try:
                            Seller_List.append(SpriteChild('span a').text())
                            Seller_List.append(SpriteChild('span span').text().split(' ')[0])
                            Seller_List.append(SpriteChild('span span').text().split(' ')[2])
                        except:
                            pass
                    
                    #常规
                    elif ListCount <=7:
                        ListCount += 1
                        Items_List.append(SpriteChild.text())
                        
                    #详细
                    else:
                        PlusList = SpriteChild.children().items()
                        for PlusListChild in PlusList:  
                            Plus_Items_List.append(PlusListChild.text())    
                            

                # 页面官方数据
                record_sheet.loc[i,'current_url'] = search_page_url
                record_sheet.loc[i,'ASIN'] = ASIN_TEXT
                record_sheet.loc[i,'keywords'] = keyword
                record_sheet.loc[i,'page'] = str(page)
                
                # TotalItemSource = doc('span[dir="auto"]')[0].text
                # TotalItem = re.findall('of(.*?)for', TotalItemSource)[0].strip()
                
                # record_sheet.loc[i,'Total_Item'] = TotalItem
                record_sheet.loc[i,'Now_Time'] = Now_Time
                
                record_sheet.loc[i,'Pagerank'] = Pagerank
                record_sheet.loc[i,'title'] = title
                record_sheet.loc[i,'sponsor'] = sponsor
                record_sheet.loc[i,'price'] = price
                record_sheet.loc[i,'review_num'] = review_num
                record_sheet.loc[i,'Rating'] = Rating
                # record_sheet.loc[i,'img'] = img
                # record_sheet.loc[i,'adds'] = adds
                
                # 页面卖家精灵数据      
                try:
                    record_sheet.loc[i,'卖家'] = Seller_List[0]
                    record_sheet.loc[i,'发货'] = Seller_List[1]
                    record_sheet.loc[i,'卖家数'] = Seller_List[2]
                    
                    record_sheet.loc[i,'属性(1)']= Items_List[2]
                    
                    record_sheet.loc[i,'卖点']= Plus_Items_List[0]
                    # 概要数据一般都是重复的,可要可不要
                    # record_sheet.loc[i,'概要']= Plus_Items_List[1]   
                except:
                    pass
                
                try:
                    record_sheet.loc[i,'类目排名①'] = Items_List[1].split('\n')[0]
                    record_sheet.loc[i,'类目排名②'] = Items_List[1].split('\n')[1]
                    record_sheet.loc[i,'类目排名③'] = Items_List[1].split('\n')[2]
                except:
                    pass
                
                try:
                    record_sheet.loc[i,'品牌'] = Items_List[0].replace(': ',':').split(':')[1]
                except:
                    pass
                try:
                    record_sheet.loc[i,'重量']= Items_List[3].replace(': ',':').split(':')[1]
                except:
                    pass
                try:
                    record_sheet.loc[i,'尺寸']= Items_List[4].replace(': ',':').split(':')[1]
                except:
                    pass
                try:                    
                    record_sheet.loc[i,'上架时间']= Items_List[5].replace(': ',':').split(':')[1]
                except:
                    pass

                i += 1
    
    driver.quit()  
# 删除了total-item
Things=pd.DataFrame(record_sheet,columns=['keywords','page','Pagerank','sponsor','ASIN','title','price','review_num','Rating','品牌','卖家','发货','卖家数','类目排名①','类目排名②','类目排名③','属性(1)','重量','尺寸','上架时间','卖点','Now_Time'])

# print(Things)


# DataFrame表格转存Excel
Time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
To_path = r"D:\PycharmProjects\关键词抓ASIN\Competitor_{0}.xlsx".format(Time)

Things.to_excel(excel_writer = To_path, index = None)
print('抓取完成') 

# DataFrame表格转图片
# plt.rcParams['font.sans-serif'] = ['SimHei']#显示中文字体
# fig = plt.figure(figsize=(2, 3), dpi=1400)#dpi表示清晰度
# ax = fig.add_subplot(111, frame_on=False)
# ax.xaxis.set_visible(False)  # hide the x axis
# ax.yaxis.set_visible(False)  # hide the y axis
# table(ax, Things, loc='center')  # 将df换成需要保存的dataframe即可
# plt.savefig('C:/Users/l1569/Desktop/Things_'+ Now_Time +'.png')


## DataFrame表格加线框
# tb=Texttable() # 初始化Texttable
# tb.set_cols_align(['c','c','l','l','c','c','c']) # 设置对齐方式
# tb.set_cols_dtype(['t','t','t','t','t','t','t']) # 设置每列的数据类型为text
# tb.set_cols_width([12,25,8,20,8,10]) # 设置列宽
# tb.header(Things.columns) # 设置表头
# tb.add_rows(Things.values,header=False) # 为表格添加数据
#print(tb.draw())


## 发送到钉钉群
# json_data = {
#           "msgtype": "text",
#           "text": {
#               "content": "AMZ：" + tb.draw(),  # 发送内容
#           },
#           "at": {
#               "atMobiles": [
#               ],
#               "isAtAll": False  # 是否要@某位用户
#           }
#       }

# ding_url = 'https://oapi.dingtalk.com/robot/send?access_token=' \
#                     '4d7674403085618ece3003a8166f5f7bce07f160851e496f78e2abc4c5026e4a'
#                     # 公司钉钉群 '314ba5ccba18c377ec9d688543a6b5afcb2baf6319023e29878278453f3ab96c'
#                     # GOGO哒     '4d7674403085618ece3003a8166f5f7bce07f160851e496f78e2abc4c5026e4a'
                  
# requests.post(url=ding_url, json=json_data)
# print('信息发送成功。')  
