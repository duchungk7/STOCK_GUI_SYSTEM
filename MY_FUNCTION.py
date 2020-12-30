#####
# Created at 2020-10-16, by Mark Pei
# txt_process_func.py for ...
######

import pandas as pd
import requests
from io import StringIO
import time

import bs4

#選擇 市場
MARKET = 'MARKET_CAT=%E8%88%88%E6%AB%83' # 興櫃
#MARKET = 'MARKET_CAT=%E4%B8%8A%E6%AB%83' # 上櫃
#MARKET = 'MARKET_CAT=%E4%B8%8A%E5%B8%82' # 上市

# 自己平台的 user-agent, 可打開網頁，按下 F12 取得
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}

# QMessageBox 顯示資訊說明
#===============================================================
from PyQt5.QtWidgets import QMessageBox

#警告 QMessageBox
#msgBox.setIcon(QMessageBox.Critical)
def Information_Box(Box_Icon, title_text, msg_text):
    msgBox = QMessageBox()  # 建立一個 message Box 對話框
    msgBox.setIcon(Box_Icon) # msgBox 加入一個 "Information" icon
    msgBox.setWindowTitle(title_text)
    msgBox.setText(msg_text)
    msgBox.setStandardButtons(QMessageBox.Ok)
    returnValue = msgBox.exec()
    msgBox.show() # 顯示 msgBox
    if returnValue == QMessageBox.Ok:
        msgBox.close()
        
# 財報 評分 打分數
#===============================================================
def financial_report_score(numA):
    score = 0
    if numA > 0 and numA < 20:
        score = 1
    if numA > 5 and numA < 30:
        score = 2
    if numA > 10 and numA < 40:
        score = 4
    if numA > 20 and numA < 50:
        score = 6
    if numA > 30 and numA < 60:
        score = 8
    if numA > 40 and numA < 70:
        score = 10
    if numA > 80:
        score = 15
    return score

# 用於 給個股 打分數
#score = computer_score(6)
#===============================================================
def computer_score(numA):
    score = 0
    if numA > 0 and numA < 5:
        score = 1
    if numA > 5 and numA < 10:
        score = 2
    if numA > 10 and numA < 20:
        score = 4
    if numA > 20 and numA < 30:
        score = 6
    if numA > 30 and numA < 40:
        score = 8
    if numA > 40 and numA < 50:
        score = 10
    if numA > 50:
        score = 15
    return score

# 將股票走勢 畫圖
#saveImage_path = plot_and_save_dfs(dfs_plot,4151)
#===============================================================
import talib
from matplotlib import pyplot as plt
def plot_and_save_dfs(dfs_new, Stock_ID):
    #提取收盘价
    closed=dfs_new['收盤'].values
    #获取均线的数据，通过timeperiod参数来分别获取 5,10,20 日均线的数据。
    ma5=talib.SMA(closed,timeperiod=5)
    ma10=talib.SMA(closed,timeperiod=10)
    ma20=talib.SMA(closed,timeperiod=30)
    
    plt.figure(figsize=(6,4), facecolor='w',edgecolor='black')
    #plt.figure(figsize=(12,8))
    #'開盤', '最高', '最低', '收盤',
    plt.plot(dfs_new['收盤'].values, 'gX-', linewidth=3, label='Close')
    plt.plot(ma5, 'y', label='5MA')
    plt.plot(ma10, 'purple', label='10MA')
    plt.plot(ma20, 'cyan', label='20MA')
    plt.legend()
    plt.title('3 Month Data')
    
    #添加网格，可有可无，只是让图像好看点
    plt.grid()
    #记得加这一句，不然不会显示图像
    
    plt.show()
    saveImage_path = './IMAGE/'+str(Stock_ID)+'.png'
    plt.savefig(saveImage_path)
    
    #return saveImage_path


# 個股 查詢
#dfs, dfs_plot = GetStock3MonthPriceData(4151)
#===============================================================
def GetStock3MonthPriceData(STOCK_ID):
    """STOCK_ID: 股票代號
       資料形態: int
       
       return: dataframe 含 最近3個月交易狀態
       交易 日期	開盤	最高	最低	收盤	張數	筆數
    """
    
    """將股票走勢 畫圖
       
       需要資訊：
       開盤	最高	最低	收盤
    """
    url = "https://goodinfo.tw/StockInfo/ShowK_Chart.asp?STOCK_ID="+str(STOCK_ID)+"&CHT_CAT2=DATE"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
    res = requests.get(url,headers=headers)
    res.encoding = "utf-8"
    
    soup = bs4.BeautifulSoup(res.text,"lxml")
    data = soup.select_one("#divPriceDetail") # 抓 ID
    
    df = pd.read_html(data.prettify())
    dfs = df[0]
    dfs.head()
    dfs.columns = dfs.columns.get_level_values(7)
    
    #過濾 不需要的 label 欄位
    dfs_label_list = ['漲跌', '漲跌  (%)', '振幅  (%)', '均張','億元','外資', '投信', '自營', '合計', '外資  持股  (%)',
                        '增減', '餘額','增減', '餘額', '券資  比  (%)']
    dfs = dfs.drop(dfs_label_list, axis=1)
    
    dfs_plot_label_list = ['交易  日期', '張數', '筆數']
    dfs_plot = dfs.drop(dfs_plot_label_list, axis=1)

    #轉換成 以前的資料為最上
    dfs_plot = dfs_plot.iloc[::-1]

    #設定 index 從 0 開始
    dfs_plot.index = range(len(dfs_plot))


    return dfs, dfs_plot
# 從csv 檔，找出個股資料
#===============================================================
def get_stock_data_from_dataframe(dfs_month_Revenue, stock_num):
    """ dfs_month_Revenue: 原始 dataframe
        stock_num： 一個陣列如：[1563, 1260, 1269, 9957, 8492]
    """
    df_stock_data = []
    
    for k in range(len(stock_num)):
        if k == 0:  #使用 dataframe 合併的方式， 所以先取得第0行資料
            for i in range(len(dfs_month_Revenue)):
                if dfs_month_Revenue['代號'][i] ==stock_num[0]:
                    df_stock_data = dfs_month_Revenue[i:i+1]
        else:
            for j in range(len(dfs_month_Revenue)):
                if dfs_month_Revenue['代號'][j] ==stock_num[k]:
                    df_stock_data = pd.concat([df_stock_data,dfs_month_Revenue[j:j+1]])
    return df_stock_data
#stock = dfs_stock_month_Revenue_data['代號'].values.tolist() #將股票代號存入陣列 list
#dfs_stock_Profitability_data = get_stock_data_from_dataframe(dfs_Profitability, stock)

# 爬取 goodinfo 網站資料-核心程式
#===============================================================
def GetStockListData(url, headers):
    res = requests.get(url,headers=headers)
    res.encoding = "utf-8"
    
    soup = bs4.BeautifulSoup(res.text,"lxml")
    data = soup.select_one("#txtStockListData")
    
    df = pd.read_html(data.prettify())
    
    dfs = df[1]
    dfs.head()

    dfs.columns = dfs.columns.get_level_values(13)
    return dfs
#dfs_dataframe = GetStockListData(url, headers)
#dfs_dataframe.to_csv('StockListData.csv')


#====================================== 取得 全部 興櫃 月營收 資訊 ======================================
def get_month_Revenue():
    #goodinfo 月營收資訊
    url = "https://goodinfo.tw/StockInfo/StockList.asp?" +MARKET+"&INDUSTRY_CAT=%E8%88%88%E6%AB%83%E5%85%A8%E9%83%A8&SHEET=%E7%87%9F%E6%94%B6%E7%8B%80%E6%B3%81&SHEET2=%E6%9C%88%E7%87%9F%E6%94%B6%E7%B5%B1%E8%A8%88&RPT_TIME=%E6%9C%80%E6%96%B0%E8%B3%87%E6%96%99"
    dfs_month_Revenue = GetStockListData(url, headers)
    
    return dfs_month_Revenue


#========================================= 取得 累計季獲利能力 =========================================
def get_Profitability():
    #goodinfo 累計季獲利能力
    url = "https://goodinfo.tw/StockInfo/StockList.asp?" +MARKET+"&INDUSTRY_CAT=%E8%88%88%E6%AB%83%E5%85%A8%E9%83%A8&SHEET=%E5%AD%A3%E7%B4%AF%E8%A8%88%E7%8D%B2%E5%88%A9%E8%83%BD%E5%8A%9B&SHEET2=%E7%8D%B2%E5%88%A9%E8%83%BD%E5%8A%9B%E2%80%93%E7%B4%AF%E5%AD%A3&RPT_TIME=%E6%9C%80%E6%96%B0%E8%B3%87%E6%96%99"
    dfs_Profitability = GetStockListData(url, headers)
    
    return dfs_Profitability


#========================================= 取得 最近漲跌幅統計 =========================================
def get_Transaction_Status():
    #交易狀況–漲跌及成交統計 ==> 短期累計漲跌統計
    url = "https://goodinfo.tw/StockInfo/StockList.asp?" +MARKET+"&INDUSTRY_CAT=%E8%88%88%E6%AB%83%E5%85%A8%E9%83%A8&SHEET=%E6%BC%B2%E8%B7%8C%E5%8F%8A%E6%88%90%E4%BA%A4%E7%B5%B1%E8%A8%88&SHEET2=%E4%BA%A4%E6%98%93%E7%8B%80%E6%B3%81%E2%80%93%E6%BC%B2%E8%B7%8C%E5%8F%8A%E6%88%90%E4%BA%A4%E7%B5%B1%E8%A8%88&RPT_TIME=%E6%9C%80%E6%96%B0%E8%B3%87%E6%96%99"
    dfs_Transaction_Status = GetStockListData(url, headers)
    return dfs_Transaction_Status


#===================================== 法人累計買賣超統計–三大法人 =====================================
def get_3Institutional_Investors():
    #法人買賣統計_三大' ==> 法人累計買賣超統計–三大法人
    url = "https://goodinfo.tw/StockInfo/StockList.asp?" +MARKET+"&INDUSTRY_CAT=%E8%88%88%E6%AB%83%E5%85%A8%E9%83%A8&SHEET=%E6%B3%95%E4%BA%BA%E8%B2%B7%E8%B3%A3%E7%B5%B1%E8%A8%88_%E4%B8%89%E5%A4%A7&SHEET2=%E6%B3%95%E4%BA%BA%E7%B4%AF%E8%A8%88%E8%B2%B7%E8%B3%A3%E8%B6%85%E7%B5%B1%E8%A8%88%E2%80%93%E4%B8%89%E5%A4%A7%E6%B3%95%E4%BA%BA&RPT_TIME=%E6%9C%80%E6%96%B0%E8%B3%87%E6%96%99"
    dfs_3Institutional_Investors = GetStockListData(url, headers)
    return dfs_3Institutional_Investors


#========================================= 取得 董監持股 統計 =========================================
def get_Director_Supervisor():
    #董監持股' >籌碼分佈–董監持股
    url = "https://goodinfo.tw/StockInfo/StockList.asp?" +MARKET+"&INDUSTRY_CAT=%E8%88%88%E6%AB%83%E5%85%A8%E9%83%A8&SHEET=%E8%91%A3%E7%9B%A3%E6%8C%81%E8%82%A1&SHEET2=%E7%B1%8C%E7%A2%BC%E5%88%86%E4%BD%88%E2%80%93%E8%91%A3%E7%9B%A3%E6%8C%81%E8%82%A1&RPT_TIME=%E6%9C%80%E6%96%B0%E8%B3%87%E6%96%99"
    dfs_Director_Supervisor = GetStockListData(url, headers)
    return dfs_Director_Supervisor


#======================================= KD指標 技術指標–KD指標 =======================================
def get_KDJ_Value():
    url_KD = "https://goodinfo.tw/StockInfo/StockList.asp?" +MARKET+"&INDUSTRY_CAT=%E8%88%88%E6%AB%83%E5%85%A8%E9%83%A8&SHEET=KD%E6%8C%87%E6%A8%99&SHEET2=%E6%8A%80%E8%A1%93%E6%8C%87%E6%A8%99%E2%80%93KD%E6%8C%87%E6%A8%99&RPT_TIME=%E6%9C%80%E6%96%B0%E8%B3%87%E6%96%99"
    dfs_KDJ = GetStockListData(url_KD, headers)
    return dfs_KDJ


#===================================== 移動均量 技術指標–移動平均量 ====================================
def get_Average_Amount():
    url_Average_Amount = "https://goodinfo.tw/StockInfo/StockList.asp?" +MARKET+"&INDUSTRY_CAT=%E8%88%88%E6%AB%83%E5%85%A8%E9%83%A8&SHEET=%E7%A7%BB%E5%8B%95%E5%9D%87%E9%87%8F&SHEET2=%E6%8A%80%E8%A1%93%E6%8C%87%E6%A8%99%E2%80%93%E7%A7%BB%E5%8B%95%E5%B9%B3%E5%9D%87%E9%87%8F&RPT_TIME=%E6%9C%80%E6%96%B0%E8%B3%87%E6%96%99"
    dfs_Average_Amount = GetStockListData(url_Average_Amount, headers)
    return dfs_Average_Amount


#====================================== MACD指標 技術指標–MACD指標 =====================================
def get_MACD_Value():
    url_MACD = "https://goodinfo.tw/StockInfo/StockList.asp?" +MARKET+"&INDUSTRY_CAT=%E8%88%88%E6%AB%83%E5%85%A8%E9%83%A8&SHEET=MACD&SHEET2=%E6%8A%80%E8%A1%93%E6%8C%87%E6%A8%99%E2%80%93MACD&RPT_TIME=%E6%9C%80%E6%96%B0%E8%B3%87%E6%96%99"
    dfs_MACD = GetStockListData(url_MACD, headers)
    return dfs_MACD

#====================================== 公司基本資料=====================================
def get_Company_Infomation():
    url_Company_Info="https://goodinfo.tw/StockInfo/StockList.asp?"+MARKET+"&INDUSTRY_CAT=%E8%88%88%E6%AB%83%E5%85%A8%E9%83%A8&SHEET=%E5%85%AC%E5%8F%B8%E5%9F%BA%E6%9C%AC%E8%B3%87%E6%96%99&SHEET2=%E5%85%AC%E5%8F%B8%E5%9F%BA%E6%9C%AC%E8%B3%87%E6%96%99&RPT_TIME=%E6%9C%80%E6%96%B0%E8%B3%87%E6%96%99"
    dfs_Company_Infomation = GetStockListData(url_Company_Info, headers)
    return dfs_Company_Infomation



#data_path = 'https://mops.twse.com.tw/nas/t21/rotc/t21sc03'
def monthly_report(data_path, year, month):
    
    # 假如是西元，轉成民國
    if year > 1990:
        year -= 1911
    
    url = data_path+'_'+str(year)+'_'+str(month)+'_0.html'
    if year <= 98:
        url = data_path+'_'+str(year)+'_'+str(month)+'.html'
    
    # 偽瀏覽器 (按 F12 ==> Network ==> Header)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
    
    # 下載該年月的網站，並用pandas轉換成 dataframe
    r = requests.get(url, headers=headers)
    r.encoding = 'big5'

    dfs = pd.read_html(StringIO(r.text), encoding='big-5')

    df = pd.concat([df for df in dfs if df.shape[1] <= 11 and df.shape[1] > 5])
    
    if 'levels' in dir(df.columns):
        df.columns = df.columns.get_level_values(1)
    else:
        df = df[list(range(0,10))]
        column_index = df.index[(df[0] == '公司代號')][0]
        df.columns = df.iloc[column_index]
    
    df['當月營收'] = pd.to_numeric(df['當月營收'], 'coerce')
    df = df[~df['當月營收'].isnull()]
    df = df[df['公司代號'] != '合計']
    
    # 偽停頓
    time.sleep(5)

    return df

#==================================================================================+
import datetime
def get_today_date():
    """ 返回 今天日期如 '2020_11_2' ，形態為 str"""
    today = datetime.date.today()
    today.year #會拿到 2020
    today.month #會拿到 11
    today.day # 會拿到 2

    date = str(today.year) + '_' + str(today.month) + '_' + str(today.day)
    return date
#date = get_today_date()

def get_time_now():
    """ 返回 今天日期如 '2020_11_2' ，形態為 str"""
    time_now = datetime.datetime.now() #現在時間
    time_now.hour   #時
    time_now.minute #分
    time_now.second #秒 59
    time_now.microsecond

    timeN = str(time_now.hour) + '_' + str(time_now.minute) + '_' + str(time_now.second)+'_'+str(time_now.microsecond)
    return timeN
#time_now = get_time_now()

#==================================================================================
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def send_gmail(content_text):
    content = MIMEMultipart()  #建立MIMEMultipart物件
    content["subject"] = "MARK 興櫃-智慧選股系統"  #郵件標題
    content["from"] = "duchung.lab@gmail.com"  #寄件者
    content["to"] = "duchungk7@gmail.com" #收件者
    content.attach(MIMEText(content_text))  #郵件內容
    
    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器 587
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login("duchung.lab@gmail.com", "qxahiinbwldvomvu")  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            print("Complete!")
            smtp.quit()
        except Exception as e:
            print("Error message: ", e)
            
#content_text = ""
#with open('./GUI/txt_file/Short_Line.txt', 'r', encoding="utf-8") as file:
#    content_text = file.read().replace('\n', '')
#file.close()
    
#send_gmail(content_text)

#==================================================================================
#函數 包裝 (量增價漲 - 即時爬蟲)
import re
import bs4
import requests
import pandas as pd

"""
說明：
1. 爬取 證券櫃檯買賣中心 盤中 每5分鐘 更新的資訊
2. 找出 盤中 量增 價漲 的股票
3. 預設設定 過濾 條件 找出 最優個股
    #設定 條件 01： 股價上漲 2% 以上
    #設定 條件 02： 股價 小於 50 元

呼叫方法：
    df_choose = choose_vol_up_price_up_realtime(2, 50)

函數回傳：一個 pandas dataframe, 內容含:
    代號	名稱	前日均價	最近成交價	前日量(張)	成交量(張)
"""
def choose_vol_up_price_up_realtime(pricechang_percent, price_range):
    #pricechangpercent > 2
    #price_range < 50 
    # 自己平台的 user-agent, 可打開網頁，按下 F12 取得
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}

    #證券櫃檯買賣中心
    #https://mis.tpex.org.tw/IB140SRT2.aspx  找 GETQ40
    url = "https://mis.tpex.org.tw/Quote.asmx/GETQ40"

    form_data= {"RankingType": "4",
                "ProductType": "01"}

    reponse= requests.post(url,data=form_data)
    soup = bs4.BeautifulSoup(reponse.text,"lxml")

    stock_symbolid = soup.find_all('symbolid') ##代號

    stock_symbolname = soup.find_all('symbolname') #名稱
    
    stock_TradePriceChangPercent = soup.find_all('tradepricechangpercent') #目前漲幅

    stock_preaverage = soup.find_all('preaverage') #前日均價
    
    stock_BuyPrice = soup.find_all('buyprice') #報買價
    
    stock_SellPrice = soup.find_all('sellprice') #報賣價

    stock_tradeprice = soup.find_all('tradeprice') #最近成交價

    stock_prevol = soup.find_all('prevol') #前日量

    stock_tradettlvol = soup.find_all('tradettlvol') #成交量

    # 選出 上漲 的 股票
    dfs = pd.DataFrame(columns=['代號','名稱','目前漲幅','前日均價', '報買價','報賣價', '最近成交價', '前日量(張)', '成交量(張)'])
    for i in range(len(stock_symbolid)):
        stockNumber = re.split(r">|<", str(stock_symbolid[i]))

        stockName = re.split(r">|<", str(stock_symbolname[i]))
        
        TradePrice_ChangPercent = re.split(r">|<", str(stock_TradePriceChangPercent[i]))

        preaverage_price = re.split(r">|<", str(stock_preaverage[i]))
        
        Buy_Price = re.split(r">|<", str(stock_BuyPrice[i]))
        
        Sell_Price = re.split(r">|<", str(stock_SellPrice[i]))

        trade_price = re.split(r">|<", str(stock_tradeprice[i]))

        stockprevol = re.split(r">|<", str(stock_prevol[i]))

        stockTradettl_vol = re.split(r">|<", str(stock_tradettlvol[i]))

        if trade_price[2] !='-' and preaverage_price[2] !='-':
            tradepricechange = float(trade_price[2]) - float(preaverage_price[2])
            tradepricechangpercent = (tradepricechange/float(preaverage_price[2]))*100

            #設定 條件 01： 股價上漲 2% 以上
            #設定 條件 02： 股價 小於 50 元
            if tradepricechangpercent > pricechang_percent and float(trade_price[2]) < price_range:
                dfs.loc[i]=[stockNumber[2], 
                            stockName[2], 
                            TradePrice_ChangPercent[2],
                            float(preaverage_price[2]),
                            float(Buy_Price[2]),
                            float(Sell_Price[2]),
                            float(trade_price[2]), 
                            int(float(stockprevol[2])/1000), 
                            int(float(stockTradettl_vol[2])/1000)]
    return dfs



