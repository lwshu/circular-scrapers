# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 11:24:24 2015

@author: lshu0
"""

import urllib2
import re
import csv
from bs4 import BeautifulSoup
from time import strptime
import os, datetime

def LoadHTML():
    init_url="http://local.kmart.com/Chicago-IL-60618/#!/weeklyad/"
    init_request = urllib2.Request(init_url)
    init_response = urllib2.urlopen(init_request)
    html=init_response.read()
    return html


def SearchFeaturedCircular(html):
    nd_pattern=re.compile('<span class="week-title">This.*?Ad:</span>(.*?)</h3>.*?data-start="(.*?)" data-end="(.*?)"',re.S )
    circ_nd=re.findall(nd_pattern,html)
    #circ_nm=circ_nd[0][0].strip()
    soup=BeautifulSoup(html,"lxml")
    circ_tag=soup.find_all("img",class_="featuredCircular")
    circ_id=circ_tag[0]['data-activityid']
    dt_start='-'.join([circ_nd[0][1].split()[5], str(strptime(circ_nd[0][1].split()[1],'%b').tm_mon), circ_nd[0][1].split()[2]])
    dt_end='-'.join([circ_nd[0][2].split()[5], str(strptime(circ_nd[0][2].split()[1],'%b').tm_mon), circ_nd[0][2].split()[2]])
    return [[circ_id,dt_start,dt_end]]
    
def SearchSecondaryCircular(html):
    nd_pattern=re.compile('<div class="secondaryCircular">.*?<div class="circularDescription">\s*<h3>(.*?)</h3>.*?data-start="(.*?)" data-end="(.*?)"',re.S )
    circ_nd=re.findall(nd_pattern,html)
    soup=BeautifulSoup(html,"lxml")
    circ_tags=soup.find_all("img",class_="circularCover")
    length=len(circ_tags)
    circ_list=[]
    for i in xrange(length):
        #circ_nm=circ_nd[i][0].strip()
        dt_start='-'.join([circ_nd[i][1].split()[5], str(strptime(circ_nd[i][1].split()[1],'%b').tm_mon), circ_nd[i][1].split()[2]])
        dt_end='-'.join([circ_nd[i][2].split()[5], str(strptime(circ_nd[i][2].split()[1],'%b').tm_mon), circ_nd[i][2].split()[2]])
        circ_id=circ_tags[i]['data-activityid']
        circ_list.append([circ_id,dt_start,dt_end])
    return circ_list
    

def CircularScrape(circ_id,storeId=10151,unitNumber=3371):
    circ_url="http://local.kmart.com/getPages?storeId={1}&unitNumber={2}&actId={0}".format(circ_id,storeId,unitNumber)
    circ_request = urllib2.Request(circ_url)
    circ_response = urllib2.urlopen(circ_request)
    circ_html=circ_response.read()
    item_pattern=re.compile('{"ksn":.*?"prdId":"(.*?)","prdName":"(.*?)".*?}',re.S)
    items=re.findall(item_pattern,circ_html)
    return items
    
def CreateList(items,circ_id,dt_start,dt_end):
    circ_tbls=[]
    for item in items:
        data={"circ_ID":circ_id,"dt_start":dt_start,"dt_end":dt_end,"item_id":item[0],"item_nm":item[1]}
        circ_tbls.append(data)
    return circ_tbls

def main():
    os.chdir("P:\Pricing\Special Projects\web scraper")
    newdir = os.path.join(os.getcwd(), datetime.datetime.now().strftime('%Y-%m-%d'))
    if not os.path.exists(newdir):
        os.makedirs(newdir)
    os.chdir(newdir)
    init_html=LoadHTML()
    circ_list=SearchFeaturedCircular(init_html)+SearchSecondaryCircular(init_html)
    print "No. of circular found: "+str(len(circ_list))
    for circInfo in circ_list:
        print "Scraping circular #"+str(circInfo[0])+".............."
        items=CircularScrape(circInfo[0])
        circ_tbls=CreateList(items,circInfo[0],circInfo[1],circInfo[2])
        circ_keys=['circ_ID','dt_start','dt_end','item_id','item_nm']
        with open("kmart-"+str(circInfo[0])+".csv","wb") as output_file:
            dict_writer = csv.DictWriter(output_file,circ_keys)
            dict_writer.writeheader()
            dict_writer.writerows(circ_tbls)
    print "Finished! Please check folder "+ datetime.datetime.now().strftime('%Y-%m-%d')
    os.chdir("..")
     
if __name__ == "__main__":
    main() 