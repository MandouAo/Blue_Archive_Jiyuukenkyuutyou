import matplotlib.pyplot as plt
import math

# 座標を計算しながら線を描画する再帰関数
def draw_tree(x, y, angle, length, depth):
    # 深さが0になったら描画をストップ
    if depth == 0:
        return

    # 次の枝の先端の座標を計算
    x_next = x + length * math.cos(math.radians(angle))
    y_next = y + length * math.sin(math.radians(angle))

    # 現在地から次の座標へ線を引く
    # color="black" でモノクロに。lw(線の太さ)は先に行くほど細くする
    plt.plot([x, x_next], [y, y_next], color="black", lw=depth * 0.4)

    # 左右の枝を再帰的に描画（長さは0.75倍、角度は25度ずつ開く）
    draw_tree(x_next, y_next, angle - 25, length * 0.75, depth - 1)
    draw_tree(x_next, y_next, angle + 25, length * 0.75, depth - 1)

# キャンバスのサイズ設定
plt.figure(figsize=(8, 8))

# 根元の座標(0, 0)から、上向き(90度)、長さ10、深さ9で描画スタート
# ※深さ(depth)を10以上にすると緻密になるが、計算量が倍々で増えるため少し時間がかかる
draw_tree(0, 0, 90, 10, 9)

# グラフの縦横比を1:1にして歪まないようにし、軸や枠線を消す
plt.axis('equal')
plt.axis('off')

# bbox_inches='tight', pad_inches=0 を入れると余白を自動でカットする
plt.savefig('fractal_tree_600dpi.png', dpi=600, bbox_inches='tight', pad_inches=0)

# 画面にも表示
plt.show()