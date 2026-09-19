# 環境構築
!apt install -y fonts-noto-cjk
!mkdir -p images

import re
import hashlib
from collections import defaultdict, Counter
from itertools import combinations
from typing import List, Dict, Any

# サードパーティ・Google関連
import gspread
from google.colab import auth
from google.auth import default
from graphviz import Digraph
from IPython.display import Image, display

# --------------------------------------------------
# 1. 設定値
# --------------------------------------------------
FILENAME = "ブルアカ生徒名前"
SHEET_NAME = "シート1"
COL_NUMBER = 1  # 列番号（1始まり）
IMAGE_DIR = "./images"

# --------------------------------------------------
# 2. データ取得・集計関数
# --------------------------------------------------
def fetch_base_data_from_sheet(filename: str, sheet_name: str, col_num: int) -> List[str]:
    auth.authenticate_user()
    creds, _ = default()
    gc = gspread.authorize(creds)
    ws = gc.open(filename).worksheet(sheet_name)
    names = [str(val).strip() for val in ws.col_values(col_num)[1:] if str(val).strip()]
    return names

def extract_frequent_patterns(names: List[str], mode: str, min_freq: int = 2) -> List[tuple[Any, int]]:
    freq = defaultdict(int)

    if mode == "SINGLE_CHAR":
        for name in names:
            for char in set(name):
                freq[char] += 1
    else:
        for name in names:
            indexed_chars = list(enumerate(name))
            pairs = combinations(indexed_chars, 2)
            results = set()
            for (i1, c1), (i2, c2) in pairs:
                gap = i2 - i1 - 1
                results.add((c1, gap, c2))
            for res in results:
                freq[res] += 1

    filtered_data = {k: v for k, v in freq.items() if v >= min_freq}
    return sorted(filtered_data.items(), key=lambda x: x[1], reverse=True)

def get_matched_names(col: List[str], pattern_data: Any, mode: str) -> List[str]:
    matched = []
    if mode == "SINGLE_CHAR":
        matched = [name for name in col if pattern_data in name]
    else:
        c1, gap, c2 = pattern_data
        for name in col:
            match_found = False
            for i in range(len(name) - gap - 1):
                if name[i] == c1 and name[i + gap + 1] == c2:
                    match_found = True
                    break
            if match_found:
                matched.append(name)

    return sorted(matched)

# --------------------------------------------------
# 3. データのグループ化・結合関数
# --------------------------------------------------
def transform_data(data: List[Dict[str, Any]], mode: str) -> List[Dict[str, Any]]:
    result = []

    if mode == "SINGLE_CHAR":
        for item in data:
            sorted_names = sorted(item['example'])
            result.append({
                'merged_members': sorted_names,
                'title': [f"{item['pattern']}：{'・'.join(sorted_names)}"]
            })
    else:
        groups = []
        for i, item in enumerate(data):
            members = set(item['example'])

            matched_groups = [
                g for g in groups
                if g['members'] == members or members.issubset(g['members']) or g['members'].issubset(members)
            ]

            if not matched_groups:
                groups.append({'members': members, 'indices': [i]})
            else:
                target = matched_groups[0]
                target['members'].update(members)
                target['indices'].append(i)

        for group in groups:
            merged_members = sorted(list(group['members']))
            titles = []

            for idx in sorted(group['indices']):
                item = data[idx]
                titles.append(f"{item['pattern']}")

            titles.sort()
            joined_titles = f"{', '.join(titles)}：{'・'.join(merged_members)}"

            result.append({
                'merged_members': merged_members,
                'title': [joined_titles]
            })

    result.sort(key=lambda x: x['title'][0])
    return result

def print_statistics(integration_names: List[Dict[str, Any]]) -> None:
    print("\n■ 完成形の配列一覧（画像番号とその中身）")
    for i, item in enumerate(integration_names):
        print(f"【画像番号: {i}】")
        print(f"  タイトル(パターン) : {', '.join(item['title'])}")
        print(f"  統合された名前     : {', '.join(item['merged_members'])}")
    print("-" * 40)

    name_counter = Counter()
    for item in integration_names:
        name_counter.update(item.get("merged_members", []))

    print(f"\n■ 画像生成数: {len(integration_names)}枚")
    print(f"■ 名前の種類数（重複なし）: {len(name_counter)}種類\n")

# --------------------------------------------------
# 4. 画像描画・オフセット計算関数
# --------------------------------------------------
def calculate_optimal_offsets(members: List[str]) -> Dict[str, int]:
    if not members:
        return {}

    offsets = {members[0]: 0}
    unresolved = set(members[1:])

    while unresolved:
        best_new_member, best_base_member = None, None
        best_offset_diff, max_match_global = -1, -1

        for target in unresolved:
            for base in offsets.keys():
                best_offset, max_match = 0, -1

                for shift in range(-len(target), len(base) + 1):
                    match_count = sum(
                        1 for idx, char in enumerate(target)
                        if 0 <= idx + shift < len(base) and base[idx + shift] == char
                    )

                    if match_count > max_match:
                        max_match = match_count
                        best_offset = shift

                if max_match > max_match_global:
                    max_match_global = max_match
                    best_new_member = target
                    best_base_member = base
                    best_offset_diff = best_offset

        offsets[best_new_member] = offsets[best_base_member] + best_offset_diff
        unresolved.remove(best_new_member)

    return offsets

def generate_and_display_graph(item: Dict[str, Any], output_dir: str = IMAGE_DIR) -> None:
    members = item["merged_members"]
    if not members:
        return

    display_name = '\n'.join(item["title"])

    pattern_chars = [t.split('：')[0].replace('.', '_') for t in item["title"]]
    safe_name = "_".join(pattern_chars[:3]) + ("_他" if len(pattern_chars) > 3 else "")
    hash_suffix = hashlib.md5("".join(members).encode()).hexdigest()[:6]
    unique_filename = f"Graph_{safe_name}_{hash_suffix}"

    dot = Digraph(
        name=unique_filename,
        directory=output_dir,
        format='png',
        graph_attr={'rankdir': 'LR'},
        node_attr={'fontname': 'Noto Serif CJK JP'},
        edge_attr={'fontname': 'Noto Serif CJK JP'},
        strict=True
    )
    dot.attr(label=display_name, labeljust="c", labelloc="b", splines="spline", fontsize="25", dpi="350", fontname="Noto Serif CJK JP")

    offsets = calculate_optimal_offsets(members)
    for m in members:
        offset = offsets[m]
        indexed_chars = [f"R_{idx + offset}_{char}" for idx, char in enumerate(m)]

        for prev_node, curr_node in zip(indexed_chars, indexed_chars[1:]):
            dot.node(prev_node, prev_node.split('_')[-1])
            dot.node(curr_node, curr_node.split('_')[-1])
            dot.edge(prev_node, curr_node)

    display(Image(dot.render()))

# --------------------------------------------------
# 5. メイン処理
# --------------------------------------------------
def main():
    run_modes = [
        {"id": "SINGLE_CHAR", "label": "【モード1】2文字専用（1文字の共通項抽出）"},
        {"id": "GAP_PATTERN", "label": "【モード2】全体（文字間の距離パターン抽出）"}
    ]

    print("■ データを取得しています...")
    base_col = fetch_base_data_from_sheet(FILENAME, SHEET_NAME, COL_NUMBER)
    print("■ 取得完了！\n")

    for mode_info in run_modes:
        mode_id = mode_info["id"]
        mode_label = mode_info["label"]

        print("=" * 60)
        print(f"■ 分析開始: {mode_label}")
        print("=" * 60)

        col = [n for n in base_col if len(n) == 2] if mode_id == "SINGLE_CHAR" else base_col
        sorted_patterns = extract_frequent_patterns(col, mode_id, min_freq=2)

        extraction_names_list = []
        for pattern_data, _ in sorted_patterns:
            matched_names = get_matched_names(col, pattern_data, mode_id)

            if mode_id == "GAP_PATTERN":
                c1, gap, c2 = pattern_data
                display_title = f"{c1}{'.' * gap}{c2}"
            else:
                display_title = str(pattern_data)

            extraction_names_list.append({"pattern": display_title, "example": matched_names})

        integration_names = transform_data(extraction_names_list, mode_id)
        print_statistics(integration_names)

        print("\n■ 画像の生成を開始します...")
        for item in integration_names:
            generate_and_display_graph(item)

        print(f"■ {mode_label} の処理完了。\n")

if __name__ == "__main__":
    main()