import numpy as np
import pandas as pd
import os



def file_name():

    try:
        L=[]
        for root, dirs, files in os.walk(path):
            for file in files:
                if os.path.splitext(file)[1] == '.xlsx':
                    L.append(os.path.join(root, file))
        return L

    except Exception as e:
        print("获取各文件路径失败", e)


def read_excel():
    
    try:
        L = file_name()

        station_total = []
        dit = {}
        
        #存放键值对“文件名：站点”
        # D:\data\festival\周四批量20191010\243-UK.xls
        for i in L:
            print(i)
            station_total.append(i[35:41])
            dit[i] = i[35:41]

        #站点去重，查非重复数量
        station_total = set(station_total)
        
        #反转键值对“站点：[文件名1, 文件名2, ....]”便于循环
        station_upload = {}
        for k,v in dit.items():
            #第一次反转站点时，创建值为列表
            if station_upload.get(v,0) == 0:
                station_upload[v] = []
            station_upload[v].append(k)
# D:\data\festival\周四合并
        #循环站点对应各文件
        for i in station_total:
            excel_upload = pd.read_excel(final_path, sheet_name=i[-2:])
            #上传文件路径
            upload_path = path[:-8] + "\{}.xls".format(i)

            #合并同站点文件
            for x in station_upload[i]:
                df = pd.read_excel(x)
                # print(df.shape, x[32:-4])
                excel_upload = pd.concat([excel_upload,df], axis = 0, sort=False)
                
            #生成上传文件
            excel_upload.to_excel(excel_writer = upload_path, index = None)
            print("{} 已完成合并".format(i))

        
        
    except Exception as e:
        print("读取数据失败", e)
        
    else:
        print("文件已创建，可上传")



def main():
    
    global path, final_path, upload_path
# D:\\data\\festival\\周\\
    # path = r"D:\data\festival\周四批量"
    #upload_path = r"D:\data\festival\周四合并\20191010"
    path = r"D:\data\周四批量\festival\周四批量20210414"
    final_path = r"D:\data\周四批量\festival\Final.xls"
    
    read_excel()

if __name__ == '__main__':
    main()