import os
import numpy as np
from PIL import Image
import scipy.ndimage as ndi
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

os.makedirs('output', exist_ok=True)

# -------------------------------------------------------------
# 1. AI 繪製圖片的假棋盤格消除器 (轉換為 100% 真透明 PNG)
# -------------------------------------------------------------
def clean_ai_checkerboard():
    input_path = '/Users/vincentlu/.gemini/antigravity/brain/834979bb-201c-41e8-985e-5d1d3f23d8e8/.user_uploaded/media_1790219905259.jpg'
    if not os.path.exists(input_path):
        return

    img = Image.open(input_path).convert('RGBA')
    arr = np.array(img, dtype=np.float32)
    
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    gray = (r + g + b) / 3.0
    
    # 灰階棋盤格特徵：R ≈ G ≈ B，且亮度介於 50 ~ 208
    is_neutral = (np.abs(r - g) < 25) & (np.abs(g - b) < 25) & (np.abs(r - b) < 25)
    checker = is_neutral & (gray <= 208.0)
    
    # 前景白色文字與線條：亮度 > 208
    fg = gray > 208.0
    fg_clean = ndi.binary_opening(fg, structure=np.ones((2, 2)))
    
    dist = ndi.distance_transform_edt(fg_clean)
    alpha = np.clip(dist * 255.0, 0.0, 255.0).astype(np.uint8)
    
    result = np.zeros_like(arr, dtype=np.uint8)
    result[:, :, 0] = 255
    result[:, :, 1] = 255
    result[:, :, 2] = 255
    result[:, :, 3] = alpha
    
    out_img = Image.fromarray(result)
    out_path = 'output/高雄116總預算_折線圖_AI修復真透明.png'
    out_img.save(out_path, format='PNG')
    print("Saved:", out_path)

# -------------------------------------------------------------
# 2. 高清向量渲染 (完整 17 年官方數據版 & 嚴格對齊版)
# -------------------------------------------------------------
def render_vector_chart(upper_include_116=True, filename='output/高雄116總預算_折線圖_高清向量純透明.png'):
    years = [f"{y}" for y in range(100, 116)] + ["116年"]
    x = np.arange(len(years))
    
    if upper_include_116:
        # 官方數據 100~116 年 (116年為 1,929.10 億)
        upper_vals = [1433, 1403, 1361, 1331, 1269, 1239, 1324, 1329, 1372, 1506, 1521, 1515, 1609, 1696, 1937, 1978, 1929.10]
    else:
        # 完全對齊 AI 生成截圖的 16 個點
        upper_vals = [1433, 1403, 1361, 1331, 1269, 1239, 1324, 1329, 1372, 1506, 1521, 1515, 1609, 1698, 1937, 1978]
        
    lower_vals = [150, 161, 135, 120, 115, 73.46, 73.09, 69.02, 65.46, 64.20, 62.09, 58.94, 57.92, 56.90, 52.00, 48.58, 47.64]

    font_path = '/System/Library/Fonts/Hiragino Sans GB.ttc'
    if not os.path.exists(font_path):
        font_path = '/System/Library/Fonts/STHeiti Light.ttc'
    prop = fm.FontProperties(fname=font_path)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(19.2, 10.8), dpi=100, sharex=True, 
                                   gridspec_kw={'height_ratios': [1.2, 1.0], 'hspace': 0.14})
    fig.patch.set_alpha(0.0)

    for ax in (ax1, ax2):
        ax.patch.set_alpha(0.0)
        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)
        ax.spines['left'].set_color('white')
        ax.spines['left'].set_linewidth(3.5)
        ax.spines['bottom'].set_color('white')
        ax.spines['bottom'].set_linewidth(3.5)
        ax.tick_params(axis='both', colors='white', labelsize=18, width=2.5, length=6)

    # 上半部折線 (1,200 ~ 2,050)
    x_upper = x[:len(upper_vals)]
    ax1.plot(x_upper, upper_vals, color='white', linewidth=4.5, marker='o', markersize=14, 
             markerfacecolor='white', markeredgecolor='white', zorder=5)
    for xi, yi in zip(x_upper, upper_vals):
        val_str = f"{yi:,}" if isinstance(yi, int) else f"{yi:,.2f}"
        ax1.annotate(val_str, (xi, yi), textcoords="offset points", xytext=(0, 16),
                     ha='center', fontsize=18, fontweight='bold', color='white', fontproperties=prop)

    ax1.set_ylim(1100, 2180)
    ax1.set_yticks([1400, 1600, 1800, 2000])
    ax1.set_yticklabels(['1,400', '1,600', '1,800', '2,000'], fontproperties=prop, fontsize=20, fontweight='bold')
    ax1.spines['bottom'].set_visible(False)
    ax1.tick_params(bottom=False)

    # 下半部折線 (0 ~ 190)
    ax2.plot(x, lower_vals, color='white', linewidth=4.5, marker='o', markersize=14, 
             markerfacecolor='white', markeredgecolor='white', zorder=5)
    for xi, yi in zip(x, lower_vals):
        val_str = f"{yi}" if yi == int(yi) else f"{yi:.2f}"
        ax2.annotate(val_str, (xi, yi), textcoords="offset points", xytext=(0, 15),
                     ha='center', fontsize=17, fontweight='bold', color='white', fontproperties=prop)

    ax2.set_ylim(0, 195)
    ax2.set_yticks([0, 70, 100, 150, 166])
    ax2.set_yticklabels(['0', '70', '100', '150', '166'], fontproperties=prop, fontsize=19, fontweight='bold')

    ax2.set_xticks(x)
    ax2.set_xticklabels(years, fontproperties=prop, fontsize=20, fontweight='bold')

    # Y 軸折斷符號 (Zigzag break)
    d = 0.015
    kwargs = dict(transform=ax1.transAxes, color='white', clip_on=False, linewidth=3.5)
    ax1.plot((-d, +d), (-d, +d), **kwargs)
    ax1.plot((-d, +d), (-d - 0.03, +d - 0.03), **kwargs)

    kwargs.update(transform=ax2.transAxes)
    ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)
    ax2.plot((-d, +d), (1 - d + 0.03, 1 + d + 0.03), **kwargs)

    plt.subplots_adjust(left=0.08, right=0.96, top=0.92, bottom=0.10)
    plt.savefig(filename, transparent=True, dpi=100)
    plt.close()
    print("Saved:", filename)

if __name__ == '__main__':
    clean_ai_checkerboard()
    render_vector_chart(upper_include_116=True, filename='output/高雄116總預算_折線圖_高清向量純透明.png')
