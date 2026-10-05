#!/usr/bin/env python3
"""
官方高階施政報告圖卡 ＆ 政治文宣事實澄清 - 雙模式 GUI 獨立產生器
已串接 OpenAI 最新旗艦繪圖模型：gpt-image-2.5-flare
執行方式：python3 run_gui.py
"""

import http.server
import socketserver
import json
import urllib.request
import urllib.parse
import datetime
import os
import webbrowser
import sys

# Load OpenAI API Key from .env
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
env_file = os.path.join(WORKSPACE_DIR, ".env")
if os.path.exists(env_file):
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("OPENAI_API_KEY="):
                os.environ["OPENAI_API_KEY"] = line.strip().split("=", 1)[1]

try:
    import openai
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    OPENAI_AVAILABLE = True
except Exception:
    client = None
    OPENAI_AVAILABLE = False

PORT = 8888
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

HTML_CONTENT = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>官方高階施政圖卡 & 政治文宣產生器 (OpenAI gpt-image-2.5-flare 驅動)</title>
  <style>
    :root {
      --primary: #059669;
      --accent: #facc15;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --text: #0f172a;
    }
    body { font-family: -apple-system, BlinkMacSystemFont, "Noto Sans TC", sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 24px; }
    .container { max-width: 1000px; margin: 0 auto; background: var(--card-bg); border-radius: 20px; box-shadow: 0 12px 40px rgba(0,0,0,0.08); padding: 36px; border: 1px solid #e2e8f0; }
    .header-bar { display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; margin-bottom: 24px; }
    h1 { color: #065f46; margin: 0; font-size: 1.8rem; display: flex; align-items: center; gap: 12px; }
    .nav-tabs { display: flex; gap: 10px; margin-bottom: 24px; }
    .tab-btn { flex: 1; padding: 14px 20px; border: 2px solid #cbd5e1; background: #f8fafc; border-radius: 12px; font-size: 1.1rem; font-weight: 800; cursor: pointer; transition: all 0.2s; text-align: center; }
    .tab-btn.active { background: #059669; color: #fff; border-color: #059669; box-shadow: 0 4px 12px rgba(5,150,105,0.25); }
    .tab-btn.active.meme-mode { background: #b91c1c; border-color: #b91c1c; }
    .engine-badge { display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; background: #ecfdf5; color: #047857; border: 1.5px solid #a7f3d0; border-radius: 20px; font-size: 0.9rem; font-weight: 700; }
    .form-group { margin-bottom: 18px; }
    label { display: block; font-weight: 700; font-size: 1rem; margin-bottom: 6px; color: #334155; }
    input[type="text"], select, textarea { width: 100%; padding: 12px 14px; border: 2px solid #cbd5e1; border-radius: 10px; font-size: 1.05rem; box-sizing: border-box; }
    input[type="text"]:focus, select:focus, textarea:focus { outline: none; border-color: #059669; }
    .grid-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .grid-3col { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
    button.submit-btn { background: #059669; color: #fff; border: none; padding: 18px 32px; font-size: 1.25rem; font-weight: 900; border-radius: 12px; cursor: pointer; width: 100%; transition: all 0.2s; margin-top: 10px; }
    button.submit-btn:hover { background: #047857; box-shadow: 0 8px 20px rgba(5,150,105,0.3); }
    .status { margin-top: 24px; padding: 16px; border-radius: 12px; font-size: 1.1rem; font-weight: 700; display: none; }
    .status.loading { background: #fef3c7; border: 2px solid #f59e0b; color: #92400e; display: block; }
    .status.success { background: #dcfce7; border: 2px solid #22c55e; color: #15803d; display: block; }
    .preview-box { margin-top: 24px; text-align: center; }
    .preview-box img { max-width: 100%; border-radius: 14px; border: 3px solid #cbd5e1; box-shadow: 0 12px 30px rgba(0,0,0,0.15); }
  </style>
</head>
<body>
  <div class="container">
    <div class="header-bar">
      <h1>🏛️ 高質感施政圖卡 & 政治文宣產生器</h1>
      <span class="engine-badge">⚡ Powered by OpenAI gpt-image-2.5-flare</span>
    </div>

    <!-- 模式切換 Tabs -->
    <div class="nav-tabs">
      <div id="tabPolicy" class="tab-btn active" onclick="switchMode('policy')">
        🌿 官方高階施政與政績圖卡 (綠色主題 ‧ 純淨無浮水印)
      </div>
      <div id="tabMeme" class="tab-btn" onclick="switchMode('meme')">
        🥊 政治文宣與事實澄清梗圖 (1:1 對立/民調/打臉)
      </div>
    </div>

    <!-- 模式 A：官方施政圖卡區塊 -->
    <div id="policySection">
      <div class="grid-2col">
        <div class="form-group">
          <label>1. 選擇圖卡主題範本:</label>
          <select id="policyPreset" onchange="applyPreset(this.value)">
            <option value="custom">自訂施政主題與文字</option>
            <option value="industry">【產業轉型】從賽馬場 到晶圓廠 (台積電2奈米進駐)</option>
            <option value="culture">【文旅經濟】從 TW ICE 到 TWICE！ (5萬人世運演唱會)</option>
            <option value="transit">【綠色交通】從延宕停工 到輕軌成圓 (綠色路網全速推進)</option>
            <option value="corridor">【半導體S廊帶】打造全球最完整半導體產業聚落</option>
          </select>
        </div>
        <div class="form-group">
          <label>2. 選擇主色系 (預設綠色):</label>
          <select id="policyDomain">
            <option value="net_zero">🌿 翡翠綠／深森林綠 (#059669 to #064E3B) - 官方主色</option>
            <option value="high_tech">⚡ 科技深靛藍 (#06152B to #092242) - S廊帶專用</option>
            <option value="transit">🚴 活力暖金橘 (#EA580C to #C2410C) - 觀光文旅</option>
          </select>
        </div>
      </div>

      <div class="grid-2col">
        <div class="form-group">
          <label>3. 施政主題檔名標籤:</label>
          <input type="text" id="policyTopic" value="從賽馬場到晶圓廠">
        </div>
        <div class="form-group">
          <label>4. 輸出比例 (Aspect Ratio):</label>
          <select id="policyRatio">
            <option value="16:9">16:9 (1792x1024 簡報/投影大圖)</option>
            <option value="1:1">1:1 (1024x1024 社群方圖)</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label>5. 上方副標題 (白字):</label>
        <input type="text" id="policySubTitle" value="選對人 走對路 ｜ 高雄六年大改變 01 ‧ 產業轉型">
      </div>

      <div class="form-group">
        <label>6. 超大主標題 (支援純白+金黃雙色):</label>
        <input type="text" id="policyMainTitle" value="從賽馬場 到晶圓廠">
      </div>

      <div class="grid-3col">
        <div class="form-group">
          <label>重點成效 1:</label>
          <input type="text" id="policyBullet1" value="✔ 煉了70年油的土地，4年迎來 台積電 2 奈米先進製程">
        </div>
        <div class="form-group">
          <label>重點成效 2:</label>
          <input type="text" id="policyBullet2" value="✔ 串聯南科台南與楠梓，打造全球最完整 半導體 S 廊帶">
        </div>
        <div class="form-group">
          <label>重點成效 3:</label>
          <input type="text" id="policyBullet3" value="✔ 招商投資突破 8,000 億元，創造 6 萬個 高薪就業機會">
        </div>
      </div>
    </div>

    <!-- 模式 B：政治文宣梗圖區塊 -->
    <div id="memeSection" style="display: none;">
      <div class="form-group">
        <label>1. 選擇圖卡版型 (Meme Template):</label>
        <select id="memeTpl">
          <option value="real-photo">📸 現場真實照片滿版壓字（強化公信力與真實感）</option>
          <option value="poll">📊 民調數據與跨黨派認同長條圖（含年代民調中心標誌）</option>
          <option value="official">🏢 行政端正向事實澄清（翡翠綠/海洋藍官方質感）</option>
          <option value="double-standard">🔥 立場對比與雙標打臉（AI 超寫實對立劇照）</option>
        </select>
      </div>

      <div class="form-group">
        <label>2. 澄清主題 / 存檔名稱:</label>
        <input type="text" id="memeTopic" value="水質監測澄清">
      </div>

      <div class="form-group">
        <label>3. 頂部大標題:</label>
        <input type="text" id="memeTitle" value="【事實大公開】水質監測真相">
      </div>

      <div class="grid-3col">
        <div class="form-group">
          <label>重點勾選 1:</label>
          <input type="text" id="memeFact1" value="☑ 水質監測結果正常">
        </div>
        <div class="form-group">
          <label>重點勾選 2:</label>
          <input type="text" id="memeFact2" value="☑ 天氣酷熱致溶氧過低">
        </div>
        <div class="form-group">
          <label>重點勾選 3:</label>
          <input type="text" id="memeFact3" value="☑ 持續擴大專案稽查">
        </div>
      </div>

      <div class="form-group">
        <label>4. 底部號召標題:</label>
        <input type="text" id="memeSubTitle" value="用數據說話，專業科學檢測守護市民水環境！">
      </div>
    </div>

    <button id="btnGenerate" class="submit-btn">🚀 一鍵調用 OpenAI gpt-image-2.5-flare 生成圖卡</button>

    <div id="statusBox" class="status"></div>
    <div id="previewBox" class="preview-box"></div>
  </div>

  <script>
    let currentMode = 'policy';

    function applyPreset(val) {
      if (val === 'industry') {
        document.getElementById('policyTopic').value = '從賽馬場到晶圓廠';
        document.getElementById('policySubTitle').value = '選對人 走對路 ｜ 高雄六年大改變 01 ‧ 產業轉型';
        document.getElementById('policyMainTitle').value = '從賽馬場 到晶圓廠';
        document.getElementById('policyBullet1').value = '✔ 煉了70年油的土地，4年迎來 台積電 2 奈米先進製程';
        document.getElementById('policyBullet2').value = '✔ 串聯南科台南與楠梓，打造全球最完整 半導體 S 廊帶';
        document.getElementById('policyBullet3').value = '✔ 招商投資突破 8,000 億元，創造 6 萬個 高薪就業機會';
      } else if (val === 'culture') {
        document.getElementById('policyTopic').value = '從TW_ICE到TWICE';
        document.getElementById('policySubTitle').value = '選對人 走對路 ｜ 高雄六年大改變 02 ‧ 文旅經濟';
        document.getElementById('policyMainTitle').value = '從 TW ICE 到 TWICE！';
        document.getElementById('policyBullet1').value = '✔ Coldplay、BLACKPINK、TWICE、Ed Sheeran 接連開唱';
        document.getElementById('policyBullet2').value = '✔ 演唱會經濟大爆發！累計吸引 300 萬觀光人次、創造 100 億元 產值';
        document.getElementById('policyBullet3').value = '✔ 智慧交通疏運大考驗：5 萬人散場 60 分鐘內完全淨空';
      } else if (val === 'transit') {
        document.getElementById('policyTopic').value = '從延宕停工到輕軌成圓';
        document.getElementById('policySubTitle').value = '選對人 走對路 ｜ 高雄六年大改變 03 ‧ 綠色交通';
        document.getElementById('policyMainTitle').value = '從延宕停工 到輕軌成圓';
        document.getElementById('policyBullet1').value = '✔ 輕軌全線成圓通車！年度總運量達 1,333 萬人次，日運量成長 22%';
        document.getElementById('policyBullet2').value = '✔ 捷運四線齊發（岡山路竹延伸線、黃線、小港林園線）全速動工';
        document.getElementById('policyBullet3').value = '✔ 連續 4 年零舉借，累計減債 352 億元，健全財政建設不停步';
      }
    }

    function switchMode(mode) {
      currentMode = mode;
      const tabPolicy = document.getElementById('tabPolicy');
      const tabMeme = document.getElementById('tabMeme');
      const policySec = document.getElementById('policySection');
      const memeSec = document.getElementById('memeSection');
      const btn = document.getElementById('btnGenerate');

      if (mode === 'policy') {
        tabPolicy.className = 'tab-btn active';
        tabMeme.className = 'tab-btn';
        policySec.style.display = 'block';
        memeSec.style.display = 'none';
        btn.style.background = '#059669';
        btn.innerHTML = '🚀 一鍵調用 OpenAI gpt-image-2.5-flare 生成施政圖卡';
      } else {
        tabPolicy.className = 'tab-btn';
        tabMeme.className = 'tab-btn active meme-mode';
        policySec.style.display = 'none';
        memeSec.style.display = 'block';
        btn.style.background = '#b91c1c';
        btn.innerHTML = '🥊 一鍵生成政治文宣澄清圖卡';
      }
    }

    document.getElementById('btnGenerate').addEventListener('click', async () => {
      const statusBox = document.getElementById('statusBox');
      const previewBox = document.getElementById('previewBox');
      
      let payload = { mode: currentMode };

      if (currentMode === 'policy') {
        payload.domain = document.getElementById('policyDomain').value;
        payload.topic = document.getElementById('policyTopic').value;
        payload.mainTitle = document.getElementById('policyMainTitle').value;
        payload.subTitle = document.getElementById('policySubTitle').value;
        payload.bullet1 = document.getElementById('policyBullet1').value;
        payload.bullet2 = document.getElementById('policyBullet2').value;
        payload.bullet3 = document.getElementById('policyBullet3').value;
        payload.ratio = document.getElementById('policyRatio').value;
      } else {
        payload.tpl = document.getElementById('memeTpl').value;
        payload.topic = document.getElementById('memeTopic').value;
        payload.title = document.getElementById('memeTitle').value;
        payload.fact1 = document.getElementById('memeFact1').value;
        payload.fact2 = document.getElementById('memeFact2').value;
        payload.fact3 = document.getElementById('memeFact3').value;
        payload.subTitle = document.getElementById('memeSubTitle').value;
        payload.ratio = '1:1';
      }

      statusBox.className = 'status loading';
      statusBox.innerHTML = '⏳ 正在向 OpenAI gpt-image-2.5-flare 旗艦模型發送生成請求，請稍候約 10-18 秒...';
      previewBox.innerHTML = '';

      try {
        const res = await fetch('/api/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        
        if (data.success) {
          statusBox.className = 'status success';
          statusBox.innerHTML = `✅ 成功透過 OpenAI gpt-image-2.5-flare 生成圖卡！<br>檔案已自動存入：<b>output/${data.filename}</b>`;
          previewBox.innerHTML = `<h3>圖卡即時預覽：</h3><img src="/output/${data.filename}?t=${Date.now()}">`;
        } else {
          throw new Error(data.error || '生成失敗');
        }
      } catch (err) {
        statusBox.className = 'status loading';
        statusBox.style.background = '#fef2f2';
        statusBox.style.borderColor = '#ef4444';
        statusBox.style.color = '#991b1b';
        statusBox.innerHTML = '❌ 生成發生錯誤：' + err.message;
      }
    });
  </script>
</body>
</html>
"""

class DualModeGUIRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode('utf-8'))
            return
        
        if self.path.startswith('/output/'):
            filename = urllib.parse.unquote(self.path.replace('/output/', '').split('?')[0])
            filepath = os.path.join(OUTPUT_DIR, filename)
            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header('Content-type', 'image/jpeg')
                self.end_headers()
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
                return

        super().do_GET()

    def do_POST(self):
        if self.path == '/api/generate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode('utf-8'))

            mode = params.get('mode', 'policy')
            date_str = datetime.datetime.now().strftime('%Y%m%d')

            if mode == 'policy':
                topic = params.get('topic', '施政成果').replace(' ', '_')
                filename = f"{date_str}_政績_{topic}.jpg"
                filepath = os.path.join(OUTPUT_DIR, filename)

                color_desc = "modern emerald green and deep forest green (#059669 to #064E3B to #0B2E24)"

                prompt_text = (
                    f"A world-class municipal executive policy report presentation infographic slide in {params.get('ratio', '16:9')} widescreen format. "
                    f"Clean minimalist design with NO watermarks, NO corner stamps, and NO signatures. "
                    f"Master color scheme is {color_desc}. "
                    f"Full-bleed high-definition authentic infrastructure photography background. "
                    f"Lower-third section features a smooth translucent emerald green gradient scrim overlay (#059669 to #064E3B) at golden ratio. "
                    f"Top line text in clean white: '{params.get('subTitle')}'. "
                    f"Huge ultra-bold heavy gothic main headline: '{params.get('mainTitle')}' in pure white and luminous golden yellow (#FACC15). "
                    f"Highlight bullet points with yellow checkmarks (✔): "
                    f"1. {params.get('bullet1')}, 2. {params.get('bullet2')}, 3. {params.get('bullet3')}. "
                    f"Key numbers are magnified 2.5x in glowing gold. Clean, sharp typography, 8k resolution."
                )
                img_size = "1792x1024" if params.get('ratio') == '16:9' else "1024x1024"
            else:
                topic = params.get('topic', '澄清圖卡').replace(' ', '_')
                filename = f"{date_str}_{topic}.jpg"
                filepath = os.path.join(OUTPUT_DIR, filename)

                prompt_text = (
                    f"A high-impact official Taiwanese political clarification infographic image in 1:1 square ratio. "
                    f"Clean minimalist design with NO corner watermarks. "
                    f"Title: {params.get('title')}. "
                    f"Fact cards: {params.get('fact1')}, {params.get('fact2')}, {params.get('fact3')}. "
                    f"Bottom banner: {params.get('subTitle')}. "
                    f"Professional, high-contrast, 8k resolution."
                )
                img_size = "1024x1024"

            # Generate via OpenAI gpt-image-2.5-flare if available
            try:
                if client:
                    response = client.images.generate(
                        model="gpt-image-2.5-flare",
                        prompt=prompt_text,
                        size=img_size,
                        quality="high",
                        n=1
                    )
                    data = response.data[0]
                    if data.b64_json:
                        import base64
                        img_data = base64.b64decode(data.b64_json)
                        with open(filepath, 'wb') as f:
                            f.write(img_data)
                    elif data.url:
                        req = urllib.request.Request(data.url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=30) as resp:
                            img_data = resp.read()
                        with open(filepath, 'wb') as f:
                            f.write(img_data)
                    else:
                        raise Exception("No image data returned")
                    res_payload = {"success": True, "filename": filename, "path": filepath, "engine": "OpenAI gpt-image-2.5-flare"}
                else:
                    raise Exception("OpenAI API Key not configured")
            except Exception as openai_err:
                # Fallback to pollinations flux
                try:
                    w = 1792 if params.get('ratio') == '16:9' else 1024
                    h = 1024
                    encoded = urllib.parse.quote(prompt_text)
                    poll_url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&nologo=true&model=flux"
                    req = urllib.request.Request(poll_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        img_data = resp.read()
                        with open(filepath, 'wb') as f:
                            f.write(img_data)
                    res_payload = {"success": True, "filename": filename, "path": filepath, "engine": "Flux (Fallback)", "warning": str(openai_err)}
                except Exception as e:
                    res_payload = {"success": False, "error": f"OpenAI error: {openai_err}, Fallback error: {e}"}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(res_payload).encode('utf-8'))

if __name__ == '__main__':
    print(f"🚀 高質感施政圖卡 & 政治文宣 GUI 服務啟動中 (OpenAI gpt-image-2.5-flare 已就緒)... 網址: http://localhost:{PORT}")
    webbrowser.open(f"http://localhost:{PORT}")
    with socketserver.TCPServer(("", PORT), DualModeGUIRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nGUI 服務已停止。")
            sys.exit(0)
