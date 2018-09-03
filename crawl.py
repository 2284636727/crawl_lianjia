import requests
import os
import bs4
import json
import time

def get_html(url,recursive_depth = 0):    
    try:
        Headers = {"User-Agent":"****"}
        r = requests.get(url,headers = Headers,timeout=300)
        r.raise_for_status
        r.encoding = ('utr-8')
        return r.text
    except Exception as e:
        print(url)
        print(e)
        recursive_depth += 1              #recursive_depth 错误重新爬最多爬3次
        if recursive_depth <= 3:
            time.sleep(5)
            return get_html(url,recursive_depth)

# 爬取有租房城市的url
city_dict_url = r"https://ajax.api.lianjia.com//config/cityConfig/getConfig?callback=jQuery1111003279487368659484_1535611119395\
                  &type=province&category=1&_=1535611119396"
city_dict_r_text = get_html(city_dict_url,0)
city_dict_json = json.loads(city_dict_r_text[43:-1])
city_dict = {}
for province in city_dict_json["data"].values():
    city_ls = province.keys()
    for city in city_ls:
        if province[city]['url'].find('fang')<0 and province[city]['url'].find('http:')<0:
            city_dict[province[city]['name']] = province[city]['url']+"zufang/"
            
print(city_dict)
'''
{'北京': 'https://bj.lianjia.com/zufang/',
 '上海': 'https://sh.lianjia.com/zufang/',
 '广州': 'https://gz.lianjia.com/zufang/',
......
 '合肥': 'https://hf.lianjia.com/zufang/',
 '郑州': 'https://zz.lianjia.com/zufang/'}
'''

# 创建数据储存文件夹
for city in city_dict.keys():
    if not os.path.exists(r"data\%s\html"%(city)):
        os.mkdir(r"data\%s\html"%(city))
    else:
        print(r"data\%s\html is exists"%(city))
    if not os.path.exists(r"data\%s\xlsx"%(city)):
        os.mkdir(r"data\%s\xlsx"%(city))
    else:
        print(r"data\%s\xlsx is exists"%(city))
    if not os.path.exists(r"data\%s\detail_html"%(city)):
        os.mkdir(r"data\%s\detail_html"%(city))
    else:
        print(r"data\%s\detail_html is exists"%(city))
        
# 爬取大页面
for city,city_url in city_dict.items():
#     city_url = city_dict["北京"]
    city_html = get_html(city_url,0)
    city_soup = bs4.BeautifulSoup(city_html)
    if city_soup.find(class_="list-head clear") is None:
        continue
    city_house_number = int(city_soup.find(class_="list-head clear").h2.span.text)
    if city_house_number > 3000:
        area_url_ls = [city_url[:-8]+i["href"] for i in city_soup.find(class_="option-list").find_all('a') if len(i["href"].split("/"))==4]
        for area_url in area_url_ls:
#             area_url = 'https://bj.lianjia.com/zufang/dongcheng/'
            area_html = get_html(area_url,0)
            area_soup = bs4.BeautifulSoup(area_html)
            area_house_number = int(area_soup.find(class_="list-head clear").h2.span.text)
            if area_house_number == 0:
                continue
            if area_house_number > 3000:
                sub_area_url_ls = [city_url[:-8]+i["href"] for i in area_soup.find(class_="option-list sub-option-list").find_all('a') if i["href"] != area_url[-18:]]
                for sub_area_url in sub_area_url_ls:
#                     sub_area_url = 'https://bj.lianjia.com/zufang/andingmen/'
                    sub_area_html = get_html(sub_area_url,0)
                    sub_area_soup = bs4.BeautifulSoup(sub_area_html)
                    if int(sub_area_soup.find(class_="list-head clear").h2.span.text) == 0:
                        continue
                    for page in range(eval(sub_area_soup.find(class_="page-box house-lst-page-box")["page-data"])['totalPage']):
                        if os.path.exists(r'data\%s\html\%s_%s.txt'%(city,sub_area_url.split('/')[-2],str(page+1))):
                            continue
                        if page!=0:
                            sub_area_html = get_html(sub_area_url+"pg"+str(page+1),0)
                        with open(r'data\%s\html\%s_%s.txt'%(city,sub_area_url.split('/')[-2],str(page+1)),'w',encoding='UTF-8') as f:
                            f.write(sub_area_html)
                        if page%20 == 0:
                            print("%s_%s:%s"%(city,sub_area_url.split('/')[-2],page+1))
                    print("%s_%s:over"%(city,sub_area_url.split('/')[-2]))
#           爬取区域房源<3000页面
            else: 
                for page in range(eval(area_soup.find(class_="page-box house-lst-page-box")["page-data"])['totalPage']):
                    if os.path.exists(r'data\%s\html\%s_%s.txt'%(city,area_url.split('/')[-2],str(page+1))):
                        continue
                    if page!=0:
                        area_html = get_html(area_url+"pg"+str(page+1),0)
                    with open(r'data\%s\html\%s_%s.txt'%(city,area_url.split('/')[-2],str(page+1)),'w',encoding='UTF-8') as f:
                        f.write(area_html)
                    if page%20==0:
                        print("%s_%s:%s"%(city,area_url.split('/')[-2],page+1))
                print("%s_%s:over"%(city,area_url.split('/')[-2]))
#   爬取城市房源小于3000页面
    else:
        for page in range(eval(city_soup.find(class_="page-box house-lst-page-box")["page-data"])['totalPage']):
            if os.path.exists(r'data\%s\html\%s.txt'%(city,str(page+1))):
                continue
            if page!=0:
                city_html = get_html(city_url+"pg"+str(page+1),0)
            with open(r'data\%s\html\%s.txt'%(city,str(page+1)),'w',encoding='UTF-8') as f:
                f.write(city_html)
            if page%20==0:
                print("%s:%s"%(city,page+1))                
        print("%s:over"%city)    
    
    
# 爬取详细信息页面
for city in os.listdir(r"data"):
    if city == 'test.txt':
        continue
    txt_ls = os.listdir(r"data\%s\html"%city)
    txt_len = len(txt_ls)
    pre = [int(txt_len*i/10) for i in range(1,11)]
    count = 0
    for txt in txt_ls:
        with open(r'data\%s\html\%s'%(city,txt),'r',encoding='UTF-8') as f:
            html = f.readlines()
            soup = bs4.BeautifulSoup(("").join(html))
            for overview_soup in soup.find(class_="house-lst").find_all('li'):
                detail_url = overview_soup.find('h2').a['href']
                if os.path.exists(r'data\%s\detail_html\%s_%s.txt'%(city,txt[:-4],detail_url.split("/")[-1][:-5])):
                    continue
                detail_html = get_html(detail_url,0)
                with open(r'data\%s\detail_html\%s_%s.txt'%(city,txt[:-4],detail_url.split("/")[-1][:-5]),'w',encoding='UTF-8') as detail_f:
                    detail_f.write(detail_html)
        count += 1
        if count in pre :
            print('%s:%s'%(city,count/txt_len))    
    
    
    
    
    
    
