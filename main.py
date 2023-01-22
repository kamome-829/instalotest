import streamlit as st
import numpy as np
import pandas as pd
import instaloader
import schedule
from time import sleep
from datetime import datetime,date
from datetime import timedelta
import os

from dotenv import load_dotenv
load_dotenv()


###################################ここからグローバル変数宣言############################


#ログテーブル配列変数宣言
YuserName = []
GrantPoint = []
LikeAcount = []
Timestamp = []
if 'YuserName' not in st.session_state:
  st.session_state["YuserName"] = []

if 'GrantPoint' not in st.session_state:
  st.session_state["GrantPoint"] = []

if 'TotalPoint' not in st.session_state:
  st.session_state["TotalPoint"] = []

if 'LikeAcount' not in st.session_state:
  st.session_state["LikeAcount"] = []

if 'PostContent' not in st.session_state:
  st.session_state["PostContent"] = []

if 'Timestamp' not in st.session_state:
  st.session_state["Timestamp"] = []

#ユーザー記録変数
if 'UserMemory' not in st.session_state:
  st.session_state["UserMemory"] = []

#ユーザーポイント数記録変数
if 'UserPoint' not in st.session_state:
  st.session_state["UserPoint"] = []

#付与ポイント係数
LIKEPOINT = 1
SEARPOINT = 3

#企業投稿配列
PushGrant = []
#前日分
if 'PushGrantAgo' not in st.session_state:
  st.session_state["PushGrantAgo"] = 0

#追加投稿件数
addcount = 0 

#フォロワー保存
FollowerUser = []

#いいねしたアカウント保存定義
LikeUser = []

#インスタ企業取得データ
profile = ""
posts = ""

#IDとpasswordを定義
INSTAGRAM_ID = os.getenv('INSTAGRAM_ID')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')
id = "kamomebot11"

#企業投稿カウント変数(常時監視変数)宣言
GrantCountTest = 0
MaxCountTest = 0
if 'MaxCountTest' not in st.session_state:
  st.session_state["MaxCountTest"] = 0

# 現在時間の取得
nowtime = []
# 何時まで実行するか定義
setlimit = []

###################################ここから処理実行############################

#Instagramにログインする(初期設定)
if 'insta' not in st.session_state:
  st.session_state["insta"] = 0
  loader = instaloader.Instaloader()
  #loader.login(INSTAGRAM_ID, INSTAGRAM_PASSWORD)
  profile = instaloader.Profile.from_username(loader.context, id)
  posts = profile.get_posts()
  GrantCountset = posts.count
  st.session_state["MaxCountTest"] = GrantCountset
  st.write(st.session_state["MaxCountTest"])


#00初期設定関数(メイン)
def stertf():
    global MaxCountTest
    profile = instaloader.Profile.from_username(loader.context, id)
    posts = profile.get_posts()
    GrantCountset = posts.count
    MaxCountTest = GrantCountset
    st.write(GrantCountset)
    
    #i = iter(posts)
    #post = next(i)
    #post = next(i)
    #for user in post.get_likes():
    #    st.write(user.username)
    
    #02 スケジュール登録
    schedule.every().days.at("00:00").do(task)


#投稿数の取得
def Grantcount():
    global posts
    global profile
    loader = instaloader.Instaloader()
    loader.login(INSTAGRAM_ID, INSTAGRAM_PASSWORD)
    profile = instaloader.Profile.from_username(loader.context, id)
    posts = profile.get_posts()
    GrantCountset = posts.count
    return GrantCountset
    

#企業が投稿したか監視関数
def Grantcheck(GrantCount):
    if st.session_state["MaxCountTest"] < GrantCount:
        #differenceは差分
        difference = GrantCount - st.session_state["MaxCountTest"]
        st.session_state["MaxCountTest"] = GrantCount
        return difference
    else:
        return 0


#フォロワーの監視関数
def Getfollowers():
    global FollowerUser
    global profile
    for user in profile.get_followers():
        FollowerUser.append(user.username)
    #st.write(FollowerUser)


#01 定期実行する関数を準備(メイン)
def task():
    #タスク１投稿監視
    GrantCount = Grantcount()
    #タスク２フォロワー監視
    Getfollowers()
    #投稿が追加されてたら実行
    pushcount = Grantcheck(GrantCount)
    getlikeuser(pushcount)
    if pushcount != 0:
        #st.write("投稿")
        #st.write(st.session_state["MaxCountTest"])
        settime(pushcount)


#ライク取得期間タイマーセット
def settime(pushcount):
    global addcount
    global posts
    #posts = profile.get_posts()
    addcount = posts.count


#いいねしたユーザー取得関数
def getlikeuser(pushcount):
    global LikeUser
    global posts
    global id
    i = iter(posts)
    turn = st.session_state["PushGrantAgo"] + pushcount
    for push in range(turn):
        post = next(i)
        for user in post.get_likes():
            LikeUser.append(user.username)
            for follower in FollowerUser:
                if follower == user.username and doubleblock(post):
                    st.session_state["YuserName"].append(user.username)
                    st.session_state["GrantPoint"].append(pointapp(1))
                    st.session_state["TotalPoint"].append(pointcalculation(pointapp(1),user.username))
                    st.session_state["LikeAcount"].append(id)
                    st.session_state["PostContent"].append(post)
                    st.session_state["Timestamp"].append(datetime.now())
            #st.write(user.username)
        #st.write(post)
    st.session_state["PushGrantAgo"] = pushcount
    #st.write(LikeUser)


#ポイントのダブル取得防止関数
def doubleblock(post):
    for PostContent in st.session_state["PostContent"]:
        if PostContent == post:
            return False
    return True
    

#ポイント加算関数
def pointapp(mode):
    if mode == 1:
        return LIKEPOINT
    if mode == 2:
        return SEARPOINT


#合ポイント数計算関数
def pointcalculation(additionpoint,username):
    indexcount = 0
    st.write(username)
    for user in st.session_state["UserMemory"]:
        if user == username:
            st.session_state["UserPoint"][indexcount] = st.session_state["UserPoint"][indexcount] + additionpoint
            st.write(st.session_state["UserPoint"][indexcount])
            return st.session_state["UserPoint"][indexcount]
        indexcount = indexcount + 1
    st.write(st.session_state["UserMemory"])
    st.session_state["UserPoint"].append(additionpoint)
    st.session_state["UserMemory"].append(username) 
    return additionpoint
    


def test():
    st.session_state["insta"] += 1
    task()


#03 イベント定時実行
#while True:
#    schedule.run_pending()
#    sleep(1)

############################ここからフロント記述#######################
st.title("Tips")

st.write("SNS投稿を広告以上の拡散力へ")
  
if st.button("0時になったよ!"):
    test()

st.write("ログテーブル")
df = pd.DataFrame({
    'ユーザー名':st.session_state["YuserName"],
    '付与ポイント数':st.session_state["GrantPoint"],
    '総合ポイント数':st.session_state["TotalPoint"],
    'like先アカウント':st.session_state["LikeAcount"],
    '投稿ID':st.session_state["PostContent"],
    'タイムスタンプ':st.session_state["Timestamp"]
})
st.write("", df)