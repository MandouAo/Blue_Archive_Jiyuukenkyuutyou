import unicodedata

# 調べたい顔文字をリストに追加
kaomoji_list = [
    "（|　|:|　|）",
    "ᓀ‸ᓂ",
    "꒰𑁬(⸝⸝ↀᯅↀ⸝⸝)໒꒱",
    "囧",
    "(눈_눈)",
    "(◠ڼ◠)",
    "꒰ঌ⎛ಲළ൭⎞໒꒱"
]

# リスト内の顔文字を順番にループ処理
for idx, kaomoji in enumerate(kaomoji_list, 1):
    print(f"\n========================================")
    print(f"【顔文字 {idx}】 {kaomoji}")
    print(f"========================================")
    print(f"{'文字':<4} | {'Unicode':<10} | {'文字名'}")
    print("-" * 60)

    # 顔文字を1文字ずつ分解して解析
    for char in kaomoji:
        code_point = f"U+{ord(char):04X}"
        name = unicodedata.name(char, "UNKNOWN")
        print(f"{char:<4} | {code_point:<10} | {name}")