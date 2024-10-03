import streamlit as st
from pptx import Presentation
from io import BytesIO
import pandas as pd
import sawakai_tool as stool
from glob import glob
import datetime
import os
import zipfile

group_id=''
group_df = pd.read_csv("./database/group_id.csv")

group_name = st.selectbox(
    'グループ名を選択してください',
    group_df['NAME'].to_list(),
)
group_id = group_df[group_df['NAME']==group_name]['ID'].to_list()[0]
st.write('グループ名は', group_name, 'です。')
st.write('グループIDは', group_id, 'です。')

analysis_numbers = st.multiselect(
    '解析回を選んでください',
    [1,2,3,4,5],)

folder = './outputs/documents/*'
files = glob(folder)
datalist = []

for f in files:
    #group_name = f.split('\\')[-1].split('_')[-3]
    #filename = f"{f.split('_')[-2]}_{f.split('_')[-1]}"
    filename = f.split('\\')[-1]
    t = os.path.getmtime(f)
    d = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
    datalist.append([filename,d])
pptx_df = pd.DataFrame(data=datalist,columns=['ファイル名','更新日時'])
st.dataframe(pptx_df)

if st.button('パワーポイントファイルを生成と更新'):
    for analysis_number in analysis_numbers:
        stool.make_sawakai_pdf(group_name,analysis_number,group_id)

choices = st.multiselect('ダウンロードするファイルを選んでください',pptx_df['ファイル名'].to_list())

##パワーポイントファイルのダウンロード
if st.button('ファイルをZIPファイルにします'):
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
    #prs = Presentation("./outputs/documents/井上友睦会_4回目.pptx")
    #bio = BytesIO()
    #prs.save(bio)
    #pptx_bio = bio
    #pptx_bio.seek(0)
    #st.download_button(label='ダウンロード', 
    #                       data=pptx_bio, 
    #                       file_name='井上友睦会_4回目.pptx', 
    #                       mime='application/vnd.openxmlformats-officedocument.presentationml.presentation'
    #                       )
