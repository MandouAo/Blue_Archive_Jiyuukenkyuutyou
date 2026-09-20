# ==========================================
# Googleスプレッドシート（D列のみ）からN-gramを抽出する統合スクリプト
# ==========================================

import spacy
from spacy.cli import download
import pandas as pd
from collections import Counter
from google.colab import auth
from google.colab import files
from google.auth import default
import gspread

# --------------------------------------------------
# 1. spaCyの英語モデルを準備（初回のみ自動ダウンロード）
# --------------------------------------------------
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("英語モデルをダウンロードしています...")
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

nlp.max_length = 2000000


# --------------------------------------------------
# 2. Googleスプレッドシートの認証と読み込み（D列のみ抽出）
# --------------------------------------------------
print("Googleドライブの認証を行っています。ポップアップが出たら許可してください...")
auth.authenticate_user()
creds, _ = default()
gc = gspread.authorize(creds)

SPREADSHEET_NAME = 'ブルアカ英単語'

try:
    worksheet = gc.open(SPREADSHEET_NAME).sheet1
    rows = worksheet.get_all_values()
except Exception as e:
    print(f"エラー: スプレッドシート『{SPREADSHEET_NAME}』が見つからないか、アクセス権限がありません。")
    raise e

# ==========================================
# D列（インデックス[3]）のみを抽出
# ==========================================
text_list = []
for row in rows:
    # 行にD列（4つ目のセル）が存在するか確認してから取得
    if len(row) > 3:
        cell_d = row[3] # A列=0, B列=1, C列=2, D列=3
        if cell_d.strip(): # 空白セルは無視
            text_list.append(cell_d)

my_text = " ".join(text_list)
print(f"D列の読み込み完了！ 総文字数: {len(my_text)}文字")


# --------------------------------------------------
# 3. N-gram抽出関数の定義
# --------------------------------------------------
def export_ngrams_to_csv(text, n=2, output_filename="ngram_list.csv"):
    if not text.strip():
        print(f"エラー: D列に有効なテキストデータがありません。（{n}語の抽出をスキップ）")
        return None

    doc = nlp(text)

    # 記号や空白だけを先に除外（ストップワードは残す）
    tokens = [token for token in doc if not token.is_punct and not token.is_space]

    ngrams = []
    for i in range(len(tokens) - n + 1):
        ngram_tokens = tokens[i:i+n]

        # フィルター：すべてがストップワードなら除外
        if all(t.is_stop for t in ngram_tokens):
            continue

        # フィルター：すべてが代名詞なら除外
        if all(t.pos_ == "PRON" for t in ngram_tokens):
            continue

        # レマ化してスペースで結合
        ngram_string = " ".join([t.lemma_.lower() for t in ngram_tokens])
        ngrams.append(ngram_string)

    # 出現回数をカウント
    ngram_freq = Counter(ngrams)

    # DataFrameに変換して頻度順にソート
    df = pd.DataFrame(ngram_freq.items(), columns=['Phrase', 'Frequency'])
    df = df.sort_values(by='Frequency', ascending=False).reset_index(drop=True)

    # CSVに出力（文字化け防止の utf-8-sig）
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    print(f" {n}語のフレーズリストを作成しました: {output_filename}")

    return df


# --------------------------------------------------
# 4. 解析の実行とCSVファイルの保存
# --------------------------------------------------
print("\n解析を開始します。データ量によっては数分かかります...")

export_ngrams_to_csv(my_text, n=2, output_filename="bigrams_2words.csv")
export_ngrams_to_csv(my_text, n=3, output_filename="trigrams_3words.csv")
export_ngrams_to_csv(my_text, n=4, output_filename="4-gram_4words.csv")

print("\nすべての解析が完了しました！ファイルをダウンロードします...")


# --------------------------------------------------
# 5. ローカルPCへのダウンロード
# --------------------------------------------------
# ファイルが見つからないエラーを防ぐため、try-exceptで囲みます
try:
    files.download("bigrams_2words.csv")
    files.download("trigrams_3words.csv")
    files.download("4-gram_4words.csv")
except Exception as e:
    print("ダウンロード中にエラーが発生しました。ファイルが作成されているか左側のフォルダアイコンから確認してください。")