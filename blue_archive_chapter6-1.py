# 1. 必要なライブラリのインポートと準備
from google.colab import auth
from google.auth import default
from google.colab import files
import gspread
import spacy
import pandas as pd
from collections import Counter

# spaCyの軽量英語モデルをロード
nlp = spacy.load("en_core_web_sm")

# --------------------------------------------------
# 設定値（必要に応じてここを変更）
# --------------------------------------------------
FILENAME = "ブルアカ英単語"
SHEET_NAME = "シート1"
COL_NUMBER = 4  # 列番号（1始まり）

# 2. Googleアカウントの認証（スプレッドシートにアクセスするため）
print("Googleアカウントの認証を行います。表示されるポップアップの指示に従ってください。")
auth.authenticate_user()
creds, _ = default()
gc = gspread.authorize(creds)

# 3. スプレッドシートを開く
wb = gc.open(FILENAME)
worksheet = wb.worksheet(SHEET_NAME)

# 4. データの取得
print("スプレッドシートからデータを取得中...")
col_d_values = worksheet.col_values(COL_NUMBER)[1:]

print(f"取得完了: 合計 {len(col_d_values)} 行のテキストを処理します。")

# 5. コーパス言語学に基づく解析処理
words = []

for sentence in col_d_values:
    # 空白行はスキップ
    if not sentence.strip():
        continue

    doc = nlp(sentence)

    for token in doc:
        # ストップワード、記号、改行/空白、数字を除外
        if token.is_stop or token.is_punct or token.is_space or token.like_num:
            continue

        # レマ化（原形に変換）し、小文字に統一
        lemma = token.lemma_.lower()

        # アルファベット1文字だけの単語（a, i など）は除外してリストに追加
        if len(lemma) > 1:
            words.append(lemma)

# 6. 集計とデータフレーム化
print("単語の集計と割合の計算中...")
word_freq = Counter(words)

# 表形式に変換し、頻度順（降順）にソート
df = pd.DataFrame(word_freq.items(), columns=['Lemma', 'Frequency'])
df = df.sort_values(by='Frequency', ascending=False).reset_index(drop=True)

# 総単語数を取得して、割合（%）と累積割合（%）を計算
total_words = df['Frequency'].sum()
df['Percentage (%)'] = (df['Frequency'] / total_words * 100).round(4)
df['Cumulative Percentage (%)'] = df['Percentage (%)'].cumsum().round(4)

# 7. CSV出力とダウンロード
output_filename = "vocab_from_spreadsheet_with_ratio.csv"
df.to_csv(output_filename, index=False, encoding='utf-8-sig')

print("\n=== 解析完了！ 上位10件の単語 ===")
print(df.head(10).to_string())
print("=================================")

print(f"\n総抽出単語数: {total_words} 語")
print("ローカルPCにCSVファイルをダウンロードします...")
files.download(output_filename)