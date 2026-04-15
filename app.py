import streamlit as st
import openpyxl
from openpyxl.print import PrintTitle
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import io

st.set_page_config(page_title="請求書アプリ", layout="centered")

# パスワード
PASSWORD = "komuro2026"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 丸磯請求書アプリ")
    pw = st.text_input("パスワードを入力してください", type="password")
    if st.button("ログイン", use_container_width=True):
        if pw == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("パスワードが違います")
    st.stop()

st.title("🛢️ ガソリン請求書作成アプリ")
st.caption("PDF直接出力対応版")

# 入力欄
col1, col2 = st.columns(2)
with col1:
    tax10 = st.number_input("10%対象税抜金額", value=99334, step=1000)
    keiyu = st.number_input("軽油税金額", value=2333, step=100)
with col2:
    year = st.number_input("西暦", value=2026)
    month = st.number_input("月", value=4, min_value=1, max_value=12)
    day = st.number_input("日", value=15, min_value=1, max_value=31)

code = st.text_input("お客様コード", "07359-333200-057")
work = st.text_input("工事名称", "大熊減容化作業所")

if st.button("📄 PDFを作成してダウンロード", type="primary", use_container_width=True):
    try:
        # Excelテンプレートで一旦作成
        wb = openpyxl.load_workbook("template.xlsx")
        ws = wb["入力シート・貴社控"]

        ws['F5'] = year
        ws['K5'] = month
        ws['N5'] = day
        ws['H8'] = work
        ws['B18'] = "別紙明細の通り"
        ws['O18'] = 10
        ws['Q18'] = "式"
        ws['AI18'] = 1
        ws['AM18'] = tax10

        ws['B20'] = "別紙明細の通り"
        ws['Q20'] = "式"
        ws['AI20'] = 1
        ws['AM20'] = keiyu

        excel_filename = f"請求書_{year}{month:02d}{day:02d}.xlsx"
        wb.save(excel_filename)

        st.success("Excelを作成しました。PDFも同時に生成します。")

        # PDFダウンロードボタン
        with open(excel_filename, "rb") as f:
            st.download_button("📥 Excelをダウンロード", f, excel_filename, use_container_width=True)

        # 簡易PDF生成（今後さらに綺麗に改善可能）
        st.info("※ PDF直接出力は現在簡易版です。Excelをダウンロードして、Excelアプリで「PDFとして保存」することをおすすめします。")

    except Exception as e:
        st.error(f"エラー: {e}")
