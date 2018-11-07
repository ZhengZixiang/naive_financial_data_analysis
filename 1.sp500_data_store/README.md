## 1. 金融数据获取
首先需要使用sql文件夹里的sql文件创建相关数据库表。文件夹下放了三个demo。

#### 一、标普500股票爬虫
使用BeautifulSoup将维基百科页面中的标普500指数所含股票信息爬取下来，并用mysqlclient将信息存到数据库表symbol中。代码在`insert_symbols.py`中实现。

#### 二、价格信息爬取
从雅虎金融爬取标普500所含股票的历史每日交易信息，并存到数据库daily_price表中。其中`price_retrieval.py`实现数据获取，`retrieving_data.py`测试能否从数据库中正常读取。

这些数据可以通过pandas-datareader这一python库获取，这里自己实现了相关代码，不如pandas-datareader高效。主要原因是由于雅虎金融页面技术及反爬虫技术升级，要求访问历史每日数据时需要客户端的crumble和cookie，因此每请求一支股票数据都要刷新crumble和cookie信息。此外一次请求可能失败，具体原因不明，因此需要设置一个attempts=10作为每支股票的重复请求循环，直到请求成功。

#### 三、Quandl期货数据获取
通过Quandl的最新API，获取特定年份和月份的期货数据信息并保存到本地，由于API变化，技术细节请详见代码`quandl_data.py`。