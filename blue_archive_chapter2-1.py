import matplotlib.pyplot as plt
import numpy as np

def draw_sierpinski(p1, p2, p3, depth):
    if depth == 0:
        # 深さが0になったら、3つの頂点の座標を使って黒色('black')で塗りつぶす
        plt.fill([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]], color='black')
    else:
        # 3つの辺の中点の座標をそれぞれ計算する
        p12 = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        p23 = ((p2[0] + p3[0]) / 2, (p2[1] + p3[1]) / 2)
        p31 = ((p3[0] + p1[0]) / 2, (p3[1] + p1[1]) / 2)

        # 中点で分割された3つの小さな三角形について、さらに再帰的に描画する
        # (真ん中の逆三角形は描画しないことで「穴」になる)
        draw_sierpinski(p1, p12, p31, depth - 1)
        draw_sierpinski(p12, p2, p23, depth - 1)
        draw_sierpinski(p31, p23, p3, depth - 1)

# --- 描画の初期設定 ---
# 最初の大きな正三角形の頂点を定義 (底辺を長さ1とする)
p1 = (0, 0)
p2 = (1, 0)
# 高さ = 底辺 × (√3 / 2)
p3 = (0.5, np.sqrt(3) / 2)

# 画像のサイズを設定
plt.figure(figsize=(8, 8))

# --- フラクタルの描画 ---
# ここで深さ(depth)を指定する。5〜7くらいがいい。
draw_sierpinski(p1, p2, p3, 5)

# グラフの縦横比を1:1にして歪まないようにし、軸や枠線を消す
plt.axis('equal')
plt.axis('off')

# bbox_inches='tight', pad_inches=0 を入れると余白を自動でカットする
plt.savefig('sierpinski_600dpi.png', dpi=600, bbox_inches='tight', pad_inches=0)

# 画像を表示
plt.show()