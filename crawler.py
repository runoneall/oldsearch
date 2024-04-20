import requests
import json
from bs4 import BeautifulSoup

def Get_Links(query_str:str):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3877.400 QQBrowser/10.8.4507.400'
    }
    url = 'https://cn.bing.com/search?'+query_str
    response = requests.get(url, headers=headers, stream=True)
    web_content = bytes()
    for chunk in response.iter_content(chunk_size=2*1024):
        if chunk:
            web_content+=bytes(chunk)
    web_content = web_content.decode('utf-8')
    soup_results = BeautifulSoup(web_content, 'html.parser')

    ol_tag = soup_results.find('ol', {'id': 'b_results'})
    li_tags = ol_tag.find_all('li', {'class': 'b_algo'})

    html = str()
    info_dict = dict()
    for li_tag in li_tags:
        div = li_tag.find('div', {'class': 'tpic'})
        if div:
            div.decompose()
        html += str(li_tag)+'\n'
        one_result = BeautifulSoup(str(li_tag), 'html.parser')

        # Get Title
        h_h2 = one_result.find('h2')
        h_a = h_h2.find('a')
        site_title = h_a.text
        info_dict[site_title] = dict()

        # Get Full URL and Domain
        h_div = one_result.find('div', {'class': 'b_tpcn'})
        h_a = h_div.find('a', {'class': 'tilk'})
        info_dict[site_title]['full_url'] = h_a.get('href')
        h_div = h_a.find('div', {'class': 'tptxt'})
        h_div = h_div.find('div', {'class': 'tptt'})
        info_dict[site_title]['domain'] = h_div.text

        # Get Site Introduce
        h_div = one_result.find('div', {'class': 'b_caption'})
        h_p = h_div.find('p', {'class': 'b_algoSlug'})
        info_dict[site_title]['info'] = h_p.text[2:]
    return info_dict

def GetMaxPage(query_str:str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    }
    url = 'https://cn.bing.com/search?'+query_str
    response = requests.get(url, headers=headers)
    soup_results = BeautifulSoup(response.text, 'html.parser')

    ol_tag = soup_results.find('ol', {'id': 'b_results'})
    li_tag = ol_tag.find('li', {'class': 'b_pag'})
    h_nav = li_tag.find('nav', {'role':'navigation'})
    h_ul = h_nav.find('ul', {'class': 'sb_pagF'})
    li_tags = h_ul.find_all('li')
    max_li = str(li_tags[-2])
    soup_maxli = BeautifulSoup(max_li, 'html.parser')
    h_a = soup_maxli.find('a')
    max_page = int(h_a.get('aria-label')[2])
    return max_page
