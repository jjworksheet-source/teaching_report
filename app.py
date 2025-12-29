import streamlit as st
import pandas as pd
from datetime import datetime

st.title("學生課堂報表處理工具")

# Step 1: 上傳檔案
st.header("步驟 1: 上傳 CSV 檔案")
uploaded_file = st.file_uploader("選擇您的 CSV 檔案", type="csv")

if uploaded_file is not None:
    # 讀取數據，使用 utf-8-sig 處理 BOM，index_col=0 處理索引欄，on_bad_lines='skip' 忽略壞行
    df = pd.read_csv(uploaded_file, encoding='utf-8-sig', index_col=0, on_bad_lines='skip', header=0)
    
    # 清理數據：移除以 '#' 開頭的行（註解行）
    if '學栍姓名' in df.columns:
        df = df[df['學栍姓名'].apply(lambda x: isinstance(x, str) and not x.startswith('#'))]
    
    # 轉換日期格式
    df['上課日期'] = pd.to_datetime(df['上課日期'], errors='coerce')
    
    # 顯示原始數據
    st.subheader("原始數據")
    st.dataframe(df)
    
    # 定義日期範圍（根據報表：2025-12-01 - 2025-12-31）
    start_date = datetime(2025, 12, 1)
    end_date = datetime(2025, 12, 31)
    
    # Step 2: 應用模板1 - 有效資料
    if st.button("應用模板1: 過濾有效資料"):
        st.header("步驟 2: 模板1 - 有效資料結果")
        
        # 過濾條件
        student_attend = ['出席', '遲到']
        teacher_attend = ['出席', '代課']
        
        df_filtered = df[
            (df['學生出席狀況'].isin(student_attend)) &  # 學生出席或遲到
            ((df['老師出席狀況'].isin(teacher_attend)) | df['老師出席狀況'].isna() | (df['老師出席狀況'] == '')) &  # 老師出席、代課或空白
            (df['上課日期'] >= start_date) & (df['上課日期'] <= end_date)  # 日期範圍
        ]
        
        # 顯示過濾後結果
        st.dataframe(df_filtered)
        
        # 儲存中間結果到 session_state
        st.session_state['df_processed'] = df_filtered
        st.success("模板1 已應用！您可以繼續添加模板2或其他步驟。")
    
    # Step 3: 後續模板（待擴展）
    st.header("步驟 3: 應用後續模板（待討論）")
    if 'df_processed' in st.session_state:
        if st.button("應用模板2: [請提供條件細節]"):
            df_next = st.session_state['df_processed']
            # 在這裡添加模板2的過濾邏輯...
            st.dataframe(df_next)
            st.success("模板2 已應用！")
    
    # 最終結果
    if 'df_processed' in st.session_state:
        st.header("最終結果")
        st.dataframe(st.session_state['df_processed'])
        csv = st.session_state['df_processed'].to_csv(index=True).encode('utf-8-sig')
        st.download_button("下載最終 CSV", csv, "final_result.csv", "text/csv")

st.info("如果需要調整讀取參數（如 header=5）或添加更多模板，請提供更多細節。我已使用 header=0，並清理註解行。如果檔案有額外標頭，請嘗試 header=5。")
