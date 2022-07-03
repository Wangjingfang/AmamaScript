#!/usr/bin/env python
# coding: utf-8

"""
关键词深度分析器
date：2022-06-27
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


def driver(kw, page):
    # driver setting
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
    flag = 0
    search_page_url = 'https://www.amazon.com/s?k={}&page={}'
    urls = [search_page_url.format(kw, i) for i in range(1, page + 1)]
    # define containers
    con_asin = []
    con_title = []
    con_sp = []
    con_rating = []
    con_review = []
    con_price = []
    con_bullet = []
    con_location = []
    con_first_rank = []
    con_second_rank = []
    con_page = []
    for page, url in enumerate(urls):
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
        html = pq(driver.page_source)

        #analysis html
        items = html('div[data-asin^=B0][data-index]').items()
        for i, item in enumerate(items):
            sp = item(".s-label-popover-default span.a-color-secondary").text()
            asin = item.attr("data-asin")
            rating = item('span.a-icon-alt').text()
            review = item('span.a-size-base.s-underline-text').text()
            rank = i + 1
            #             rank = item.attr('data-index')
            link = 'https://www.amazon.com' + item(
                'h2.a-size-mini a.a-link-normal').attr('href')
            driver.get(link)
            #             driver.refresh()
            #analysis html-child get bullet and category rank
            html_resource = driver.page_source
            html_child = pq(html_resource)
            #price
            price = html_child(
                'div#apex_desktop_newAccordionRow div.a-section.a-spacing-none.aok-align-center span.a-offscreen'
            ).text()
            if len(price) == 0:
                try:
                    price = html_child(
                        'div.a-box-inner .a-section.a-spacing-micro span.a-offscreen'
                    ).text()
                    price = re.search('(\S*)', price).group()
                except:
                    price = ''
            title = html_child("span#productTitle").text()
            bullets = html_child(
                'ul.a-unordered-list.a-vertical.a-spacing-mini li:not([id]) span.a-list-item'
            ).text()

            try:
                first_category_rank = re.findall('#(\S*) in', html_resource)[0]
                second_category_rank = re.findall('#(\S*) in',
                                                  html_resource)[1]
            except:
                first_category_rank = ""
                second_category_rank = ""

            #Save data
            con_asin.append(asin)
            con_title.append(title)
            con_page.append(page + 1)
            con_sp.append(sp)
            con_bullet.append(bullets)
            con_location.append(rank)
            con_rating.append(rating)
            con_price.append(price)
            con_review.append(review)
            con_first_rank.append(first_category_rank)
            con_second_rank.append(second_category_rank)


#     driver.quit()
    crawl_result = pd.DataFrame({
        'Asin': con_asin,
        'Title': con_title,
        'Price': con_price,
        'Rating': con_rating,
        'Reviews': con_review,
        'Location': con_location,
        'Bullets': con_bullet,
        'Large Rank': con_first_rank,
        'Small Rank': con_second_rank,
        'SP': con_sp,
        'Page': con_page
    })
    crawl_result['Price'] = crawl_result['Price'].str.replace('[$,]',
                                                              '',
                                                              regex=True)
    crawl_result['Rating'] = crawl_result['Rating'].str.replace(
        ' out of 5 stars', '', regex=True)
    crawl_result['Reviews'] = crawl_result['Reviews'].str.replace(',',
                                                                  '',
                                                                  regex=True)
    crawl_result['Large Rank'] = crawl_result['Large Rank'].str.replace(
        ',', '', regex=True)
    crawl_result['Small Rank'] = crawl_result['Small Rank'].str.replace(
        ',', '', regex=True)
    return crawl_result


# In[8]:


res = driver('ice maker', 1)
res


# In[ ]:


#导出原数据表格
res.to_csv('关键词深度数据分析.csv')


# In[44]:


res_copy = res.copy()

res_copy['Rating'] = pd.to_numeric(res_copy['Rating'], errors='ignore').astype('float')
res_copy['Price'] = pd.to_numeric(res_copy['Price'], errors='ignore').astype('float')
res_copy['Reviews'] = pd.to_numeric(res_copy['Reviews'], errors='ignore').astype('float')


# In[52]:


#关键词产品统计
print('平均评分: ', res_copy['Rating'].mean())
print('平均价格: ', res_copy['Price'].mean())
print('平均评论数量: ', res_copy['Reviews'].mean())


# In[75]:


import matplotlib.pyplot as plt
#评分分布统计
res_copy['Rating'].hist(bins=10)
plt.title('Rating Distribution')
plt.xlabel('Rating')
plt.ylabel("Number of ASINs")

plt.show()


# In[77]:


#评论数量分布统计
res_copy['Reviews'].hist(bins=5)
plt.title('Reviews Distribution')
plt.xlabel('Reviews')
plt.ylabel("Number of ASINs")

plt.show()


# In[78]:


#价格分布统计
res_copy['Price'].hist(bins=5)
plt.title('Price Distribution')
plt.xlabel('Price')
plt.ylabel("Number of ASINs")

plt.show()

