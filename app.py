import streamlit as st
import pandas as pd
from datetime import datetime

st.title("學生課堂報表處理工具")

# Step 1: 上傳檔案
st.header("步驟 1: 上傳 CSV 或 Excel 檔案")
uploaded_file = st.file_uploader("選擇您的檔案", type=["csv", "xlsx"])  # 移除 'xls' 以避免錯誤

if uploaded_file is not None:
    try:
        # 根據檔案類型讀取數據
        file_name = uploaded_file.name.lower()
        if file_name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig', index_col=0, on_bad_lines='skip', header=5)
        elif file_name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, index_col=0, header=5, engine='openpyxl')
        
        # 清理數據：移除以 '#' 開頭的行（如果存在）
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
    
    except ImportError as e:
        st.error(f"讀取檔案時發生錯誤：{str(e)}。請確保環境中安裝了必要的套件（如 openpyxl for .xlsx）。如果檔案是 .xls 格式，請轉換為 .xlsx。")
    except Exception as e:
        st.error(f"發生錯誤：{str(e)}")

st.info("已更新代碼以移除 .xls 支援，並添加錯誤處理。如果您在 Streamlit Cloud 上運行，請在 requirements.txt 中添加 'openpyxl'。對於 .xls 檔案，請先轉換為 .xlsx 格式上傳。如果需要支援 .xls，請在 requirements.txt 添加 'xlrd'。")
