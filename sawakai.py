import streamlit as st
from pptx import Presentation
from io import BytesIO
import pandas as pd
import sawakai_tool as stool
from glob import glob
import datetime
import os
import zipfile
import wget
import io
import base64
from chardet import detect
from glob import glob


st.set_page_config(
    layout="wide"  # wideに設定することで表示幅を広げる
)

group_id=''
group_df = pd.read_csv("./database/group_id.csv")

group_name = st.sidebar.selectbox(
    'グループ名を選択してください',
    group_df['NAME'].to_list(),
)
group_id = group_df[group_df['NAME']==group_name]['ID'].to_list()[0]
st.sidebar.write('グループ名は', group_name, 'です。')
st.sidebar.write('グループIDは', group_id, 'です。')

## 対象の解析回を選択
analysis_number = st.sidebar.multiselect(
    '解析回を選んでください',
    [1,2,3,4,5],[1])

folder = './outputs/documents/*'
files = glob(folder)
datalist = []

analysis_group_dict = {"豊田Gr1":1, "豊田Gr2":2, "豊田Gr3":3, "豊田Gr4":4,"佐賀Gr1":41,"佐賀Gr2":40}

analysis_number_str = '(' + ', '.join(map(str, analysis_number)) + ')'
st.sidebar.write("You selected:", analysis_number_str)

select_users = st.sidebar.radio("ユーザ選択", ("なし","あり"), horizontal=True)
if select_users == "あり":
    user_list = stool.get_user_list(analysis_group=group_id,analysis_number=analysis_number_str)
    ## 対象の解析回を選択
    target_users = st.sidebar.multiselect(
        "対象のユーザを選択してください",
        user_list
    )
    target_users_str = '(' + ', '.join(map(str, target_users)) + ')'

    st.sidebar.write("You selected:", target_users_str)

if st.sidebar.button('V1 茶話会パワポの生成と更新'):
    for analysis_number in analysis_number:
        if select_users == "あり":
            stool.make_sawakai_pdf(group_name,analysis_number,group_id,version=1,user_list=target_users_str)
        else:
            stool.make_sawakai_pdf(group_name,analysis_number,group_id,version=1,user_list="")
    st.rerun()

if st.sidebar.button('v2 茶話会パワポの生成と更新'):
    for analysis_number in analysis_number:
        if select_users == "あり":
            stool.make_sawakai_pdf(group_name,analysis_number,group_id,version=2,user_list=target_users_str)
        else:
            stool.make_sawakai_pdf(group_name,analysis_number,group_id,version=2,user_list="")
    st.rerun()

for f in files:
    filename = f.split('\\')[-1]
    t = os.path.getmtime(f)
    d = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
    datalist.append([filename,d])
pptx_df = pd.DataFrame(data=datalist,columns=['ファイル名','更新日時'])
st.dataframe(pptx_df)

choices = st.multiselect('ダウンロードするファイルを選んでください',pptx_df['ファイル名'].to_list())

##パワーポイントファイルのダウンロード
if st.button('選択したファイルをZIPファイルにします'):
    if not os.path.exists(f'./outputs/zip'):
        os.mkdir(f'./outputs/zip')
    # ZIPファイルを作成
    with zipfile.ZipFile('./outputs/zip/sawakai_tools.zip', 'w') as zipf:
        for pptx_file in choices:
             zipf.write(f'./outputs/documents/{pptx_file}')

    with open("./outputs/zip/sawakai_tools.zip", "rb") as fp:
        btn = st.download_button(
            label="ZIPファイルをダウンロードします",
            data=fp,
            file_name="sawakai_tools.zip",
            mime="application/zip"
        )

st.sidebar.divider()
##フォルダを指定
def folder_selector(folder_path='./verify_result/'):
    foldernames = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
    selected_folder = st.sidebar.selectbox('目検結果のあるフォルダを選択', foldernames)
    return os.path.join(folder_path, selected_folder)

selected_folder = folder_selector()
st.sidebar.write('You selected `%s`' % selected_folder)

if st.sidebar.button('目検結果をアップロードします'):
    csvfiles = glob(f'{selected_folder}/*.csv')
    stool.upload_verification_result(csvfiles)
        