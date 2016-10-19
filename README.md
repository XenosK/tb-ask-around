# Taobao ask around

------



> * 种子 url
> * 评论 API sign
> * request 


## 种子url
通过搜索页面找到获取商品API
```
https://s.taobao.com/search?data-key=s&data-value=44&ajax=true&_ksTS=1476860811722_789&callback=jsonp790&q=df&style=grid&seller_type=taobao&spm=a219r.lm874.1000187.1&cps=yes&cat=50340020&bcoffset=4&p4ppushleft=1%2C48
```
整理分析得到
```
首页:https://s.taobao.com/search?data-key=cat&data-value={{cat_id}}&ajax=true&sort=sale-desc

翻页: https://s.taobao.com/search?data-key=s&data-value={{page_nums}}&ajax=true&cat={{cat_id}}&sort=sale-desc
```
(还有一种https://s.taobao.com/list?.....的api没试）

通过这个api， 可以得到淘宝所有商品的分类名称，分类id(cat_id),
通过cat_id，还能得到下一级的cat_id，
同时包含当前cat_id的商品信息。

## 评论 API sign

评论API
```
https://api.m.taobao.com/h5/mtop.taobao.ocean.quest.detail.pc/1.0/?appKey=12574478
&t=1476861603779
&sign=0acf3452c3cb265a1b14a702155abafe
&api=mtop.taobao.ocean.quest.detail.pc
&v=1.0
&type=jsonp
&dataType=jsonp
&callback=mtopjsonp5
&data=%7B%22topicId%22%3A%224144631166%22%7D
```
通过分析js文件
https://g.alicdn.com/??mtb/lib-promise/3.0.1/polyfillB.js,mtb/lib-mtop/2.0.8/mtop.js

主要参数有：
> * t: 当前时间
> * data: 形如 {"itemid":"xxx"} 的url编码
> * appKey: 12574478不会变
> * sign: 为当前cookie的一部分和上面参数组合成的字符串的MD5值 md5("cookie&t&appkey&data")


 
## request
由于 sign 有时间限制，所以获取商品信息时，每次只生成一次下一页，获取评论时，也只请求一次下一页，控制request数量。

## 爬取过程


