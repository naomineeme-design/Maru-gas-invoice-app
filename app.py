import streamlit as st
import openpyxl
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import datetime

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
st.caption("iPad対応・PDF直接出力版")

st.subheader("① 金額入力")
col1, col2 = st.columns(2)
with col1:
    tax10 = st.number_input("10%対象税抜金額", value=99334, step=1000)
with col2:
    keiyu = st.number_input("軽油税金額", value=2333, step=100)

st.subheader("② 請求書情報")
col_a, col_b = st.columns(2)
with col_a:
    year = st.number_input("西暦", value=2026)
    month = st.number_input("月", value=4, min_value=1, max_value=12)
    day = st.number_input("日", value=15, min_value=1, max_value=31)
with col_b:
    code = st.text_input("お客様コード", "07359-333200-057")
    work = st.text_input("工事名称", "大熊減容化作業所")

if st.button("📄 PDFを作成してダウンロード", type="primary", use_container_width=True):
    # PDFをメモリ上で作成
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # シンプルな請求書レイアウト
    c.setFont("Helvetica", 16)
    c.drawString(20*mm, height - 30*mm, "請　求　書")

    c.setFont("Helvetica", 12)
    c.drawString(20*mm, height - 50*mm, f"請求日: {year}年 {month}月 {day}日")
    c.drawString(20*mm, height - 65*mm, f"工事名称: {work}")
    c.drawString(20*mm, height - 80*mm, f"お客様コード: {code}")

    c.setFont("Helvetica", 14)
    c.drawString(20*mm, height - 110*mm, "別紙明細の通り")

    c.setFont("Helvetica", 12)
    c.drawString(20*mm, height - 140*mm, f"10%対象税抜金額: ¥{tax10:,}")
    c.drawString(20*mm, height - 160*mm, f"軽油税　　　　　: ¥{keiyu:,}")
    c.drawString(20*mm, height - 180*mm, f"請求金額（税込）: ¥{int(tax10 * 1.1 + keiyu):,}")

    c.save()
    buffer.seek(0)

    st.success("✅ PDFを作成しました！")
    st.download_button(
        label="📥 PDFをダウンロード",
        data=buffer,
        file_name=f"請求書_{year}{month:02d}{day:02d}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

st.info("このPDFは簡易版です。将来的にレイアウトをより請求書らしく改善できます。")
