import xlwt,time,xlrd
import time
import pandas as pd
import os

"""
20230928,Amazon将广告活动等添加了ID 信息，上传必须有原广告活动，广告组等信息的ID，所有增加关键词和ASIN分为两部分
    1.1有原广告活动和广告组，增加关键词和ASIN；
    1.2 有原广告活动，没有广告组,增加关键词和ASIN；
    2.新增广告活动和广告组；
    
    ## 
    将下载的含有ID的数据，合并整理成一个文件夹
    
"""
super_path = r"C:\Users\Administrator\Desktop\Super Browser"
def raw_bulkdownload_data(path):
    try:
        L = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if "uploaddata" in file:
                    L.append(os.path.join(root,file))
                    print((os.path.join(root,file)))

        upload_file = pd.read_excel(r"D:\data\20230928后带ID文件\upload.xlsx", sheet_name="Sheet1", engine="openpyxl")
        m = 0
        n = 0
        for l in L:
            df = pd.read_excel(l, sheet_name="Sponsored Products Campaigns",engine="openpyxl")
            df = df.drop(df.columns[34:], axis=1)
            filename = l.split("\\")[-1]
            df["Country"] = filename[4:6]
            df["Station"] = filename[:6]
            df.columns = list(upload_file.columns)
            print(filename[:6], df.shape)
            upload_file = pd.concat([upload_file, df], axis=0)

            n += 1
            m += df.shape[0]

        print(m, n)
        print(upload_file.shape)

        upload_file["Station_Campaign"] = upload_file["Station"] + upload_file["Campaign Name (Informational only)"]
        upload_file['Campaign ID'] = upload_file['Campaign ID'].astype(str)
        upload_file['Ad Group ID'] = upload_file['Ad Group ID'].astype(str)
        upload_file['Portfolio ID'] = upload_file['Portfolio ID'].astype(str)
        upload_file['Ad ID'] = upload_file['Ad ID'].astype(str)
        # 非ID 信息感觉可以删掉 前31列
        columns_to_drop = ['Product','Entity','Operation','Keyword ID','Product Targeting ID','Campaign Name','Ad Group Name',
                           'Campaign Name (Informational only)', 'Ad Group Name (Informational only)', 'Portfolio Name (Informational only)',
                           'Start Date', 'End Date', 'Targeting Type', 'State',	'Campaign State (Informational only)', 'Ad Group State (Informational only)',
                           'Daily Budget', 'SKU', 'ASIN (Informational only)', 'Eligibility Status (Informational only)', 'Reason for Ineligibility (Informational only)',
                           'Ad Group Default Bid', 'Ad Group Default Bid (Informational only)', 'Bid', 'Keyword Text', 'Match Type', 'Bidding Strategy',
                           'Placement','Percentage', 'Product Targeting Expression','Country', 'Station', 'Station_Campaign']

        upload_file = upload_file.drop(columns_to_drop, axis=1)
        todaydir = time.strftime("%Y-%m-%d", time.localtime())
        uploadpath = r"D:\data\20230928后带ID文件\{}-rawuploaddata.xlsx".format(todaydir)
        upload_file.to_excel(excel_writer= uploadpath, index = None)

        return upload_file

    except Exception as e:
        print("合并uploaddata 失败", e)


def main():

    path = r"D:\data\20230928后带ID文件\testdata.xlsx"
    data_to_save = r"D:\data\searchwords\历史手动广告投放词.xlsx"
    data_to_current = r"D:\data\searchwords\本次手动广告投放词.xlsx"

    campaign_budget = 500
    group_default_bid = 0.05

    # 不同组的竞价增幅倍率
    asin_up = 1
    broad_up = 1
    phrase_up = 1.05
    exact_up = 1.08

    # 手动不同匹配类型的判断标准
    asin_acos = 0.18
    asin_cr = 0.06
    asin_order = 2

    broad_acos = 0.22
    broad_cr = 0.05
    broad_order = 2

    phrase_acos = 0.20
    phrase_cr = 0.07
    phrase_order = 3

    exact_acos = 0.18
    exact_cr = 0.09
    exact_order = 4

    # 不符合标准的出单词（pending）将限制最高竞价
    base_bid_us = 0.4
    base_bid_ca = 0.5
    base_bid_uk = 0.35
    base_bid_de = 0.35
    base_bid_fr = 0.3
    base_bid_it = 0.3
    base_bid_es = 0.3
    base_bid_au = 0.5
    base_bid_ae = 0.5
    base_bid_jp = 15
    base_bid_mx = 0.8
    base_bid_br = 0.12
    base_bid_nl = 0.3
    base_bid_sg = 0.2
    base_bid_sa = 0.2

    # raw_bulkdata = raw_bulkdownload_data(super_path)
    raw_bulkdata = pd.read_excel(r"D:\data\20230928后带ID文件\rawuploaddata.xlsx", sheet_name= 0, engine="openpyxl")
    keywords_data = read_excel(path, data_to_save, data_to_current,
                               asin_acos, asin_cr, asin_order,
                               broad_acos, broad_cr, broad_order,
                               phrase_acos, phrase_cr, phrase_order,
                               exact_acos, exact_cr, exact_order)

    data_to_campaign(keywords_data,raw_bulkdata,campaign_budget,group_default_bid,asin_up,broad_up,phrase_up,exact_up,
                     base_bid_us,base_bid_ca,base_bid_uk,base_bid_de,base_bid_fr,base_bid_it,base_bid_es,
                     base_bid_au,base_bid_ae,base_bid_jp,base_bid_mx,base_bid_br,base_bid_nl,base_bid_sg,base_bid_sa)

# 读取tableau导出的数据信息
def read_excel(path, data_to_save, data_to_current,
                               asin_acos, asin_cr, asin_order,
                               broad_acos, broad_cr, broad_order,
                               phrase_acos, phrase_cr, phrase_order,
                               exact_acos, exact_cr, exact_order):
    try:
        df = pd.read_excel(path, sheet_name= 0 ,engine="openpyxl")

        # Step1: 获取搜索词数据，搜索词默认Broad, 待判断Phrase,Exact
        keywords_step1 = df[['Station','Campaign Name_M','SellSKU','Search Term Type', 'Customer Search Term', 'Bid', "CR", "Orders", "ACOS"]]
        keywords_step1.replace({"Keywords":"Broad"}, inplace=True)

        # 获取ASIN和ASIN_pending
        keywords_step1_ASIN_total = keywords_step1[(keywords_step1["Search Term Type"] == "ASIN")]
        keywords_step1_ASIN = keywords_step1[(keywords_step1["Search Term Type"] == "ASIN") & (keywords_step1.Orders >= asin_order) & (keywords_step1.CR >= asin_cr) & (keywords_step1.ACOS <= asin_acos)]
        keywords_step1_ASIN_total_concat = pd.concat([keywords_step1_ASIN, keywords_step1_ASIN_total], axis=0)
        keywords_step1_ASIN_total_concat = keywords_step1_ASIN_total_concat.drop_duplicates()
        keywords_step1_ASIN_pending = keywords_step1_ASIN_total_concat[keywords_step1_ASIN.shape[0]:]
        keywords_step1_ASIN_pending.replace({"ASIN": "ASIN_Pending"}, inplace=True)

        # 获取Broad和Broad_pending
        keywords_step1_Broad_total = keywords_step1[(keywords_step1["Search Term Type"] == "Broad")]
        keywords_step1_Broad = keywords_step1[(keywords_step1["Search Term Type"] == "Broad") & (keywords_step1.Orders >= broad_order) & (keywords_step1.CR >= broad_cr) & (keywords_step1.ACOS <= broad_acos)]
        keywords_step1_Broad_total_concat = pd.concat([keywords_step1_Broad, keywords_step1_Broad_total], axis=0)
        keywords_step1_Broad_total_concat = keywords_step1_Broad_total_concat.drop_duplicates()
        keywords_step1_Broad_pending = keywords_step1_Broad_total_concat[keywords_step1_Broad.shape[0]:]
        keywords_step1_Broad_pending.replace({"Broad": "Broad_Pending"}, inplace=True)

        # 获取Phrase
        keywords_step1_Phrase = keywords_step1[(keywords_step1["Search Term Type"] == "Broad") & (keywords_step1.Orders >= phrase_order) & (keywords_step1.CR >= phrase_cr) & (keywords_step1.ACOS <= phrase_acos)]
        keywords_step1_Phrase.replace({"Broad": "Phrase"}, inplace=True)

        # 获取Exact
        keywords_step1_Exact = keywords_step1[(keywords_step1["Search Term Type"] == "Broad") & (keywords_step1.Orders >= exact_order) & (keywords_step1.CR >= exact_cr) & (keywords_step1.ACOS <= exact_acos)]
        keywords_step1_Exact.replace({"Broad": "Exact"}, inplace=True)

        # Step2:合并以上6个组
        keywords_step2 = pd.concat([keywords_step1_ASIN,keywords_step1_ASIN_pending,keywords_step1_Broad,keywords_step1_Broad_pending,
                                    keywords_step1_Phrase,keywords_step1_Exact], axis = 0, sort=False)

        #各项手动投放词存储
        previous_keywords_total = pd.read_excel(data_to_save, sheet_name=0)
        previous_keywords = previous_keywords_total[['Station', 'Campaign Name_M','Search Term Type', 'Customer Search Term']]
        keywords_info = keywords_step2[['Station', 'Campaign Name_M','Search Term Type', 'Customer Search Term']]
        keywords_info_concat = pd.concat([previous_keywords, keywords_info], axis=0, sort=False)
        # 剔除新增重复的关键词[previous_keywords.shape[0]:]
        keywords_info_concat = keywords_info_concat.drop_duplicates()
        keywords_info_to_save = keywords_info_concat[previous_keywords.shape[0]:]
        keywords_info_to_save['Date'] = time.strftime("%Y/%m/%d", time.localtime())

        # # 写入历史关键词记录文档
        # new_keywords_info_to_save = pd.concat([previous_keywords_total, keywords_info_to_save], axis=0, sort=False)
        #
        # new_keywords_info_to_save.to_excel(excel_writer=data_to_save, index=None)

        # Step3: 非重复关键词
        keywords_step3 = keywords_info_to_save[['Station','Campaign Name_M','Search Term Type', 'Customer Search Term']]
        keywords_step3 = pd.merge(keywords_step3, keywords_step2, how="left")

        # # 此次手动投放的数据源
        # keywords_step3.to_excel(excel_writer=data_to_current, index=None)

        return keywords_step3

    except Exception as e:
        print("读取失败", e)

def data_to_campaign(keywords_data,raw_bulkdata,campaign_budget_normal,group_default_bid_nornal,asin_up,broad_up,
                     phrase_up,exact_up,base_bid_us,base_bid_ca,base_bid_uk,base_bid_de,base_bid_fr,
                     base_bid_it,base_bid_es,base_bid_au,base_bid_ae,base_bid_jp,base_bid_mx,base_bid_br,
                     base_bid_nl,base_bid_sg,base_bid_sa):

    global Campaign_M_info, station


    try:
        # 2023.09.28 增加 含有ID的数据列，插入到keyword_data表中

        keywords_data['Station_Campaign'] = keywords_data['Station'] + keywords_data['Campaign Name_M']
        keywords_data['Station_Campaign_Group'] = keywords_data['Station_Campaign'] + keywords_data['Search Term Type']

        # 这里暂时没有考虑 需要新增广告组的情况处理；
        keywords_data = pd.merge(keywords_data, raw_bulkdata, on="Station_Campaign_Group" ,how="left")

        station_set = set(map(lambda x:x[-6:], keywords_data['Station']))
#------------------------------------
        for station in station_set:
            ## 获取站点内手动活动名称（去重)
            Campaign_Name_ = list(keywords_data.loc[keywords_data['Station'] == station]['Campaign Name_M'])
            Campaign_Name_M = list(set(Campaign_Name_))
            Campaign_Name_M.sort(key=Campaign_Name_.index)

            # 列表预备接受不同站点下所有手动数据dataframe
            Campaign_M_info = []

            # 循环每个手动数据
            for i in Campaign_Name_M:

                # 获取手动的sku 值 # 'Neabot-P1-Pro-FBA'
                SellSKU = keywords_data.loc[(keywords_data['Station'] == station) & (keywords_data['Campaign Name_M'] == i)]['SellSKU'].iloc[0]

                # Step1: 获取搜索词数据
                keywords_step1 = keywords_data.loc[(keywords_data['Station'] == station) & (keywords_data['Campaign Name_M'] == i)][['Search Term Type', 'Customer Search Term', 'Bid', "CR", "Orders", "ACOS"]]

                # 获取手动投放的6个组
                keywords_step1_ASIN_pending = keywords_step1[(keywords_step1["Search Term Type"] == "ASIN_Pending")]
                keywords_step1_Broad_pending = keywords_step1[(keywords_step1["Search Term Type"] == "Broad_Pending")]
                keywords_step1_ASIN = keywords_step1[(keywords_step1["Search Term Type"] == "ASIN")]
                keywords_step1_Broad = keywords_step1[(keywords_step1["Search Term Type"] == "Broad")]
                keywords_step1_Phrase = keywords_step1[(keywords_step1["Search Term Type"] == "Phrase")]
                keywords_step1_Exact = keywords_step1[(keywords_step1["Search Term Type"] == "Exact")]

                # 两个ASIN组设置Targeting
                for x in [keywords_step1_ASIN_pending, keywords_step1_ASIN]:
                    x["Product Targeting ID"] = x["Customer Search Term"].map(lambda x: 'asin="' + x.upper() + '"')
                    x.drop(["Customer Search Term"], axis=1, inplace=True)

                # 两个Pending组限制最高竞价
                for inx, y in enumerate([keywords_step1_ASIN_pending, keywords_step1_Broad_pending]):
                    bid_up = asin_up if inx == 0 else broad_up
                    if station[-2:] == "US":
                        y["Bid"] = y["Bid"].map(lambda x: base_bid_us if round(x * bid_up, 2) > base_bid_us else round(x * bid_up, 2))
                    elif station[-2:] == "CA":
                        y["Bid"] = y["Bid"].map(lambda x: base_bid_ca if round(x * bid_up, 2) > base_bid_ca else round(x * bid_up, 2))
                    elif station[-2:] == "UK":
                        y["Bid"] = y["Bid"].map(lambda x: base_bid_uk if round(x * bid_up, 2) > base_bid_uk else round(x * bid_up, 2))
                    elif station[-2:] == "DE":
                        y["Bid"] = y["Bid"].map(lambda x: base_bid_de if round(x * bid_up, 2) > base_bid_de else round(x * bid_up, 2))
                    elif station[-2:] == "FR":
                        y["Bid"] = y["Bid"].map(lambda x: base_bid_fr if round(x * bid_up, 2) > base_bid_fr else round(x * bid_up, 2))
                    elif station[-2:] == "IT":
                        y["Bid"] = y["Bid"].map(lambda x: base_bid_it if round(x * bid_up, 2) > base_bid_it else round(x * bid_up, 2))
                    elif station[-2:] == "ES":
                        y["Bid"] = y["Bid"].map(lambda x: base_bid_es if round(x * bid_up, 2) > base_bid_es else round(x * bid_up, 2))
                    elif station[-2:] == "AU":
                        y["Bid"] = y["Bid"].map(lambda x: base_bid_au if round(x * bid_up, 2) > base_bid_au else round(x * bid_up, 2))
                    elif station[-2:] == "AE":
                        y["Bid"] = y["Bid"].map(lambda x: base_bid_ae if round(x * bid_up, 2) > base_bid_ae else round(x * bid_up, 2))
                    elif station[-2:] == "JP":
                        y["Bid"] = y["Bid"].map(lambda x: base_bid_jp if round(x * bid_up, 2) > base_bid_jp else round(x * bid_up, 2))
                    elif station[-2:] == "MX":
                        y["Bid"] = y["Bid"].map(lambda x: base_bid_mx if round(x * bid_up, 2) > base_bid_mx else round(x * bid_up, 2))
                    elif station[-2:] == "BR":
                        y["Bid"] = y["Bid"].map(lambda x: base_bid_br if round(x * bid_up, 2) > base_bid_br else round(x * bid_up, 2))
                    elif station[-2:] == "NL":
                        y["Bid"] = y["Bid"].map(lambda x: base_bid_nl if round(x * bid_up, 2) > base_bid_nl else round(x * bid_up, 2))
                    elif station[-2:] == "SG":
                        y["Bid"] = y["Bid"].map(lambda x: base_bid_sg if round(x * bid_up, 2) > base_bid_sg else round(x * bid_up, 2))
                    elif station[-2:] == "SA":
                        y["Bid"] = y["Bid"].map(lambda x: base_bid_sa if round(x * bid_up, 2) > base_bid_sa else round(x * bid_up, 2))
                    else:
                        y["Bid"] = y["Bid"].map(lambda x: round(x * bid_up, 2))

                # 正常四组设置竞价增幅
                keywords_step1_ASIN["Bid"] = keywords_step1_ASIN["Bid"].map(lambda x: round(x * asin_up,2))
                keywords_step1_Broad["Bid"] = keywords_step1_Broad["Bid"].map(lambda x: round(x * broad_up, 2))
                keywords_step1_Phrase["Bid"] = keywords_step1_Phrase["Bid"].map(lambda x: round(x * phrase_up,2))
                keywords_step1_Exact["Bid"] = keywords_step1_Exact["Bid"].map(lambda x: round(x * exact_up, 2))

                if station[-2:] == "JP":
                    campaign_budget = 1500
                    group_default_bid = 10
                elif station[-2:] == "BR":
                    campaign_budget = 20
                    group_default_bid = 0.07
                elif station[-2:] in ["AE", "SA"]:
                    campaign_budget = 20
                    group_default_bid = 0.24
                elif station[-2:] in ["MX", "AU"]:
                    campaign_budget = 20
                    group_default_bid = 0.1
                else:
                    campaign_budget = campaign_budget_normal
                    group_default_bid = group_default_bid_nornal

                for g in [keywords_step1_ASIN_pending, keywords_step1_ASIN, keywords_step1_Broad_pending, keywords_step1_Broad,keywords_step1_Phrase, keywords_step1_Exact]:
                    g["Bid"] = g["Bid"].map(lambda x: group_default_bid if x < group_default_bid else x)

                # 组信息 # ['Search Term Type', 'Bid', 'SKU']
                keywords_step1_group = pd.DataFrame({"Search Term Type": ["Type", "Type"], "Bid": [group_default_bid, ""], "SKU": ["_", SellSKU]})

                # Step2: 以活动+组名+组手动词的顺序拼接dataframe，然后添加其他列信息
                keywords_step2 = pd.concat([pd.DataFrame({"Campaign": [i,""], "Campaign Daily Budget":[campaign_budget,""],"Campaign Start Date":["",""],"Campaign Targeting Type":["Manual",""]}),
                                            keywords_step1_group.replace("Type", "ASIN_Pending"), keywords_step1_ASIN_pending,
                                            keywords_step1_group.replace("Type", "ASIN"), keywords_step1_ASIN,
                                            keywords_step1_group.replace("Type", "Broad_Pending"), keywords_step1_Broad_pending,
                                            keywords_step1_group.replace("Type", "Broad"), keywords_step1_Broad,
                                            keywords_step1_group.replace("Type", "Phrase"), keywords_step1_Phrase,
                                            keywords_step1_group.replace("Type", "Exact"), keywords_step1_Exact],axis=0, sort=False)

                keywords_step2.index = range(len(keywords_step2))
                keywords_step2.drop([1], inplace=True)
                keywords_step2.drop(["CR", "Orders"], axis=1, inplace=True)

                # 替换列标题空格，替换None值，方便定位
                keywords_step2.rename(columns=lambda x: x.replace(' ', '_'), inplace=True)
                keywords_step2.replace({None: "_"}, inplace=True)

                # 增加活动名字列
                keywords_step2["Campaign"] = i

                # 增加Match Type
                keywords_step2.loc[keywords_step2.Product_Targeting_ID != "_", "Match Type"] = "Targeting Expression"
                for z in ["Broad", "Phrase", "Exact"]:
                    keywords_step2.loc[(keywords_step2.Search_Term_Type == z) & (keywords_step2.Customer_Search_Term != "_"), "Match Type"] = z

                keywords_step2.loc[(keywords_step2.Search_Term_Type == "Broad_Pending") & (keywords_step2.Customer_Search_Term != "_"), "Match Type"] = "Broad"

                # 增加Campaign Status列
                keywords_step2.loc[keywords_step2.Campaign_Targeting_Type == "Manual", "Campaign Status"] = "Enabled"

                # 增加Ad Group Status列
                keywords_step2.loc[keywords_step2.Bid == group_default_bid, "Ad Group Status"] = "Enabled"

                # 增加Status列
                for a in [keywords_step2.Customer_Search_Term, keywords_step2.Product_Targeting_ID, keywords_step2.SKU]:
                    keywords_step2.loc[a != "_", "Status"] = "Enabled"

                # 增加剩余3列
                for b in ["Campaign ID", "Campaign End Date", "Bidding strategy"]:
                    keywords_step2[b] = ""

                # 清除多余值Campaign_Start_Date
                for c in [None, "_"]:
                    keywords_step2.replace({c: ""}, inplace=True)

                keywords_step3 = keywords_step2[["Campaign ID", "Campaign", "Campaign_Daily_Budget", "Campaign_Start_Date", "Campaign End Date", "Campaign_Targeting_Type", "Search_Term_Type", "Bid", "SKU", "Customer_Search_Term", "Product_Targeting_ID", "Match Type", "Campaign Status", "Ad Group Status", "Status", "Bidding strategy"]]

                # 每个手动数据传入列表储存
                Campaign_M_info.append(keywords_step3)

            station_values()
    except Exception as e:
        print("计算失败",e)

# 根据站点获取信息填写方式
def station_values():

    global campaign_date, sheet_head, campaign_budget, Campaign_Start_Date, campaign_type, campaign_status

    try:
        station_type = station[-2:]
        if station_type in ["CA", "AU", "AE", "MX", "BR", "SG", "JP", "SA"]:
            station_type = "US"
        if station_type in ["DE", "FR", "IT", "ES", "NL", "IN"]:
            station_type = "UK"

        timeArray = time.localtime(time.time())

        station_info = {'US': {'Date': time.strftime("%Y/%m/%d", timeArray), 'Manual': 'Manual', 'Status': 'Enabled',
                               'title_name': ['Campaign ID', 'Campaign', 'Campaign Daily Budget', 'Campaign Start Date',
                                              'Campaign End Date', 'Campaign Targeting Type', 'Ad Group', 'Max Bid',
                                              'SKU', 'Keyword or Product Targeting', "Product Targeting ID",
                                              'Match Type', 'Campaign Status', 'Ad Group Status', 'Status',
                                              'Bidding strategy']},
                        'UK': {'Date': time.strftime("%d/%m/%Y", timeArray), 'Manual': 'Manual', 'Status': 'Enabled',
                               'title_name': ['Campaign ID', 'Campaign Name', 'Campaign Daily Budget',
                                              'Campaign Start Date', 'Campaign End Date', 'Campaign Targeting Type',
                                              'Ad Group Name', 'Max Bid', 'SKU', 'Keyword or Product Targeting',
                                              "Product Targeting ID", 'Match Type', 'Campaign Status',
                                              'Ad Group Status', 'Status', 'Bid+']}}

        campaign_date = station_info[station_type]['Date']
        sheet_head = station_info[station_type]['title_name']
        campaign_type = station_info[station_type]['Manual']
        campaign_status = station_info[station_type]['Status']
        Campaign_Start_Date = station_info[station_type]['title_name'][3]

        write_excel()

    except Exception as e:
        print("获取失败", e)

# 写Excel
def write_excel():
    try:
        pd_save = pd.DataFrame([sheet_head, ], columns=sheet_head)

        for i in Campaign_M_info:
            i.columns = sheet_head
            i.loc[0, Campaign_Start_Date] = campaign_date
            i.replace({"Enabled": campaign_status}, inplace=True)
            i.replace({"Manual": campaign_type}, inplace=True)
            pd_save = pd.concat([pd_save, i])

        to_path = r"D:\data\上传文件-手动广告\{0} 手动广告.xlsx".format(station)

        pd_save.to_excel(excel_writer=to_path, header=None, index=None)

    except Exception as e:
        print("写入失败", e)
#
if __name__ =='__main__':
    main()
