import streamlit as st
from PIL import Image
import openpyxl
import easyocr
import re

st.set_page_config(page_title="請求書アプリ", layout="centered")

# ====================== パスワード ======================
PASSWORD = "komuro2026"   # ここは変更してください

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

# ====================== 本体 ======================
st.title("🛢️ ガソリン請求書作成アプリ")
st.caption("iPad・スマホ対応 改善版")

@st.cache_resource
def get_ocr():
    return easyocr.Reader(['ja', 'en'], gpu=False)

reader = get_ocr()

# セッション状態で値を保持
if "tax10" not in st.session_state:
    st.session_state.tax10 = 0
if "keiyu" not in st.session_state:
    st.session_state.keiyu = 0

st.subheader("① 請求書の写真")
camera = st.camera_input("📸 背面カメラで撮影（画面上部のカメラアイコンで切り替え可能）", key="cam")
upload = st.file_uploader("📁 写真を選択（おすすめ）", type=["jpg", "jpeg", "png"])

image = None
if camera:
    image = Image.open(camera)
elif upload:
    image = Image.open(upload)

if image:
    st.image(image, use_column_width=True)

    if st.button("🔍 金額を自動読み取り", type="primary", use_container_width=True):
        with st.spinner("OCR処理中..."):
            text = " ".join(reader.readtext(image, detail=0, width_ths=0.7))

            # 読み取り精度を大幅強化
            tax10_match = re.search(r'10%\s*対象合計[:：]?\s*([0-9,]+)', text) or \
                         re.search(r'税率\s*10%\s*対象[:：]?\s*([0-9,]+)', text) or \
                         re.search(r'税抜金額[:：]?\s*([0-9,]+)', text)
            
            keiyu_match = re.search(r'軽油税合計[:：]?\s*([0-9,]+)', text) or \
                         re.search(r'軽油税[:：]?\s*([0-9,]+)', text)

            st.session_state.tax10 = int(tax10_match.group(1).replace(',', '')) if tax10_match else 0
            st.session_state.keiyu = int(keiyu_match.group(1).replace(',', '')) if keiyu_match else 0

            st.success(f"✅ 10%対象: ¥{st.session_state.tax10:,}円　軽油税: ¥{st.session_state.keiyu:,}円")

    # ====================== 入力フォーム ======================
    st.subheader("② 請求書情報")

    col1, col2 = st.columns(2)
    with col1:
        year = st.number_input("西暦", value=2026)
        month = st.number_input("月", value=3, min_value=1, max_value=12)
        day = st.number_input("日", value=15, min_value=1, max_value=31)
    with col2:
        code = st.text_input("お客様コード", "07359-333200-057")
        work = st.text_input("工事名称", "大熊減容化作業所")

    if st.button("📄 Excelを作成する", type="primary", use_container_width=True):
        try:
            wb = openpyxl.load_workbook("2026  実験　丸磯　大熊減溶化作業所　.xlsx")
            ws = wb["入力シート・貴社控"]

            ws['F5'] = year
            ws['K5'] = month
            ws['N5'] = day
            ws['H8'] = work
            ws['B18'] = "別紙明細の通り"
            ws['O18'] = 10
            ws['Q18'] = "式"
            ws['AI18'] = 1
            ws['AM18'] = st.session_state.tax10
            ws['B20'] = "別紙明細の通り"
            ws['Q20'] = "式"
            ws['AI20'] = 1
            ws['AM20'] = st.session_state.keiyu

            filename = f"請求書_{year}{month:02d}{day:02d}.xlsx"
            wb.save(filename)

            with open(filename, "rb") as f:
                st.download_button("📥 Excelをダウンロード", f, filename, use_container_width=True)
            
            st.success("✅ Excelファイルを作成しました！")
        except Exception as e:
            st.error(f"エラー: {e}")

st.caption("改善版です。OCR精度がまだ低い場合は写真を明るく・まっすぐに撮ってみてください。")
