#!/usr/bin/env python
# coding: utf-8

# In[12]:
"""
Amazon Spider Listing 词频率分析
date: 2022-06-27
"""

import time
import re
import pandas as pd
from pyquery import PyQuery as pq
import string
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# In[13]:


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


# In[14]:


def driver(asin_list):
    # driver setting
    options = webdriver.ChromeOptions()
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        #         'profile.default_content_setting_values.javascript': 2
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--disable-blink-features=AutomationControlled")
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

    # define containers
    con_title = []
    con_bullet = []
    con_dsp = []

    #get target html
    area = '10010'
    flag = 0
    search_page_url = 'https://www.amazon.com/dp/{}'
    for asin in (asin_list):
        url = search_page_url.format(asin)
        driver.get(url)
        if flag == 0:
            select_area_code(driver, area)
            flag = 1
        html_resource = driver.page_source
        doc = pq(html_resource)
        title = doc("span#productTitle").text()
        bullets = doc(
            'ul.a-unordered-list.a-vertical.a-spacing-mini li:not([id]) span.a-list-item'
        ).text()
        product_description = doc('div#productDescription span').text()

        #start save
        con_title.append(title)
        con_bullet.append(bullets)
        con_dsp.append(product_description)
    res = pd.DataFrame({
        'Asin': asin_list,
        'Title': con_title,
        'Bullets': con_bullet,
        #'Description': con_dsp
    })
    return res


# In[16]:


#输入卖得好的或者是Top sellers的ASINs， 建议8-10个同赛道产品
res = driver(['B09QCTFPKF', 'B07NVDFKH8', 'B07CJ2V1LR', 'B07VCR8Y42'])
res 


# In[57]:


#总Title


# In[108]:


#总Bullets


# In[109]:


def words_count(df, root_cnt=1):
    Bullets = ' '.join(df['Bullets'])
    with open('Bullets_Save.txt', 'w') as f:
        f.write(Bullets)
    Title = ' '.join(df['Title'])
    with open('Title_Save.txt', 'w') as f:
        f.write(Title)
    
    dic_title = {}
    dic_bullet = {}
    lst_title = ' '.join(df['Title'].str.lower()).split(' ')
    lst_bullet = ' '.join(df['Bullets'].str.lower()).split(' ')
    lst_title = [i.translate(str.maketrans('', '', string.punctuation)) for i in lst_title]
    lst_bullet = [i.translate(str.maketrans('', '', string.punctuation)) for i in lst_bullet]
    #print(lst_title)
    #print(lst_bullet)
    if root_cnt == 1:
        d = 0
    else:
        d =1
    title_change_lst = [' '.join(lst_title[i:i + root_cnt]) for i in range(len(lst_title) - d)]
    bullet_change_lst = [' '.join(lst_bullet[i:i + root_cnt]) for i in range(len(lst_bullet) - d)]
    for word in title_change_lst:
        if word in dic_title:
            dic_title[word] += 1
        else:
            dic_title[word] = 1
            
    for word in bullet_change_lst:
        if word in dic_bullet:
            dic_bullet[word] += 1
        else:
            dic_bullet[word] = 1


    df_title = pd.DataFrame({'词根': dic_title.keys(), '频数': dic_title.values()}) 
    df_bullet = pd.DataFrame({'词根': dic_bullet.keys(), '频数': dic_bullet.values()})
    df_title_sum = df_title['频数'].sum()
    df_bullet_sum = df_bullet['频数'].sum()
    
    df_title['词频'] = df_title['频数']/df_title_sum
    df_bullet['词频'] = df_bullet['频数']/df_title_sum

    return df_title, df_bullet


# In[115]:


#输入词根的长度
term_um = 2

df_title, df_bullet = words_count(res, root_cnt=term_um)


# In[106]:


#打印Title的统计
df_title


# In[107]:


#打印五点的统计
df_bullet


# In[116]:


#输入自己的ASIN
my_asin = driver(['B09QCTFPKF'])


# In[119]:


my_title, my_bullet =  words_count(my_asin, root_cnt=term_um)


# In[127]:


my_title_list = list(my_title['词根'])
my_bullet_list = list(my_bullet['词根'])


# In[123]:


def in_title(x):
    if x in my_title_list:
        return '已覆盖'
    else:
        return '未覆盖'
    
def in_bullet(x):
    if x in my_bullet_list:
        return '已覆盖'
    else:
        return '未覆盖'    


# In[125]:


#检查自己的标题是否已经埋好
df_title['是否覆盖'] = df_title['词根'].apply(in_title)
df_title


# In[128]:


#检查自己的五点是否已经埋好
df_bullet['是否覆盖'] = df_bullet['词根'].apply(in_bullet)
df_bullet


# In[129]:


#保存标题和五点的词频统计文件
df_title.to_csv('标题词根分析.csv')
df_bullet.to_csv('五点词根分析.csv')

