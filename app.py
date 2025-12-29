import streamlit as st
import pandas as pd
from datetime import datetime, time

st.title("學生課堂報表處理工具")

# Step 1: 上傳檔案
st.header("步驟 1: 上傳 CSV 或 Excel 檔案")
st.info("提示：如果使用 .xls 檔案，請考慮轉換為 .xlsx 以避免相容性問題。")
uploaded_file = st.file_uploader("選擇您的檔案", type=["csv", "xls", "xlsx"])

if uploaded_file is not None:
    try:
        # 根據檔案類型讀取數據
        file_name = uploaded_file.name.lower()
        if file_name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig', index_col=0, on_bad_lines='skip', header=0)  # 修正為 header=0 針對 CSV
        elif file_name.endswith(('.xls', '.xlsx')):
            engine = 'xlrd' if file_name.endswith('.xls') else 'openpyxl'
            df = pd.read_excel(uploaded_file, index_col=0, header=5, engine=engine)  # 保持 header=5 針對 Excel
        else:
            raise ValueError("不支援的檔案類型。請上傳 CSV、XLS 或 XLSX 檔案。")
        
        # 修正欄位名稱（從 '學栍姓名' 改為 '學生姓名'）
        if '學栍姓名' in df.columns:
            df = df.rename(columns={'學栍姓名': '學生姓名'})
        
        # 清理數據：移除以 '#' 開頭的行（如果存在）
        if '學生姓名' in df.columns:
            df = df[df['學生姓名'].apply(lambda x: isinstance(x, str) and not x.startswith('#'))]
        
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
            st.success("模板1 已應用！您可以繼續應用模板2。")
        
        # Step 3: 應用模板2 - 群組班級樞紐表
        st.header("步驟 3: 應用後續模板")
        if 'df_processed' in st.session_state:
            if st.button("應用模板2: 群組班級樞紐表"):
                df_next = st.session_state['df_processed']
                
                # 定義唯一班級的群組鍵
                group_keys = ['分校', '老師', '上課日期', '時間', '星期', '年級', '班別']
                
                # 群組並聚合數據
                def aggregate_group(group):
                    # 欄位A: 老師 (取第一個，假設一致)
                    teacher = group['老師'].iloc[0]
                    
                    # 欄位B: 分校 (取第一個)
                    branch = group['分校'].iloc[0]
                    
                    # 欄位C: concat 老師/上課日期/時間/星期/年級/班別
                    concat_str = f"{teacher}/{group['上課日期'].iloc[0].date()}/{group['時間'].iloc[0]}/{group['星期'].iloc[0]}/{group['年級'].iloc[0]}/{group['班別'].iloc[0]}"
                    
                    # 欄位D: duration - 解析時間為時間1 (開始) 和時間2 (結束)
                    time_str = group['時間'].iloc[0]
                    if '-' in time_str:
                        start_time_str, end_time_str = time_str.split('-')
                        time1 = datetime.strptime(start_time_str.strip(), '%H:%M').time()
                        time2 = datetime.strptime(end_time_str.strip(), '%H:%M').time()
                        duration = f"{time1.strftime('%H:%M')} - {time2.strftime('%H:%M')}"
                    else:
                        duration = time_str  # 如果格式異常，保留原值
                    
                    # 欄位E: total hour - 計算小時差
                    if '-' in time_str:
                        start_dt = datetime.strptime(start_time_str.strip(), '%H:%M')
                        end_dt = datetime.strptime(end_time_str.strip(), '%H:%M')
                        total_hours = (end_dt - start_dt).total_seconds() / 3600
                    else:
                        total_hours = 0.0
                    
                    # 欄位F: 所有學栍姓名 (唯一並以逗號分隔)
                    students = ', '.join(group['學栍姓名'].unique())  # 更新為修正後的欄位名
                    
                    return pd.Series({
                        '老師': teacher,
                        '分校': branch,
                        'Concat': concat_str,
                        'Duration': duration,
                        'Total Hours': total_hours,
                        'Students': students
                    })
                
                # 應用群組聚合
                df_grouped = df_next.groupby(group_keys).apply(aggregate_group).reset_index(drop=True)
                
                # 顯示結果
                st.header("步驟 3: 模板2 - 群組班級結果")
                st.dataframe(df_grouped)
                
                # 更新 session_state 以供後續使用
                st.session_state['df_processed'] = df_grouped
                st.success("模板2 已應用！已群組為唯一班級，並計算持續時間與總小時。")
        
        # 最終結果
        if 'df_processed' in st.session_state:
            st.header("最終結果")
            st.dataframe(st.session_state['df_processed'])
            csv = st.session_state['df_processed'].to_csv(index=True).encode('utf-8-sig')
            st.download_button("下載最終 CSV", csv, "final_result.csv", "text/csv")
    
    except ImportError as e:
        st.error(f"缺少必要套件：{str(e)}。請嘗試將 Python 版本設為 3.12（在應用程式設定中），或將檔案轉換為 .xlsx。檢查應用程式日誌以獲取更多細節。")
    except ValueError as ve:
        st.error(str(ve))
    except Exception as e:
        st.error(f"發生錯誤：{str(e)}。如果檔案是 .xls，請確保 Python 版本相容，或轉換為 .xlsx。")
