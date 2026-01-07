import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta
import analyzer
import os
import base64
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")

# 実行ファイルのディレクトリを取得
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ページ設定
st.set_page_config(
    page_title="チャットログ分析ダッシュボード",
    page_icon=os.path.join(BASE_DIR, "assets", "icon_dashboard.png"),
    layout="wide"
)

# --- 共通スタイル設定 ---
st.markdown("""
<style>
    /* 8pxグリッド & タイポグラフィ */
    :root {
        --grid-unit: 8px;
        --space-xs: calc(var(--grid-unit) * 1); /* 8px */
        --space-s:  calc(var(--grid-unit) * 2); /* 16px */
        --space-m:  calc(var(--grid-unit) * 3); /* 24px */
        --space-l:  calc(var(--grid-unit) * 4); /* 32px */
    }
    .main {
        background-color: #F8F9FA;
        padding: var(--space-m);
    }
    /* ヘッダー位置調整 */
    .header-container {
        display: flex;
        align-items: center;
        gap: var(--space-s);
        margin-top: var(--space-m);
        margin-bottom: var(--space-s);
    }
    .sidebar-header-container {
        display: flex;
        align-items: center;
        gap: var(--space-xs);
        margin-bottom: var(--space-xs);
    }
    h1 {
        margin: 0 !important;
        font-size: 2rem !important;
        line-height: 1.2 !important;
        color: #1B5E20 !important;
    }
    h2 {
        margin: 0 !important;
        font-size: 1.5rem !important;
        line-height: 1.2 !important;
        color: #1B5E20 !important;
    }
    h3 {
        margin: 0 !important;
        font-size: 1.2rem !important;
        line-height: 1.2 !important;
        color: #1B5E20 !important;
    }
    /* 全てのボタン（ダウンロード、フィルタ等） */
    button[kind="primary"], button[kind="secondary"], .stDownloadButton > button {
        background-color: #2E7D32 !important;
        color: white !important;
        border: 1px solid #1B5E20 !important;
        font-weight: bold !important;
        border-radius: 4px !important;
        padding: var(--space-xs) var(--space-s) !important;
        height: auto !important;
    }
    /* ページネーション表示 */
    .page-info {
        color: #2E7D32;
        font-weight: bold;
        font-size: 1.1em;
        margin: 0 !important;
    }
    /* グラフ等のコンテナ余白 */
    .stPlotlyChart {
        margin-top: var(--space-s);
    }
</style>
""", unsafe_allow_html=True)

# --- ユーティリティ ---
def img_to_html(img_path, width=28):
    try:
        full_path = os.path.join(BASE_DIR, img_path) if not os.path.isabs(img_path) else img_path
        with open(full_path, "rb") as f:
            img_data = f.read()
        img_64 = base64.b64encode(img_data).decode()
        return f'<img src="data:image/png;base64,{img_64}" width="{width}" style="display: block; user-select: none; cursor: pointer;">'
    except Exception as e:
        return f"<!-- Icon Error: {str(e)} -->"

def render_header(level, icon_path, text, icon_size=28, is_sidebar=False):
    container_class = "sidebar-header-container" if is_sidebar else "header-container"
    tag = f"h{level}"
    html = f'''
    <div class="{container_class}">
        {img_to_html(icon_path, icon_size)}
        <{tag}>{text}</{tag}>
    </div>
    '''
    if is_sidebar:
        st.sidebar.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)

# --- サイドバー ---
render_header(2, "assets/icon_settings.png", "設定", 32, is_sidebar=True)
st.sidebar.markdown("---")

# 期間フィルタ (デフォルトを60日間に延長)
today = datetime.now()
start_date_val = today - timedelta(days=60)
end_date_val = today

st.sidebar.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True) # 8pxグリッド調整
render_header(3, "assets/icon_calendar.png", "期間フィルタ", 24, is_sidebar=True)
start_date = st.sidebar.date_input("開始日", start_date_val)
end_date = st.sidebar.date_input("終了日", end_date_val)

apply_filter = st.sidebar.button("フィルタ適用", width='stretch')

st.sidebar.markdown("---")
render_header(3, "assets/icon_export.png", "エクスポート", 24, is_sidebar=True)

# --- メインエリア ---
render_header(1, "assets/icon_dashboard.png", "チャットログ分析ダッシュボード", 48)
st.markdown('<p style="margin-bottom: 24px; color: #666;">仮想ヘルプAI 会話ログ分析</p>', unsafe_allow_html=True)
st.info(f"📍 データソース: 仮想ヘルプデスクチャット (最終更新: {today.strftime('%Y-%m-%d %H:%M')})")

# データの読み込み
@st.cache_data
def get_raw_data():
    return analyzer.load_data("data/sample_chat.csv")

raw_df = get_raw_data()

# フィルタリング
filtered_df = raw_df[
    (raw_df['timestamp'].dt.date >= start_date) & 
    (raw_df['timestamp'].dt.date <= end_date)
].copy()

# データ取得演出 (初回またはフィルタ適用時)
if 'fetched' not in st.session_state or apply_filter:
    progress_bar = st.progress(0)
    status_text = st.empty()
    for i in range(100):
        time.sleep(0.01) # シミュレーション
        progress_bar.progress(i + 1)
        status_text.text(f"データ取得中... {i+1}%")
    status_text.success("データの取得が完了しました")
    time.sleep(0.5)
    status_text.empty()
    progress_bar.empty()
    st.session_state.fetched = True

# --- 分析処理 ---

# キーワード抽出
keywords = analyzer.extract_keywords(filtered_df['message'].tolist())

# カテゴリ分類 (セッション状態に保存して再計算を防ぐ)
if 'classified_df' not in st.session_state or apply_filter:
    with st.spinner("AIによるカテゴリ分類を実行中..."):
        categories = analyzer.classify_category_ai(filtered_df['message'].tolist(), GEMINI_API_KEY)
        filtered_df['category'] = categories
        st.session_state.classified_df = filtered_df
else:
    filtered_df = st.session_state.classified_df

category_counts = analyzer.aggregate_data(filtered_df)

# --- UI レイアウト ---

col1, col2 = st.columns([1, 1])

with col1:
    render_header(3, "assets/icon_keywords.png", "頻出キーワード TOP 10", 28)
    if keywords:
        kw_df = pd.DataFrame(keywords)
        kw_df.columns = ["キーワード", "出現回数", "割合 (%)"]
        st.dataframe(kw_df, width='stretch', hide_index=True)
    else:
        st.write("該当データがありません")

with col2:
    render_header(3, "assets/icon_piechart.png", "カテゴリ別集計", 28)
    if category_counts:
        fig = go.Figure(data=[go.Pie(
            labels=list(category_counts.keys()),
            values=list(category_counts.values()),
            hole=.3,
            marker=dict(colors=['#81C784', '#FFF176', '#E57373', '#64B5F6', '#BA68C8'])
        )])
        fig.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            height=300,
            showlegend=True
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.write("該当データがありません")

st.markdown("---")

# 詳細ログ
render_header(3, "assets/icon_log.png", "詳細ログ表示", 28)
selected_cat = st.selectbox("カテゴリで絞り込み", ["すべて"] + list(category_counts.keys()))

display_df = filtered_df.copy()
if selected_cat != "すべて":
    display_df = display_df[display_df['category'] == selected_cat]

with st.expander("ログ一覧を表示", expanded=True):
    # 分類フィルタ適用後のデータ
    display_df = display_df.sort_values('timestamp', ascending=False)
    
    # --- ページ送り機能 (Pagination) ---
    items_per_page = 20
    total_pages = (len(display_df) - 1) // items_per_page + 1
    
    if 'current_page' not in st.session_state or apply_filter:
        st.session_state.current_page = 1
        
    col_p1, col_p2, col_p3 = st.columns([1, 1, 1])
    
    with col_p1:
        if st.button("＜", key="prev_p", disabled=(st.session_state.current_page <= 1), width='stretch'):
            st.session_state.current_page -= 1
            st.rerun()
            
    with col_p2:
        st.markdown(f"<p class='page-info' style='text-align: center; line-height: 2.5;'>{st.session_state.current_page} / {total_pages}</p>", unsafe_allow_html=True)
        
    with col_p3:
        if st.button("＞", key="next_p", disabled=(st.session_state.current_page >= total_pages), width='stretch'):
            st.session_state.current_page += 1
            st.rerun()

    # ページに応じたスライス
    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    
    st.dataframe(
        display_df.iloc[start_idx:end_idx][['timestamp', 'user_id', 'message', 'category']],
        width='stretch',
        hide_index=True
    )
    
    st.info(f"💡 全 {len(display_df)} 件中 {start_idx + 1} 〜 {min(end_idx, len(display_df))} 件を表示中")

# ダウンロードボタン (サイドバー)
csv = display_df.to_csv(index=False, encoding='utf-8-sig')
st.sidebar.download_button(
    label="CSVダウンロード",
    data=csv,
    file_name=f"chat_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv",
    width='stretch'
)

st.sidebar.markdown(f"**表示件数:** {len(display_df)} 件")
