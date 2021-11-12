# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 16:07:09 2020

@author: Administrator
"""
'''
# =============================================================================
# 预算自动化调整：针对我当前设置的预算
#超出预算的无法用此方法进行修改，里面涉及非常多的逻辑，暂时只修改固定值的预算
让windows每天自动执行两次：第一次执行8:30；  第二次执行18:30；《任务计划程序库》中定义好执行的时间；在log（E盘的log）中生成对应的记录文件
在224行中已设置根据自己的调价策略设置的规则，保证针对自己账号的权限的可用性
# =============================================================================
'''
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
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


def get_code():
    img = brower.find_element_by_xpath('//*[@id="root"]/div/div[3]/form/div[4]/div/div/span/span/img')
    img.screenshot(r'D:\PycharmProjects\vode_pic\pictures.png')  # 验证码文件夹位置
    time.sleep(2)
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
def code_judge(brower):
    try:
        brower.find_element_by_xpath('//*[@id="root"]/div/div[3]/form/div[4]/div/div/div')
        return 1
    except:
        print('验证码输入正确')
        return 0

def login_cpc():
    customerID = brower.find_element_by_xpath('//*[@id="CustomerId"]')
    customerName = brower.find_element_by_xpath('//*[@id="UserName"]')
    customerPassword = brower.find_element_by_xpath('//*[@id="PassWord"]')
    verify_code = brower.find_element_by_xpath('//*[@id="ValidateCode"]')

    customerID.clear()
    customerName.clear()  # 清除用户名的字符
    customerPassword.clear()  # 清除密码的字符
    customerID.send_keys('1')
    customerName.send_keys('XXXX')  # 写入自己的账号，字符加引号
    customerPassword.send_keys('XXXX')  # 写入自己的密码

    # 验证码登录确认
    time.sleep(1)
    verify_code.clear()
    verify_code.send_keys(get_code())
    time.sleep(2)

    # 此处判断验证码正确否，若不正确，点击验证码图片进行刷新，并进行再次识别，识别后进行while再次判断；
    while code_judge(brower):
        verify_code.clear()
        brower.find_element_by_xpath('//*[@id="root"]/div/div[3]/form/div[4]/div/div/span/span/img').click()
        verify_code.send_keys(get_code())
        time.sleep(2)

    login = brower.find_element_by_xpath('//*[@id="root"]/div/div[3]/form/div[5]/div/div/span/button').submit()  # 此处用click()不行，只能用submit提交
    time.sleep(10)
    print('网站已成功进入。。。')
    # 广告活动页面的进入
    campaign_page = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/header/div/div/div[1]/div[2]/ul/li[6]/a').click()
    time.sleep(5)  # 此网站较慢，暂停5s

# 广告初始的设定，进行活动页面，去除操作时间，修
def cam_page_setting():
    
    WebDriverWait(brower, 30).until(ec.presence_of_element_located((By.XPATH, '//*[@class = "ant-tabs-nav ant-tabs-nav-animated"]/div/div[1]')))
    for i in range(100):
        if brower.find_element_by_xpath('//*[@class = "ant-tabs-nav ant-tabs-nav-animated"]/div/div[1]').get_attribute('aria-disabled') == 'false':
            print(' 广告加载页面成功')
            break
        else:
            time.sleep(2)
            print(' 等待中')
    
    print('广告活动页面加载成功')
    #去除操作时间
    time.sleep(1)
    # above = brower.find_element_by_xpath('//*[@id="activity"]/form/div[1]/div[2]/div/div[2]/div/div[2]/div/span/span/span/span/i[2]')
    # ActionChains(brower).move_to_element(above).perform()
    time.sleep(1)
    # operation_time_x = brower.find_element_by_xpath('//*[@id="activity"]/form/div[1]/div[2]/div/div[2]/div/div[2]/div/span/span/span/span/i[2]/svg').click()
    # operation_time_x = brower.find_element_by_xpath('//*[@id="activity"]/form/div[1]/div[2]/div/div[2]/div/div[2]/div/span/span/span/span/i[1]').click()
    time.sleep(1)
    
    #选择过去7天
    # date_category =brower.find_element_by_xpath ('//*[@id="activity"]/form/div[1]/div[1]/div/div[2]/div/div[2]/div/span/div/span/div/div/span/i').click()
    # time.sleep(1)

    # <li role="option" unselectable="on" class="ant-select-dropdown-menu-item" aria-selected="false" style="user-select: none;">过去7天</li>
    #日期下拉框的选择；定位日期中的自定义标签（li[9]）,过去7天li[7]）,过去30天li[8]），可自己修改
    # date_customize = brower.find_element_by_xpath('//li[contains(text(),"过去7天")]').click()


    # # 选择国家
    # brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[1]/form[1]/div[1]/div[2]/div/span/span/span/span').click()
    # for i in ["美国", "加拿大", "英国", "德国", "法国", "意大利", "西班牙","日本","荷兰","澳大利亚","墨西哥","新加坡","巴西"]:
    #     brower.find_element_by_xpath('//span[@title="{0}"]'.format(i)).click()  # 选择国家
    #     brower.find_element_by_xpath('//span[@title="{0}"]/preceding-sibling::span[2]'.format(i)).click()  # 打开国家列表，为反选来源渠道做准备
    # time.sleep(2)
    #
    # # 反选渠道来源
    # for i in [
    #     'Amazon-Z01231-US',
    #     'Amazon-Z01497-US',
    #     'Amazon-Z01231-UK',
    #     'Amazon-Z01231-DE',
    #     'Amazon-Z01285-DE',
    # ]:
    #     brower.find_element_by_xpath('//*[@title="{0}"]'.format(i)).click()
    # print("已完成国家选择与反选")

    # 选择国家
    # '//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[5]/form[1]/div[1]/div[2]/div/span/span/span'
    click_country = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[1]/form[1]/div[1]/div[2]/div/span/span/span/span').click()
    # click_country = brower.find_element_by_xpath('//*[@id="targeting"]/form/div[1]/div[1]/div[1]/div[1]/div/div[2]/div/span/span/span/span').click()
    # '//*[@id="rc-tree-select-list_4"]/ul/li[2]/ul/li[2]/span[3]'
    us_click = brower.find_element_by_xpath('//*[starts-with(@id,"rc-tree-select-list_")]/ul/li[1]/span[2]/span').click()
    ca_click = brower.find_element_by_xpath('//*[starts-with(@id,"rc-tree-select-list_")]/ul/li[2]/span[2]/span').click()
    jp_click = brower.find_element_by_xpath('//*[starts-with(@id,"rc-tree-select-list_")]/ul/li[3]/span[2]/span').click()
    uk_click = brower.find_element_by_xpath('//*[starts-with(@id,"rc-tree-select-list_")]/ul/li[4]/span[2]/span').click()
    de_click = brower.find_element_by_xpath('//*[starts-with(@id,"rc-tree-select-list_")]/ul/li[5]/span[2]/span').click()
    fr_click = brower.find_element_by_xpath('//*[starts-with(@id,"rc-tree-select-list_")]/ul/li[6]/span[2]/span').click()
    it_click = brower.find_element_by_xpath('//*[starts-with(@id,"rc-tree-select-list_")]/ul/li[7]/span[2]/span').click()
    es_click = brower.find_element_by_xpath('//*[starts-with(@id,"rc-tree-select-list_")]/ul/li[8]/span[2]/span').click()
    au_click = brower.find_element_by_xpath('//*[starts-with(@id,"rc-tree-select-list_")]/ul/li[9]/span[2]/span').click()
    nl_click = brower.find_element_by_xpath('//*[starts-with(@id,"rc-tree-select-list_")]/ul/li[13]/span[2]/span').click()
    sg_click = brower.find_element_by_xpath('//*[starts-with(@id,"rc-tree-select-list_")]/ul/li[15]/span[2]/span').click()
    time.sleep(2)

    us_unclick = brower.find_element_by_xpath('//*[@class="ant-select-dropdown ant-select-tree-dropdown ant-select-dropdown--multiple ant-select-dropdown-placement-bottomLeft"]/div/ul/li[1]/span[1]').click()
    us_unchoose1 = brower.find_element_by_xpath('//*[@title="Amazon-Z01231-US"]').click()
    us_unchoose2 = brower.find_element_by_xpath('//*[@title="Amazon-Z01497-US"]').click()
    # us_unchoose2 = brower.find_element_by_xpath('//*[@title="Amazon-Z01027-US"]').click()
    # us_unchoose3 = brower.find_element_by_xpath('//*[@title="Amazon-Z01556-US"]').click()

    time.sleep(1.5)
    # '//*[@id="rc-tree-select-list_7"]/ul/li[4]/span[3]'
    uk_unclick = brower.find_element_by_xpath('//*[@class="ant-select-dropdown ant-select-tree-dropdown ant-select-dropdown--multiple ant-select-dropdown-placement-bottomLeft"]/div/ul/li[4]/span[1]').click()
    uk_unchoose = brower.find_element_by_xpath('//*[@title="Amazon-Z01231-UK"]').click()

    time.sleep(1)
    de_unclick = brower.find_element_by_xpath('//*[@class="ant-select-dropdown ant-select-tree-dropdown ant-select-dropdown--multiple ant-select-dropdown-placement-bottomLeft"]/div/ul/li[5]/span[1]').click()
    # de_unchoose = brower.find_element_by_xpath('//*[@title="Amazon-Z01231-DE"]').click()
    us_unchoose3 = brower.find_element_by_xpath('//*[@title="Amazon-Z01285-DE"]').click()

    #点击高级搜索的下拉框
    time.sleep(1)

    advance_search_box = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[1]/form[1]/div[12]/div/div/span/button[3]')
    ActionChains(brower).move_to_element(advance_search_box).click().perform()
    time.sleep(2)


#批量竞价的修改
def auto_change_budget(min_budget,max_budget,min_acos,max_acos,min_order,max_order,min_spend,max_spend,min_CR,max_CR,pending_budget):
    #高级搜索设定
    daily_budget_min = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[1]/form[2]/div[6]/div[2]/div/span/span/div/div[1]/div/div[2]/input')
    daily_budget_min.send_keys(Keys.CONTROL, 'a') #此处使用clear()失效，采用键盘功能进行全选后删除
    daily_budget_min.send_keys(Keys.DELETE)
    daily_budget_min.send_keys(str(min_budget))
    daily_budget_max = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[1]/form[2]/div[6]/div[2]/div/span/span/div/div[3]/div/div[2]/input')
    daily_budget_max.send_keys(Keys.CONTROL, 'a') #此处使用clear()失效，采用键盘功能进行全选后删除
    daily_budget_max.send_keys(Keys.DELETE)
    daily_budget_max.send_keys(str(max_budget))
    Acos_min = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[1]/form[2]/div[14]/div[2]/div/span/span/div/div[1]/div/div[2]/input')
    Acos_min.send_keys(Keys.CONTROL, 'a') #此处使用clear()失效，采用键盘功能进行全选后删除
    Acos_min.send_keys(Keys.DELETE)
    Acos_min.send_keys(str(min_acos))
    Acos_max = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[1]/form[2]/div[14]/div[2]/div/span/span/div/div[3]/div/div[2]/input')
    Acos_max.send_keys(Keys.CONTROL, 'a') #此处使用clear()失效，采用键盘功能进行全选后删除
    Acos_max.send_keys(Keys.DELETE)
    Acos_max.send_keys(str(max_acos))
    
    Order_min = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[1]/form[2]/div[12]/div[2]/div/span/span/div/div[1]/div/div[2]/input')
    Order_min.send_keys(Keys.CONTROL, 'a') #此处使用clear()失效，采用键盘功能进行全选后删除
    Order_min.send_keys(Keys.DELETE)
    Order_min.send_keys(str(min_order))
    Order_max = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[1]/form[2]/div[12]/div[2]/div/span/span/div/div[3]/div/div[2]/input')
    Order_max.send_keys(Keys.CONTROL, 'a') #此处使用clear()失效，采用键盘功能进行全选后删除
    Order_max.send_keys(Keys.DELETE)
    Order_max.send_keys(str(max_order))
    Spend_min = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[1]/form[2]/div[13]/div[2]/div/span/span/div/div[1]/div/div[2]/input')
    Spend_min.send_keys(Keys.CONTROL, 'a') #此处使用clear()失效，采用键盘功能进行全选后删除
    Spend_min.send_keys(Keys.DELETE)
    Spend_min.send_keys(str(min_spend))
    Spend_max = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[1]/form[2]/div[13]/div[2]/div/span/span/div/div[3]/div/div[2]/input')
    Spend_max.send_keys(Keys.CONTROL, 'a') #此处使用clear()失效，采用键盘功能进行全选后删除
    Spend_max.send_keys(Keys.DELETE)
    Spend_max.send_keys(str(max_spend))
    # CR_min = brower.find_element_by_xpath('//*[@id="activity"]/form/div[1]/div[3]/div[2]/div/div[5]/div/div[2]/div/span/span/div/div[1]/div/div[2]/input')
    CR_min = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[1]/form[2]/div[10]/div[2]/div/span/span/div/div[1]/div/div[2]/input')
    CR_min.send_keys(Keys.CONTROL, 'a') #此处使用clear()失效，采用键盘功能进行全选后删除
    CR_min.send_keys(Keys.DELETE)
    CR_min.send_keys(str(min_CR))
    # CR_max = brower.find_element_by_xpath('//*[@id="activity"]/form/div[1]/div[3]/div[2]/div/div[5]/div/div[2]/div/span/span/div/div[3]/div/div[2]/input')
    CR_max = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[1]/form[2]/div[10]/div[2]/div/span/span/div/div[3]/div/div[2]/input')
    CR_max.send_keys(Keys.CONTROL, 'a') #此处使用clear()失效，采用键盘功能进行全选后删除
    CR_max.send_keys(Keys.DELETE)
    CR_max.send_keys(str(max_CR))

    time.sleep(5)
    
    advance_search_click = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[1]/form[1]/div[12]/div/div/span/button[1]')
    ActionChains(brower).move_to_element(advance_search_click).click().perform()
    time.sleep(15)  #此处只有20条，10s内加载完成
    
    #此处判断全选按钮是否是可选的 ，如果不可选为display ,返回结果值为false,可以用if  else判断    
    if brower.find_element_by_xpath('//*[@class="ant-table-body"]/table/thead/tr/th/span/div/span/div/label/span/input').is_enabled():
    
    #如果广告活动栏网页加载完成，则该值为false,否则该值为true
    #brower.find_element_by_xpath('//*[@class = "ant-tabs-nav ant-tabs-nav-animated"]/div/div[1]').get_attribute('aria-disabled')

        time.sleep(1)
        #页面500条设置，

        print("跳转500页")
        # 翻页500页，此处莫名其妙的容易出现报错，设置一个try except,当出现报错的时候进行重复最多5次
        js = "var q=document.documentElement.scrollTop=100000"
        brower.execute_script(js)

        time.sleep(2)
        pending_campaign_num = int(brower.find_element_by_xpath('//*[@class="ant-pagination-total-text"]').text.split(' ')[1])
        try:
            turn_page_box = brower.find_element_by_xpath('//*[@class="ant-pagination ant-table-pagination mini"]/li/div/div').click()
            print('已找到元素')
        except:
            print('未找到元素')
        # turn_page_box = brower.find_element_by_xpath('//*[@class = "ant-select-sm ant-pagination-options-size-changer ant-select ant-select-enabled"]/div/span').click()
        # turn_page_box = brower.find_element_by_xpath('//*[@class = "ant-pagination-options-size-changer ant-select ant-select-enabled"]/div/span').click()
        time.sleep(1)  # 此处间隔时间越短越好，终于调试出来了
        turn_page_500 = brower.find_element_by_xpath('//*[@class = "ant-select-dropdown ant-select-dropdown--single ant-select-dropdown-placement-topLeft"]/div/ul/li[6]').click()

        #turn_page_500 = brower.find_element_by_xpath('//*[@style = "min-width: 82px; left: 1781px; top: 2385.8px;"]/div/ul/li[6]').click()
        #WebDriverWait(brower, 300).until(ec.element_to_be_clickable((By.XPATH,'//*[@class = "ant-select-dropdown ant-select-dropdown--single ant-select-dropdown-placement-topLeft"]/div/ul/li[6]')))
        
        time.sleep(6) #此处一定要有等待，待搜索后，全选框才会消失，下面是等待页面加载完成，全选框会出现；
        #此处是切换到500条后，等待页面加载完成，此处应用presence是不行的，只能用visibility可见来判断
        # WebDriverWait(brower, 60).until(ec.presence_of_element_located((By.XPATH,'//*[@id="activity"]/div/div/div/div/div[2]/div/div/div/div/div/table/thead/tr/th[1]/span/div/span[1]/div/label/span')))
        # WebDriverWait(brower, 50).until(ec.visibility_of_element_located((By.XPATH,'//*[@id="activity"]/div/div/div/div/div[2]/div/div/div/div/div/table/thead/tr/th[1]/span/div/span[1]/div/label/span')))

        #将页面返回到顶部位置
        js="var q=document.documentElement.scrollTop=0"  
        brower.execute_script(js)
        #全选页面，进行预算调整
        choose_all_box = brower.find_element_by_xpath('//*[@class="ant-table-body"]/table/thead/tr/th/span/div/span/div/label/span/input')
        ActionChains(brower).move_to_element(choose_all_box).click().perform()
        time.sleep(5)
        bulk_operation_box_above = brower.find_element_by_xpath('//*[@id="root"]/div/section/section/main/div/div[2]/div/div[3]/div[1]/div[4]/button[3]')
        ActionChains(brower).move_to_element(bulk_operation_box_above).perform()
        time.sleep(2)
        print(1234)
        bulk_change_default_bid = brower.find_element_by_xpath('//*[@class = "ant-dropdown ant-dropdown-placement-bottomLeft"]/ul/li[9]').click()
        time.sleep(3)
        budget_change_box = brower.find_element_by_xpath('//*[@class="ant-radio-group ant-radio-group-outline"]/label[2]/span/input').click()
        print('勾选固定值')
        change_bid_value = brower.find_element_by_xpath('//*[@class="ant-radio-group ant-radio-group-outline"]/label[2]/span[2]/span/div/div[2]/input')


        change_bid_value.send_keys(Keys.CONTROL,'a') #此处使用clear()失效，采用键盘功能进行全选后删除
        change_bid_value.send_keys(Keys.DELETE)
        change_bid_value.send_keys(str(pending_budget))
        time.sleep(1)
        change_bid_value_confirm = brower.find_element_by_xpath('//*[@class = "ant-modal-footer"]/div/button[2]').click()
        
        time.sleep(1)
        WebDriverWait(brower, 500).until(ec.presence_of_element_located((By.XPATH, '//*[@class = "ant-modal-confirm-btns"]/button')))
        time.sleep(3)
        change_suceess_verifty = brower.find_element_by_xpath('//*[@class = "ant-modal-confirm-btns"]/button').click()
        print(' 打印屏幕显示内容：修改成功')
        
        #第一次预算修改完成后，等待全选框按钮可见
        # '/html/body/div[5]/div/div[2]/div/div[2]/div[3]/div/button[2]'
        # # 知道了
        # '/html/body/div[7]/div/div[2]/div/div[2]/div/div/div[2]/button'    '//*[@class="ant-modal-content"]/div/div/div[2]/button'
        # # 修改成功个数
        # '/html/body/div[7]/div/div[2]/div/div[2]/div/div/div[1]/div'      '//*[@class="ant-modal-content"]/div/div/div[1]/div'   '//*[@class="ant-modal-confirm-content"]'
        time.sleep(12)
        # WebDriverWait(brower, 30).until(ec.visibility_of_element_located((By.XPATH,'//*[@id="activity"]/div/div/div/div/div[2]/div/div/div/div/div/table/thead/tr/th[1]/span/div/span[1]/div/label/span')))
        # WebDriverWait(brower, 30).until(ec.element_to_be_clickable((By.XPATH,'//*[@id="activity"]/form/div[1]/div[3]/div[4]/button[1]')))
        print(' 等待页面加载完成，待下一次修改中；')
        
    
    else:
        print(' 无需要修改的预算')
        pending_campaign_num = 0
        
    return pending_campaign_num


# budget_sheet = pd.DataFrame({'bugdet_min':[1,1.5,1.5,2,2.5,3,3.5,6.5],
#                               'budget_max':[1.51,2,2,2.5,3,3.5,4,7],
#                               'Acos_min':[0.01,0.01,15,0.01,0.01,0.01,0.01,0.01],
#                               'Acos_max':[20,15,22,30,22,35,22,20],
#                               'final_budget':[6,200,6.87,15,8,15,200,200]})

budget_sheet = pd.read_excel(r"D:\PycharmProjects\预算修改逻辑.xlsx")

# url = "http://94.74.123.132"
url = 'http://888cpc.irobotbox.com/'

# brower.get(url)
chrome_options = Options()
chrome_options.add_argument('--no-sandbox') #解决DevToolsActivePort文件不存在的报错
chrome_options.add_argument('window-size=2560x1440')  #指定浏览器分辨率
chrome_options.add_argument('--disable-gpu')  #谷歌文档提到需要加上这个属性来规避bug
chrome_options.add_argument('--headless')  #浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败

brower = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
# brower=webdriver.Chrome(ChromeDriverManager().install())
brower.get(url)
print('CPC网页进入成功')
brower.implicitly_wait(5)
brower.maximize_window()  #窗口最大化
login_cpc()
cam_page_setting()
 
    
for i in range(len(budget_sheet)):
    print('正在第%d次修改中，请稍后；'%(i+1))
    try:
        change_cam_num = auto_change_budget(budget_sheet.loc[i,'budget_min'],budget_sheet.loc[i,'budget_max'],budget_sheet.loc[i,'Acos_min'],
                                            budget_sheet.loc[i,'Acos_max'],budget_sheet.loc[i,'Order_min'],budget_sheet.loc[i,'Order_max'],
                                            budget_sheet.loc[i,'Spend_min'],budget_sheet.loc[i,'Spend_max'],budget_sheet.loc[i,'CR_min'],
                                            budget_sheet.loc[i,'CR_max'],budget_sheet.loc[i,'final_budget'])
        budget_sheet.loc[i,'修改的广告活动数量'] = change_cam_num
        budget_sheet.loc[i,'批量修改广告预算时间'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
    except:
        print(' 竞价修改失败；')
        brower.refresh()
        time.sleep(5)
        cam_page_setting()
        budget_sheet.loc[i,'修改的广告活动数量'] = '竞价修改失败'
        budget_sheet.loc[i,'批量修改广告预算时间'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

sheet_name = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime()) + '_log.xlsx'
print('日志文件已生成，请在D盘中查看')
budget_sheet.to_excel(r'D:\坚果云\我的坚果云\log\%s'%sheet_name,index = False)

brower.quit()













