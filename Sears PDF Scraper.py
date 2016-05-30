# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 12:33:58 2015

@author: lshu0
"""

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
import re
import os,glob

def SearchPDF():
    PDFpath = []
    start_dir="P:/Advertising/AD PLANNING/Weekly Plans/Jump Drive Materials/Sears Circular Ads - Final Release/2015 Released Ads"
    pattern   = "*.pdf"
    for x in os.walk(start_dir):
        PDFpath.extend(glob.glob(os.path.join(x[0],pattern)))    
    return PDFpath
    
def PDF2Text(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    
    text = retstr.getvalue()
    text=text.replace(" ","").replace("\n","")
    return text
    
def OriginalList(text):
    id_pattern=re.compile('#(.*?)[\&\.\"\*\sa-zA-Z$())†+-]',re.S)
    item_ids=re.findall(id_pattern,text)
    item_ids=[item_id if len(item_id)==0 or item_id[-1]!="%" else item_id[:-3] for item_id in item_ids]
    return item_ids
    
def RemoveSpecial(List):
    SpecialList=["7109143","0001051","0054530","0005543","2101175210","0117740413"]
    NewList=[item_id for item_id in List if item_id not in SpecialList]
    return NewList
    
def RemoveShort(List):
    NewList=[item_id for item_id in List if len(item_id)>6]
    return NewList
    
def Comma(List):
    id_list=[]
    for item_id in List:
        if "," not in item_id:
            id_list.append(item_id)
        else:
            id_list+=item_id.split(",")
    return id_list
    
def Pound(List):
    List2=[item_id.strip("#") for item_id in List]
    for item_id in List2:
        if "#" in item_id:
            List2+=item_id.split("#")
            List2.remove(item_id)
    return List2
    
def Slash(List):
    id_list=[]
    for item_id in List:
        if "/" not in item_id:
            id_list.append(item_id)
        else:    
            sub_list=item_id.split("/")
            if len(sub_list[0])<9 and len(sub_list[0])>6:
                id_list.append(sub_list[0])
                length=len(sub_list)
                for i in xrange(1,length):
                    if len(sub_list[i])==4:
                        id_list.append(sub_list[0][:3]+sub_list[i])
                    if len(sub_list[i])>0:
                        id_list.append(sub_list[0][:-len(sub_list[i])]+sub_list[i])

    return id_list
    
def Semicolon(List):
    id_list=[]
    for item_id in List:
        if ";" in item_id:
            List+=item_id.split(";")
        else:
            id_list.append(item_id)
    return id_list

def GetDivItem(List):
    div=[]
    item=[]
    for item_id in List:
        if item_id.isdigit() == True:
            if len(item_id)>8:
                div.append(int(item_id[:3]))
                item.append(str(int(item_id[3:7]))+"*")
                div.append(int(item_id[:3]))
                item.append(str(int(item_id[3:8]))+"*")
            else:
                div.append(int(item_id[:3]))      
                item.append(int(item_id[3:]))     
        else:
            continue
    div_item_list=zip(div,item)
    div_item_list2=list(set(div_item_list))
    return div_item_list2
        
def main():
    os.chdir("P:\Pricing\Special Projects\PDF scraper")
    import shelve
    shelf = shelve.open("PDFList.db")
    if len(shelf)==0:
        pathList=SearchPDF()
        shelf['list']=pathList
        shelf.close()
    else: 
        originList = shelf['list']
        newList=SearchPDF()
        pathList=list(set(newList) - set(originList))
        shelf['list']=newList
        shelf.close()
    import csv
    location="P:/Pricing/Special Projects/PDF scraper/"
    error_log=shelve.open("error.db")
    for path in pathList:
        try:
            Circ_text=PDF2Text(path)
            print path
            List=OriginalList(Circ_text)
            List=Comma(List)
            List=Pound(List)
            List=Pound(List)
            List=RemoveSpecial(List)
            List=RemoveShort(List)
            List=Slash(List)
            List=Semicolon(List)
            List=RemoveShort(List)
            div_item=GetDivItem(List)
            with open(location+path.split("\\")[-1][:-4]+'.csv','wb') as out:
                csv_out=csv.writer(out)
                csv_out.writerow(['div','item'])
                for row in div_item:
                    csv_out.writerow(row)
        except:            
            print "An error occurs while parsing " + path.split("\\")[-1][:-4]+" skip to the next one"
            error_log[path.split("\\")[-1][:-4]]=path.split("\\")[-1][:-4]
    error_log.close()
    
if __name__ == "__main__":
    main() 
