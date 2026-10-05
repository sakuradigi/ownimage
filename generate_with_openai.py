#!/usr/bin/env python3
"""
OpenAI GPT Image 2.5 官方高質感施政圖卡生成腳本
使用方式：
  python3 generate_with_openai.py --topic "從賽馬場到晶圓廠" --count 2
"""

import os
import sys
import argparse
import base64
import urllib.request
import datetime
import openai

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load .env
env_file = os.path.join(WORKSPACE_DIR, ".env")
if os.path.exists(env_file):
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("OPENAI_API_KEY="):
                os.environ["OPENAI_API_KEY"] = line.strip().split("=", 1)[1]

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("❌ 找不到 OPENAI_API_KEY，請確認 .env 設定。")
    sys.exit(1)

client = openai.OpenAI(api_key=api_key)

def generate_slide(topic, subtitle, main_title, bullets, ratio="16:9", model="gpt-image-2.5-flare", count=1):
    date_str = datetime.datetime.now().strftime("%Y%m%d")

    color_desc = "modern emerald green and deep forest green (#059669 to #064E3B to #0B2E24)"
    img_size = "1792x1024" if ratio == "16:9" else "1024x1024"

    bullets_str = ", ".join([f"✔ {b}" for b in bullets])
    prompt = (
        f"A world-class municipal executive policy report presentation infographic slide in {ratio} widescreen format. "
        f"Clean minimalist design with NO watermarks, NO corner stamps, and NO signatures. "
        f"Master color scheme is {color_desc}. "
        f"Full-bleed high-definition authentic infrastructure photography background. "
        f"Lower-third section features a smooth translucent emerald green gradient scrim overlay (#059669 to #064E3B) at golden ratio. "
        f"Top line text in clean white: '{subtitle}'. "
        f"Huge ultra-bold heavy gothic main headline: '{main_title}' in pure white and luminous golden yellow (#FACC15). "
        f"Highlight bullet points with yellow checkmarks (✔): {bullets_str}. "
        f"Key numbers are magnified 2.5x in glowing gold. Clean, sharp typography, 8k resolution."
    )

    print(f"🚀 正在呼叫 OpenAI {model} 生成圖卡（共 {count} 張）：{topic} ...")
    saved_files = []
    try:
        response = client.images.generate(
            model=model,
            prompt=prompt,
            size=img_size,
            n=count
        )
        for idx, data in enumerate(response.data):
            suffix = f"_{idx + 1}" if count > 1 else ""
            filename = f"{date_str}_政績_{topic.replace(' ', '_')}{suffix}.jpg"
            filepath = os.path.join(OUTPUT_DIR, filename)

            if data.b64_json:
                img_bytes = base64.b64decode(data.b64_json)
                with open(filepath, "wb") as f:
                    f.write(img_bytes)
            elif data.url:
                req = urllib.request.Request(data.url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    img_bytes = resp.read()
                with open(filepath, "wb") as f:
                    f.write(img_bytes)
            else:
                continue

            saved_files.append(filepath)
            print(f"✅ 成功生成並儲存至：{filepath}")

        return saved_files
    except Exception as e:
        print(f"❌ 生成失敗：{e}")
        return []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenAI GPT Image 2.5 施政圖卡產生器")
    parser.add_argument("--topic", default="從賽馬場到晶圓廠", help="主題名稱")
    parser.add_argument("--subtitle", default="選對人 走對路 ｜ 高雄六年大改變 01 ‧ 產業轉型", help="副標題")
    parser.add_argument("--main_title", default="從賽馬場 到晶圓廠", help="主標題")
    parser.add_argument("--ratio", default="16:9", help="輸出比例 (16:9 或 1:1)")
    parser.add_argument("--model", default="gpt-image-2.5-flare", choices=["gpt-image-2.5-flare", "gpt-image-2.5-sunburst"], help="OpenAI 模型")
    parser.add_argument("--count", type=int, default=1, choices=[1, 2, 3, 4], help="生成張數 (1~4)")
    args = parser.parse_args()

    sample_bullets = [
        "煉了70年油的土地，4年迎來 台積電 2 奈米先進製程",
        "串聯南科台南與楠梓，打造全球最完整 半導體 S 廊帶",
        "招商投資突破 8,000 億元，創造 6 萬個 高薪就業機會"
    ]

    generate_slide(args.topic, args.subtitle, args.main_title, sample_bullets, args.ratio, args.model, args.count)
