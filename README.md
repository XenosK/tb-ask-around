# Taobao ask around

------

## 爬取目标
淘宝商城任意商品详情页 - 累计评论 - 问大家
这些内容都是买家真实的问答数据, 十分有最为语料的价值


## 启动（需设置待爬取类别）
```
scrapy crawl ask
```
## 爬取思路
1. 找到'问大家'api
2. 找到获取具体商品id的api
3. 找到获取获取某一类商品的api


## 爬取过程
### 1.分析问大家页面

通过浏览器调试工具分析请求, 页面调用形如
```
https://api.m.taobao.com/h5/mtop.taobao.ocean.quest.list.pc/1.0/?appKey=12574478&t=1484980011054&sign=67223645e6475e5195a9a1bf027b54cd&api=mtop.taobao.ocean.quest.list.pc&v=1.0&type=jsonp&dataType=jsonp&callback=mtopjsonp2&data=%7B%22itemId%22%3A%22537229921586%22%7D
```
的api来获取问大家内容, 可以发现只有itemId（此商品的id）与此商品有关, 所以为了爬取所有商品, 我们需要一个获取商品id的方法.

还要注意api中sign参数, 可以判断这个api为了防止被篡改加了签名. 所以我们要先分析sign的生成方式.

通过查找本页js文件, 判断生成sign的代码在
```
https://g.alicdn.com/??mtb/lib-promise/3.0.1/polyfillB.js,mtb/lib-mtop/2.0.8/mtop.js
```
中
经过调试分析 api中参数主要有

> * t: 当前时间
> * data: 形如 {"itemid":"xxx"} 的url编码
> * appKey: 12574478 不会变
> * sign: 为当前cookie的一部分和上面参数组合成的字符串的MD5值 md5("cookie&t&appkey&data")
所以现在只要有获取到商品id的方法, 就能获取到问答数据




### 2.分析获取商品id方法
通过测试淘宝的搜索系统
整理分析得到
```
首页:https://s.taobao.com/search?data-key=cat&data-value={{cat_id}}&ajax=true&sort=sale-desc

翻页: https://s.taobao.com/search?data-key=s&data-value={{page_nums}}&ajax=true&cat={{cat_id}}&sort=sale-desc
```
(还有一种https://s.taobao.com/list?.....的api）
cat_id就代表商品类别的id, cat_id为空时就得到所有类别, 通过这个api， 可以得到淘宝所有商品的分类、分类下的商品以及子分类。
所以选取所需的分类, 就能得到此分类下所有商品的问答数据.


## 问题
1.由于sign有时间限制, 10分钟左右, 所以不能让解析商品id的请求堆积太多, 影响获取评论的请求, 导致请求大范围失效.

解决方法: 不集中解析商品id, '翻页'是每次只翻一页

2.子类别和其父类别得到的商品可能相同.

解决办法: 使用bloomfilter去重, 本项目使用了https://github.com/jaybaird/python-bloomfilter
