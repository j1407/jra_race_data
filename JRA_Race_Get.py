# -*- coding: utf-8 -*-
import urllib.request
import codecs
import time
from datetime import datetime as dt
from collections import Counter
from bs4 import BeautifulSoup
import pandas
import re
import csv

yea = 2018
mon = 13
'''
    2019,01,22現在のYahoo競馬のフォーマットには対応しているが、今後変更されるかもしれないのでそこは注意
    また、プログラムは正しいが途中で止まることがあるが、それはネットワークの回線が遅いからなので、混線しないように注意
    一部障害レースの右回り、左回りの記述に機械文字が混入しているが、そこは後で取り除く必要あり
'''
for month in range(mon, mon+1):
    cal_html=urllib.request.urlopen("http://keiba.yahoo.co.jp/schedule/list/"+str(yea)+"/?month="+str(month))
    cal_soup = BeautifulSoup(cal_html,"lxml")
    
    for atag in cal_soup.find_all("a",href=re.compile("/race/list/.*$")):
        race_src=atag.get("href")
        race_src=re.sub(r"/$","",race_src)
        race_src=re.sub(r"list","result",race_src)
        for race_no in range(1,13):
            race="http://keiba.yahoo.co.jp"+str(race_src)+str(race_no).rjust(2,"0")
            try:
                race_html=urllib.request.urlopen(race)
            except urllib.error.HTTPError:
                print("何かしらのエラーが発生しています(当日が12Rまでない可能性ならOK)")
                continue
            race_soup=BeautifulSoup(race_html,"lxml")
            # 日付の取得
            race_date=race_soup.find_all("h4")
            race_date=re.sub(r"<[^>]*?>","",str(race_date))
            race_date=re.sub(r"[年月]","/",str(race_date))
            race_date=re.sub(r"[\[\]]","",str(race_date))
            race_date=re.sub(r"日.*$","",str(race_date))
            race_date=dt.strptime(race_date,"%Y/%m/%d")
            race_date=re.sub(" 00:00:00","",str(race_date))
            #print(race_date)
                
            # 競馬場名の取得
            race_course_num=race_src[15:17]
            if race_course_num == "01":
                race_course="札幌"
            elif race_course_num == "02":
                race_course="函館"
            elif race_course_num == "03":
                race_course="福島"
            elif race_course_num == "04":
                race_course="新潟"
            elif race_course_num == "05":
                race_course="東京"
            elif race_course_num == "06":
                race_course="中山"
            elif race_course_num == "07":
                race_course="中京"
            elif race_course_num == "08":
                race_course="京都"
            elif race_course_num == "09":
                race_course="阪神"
            elif race_course_num == "10":
                race_course="小倉"
            #print(race_course)
            #print(race_no)
            # レース番号はrace_no
                        
            # レース名の取得
            race_name=race_soup.find_all("h1",class_="fntB")
            race_name=re.sub(r"<[^>]*?>","",str(race_name))
            race_name=re.sub(r"[ \n\[\]]","",str(race_name))
            # 大阪―ハンブルグカップ対策
            race_name=re.sub(r"[—―]","-",str(race_name))
            # 19XX-19XXsダービーメモリーズ対策
            race_name=re.sub(r"〜","-",str(race_name))
            # 重賞の回次を削除
            race_name=re.sub(r"第.*?回","",str(race_name))
            print(race_date, race_course, race_no, race_name)
                        
            # コース区分・距離の取得
            race_info=race_soup.find_all("p",class_="fntSS gryB",attrs={'id':'raceTitMeta'})
            track=re.sub(r"\n","",str(race_info))
            track=re.sub(r" \[.*","",str(track))
            track=re.sub(r"[\[m]","",str(track))
            track=re.sub("・外","",str(track))
            track=re.sub("・内","",str(track))
            track=re.sub(r"・"," ",str(track))
            track=re.sub(r" ",",",str(track))
            track=re.sub(r"<[^>]*?>","",str(track))
            track = track.split(',')
            track = [track[0],track[1],track[2],track[8],track[10]]
            track=re.sub(r"'","",str(track))
            track=re.sub(r", ",",",str(track))
            track=re.sub(r"[\[\]]","",str(track))
            #print(track)
            
            # 馬場状態の取得
            cond=race_soup.find_all("img",attrs={'width':'25'})
            cond=re.sub(r"\[<img alt=\"","",str(cond))
            cond=re.sub(r"\" border.*$","",str(cond))
            #print(cond)
                                                
            # 賞金額の取得
            prize=re.sub(r".*本賞金：","",str(race_info))
            prize=re.sub(r"\n","",prize)
            prize=re.sub(r"、.*","",prize)
            prize=int(prize)
            #print(prize)
                                                
            # 出走馬の取得
            horses=race_soup.find_all("a",href=re.compile("/directory/horse"))
            horses=re.sub(r"<[^>]*?>","",str(horses))
            horses=re.sub(r"[\[\]]","",str(horses))
            horses=horses.split(", ")
            horses_num=len(horses)
            # 馬情報の取得
            horse_info_all=race_soup.find_all("table",attrs={'id':'raceScore'})
            for elem in horse_info_all:
                horse_info=elem.find_all("td")
                # 降着用
                horse_info=re.sub(r"<span>\([0-9]{1,2}\)</span>",",",str(horse_info))
                horse_info=re.sub(r"<[^>]*?>",",",str(horse_info))
                horse_info=re.sub("\(",", ",str(horse_info))
                horse_info=re.sub("\)",", ",str(horse_info))
                horse_info=re.sub("\+",",",str(horse_info))
                horse_info=re.sub("[☆★△▲]",",",str(horse_info))
                horse_info=re.sub(r"[\[\]]",",",str(horse_info))
                horse_info=re.sub(r"\n",",",str(horse_info))
                horse_info=re.sub(r"/"," ",str(horse_info))
                horse_info=horse_info.split(",")
                horse_info=[x.strip() for x in horse_info]
                horse_info=[x for x in horse_info if x]
                horse_info=[x for x in horse_info if x!='B']
                horse_info=[x for x in horse_info if (('馬身'not in x )and('アタマ'!= x)and('クビ'!= x)and('ハナ'!= x)and('大差'!= x))]
                i=0
                j=14
                if str(track[2]+track[3]) == "直線": # 芝の時のみ
                    j=13
                out=codecs.open("./"+str(yea)+"/jra_race_result_"+str(yea)+"_"+str(mon).rjust(2,"0")+".csv","a","utf-8")
                for num in range(1,horses_num+1):
                    each_horse=horse_info[i:j]
                    if each_horse[0]=="中止" or each_horse[0]=="取消" or each_horse[0]=="除外" or each_horse[0]=="失格":
                        this_result=99
                        continue
                    else:
                        this_result=int(each_horse[0])
                    each_horse[0] = str(this_result)
                    # タイムの秒換算
                    counter=Counter(str(each_horse[6]))
                    if counter['.'] == 0:
                        horse_time=""
                        horse_time_sec=""
                    else:
                        if counter['.'] == 1:
                            horse_time_orig=re.sub(r"$","0",str(each_horse[6]))
                            horse_time=dt.strptime(horse_time_orig,"%S.%f")
                            horse_time_sec=(horse_time.second+(horse_time.microsecond/1000000))
                        else:
                            horse_time_orig=re.sub(r"^|$","0",str(each_horse[6]))
                            horse_time=dt.strptime(horse_time_orig,"%M.%S.%f")
                            horse_time_sec=(horse_time.minute*60)+horse_time.second+(horse_time.microsecond/1000000)
                    
                    each_horse[6]=horse_time_sec
                    # 性別と馬齢と馬体重の分離
                    sex=re.sub(r"[0-9]","",str(each_horse[4]))
                    sex=re.sub(r"せん","セ",str(sex))
                    age_wei=re.sub(r"[牡牝せん]","",str(each_horse[4]))
                    sexs=[x for x in sex if x]
                    sex = sexs[0]
                    age_wei = age_wei.split(" ")
                    each_horse[4]=sex
                    each_horse.insert(5,age_wei[0])
                    each_horse.insert(6,age_wei[1])
                    if str(track[2]+track[3]) == "直線":
                        each_horse.insert(9,"-")
                    each_horse=re.sub(r"'","",str(each_horse))
                    each_horse=re.sub(r", ",",",str(each_horse))
                    each_horse=re.sub(r"[\[\]]","",str(each_horse))
                        
                    out.write(str(race_date)+","+race_course+","+str(race_no).rjust(2,"0")+","+race_name+","+track+","+cond+","+str(horses_num)+","+each_horse+"\n")
                    #print(str(race_date)+","+race_course+","+str(race_no).rjust(2,"0")+","+race_name+","+track+","+cond+","+str(horses_num)+","+each_horse)
                    i=i+14
                    j=j+14
                    if str(track[2]+track[3]) == "直線":
                        i -= 1
                        j -= 1

                out.close()
