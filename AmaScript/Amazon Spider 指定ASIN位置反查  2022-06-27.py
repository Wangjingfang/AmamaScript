#!/usr/bin/env python
# coding: utf-8


"""
Amazon Spider 指定ASIN位置反查
date:2022-06-27
"""
# In[7]:


import time
import re
import pandas as pd
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# In[8]:


def select_area_code(driver, code):
    while True:
        try:
            driver.find_element(By.ID, 'glow-ingress-line1').click()
            time.sleep(2)
        except Exception as e:
            driver.refresh()
            time.sleep(10)
            continue
        try:
            driver.find_element(By.ID, "GLUXChangePostalCodeLink").click()
            time.sleep(1)
        except:
            pass
        try:
            driver.find_element(By.ID, 'GLUXZipUpdateInput').send_keys(code)
            time.sleep(1)
            break
        except Exception as NoSuchElementException:
            try:
                driver.find_element(By.ID, 'GLUXZipUpdateInput_0').send_keys(
                    postal.split('-')[0])
                time.sleep(1)
                driver.find_element(By.ID, 'GLUXZipUpdateInput_1').send_keys(
                    postal.split('-')[1])
                time.sleep(1)
                break
            except Exception as NoSuchElementException:
                driver.refresh()
                time.sleep(5)
                continue
        print("input area code again")
    driver.find_element(By.ID, 'GLUXZipUpdate').click()
    time.sleep(1)
    driver.refresh()
    time.sleep(1)


# In[9]:


def driver(kws, pages):
    options = webdriver.ChromeOptions()
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        #         'profile.default_content_setting_values.javascript': 2
    }
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument", {
            "source":
            """
                    Object.defineProperty(navigator, 'webdriver', {
                      get: () => undefined
                    })
                  """
        })
    driver.implicitly_wait(3)
    wait = WebDriverWait(driver, 3)
    #get target html
    area = '10010'
    search_page_url = 'https://www.amazon.com/s?k={}&page={}'

    con_kw = []
    con_asin = []
    con_rank = []
    con_sp = []
    con_link = []
    con_page = []
    flag = 0
    for kw in kws:
        for page in range(1, pages + 1):
            kw_new = '+'.join(kw.split(' '))
            url = search_page_url.format(kw_new, page)
            driver.get(url)
            if flag == 0:
                select_area_code(driver, area)
                flag = 1
            try:
                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.s-result-list")))
            except:
                driver.refresh()
            doc = pq(driver.page_source)
            items = doc('div[data-asin^=B0][data-index]').items()
            for i, item in enumerate(items):
                sp = item(
                    ".s-label-popover-default span.a-color-secondary").text()
                asin = item.attr("data-asin")
                #                 rank = item.attr('data-index')
                rank = i
                link = 'https://www.amazon.com' + item(
                    'h2.a-size-mini a.a-link-normal').attr('href')
                con_kw.append(kw)
                con_asin.append(asin)
                con_rank.append(rank)
                con_sp.append(sp)
                con_link.append(link)
                con_page.append(page)

    res = pd.DataFrame({
        '关键词': con_kw,
        '排名': con_rank,
        'Asin': con_asin,
        'SP广告位置': con_sp,
        '页数': con_page,
        '链接': con_link
    })
    return res


# In[10]:


#输入你想被分析的关键词，多个关键词可以用逗号隔开，每个关键词必须加单引号
keyword = ['ice maker']


# In[11]:


#输入你想爬取的页数
pages = 5


# In[12]:


#开始爬取加打印结果
res = driver(keyword, pages)
res


# In[28]:


#输入希望反查位置的ASIN
asins = ['B08ZYJ8CRX', 'B0B12TJ3Q7']


# In[29]:


tar_asin = asins
tar_res = res[res['Asin'].isin(tar_asin)]
tar_res


# In[30]:


#导出结果， Sponsored代表广告位置
name = '反查结果'
tar_res.to_csv(name + '.csv')


# In[ ]:




