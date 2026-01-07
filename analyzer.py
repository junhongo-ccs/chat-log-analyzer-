import pandas as pd
from janome.tokenizer import Tokenizer
from collections import Counter
from google import genai
import os
from typing import List, Dict
import streamlit as st
from utils.stopwords import STOPWORDS

# Janome Tokenizer
tokenizer = Tokenizer()

def load_data(file_path: str) -> pd.DataFrame:
    """CSVからデータを読み込み、timestampを日時型に変換する。"""
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def extract_keywords(messages: List[str], top_n: int = 10) -> List[Dict]:
    """メッセージ一覧から名詞・動詞を抽出し、頻度順にランキングを返す。"""
    words = []
    for message in messages:
        tokens = tokenizer.tokenize(message)
        for token in tokens:
            pos = token.part_of_speech.split(',')[0]
            base_form = token.base_form
            if pos in ['名詞', '動詞'] and base_form not in STOPWORDS and len(base_form) > 1:
                words.append(base_form)
    
    counts = Counter(words).most_common(top_n)
    total = sum([c[1] for c in counts]) if counts else 1
    
    return [
        {"keyword": word, "count": count, "percentage": round(count / total * 100, 1)}
        for word, count in counts
    ]

def classify_category_ai(messages: List[str], api_key: str = None) -> List[str]:
    """Gemini APIを使用してメッセージをカテゴリ分類する。"""
    if not api_key:
        return [mock_classify(m) for m in messages]
    
    try:
        client = genai.Client(api_key=api_key)
        
        # 利用可能なモデルを順に試行する
        def try_generate(model_name, prompt):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                return response.text.strip()
            except Exception:
                return None

        results = []
        for msg in messages:
            prompt = f"""
            以下のユーザーメッセージを、下記の5カテゴリのいずれか1つに分類してください。
            カテゴリ名のみを返してください。

            カテゴリ:
            1. 操作方法
            2. 機能の場所
            3. エラー/トラブル
            4. 機能要望
            5. その他

            メッセージ: "{msg}"

            分類結果:
            """
            category = None
            for model_name in ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]:
                category = try_generate(model_name, prompt)
                if category:
                    # 分類が成功したモデルを初回のみ表示（オプション）
                    if 'last_working_model' not in st.session_state:
                         st.session_state.last_working_model = model_name
                         print(f"Working model found: {model_name}")
                    break
            
            if not category:
                results.append(mock_classify(msg))
                continue
            
            # バリデーション
            valid_categories = ["操作方法", "機能の場所", "エラー/トラブル", "機能要望", "その他"]
            if category not in valid_categories:
                found = False
                for valid in valid_categories:
                    if valid in category:
                        results.append(valid)
                        found = True
                        break
                if not found:
                    results.append("その他")
            else:
                results.append(category)
        return results
    except Exception as e:
        st.error(f"Gemini API Error: {e}")
        return [mock_classify(m) for m in messages]

def mock_classify(message: str) -> str:
    """APIキーがない場合、あるいはエラー時のための簡易分類ロジック。"""
    if any(kw in message for kw in ["どこ", "どうやって", "やり方", "教え", "方法"]):
        return "操作方法"
    if any(kw in message for kw in ["ボタン", "メニュー", "場所", "見つからない", "設定"]):
        return "機能の場所"
    if any(kw in message for kw in ["エラー", "できない", "失敗", "真っ白", "接続"]):
        return "エラー/トラブル"
    if any(kw in message for kw in ["欲しい", "追加", "改善", "オフにしたい", "自動保存"]):
        return "機能要望"
    return "その他"

def aggregate_data(df: pd.DataFrame) -> Dict[str, int]:
    """DFに含まれるカテゴリをカウントする。"""
    if 'category' not in df.columns:
        return {}
    return df['category'].value_counts().to_dict()
