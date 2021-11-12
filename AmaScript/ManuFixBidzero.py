# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 20:58:04 2020

@author: Administrator
"""

"""
脚本说明：关键词位置的
在关键词，设置好条件：spend>3 order = 0 bid > 0.03;  服务状态：广告超出预算，关键词已启用;去除品牌店铺

"""
import requests
import json
import base64
import urllib
import os,time,datetime
from selenium import webdriver
# 脚本管理器
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains  #鼠标动作
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from PIL import Image
from selenium.webdriver.chrome.options import Options

import muggle_ocr
sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.Captcha)

import warnings
warnings.filterwarnings('ignore')

record_log = pd.read_excel(r"D:\坚果云\我的坚果云\log\关键词位置竞价调整记录-出单0.xlsx")
length = len(record_log)
record_log.loc[length,'调整日期'] = time.strftime("%Y-%m-%d", time.localtime())
record_log.loc[length,'开始时间'] = time.strftime("%H:%M:%S", time.localtime())

#从muggle_ocr识别验证码
def get_code():
    img = brower.find_element_by_xpath('//*[@id="root"]/div/div[3]/form/div[4]/div/div/span/span/img')
    img.screenshot(r'D:\PycharmProjects\vode_pic\pictures.png')  # 验证码文件夹位置

    with open(r'D:\PycharmProjects\vode_pic\pictures.png', "rb") as f:
        b = f.read()
    text = sdk.predict(image_bytes=b)

    return text
'''
def get_code(brower, sdk):
    brower.save_screenshot(r'D:\PycharmProjects\vode_pic\pictures.png')
    page_snap_obj = Image.open(r'D:\PycharmProjects\vode_pic\pictures.png')

    img = brower.find_element_by_xpath('//*[@id="root"]/div/div[3]/form/div[4]/div/div/span/span/img')
    time.sleep(2)
    # location = img.location
    size = img.size
    left = 2090  # 2112  2092 #location['x']  后面的数值2112为显示浏览界面时验证码的定位位置，前面的数值2092为隐藏浏览器界面时验证码的定位位置
    top = 730  # 723  805   #location['y']
    right = left + size['width']
    bottom = top + size['height']
    image_obj = page_snap_obj.crop((left, top, right, bottom))  # 按照验证码的长宽，切割验证码
    # image_obj.show()  # 打开切割后的完整验证码

    image_obj.save(r'D:\PycharmProjects\vode_pic\code.png')

    with open(r'D:\PycharmProjects\vode_pic\code.png', "rb") as f:
        b = f.read()
    text = sdk.predict(image_bytes=b)
    return text
'''

# 判断验证码是否正确，输入验证码后，如果出现错误，网页会提示，提示元素出现，返回1表示验证码输入错误；否则返回0验证码输入正确
def code_judge():
    try:
        brower.find_element_by_xpath('//*[@id="root"]/div/div[3]/form/div[4]/div/div/div')
        return 1
    except:
        print('验证码输入正确')
        return 0
# 从百度API 识别验证码
# def get_code():
#
#     img = brower.find_element_by_xpath('//*[@id="root"]/div/div[3]/form/div[4]/div/div/span/span/img')
#     img.screenshot(r'D:\PycharmProjects\vode_pic\code.png')#验证码文件夹位置
#
#     API_Key = 'ietO2L7PZqQ9GCzRlzCIRwSl'   #你的key
#     Secret_Key = 'pVdoXjjhXjEsQxoG6aVi3YYVS29RQmSF'   #你的秘钥
#     # 获取token
#     res = requests.get('https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + API_Key + '&client_secret=' + Secret_Key)
#     res = json.loads(str(res.text))
#     access_token = res['access_token']
#     #传输百度API
#     #通用文字(高精度)  一天500次免费：https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic
#     #网络图片(复杂背景)一天500次免费：https://aip.baidubce.com/rest/2.0/ocr/v1/webimage
#     temp_url = 'https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic' + '?access_token=' + access_token
#     temp_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
#     temp_file = open(r'D:\01工作资料\000数据脚本\log\vcode_pic\code.png', 'rb')   #验证码文件夹位置
#     temp_image = temp_file.read()
#     temp_file.close()
#     temp_data = {'image': base64.b64encode(temp_image)}
#     temp_data = urllib.parse.urlencode(temp_data)
#     temp_res = requests.post(url=temp_url, data=temp_data, headers=temp_headers)
#
#     res = json.loads(str(temp_res.text))
#
#     try:
#         code = res['words_result'][0]['words'].strip().replace(' ','')
#     except:
#         code = 'retry'
#         print('验证码重试ing')
#     return code


#网站密码输入以及登录
def login_cpc():


    customerID = brower.find_element_by_xpath('//*[@id="CustomerId"]')
    customerName = brower.find_element_by_xpath('//*[@id="UserName"]')
    customerPassword = brower.find_element_by_xpath('//*[@id="PassWord"]')
    verify_code = brower.find_element_by_xpath('//*[@id="ValidateCode"]')
    
    customerID.clear()
    customerName.clear()  #清除用户名的字符
    customerPassword.clear()  #清除密码的字符
    customerID.send_keys('1')
    customerName.send_keys('XXXX')  #写入自己的账号，字符加引号
    customerPassword.send_keys('xxxx')    #写入自己的密码
    
    #验证码登录确认
    time.sleep(1)
    verify_code.clear()
    verify_code.send_keys(get_code())
    time.sleep(2)
    # 此处判断验证码正确否，若不正确，点击验证码图片进行刷新，并进行再次识别，识别后进行while再次判断；
    while code_judge():
        verify_code.clear()
        brower.find_element_by_xpath('//*[@id="root"]/div/div[3]/form/div[4]/div/div/span/span/img').click()
        verify_code.send_keys(get_code())
        time.sleep(2)

    login = brower.find_element_by_xpath('//*[@id="root"]/div/div[3]/form/div[5]/div/div/span/button').submit()  # 此处用click()不行，只能用submit提交
    time.sleep(10)
    print('网站已成功进入。。。')
    # 广告活动页面的进入
    campaign_page = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/header/div/div/div[1]/div[2]/ul/li[6]/a')
    ActionChains(brower).move_to_element(campaign_page).click().perform()
    time.sleep(5)  # 此网站较慢，暂停5s

        # while code_judge(brower):
        #    verify_code.clear()
        #    brower.find_element_by_xpath('//*[@id="root"]/div/div[3]/form/div[4]/div/div/span/span/img').click()
        #    verify_code.send_keys(get_code())
        #    time.sleep(2)
        #
        #
        # login = brower.find_element_by_xpath('//*[@id="root"]/div/div[3]/form/div[5]/div/div/span/button').submit()  #此处用click()不行，只能用submit提交
        # time.sleep(10)
        # print('网站已成功进入。。。')
        # #广告活动页面的进入
        # campaign_page = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/header/div/div/div[1]/div[2]/ul/li[4]/a').click()
        # time.sleep(5)  #此网站较慢，暂停5s

#进入广广告活动页面设置，以及在关键词位置的设置；
def setting_targeting():

    # #去除操作时间
    # time.sleep(1)
    # above = brower.find_element_by_xpath('//*[@id="activity"]/form/div[1]/div[2]/div/div[2]/div/div[2]/div/span/span/span/span/i[2]')
    # ActionChains(brower).move_to_element(above).perform()
    # time.sleep(1)
    # operation_time_x = brower.find_element_by_xpath('//*[@id="activity"]/form/div[1]/div[2]/div/div[2]/div/div[2]/div/span/span/span/span/i[1]').click()
    # time.sleep(1)
    #
    # #选择过去7天
    # date_category =brower.find_element_by_xpath ('//*[@id="activity"]/form/div[1]/div[1]/div/div[2]/div/div[2]/div/span/div/span/div/div/span/i').click()
    # time.sleep(1)
    # #日期下拉框的选择；定位日期中的自定义标签（li[9]）,过去7天li[7]）,过去30天li[8]），可自己修改
    # # date_customize = brower.find_element_by_xpath('//*[@style = "position: absolute; top: 0px; left: 0px; width: 100%;"]/div/div/div/ul/li[7]').click()
    # date_customize = brower.find_element_by_xpath('//li[contains(text(),"过去7天")]').click()
    # time.sleep(1)

    # 进入关键词位置
    targeting = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[1]/div/div/div/div/div/div[5]')
    ActionChains(brower).move_to_element(targeting).click().perform()
    time.sleep(10)

    
    #选择国家
    click_country = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[5]/form[1]/div[1]/div[2]/div/span/span/span').click()
    us_click = brower.find_element_by_xpath('//*[starts-with(@id,"rc-tree-select-list_")]/ul/li[1]/span[2]/span').click()
    ca_click = brower.find_element_by_xpath('//*[starts-with(@id,"rc-tree-select-list_")]/ul/li[2]/span[2]/span').click()
    uk_click = brower.find_element_by_xpath('//*[starts-with(@id,"rc-tree-select-list_")]/ul/li[4]/span[2]/span').click()
    de_click = brower.find_element_by_xpath('//*[starts-with(@id,"rc-tree-select-list_")]/ul/li[5]/span[2]/span').click()
    fr_click = brower.find_element_by_xpath('//*[starts-with(@id,"rc-tree-select-list_")]/ul/li[6]/span[2]/span').click()
    it_click = brower.find_element_by_xpath('//*[starts-with(@id,"rc-tree-select-list_")]/ul/li[7]/span[2]/span').click()
    es_click = brower.find_element_by_xpath('//*[starts-with(@id,"rc-tree-select-list_")]/ul/li[8]/span[2]/span').click()
    time.sleep(1)
    us_unclick = brower.find_element_by_xpath('//*[@class="ant-select-dropdown ant-select-tree-dropdown ant-select-dropdown--multiple ant-select-dropdown-placement-bottomLeft"]/div/ul/li[1]/span[1]').click()
    us_unchoose = brower.find_element_by_xpath('//*[@title="Amazon-Z01231-US"]').click()
    # us_unchoose2 = brower.find_element_by_xpath('//*[@title="Amazon-Z01027-US"]').click()
    # us_unchoose3 = brower.find_element_by_xpath('//*[@title="Amazon-Z01556-US"]').click()


    time.sleep(1)
    uk_unclick = brower.find_element_by_xpath('//*[@class="ant-select-dropdown ant-select-tree-dropdown ant-select-dropdown--multiple ant-select-dropdown-placement-bottomLeft"]/div/ul/li[4]/span[1]').click()
    uk_unchoose = brower.find_element_by_xpath('//*[@title="Amazon-Z01231-UK"]').click()

    time.sleep(1)
    de_unclick = brower.find_element_by_xpath('//*[@class="ant-select-dropdown ant-select-tree-dropdown ant-select-dropdown--multiple ant-select-dropdown-placement-bottomLeft"]/div/ul/li[5]/span[1]').click()
    de_unchoose = brower.find_element_by_xpath('//*[@title="Amazon-Z01231-DE"]').click()
    us_unchoose3 = brower.find_element_by_xpath('//*[@title="Amazon-Z01285-DE"]').click()
   #  DEexclude_click =

#选择销售人员，去除品牌店铺的人群   基础页面的设置  选择Amazon平台运营中心，去除品牌店铺人员的名单
'''
#选择销售人员，去除品牌店铺的人群   基础页面的设置  选择Amazon平台运营中心，去除品牌店铺人员的名单 
    click_sales = brower.find_element_by_xpath('//*[@id="keyword"]/form/div[1]/div[2]/div/div[3]/div/div[2]/div/span/span/span/span').click()
    choose_amazon  = brower.find_element_by_xpath('//*[@class="ant-select-dropdown ant-select-tree-dropdown ant-select-dropdown--multiple ant-select-dropdown-placement-bottomLeft"]/div/ul/li[5]/span[2]').click()
    #去除人员时，需要先点击人员所在的小组，否则会找不到该元素；例如彭璐：需要先点击展开C部，在点击展开C1部，然后才能去除其被勾选的框
    #展开Amazon运营平台
    time.sleep(2)
    #choose_amazon = brower.find_element_by_xpath('//*[@class = "ant-select-dropdown ant-select-tree-dropdown ant-select-dropdown--multiple ant-select-dropdown-placement-bottomLeft"]/div/ul/li[5]/span[1]').click()
    choose_amazon = brower.find_element_by_xpath('//*[@class = "ant-select-dropdown ant-select-tree-dropdown ant-select-dropdown--multiple ant-select-dropdown-placement-bottomLeft"]/div/ul/li[5]/span[1]').click()

    #展开C部
    choose_c_group = brower.find_element_by_xpath('//*[@class = "ant-select-dropdown ant-select-tree-dropdown ant-select-dropdown--multiple ant-select-dropdown-placement-bottomLeft"]/div/ul/li[5]/ul/li[12]/span[1]').click()

    #展开C1小组
    choose_c1 = brower.find_element_by_xpath('//*[@class = "ant-select-dropdown ant-select-tree-dropdown ant-select-dropdown--multiple ant-select-dropdown-placement-bottomLeft"]/div/ul/li[5]/ul/li[12]/ul/li[2]/span[1]').click()
    #去除勾选的销售彭璐
    unchoose_brand_sales = brower.find_element_by_xpath('//span[@title = "彭璐"]').click()
    time.sleep(1)

    #展开C2小组
    choose_c2 = brower.find_element_by_xpath('//*[@class = "ant-select-dropdown ant-select-tree-dropdown ant-select-dropdown--multiple ant-select-dropdown-placement-bottomLeft"]/div/ul/li[5]/ul/li[12]/ul/li[3]/span[1]').click()
    #去除勾选的销售魏青
    unchoose_brand_sales = brower.find_element_by_xpath('//span[@title = "魏青"]').click()
    time.sleep(1)

    #展开C3小组
    choose_c3 = brower.find_element_by_xpath('//*[@class = "ant-select-dropdown ant-select-tree-dropdown ant-select-dropdown--multiple ant-select-dropdown-placement-bottomLeft"]/div/ul/li[5]/ul/li[12]/ul/li[4]/span[1]').click()
    #去除勾选的销售霍倩倩
    unchoose_brand_sales = brower.find_element_by_xpath('//span[@title = "霍倩倩"]').click()
    time.sleep(1)

    #展开G部，以及G1组，去除勾选丁文艳
    choose_g_group = brower.find_element_by_xpath('//*[@class = "ant-select-dropdown ant-select-tree-dropdown ant-select-dropdown--multiple ant-select-dropdown-placement-bottomLeft"]/div/ul/li[5]/ul/li[13]/span[1]').click()
    choose_g1 = brower.find_element_by_xpath('//*[@class = "ant-select-dropdown ant-select-tree-dropdown ant-select-dropdown--multiple ant-select-dropdown-placement-bottomLeft"]/div/ul/li[5]/ul/li[13]/ul/li[2]/span[1]').click()
    unchoose_brand_sales = brower.find_element_by_xpath('//span[@title = "丁文艳"]').click()
    time.sleep(1)
    #选择关键词位置的服务状态：这里只选择“广告超出预算”和“关键词已启用”  --测试通过
    service_status = brower.find_element_by_xpath('//*[@id="keyword"]/form/div[1]/div[2]/div/div[1]/div/div[2]/div/span/div/div/div/div').click()
    campagin_out_budget = brower.find_element_by_xpath('//*[@class="ant-select-dropdown ant-select-dropdown--multiple ant-select-dropdown-placement-bottomLeft"]/div/ul/li[5]').click() #广告超出预算
    time.sleep(1)
    campagin_out_budget = brower.find_element_by_xpath('//*[@class="ant-select-dropdown ant-select-dropdown--multiple ant-select-dropdown-placement-bottomLeft"]/div/ul/li[14]').click() #关键词已启用
    time.sleep(1)
    WebDriverWait(brower, 60).until(ec.invisibility_of_element_located((By.XPATH,'//*[@id="keyword"]/div/div[1]/div/div/div[2]/div/div/div/div/div/table/thead/tr[1]/th[1]/span/div/span[1]/div/label/span/input')))

'''


    

#进行高级设置
def setting_advance_search():
    # 进入高级搜索
    element = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[5]/form[1]/div[13]/div/div/span/button[3]/span')
    ActionChains(brower).move_to_element(element).click().perform()
    time.sleep(1)

    changebidrule_click = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[5]/form[2]/div[2]/div[2]/div/span/div/div/span').click()
    time.sleep(2)
    unsetrule_click = brower.find_element_by_xpath('//ul/li[contains(text(),"未设置")]').click()

    targeting_type = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[5]/form[1]/div[12]/div[2]/div/span/div/div/span').click()
    choose_manual = brower.find_element_by_xpath('//ul/li[contains(text(),"手动")]').click()
    time.sleep(1.5)
    
    #花费大于3，出单数为0的广告活动
    spend_min = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[5]/form[2]/div[11]/div[2]/div/span/span/div/div[1]/div/div[2]/input').send_keys(str(2.5))
    order_max = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[5]/form[2]/div[10]/div[2]/div/span/span/div/div[3]/div/div[2]/input').send_keys(0)
    # click_min = brower.find_element_by_xpath('//*[@id="keyword"]/form/div[1]/div[3]/div[2]/div/div[1]/div/div[2]/div/span/span/div/div[1]/div/div[2]/input').send_keys(12)
    time.sleep(8)
    # '//*[@id="keyword"]/form/div[1]/div[3]/div[5]/button[1]'
    #进行高级搜索
    advance_search_click = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[5]/form[1]/div[13]/div/div/span/button[1]')
    ActionChains(brower).move_to_element(advance_search_click).click().perform()
    time.sleep(15)

#进行500条翻页
def turn_500_page():
    #翻页500页，此处莫名其妙的容易出现报错，设置一个try except,当出现报错的时候进行重复最多5次
    time.sleep(5)
    js="var q=document.documentElement.scrollTop=100000"  
    brower.execute_script(js)
    time.sleep(5)
    try:
        turn_page_box = brower.find_element_by_xpath('//*[@class="ant-pagination ant-table-pagination mini"]/li/div/div').click()
        print('已找到元素')
    except:
        print('未找到元素')
    time.sleep(1)  #此处间隔时间越短越好，终于调试出来了
    turn_page_500 = brower.find_element_by_xpath('//*[@class = "ant-select-dropdown ant-select-dropdown--single ant-select-dropdown-placement-topLeft"]/div/ul/li[6]').click()

    time.sleep(30)

    #此处是切换到500条后，等待页面加载完成，此处应用presence是不行的，只能用visibility可见来判断
    # WebDriverWait(brower, 60).until(ec.invisibility_of_element_located((By.XPATH,'//*[@id="keyword"]/div/div[1]/div/div/div[2]/div/div/div/div/div/table/thead/tr[1]/th[1]/span/div/span[1]/div/label/span/input')))
    # time.sleep(2)

#进行日期排序        
def sort_desc_date():
    js="var q=document.documentElement.scrollTop=0"  
    brower.execute_script(js)
    #进行两次排序，对操作时间先降序，再升序,
    #重大疑问：为什么是ec.invisibility  等待元素不可见才能测试成功，排序成功后还需要再等待几秒，再能进行再次排序
    time.sleep(20)
    sort_1 = brower.find_element_by_xpath('//*[@class="ant-table-thead"]/tr/th[21]/span/div/span[2]/div/i').click()

    WebDriverWait(brower, 45).until(ec.invisibility_of_element_located((By.XPATH, '//*[@class = "ant-table-tbody"]/tr[1]/td[10]/div/span/span/input')))
    time.sleep(10)  # 这里的排序莫名其妙的出错，所以设置较长的等待时间，等待时间较短的话，会找到sort排序元素
    sort_2 = brower.find_element_by_xpath('//*[@class="ant-table-thead"]/tr/th[21]/span/div/span[2]/div/i').click()
    WebDriverWait(brower, 45).until(ec.invisibility_of_element_located((By.XPATH, '//*[@class = "ant-table-tbody"]/tr[1]/td[10]/div/span/span/input')))
    time.sleep(10)

#这里最多修改500条，不足500条的时候会进行判断找到最符合的日期值（比当前日期小4天的最大日期值，并获得该定位）
def get_pending_num(page_n):
    if page_n > 500:
        n = 499
    else:
        n = page_n - 1
                
    x = 1
    while x:
        time_xpath = f'//*[@class = "ant-table-tbody"]/tr[{n}]/td[21]/div/div[2]'
        pending_judge_time = brower.find_element_by_xpath(time_xpath).text.split(' ')[0]
        if len(pending_judge_time) == 0:
            x = 0 
        else:
            pending_judge_time = datetime.datetime.strptime(pending_judge_time,'%Y-%m-%d')
            if pending_judge_time + datetime.timedelta(days = 7) > datetime.datetime.today() and n > 1:
                n = n - 1
                x = 1
            else:
                x = 0
    
    return n  #返回的值比实际条数少一条，由于起始值为0开头的


#要进入的网站
# url = "http://94.74.123.132"
def get_in_google():
    global brower
    # 要进入的网站
    url = 'http://888cpc.irobotbox.com/'

    # brower = webdriver.Chrome(ChromeDriverManager().install())

    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox') #解决DevToolsActivePort文件不存在的报错
    chrome_options.add_argument('window-size=2560x1440')  #指定浏览器分辨率
    chrome_options.add_argument('--disable-gpu')  #谷歌文档提到需要加上这个属性来规避bug
    chrome_options.add_argument('--headless')  #浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
    brower=webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
    # brower = webdriver.Chrome(ChromeDriverManager().install())

    brower.get(url)
    print('CPC网页进入成功')
    brower.implicitly_wait(5)
    brower.maximize_window()  # 窗口最大化

print('正在进入网页： ')
get_in_google()

print('正在登陆CPC网站，请稍后：')
login_cpc()

print('正在进行关键词位置的页面设置，请稍后：')
setting_targeting()

print('正在进行高级设置，请稍后：')
setting_advance_search()

print('正在排序中，请稍后：')    
sort_desc_date()


print('正在切换页面到500条，请稍后：')
turn_500_page()


time.sleep(2)
total_page = int(brower.find_element_by_xpath('//*[@class="ant-pagination ant-table-pagination mini"]/li[1]').text.split(' ')[1])
print('正在计算需要调整的条数，请稍后：')
total_change_num = get_pending_num(total_page)
record_log.loc[length,'待修改'] = total_change_num
print('需要修改的竞价位置的条数有：%s条'%total_change_num)
print('正在修改竞价中：请稍后')
actully_changed = 0
if total_change_num > 0:
    for i in range(1,total_change_num):
        #注意此处直接在find_xpath中找不到对应的格式化字符串，只有先将xpath路径格式化后（传入参数i），再送入查询才能找到该值
        get_bid_xpath = f'//*[@class = "ant-table-tbody"]/tr[{i}]/td[10]/div/div'
        get_bid = float(brower.find_element_by_xpath(get_bid_xpath).text.split(' ')[1])
        get_CPC_xpath = f'//*[@class = "ant-table-tbody"]/tr[{i}]/td[16]'
        get_CPC = float(brower.find_element_by_xpath(get_CPC_xpath).text)
        get_spend_xpath = f'//*[@class = "ant-table-tbody"]/tr[{i}]/td[14]/div'
        get_spend = float(brower.find_element_by_xpath(get_spend_xpath).text.split(' ')[1])
        
        
        if round(get_bid,2) == 0.02:
            continue
        
        else:
            if get_bid < get_CPC:
                adjust_bid = get_bid * 0.8
                    
            else:
                if get_spend < 3:
                    adjust_bid = get_CPC * 0.9
                elif get_spend >= 3 and get_spend < 4:
                    adjust_bid = get_CPC * 0.85
                elif get_spend >= 4 and get_spend < 5:
                    adjust_bid = get_CPC * 0.8
                elif get_spend >= 5 and get_spend < 6: 
                    adjust_bid = get_CPC * 0.7
                elif get_spend >= 6 and get_spend < 7:
                    adjust_bid = get_CPC * 0.65
                elif get_spend >= 7 and get_spend < 8:
                    adjust_bid = get_CPC * 0.6
                else:
                    adjust_bid = get_CPC * 0.5
                    
            adjust_bid = round(adjust_bid,2)
            
            if round(adjust_bid,2) == round(get_bid,2):
                adjust_bid = get_bid - 0.01

            if adjust_bid < 0.02:
                adjust_bid = 0.02
            
            #一旦出现错误，重新点击高级搜索，之前排序好继续执行;并重新计算符合要调整的广告的日期所在的位置（total_change_num）
            # 在CPC的关键词位置界面设置竞价，并将修改后的值写入到竞价位置

                
            change_bid_ico_xpath = f'//*[@class = "ant-table-tbody"]/tr[{i}]/td[10]/div/i'    #//*[@class = "ant-table-tbody"]/tr[1]/td[9]/div/i
            change_bid_ico = brower.find_element_by_xpath(change_bid_ico_xpath).click()
            time.sleep(1)
            input_bid_value_xpath = f'//*[@class = "ant-table-tbody"]/tr[{i}]/td[10]/div/span/span/input'  #//*[@class = "ant-table-tbody"]/tr[1]/td[9]/div/span/span/input
            bid_value = brower.find_element_by_xpath(input_bid_value_xpath)
            bid_value.send_keys(Keys.CONTROL, 'a') #此处使用clear()失效，采用键盘功能进行全选后删除
            bid_value.send_keys(Keys.DELETE)
            bid_value.send_keys(str(adjust_bid))
            time.sleep(1)
            #bid_change_verify = brower.find_element_by_xpath('//*[@class = "ant-popover ant-popover-placement-rightBottom"]/div/div[2]/div/div/div[2]/button[2]').click()
            #等待竞价修改成功，竞价旁边出现一个绿色的小对号
            #change_success_ico_xpath = f'//*[@id="targeting"]/div[1]/div/div/div[2]/div/div/div/div/div/table/tbody/tr[{i + 1}]/td[9]/div/div/div/div/div/a[2]/i'
            #WebDriverWait(brower, 60).until(ec.presence_of_element_located((By.XPATH,change_success_ico_xpath)))
            actully_changed = i  #记录当前修改的条数
    
    time.sleep(2)
    batch_change = brower.find_element_by_xpath('//*[@class="ant-table-thead"]/tr/th[10]/span/div/span/button')
    ActionChains(brower).move_to_element(batch_change).click().perform()
    time.sleep(30)    
    print('竞价修改完成，请在Excel中查看')
    brower.quit()
else:
    print('当前无需需要修改的竞价的关键词位置，已直接退出~~')
    brower.quit()        

record_log.loc[length,'已修改'] = actully_changed
record_log.loc[length,'结束时间'] = time.strftime("%H:%M:%S", time.localtime())
record_log.to_excel(r"D:\坚果云\我的坚果云\log\关键词位置竞价调整记录-出单0.xlsx",index = False)














