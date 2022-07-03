#!/usr/bin/env python
# coding: utf-8

"""
Listing页面广告位置分析
date:2022-06-27
"""
# In[5]:


import time
import re
import pandas as pd
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# In[6]:


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


# In[7]:


def driver(asin='B08ZYJ8CRX'):
    options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                      get: () => undefined
                    })
                  """
    })
    #     driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(3)
    wait = WebDriverWait(driver, 3)

    #get target html
    area = '10010'
    tar_url = 'https://www.amazon.com/dp/{}?th=1'.format(asin)
    driver.get(tar_url)
    select_area_code(driver, area)

    #ajax 懒加载
    js = "return action=document.body.scrollHeight"
    height = 0
    new_height = driver.execute_script(js)
    while height < new_height:
        # 将滚动条调整至页面底部
        for i in range(height, new_height, 100):
            driver.execute_script('window.scrollTo(0, {})'.format(i))
            time.sleep(0.1)
        height = new_height
        #         time.sleep(2)
        new_height = driver.execute_script(js)
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div#dp-ads-center-promo_feature_div")))

    #define containers
    sp_label = []
    con_asin = []
    con_title = []
    con_rating = []
    con_review = []
    con_price = []

    #Pyquery analysis
    doc = pq(driver.page_source)
    items = doc('div[id^=sp_detail][data-a-carousel-options]').items()
    elements = driver.find_elements(
        By.CSS_SELECTOR, 'div[id^=sp_detail][data-a-carousel-options]')
    for item, element in zip(items, elements):
        label = item('h2.a-carousel-heading').text()
        label = re.findall(r'(.*)\n.sp', label)
        #         print('label:', label)
        try:
            max_page = int(item('span.a-carousel-page-max').text())
        except:
            break
        for i in range(max_page):
            wait.until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'div[id^=sp_detail][data-a-carousel-options] li div[data-asin]'
                )))
            doc_child = pq(driver.page_source)
            items_child = doc_child(
                'div[id^=sp_detail][data-a-carousel-options]').items()
            for child in items_child:
                #                 print('label1:', child('h2').text())
                #                 return 0
                label_child = child('h2.a-carousel-heading').text()
                label_child = re.findall(r'(.*)\n.sp', label_child)
                if label_child != label:
                    break
                else:
                    items_child = child('li div[data-asin]').items()
                    for li in items_child:
                        asin = li.attr('data-asin')
                        price = li('span.a-size-medium.a-color-price').text()
                        title = li('div.sponsored-products-truncator-truncated'
                                   ).text()
                        rating = li('i.a-icon.a-icon-star').attr(
                            'class')  #[-3:].replace('-', '.')
                        review = li('span.a-color-link').text()
                        #save
                        sp_label.append(label)
                        con_asin.append(asin)
                        con_title.append(title)
                        con_rating.append(rating)
                        con_review.append(review)
                        con_price.append(price)
            element.find_element(
                By.CSS_SELECTOR,
                'div.a-carousel-right span.a-button-inner').click()
            time.sleep(2)
#         break

    res = pd.DataFrame({
        'SP Label': sp_label,
        'Asin': con_asin,
        'Price': con_price,
        'Title': con_title,
        'Rating': con_rating,
        'Review': con_review
    })
    return res


# In[8]:


res = driver('B081MYC174')
res


# In[9]:


#导出自己Listing页面的ASIN
res.to_csv('Listing页面的ASIN.csv')


# In[ ]:




