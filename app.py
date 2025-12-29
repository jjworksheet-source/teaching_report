import streamlit as st
import pandas as pd
from io import StringIO

# 模擬Excel內容（用戶提供的<DOCUMENT>內容，實際上傳到GitHub後，可替換為上傳檔案或讀取本地檔案）
# 這裡使用StringIO讀取文本作為TSV（tab分隔）
data_text = """
學栍姓名	學生編號	分校	年級	學生備註	班別	上課日期	星期	時間	學生出席狀況	補堂	備註	老師	老師出席狀況	課室	學校	家長電話	家長電郵	單堂收費	欠數總額	發票日期	發票編號	發票銀碼	收據編號	收據銀碼	狀態	第一堂上課日期	最後上課日期	報讀情況

林雋佑	NPCNPC010571	WCC	P2	b我愛二s軒灣o	pp 博智	2025-04-23	三	16:00-17:30	病假	至: hp 進階寫作 初級 2025-12-08(一)@16:30-18:00		Ms Lilian le	出席	NPC-Live (線上課)	_軒灣_軒尼詩道官立小學 (灣仔)	98660870	Wong.wingnga@gmail.com	400.0	0.0	2025-03-31	INV-NPC-007555_b	4,125.0	R-NP-006268	4,125.0	舊生	2024-04-17	2026-07-29	補堂

# ... (這裡省略完整內容，實際代碼中請貼上用戶提供的全部數據文本)
# 注意：如果數據太長，可將其存為本地'tsv'檔案，並使用pd.read_csv('data.tsv', sep='\t')讀取
"""

st.title("學生課堂報表處理工具")

# Step 1: 載入數據
st.header("步驟 1: 載入原始數據")
df = pd.read_csv(StringIO(data_text), sep='\t', encoding='utf-8', on_bad_lines='skip')  # 使用tab分隔讀取，忽略壞行
df['上課日期'] = pd.to_datetime(df['上課日期'], errors='coerce')  # 轉換日期格式

# 顯示原始數據
st.dataframe(df)

# 定義日期範圍（根據B4: 2025-12-01 - 2025-12-31）
start_date = pd.to_datetime('2025-12-01')
end_date = pd.to_datetime('2025-12-31')

# Step 2: 應用模板1 - 有效資料
if st.button("應用模板1: 過濾有效資料"):
    st.header("步驟 2: 模板1 - 有效資料結果")
    
    # 過濾條件
    # 學生出席狀況: 出席 或 遲到
    student_attend = ['出席', '遲到']
    
    # 老師出席狀況: 出席, 代課, 或空白 (包括NaN或空字串)
    teacher_attend = ['出席', '代課']
    df_filtered = df[
        (df['學生出席狀況'].isin(student_attend)) &  # 學生出席
        ((df['老師出席狀況'].isin(teacher_attend)) | df['老師出席狀況'].isna() | (df['老師出席狀況'] == '')) &  # 老師出席或空白
        (df['上課日期'] >= start_date) & (df['上課日期'] <= end_date)  # 日期範圍
    ]
    
    # 顯示過濾後結果
    st.dataframe(df_filtered)
    
    # 儲存中間結果到session_state，以便後續模板使用
    st.session_state['df_processed'] = df_filtered
    st.success("模板1 已應用！您可以繼續添加模板2或其他步驟。")

# Step 3: 後續模板（範例，待討論template 2）
# 這裡預留空間，您可以告訴我template 2的細節，我再添加
st.header("步驟 3: 應用後續模板（待擴展）")
if 'df_processed' in st.session_state:
    if st.button("應用模板2: [請描述條件]"):
        # 例如：過濾其他條件
        df_next = st.session_state['df_processed']  # 從上一步取出
        # ... 添加template 2邏輯 ...
        st.dataframe(df_next)
        st.success("模板2 已應用！")

# 最終結果
if 'df_processed' in st.session_state:
    st.header("最終結果")
    st.dataframe(st.session_state['df_processed'])
    st.download_button("下載最終CSV", st.session_state['df_processed'].to_csv(index=False), "final_result.csv")

st.info("如果需要添加更多模板或修改條件，請提供細節。我會更新代碼。")
