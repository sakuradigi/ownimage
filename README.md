# ⚡️ GPT Image 2.5 梗圖與圖像創作工作台

專為政治梗圖、文宣圖卡與社群視覺創作打造的輕量化 Web 工作台。完全支援 OpenAI 最新發布的 **GPT Image 2.5** 系列模型，整合了 **Fabric.js 互動式畫布**、**局部塗抹修圖 (Inpainting)**、**經典梗圖文字排版** 與 **本機安全金鑰機制**。

---

## ✨ 核心特色

1. **支援 OpenAI GPT Image 2.5 雙旗艦模型**：
   * 🌟 **`gpt-image-2.5-sunburst`**：旗艦高精細模型，特別擅長複雜細節與精準修圖，能極佳維持人物外觀與主體一致性。
   * ⚡️ **`gpt-image-2.5-flare`**：極速模型（速度提升 50%），日常構想出圖必備。
   * 🪟 **原生透明背景支援**：支援輸出去背透明背景（Transparent PNG/WebP）。
2. **互動式局部修圖畫布 (Inpaint / Masking)**：
   * 切換至「局部遮罩修圖」分頁，即可使用紅色筆刷在圖片上圈選/塗抹想修改的局部（例如換帽子、換手勢、微調五官表情）。
   * 自動合成 OpenAI 規格的透明遮罩並發送至 `/v1/images/edits` 端點精準重繪。
3. **經典梗圖字效 (Meme Typography)**：
   * 一鍵加入「+頂部文字」或「+底部文字」。
   * 預設套用**白字黑粗邊 (Impact / Heavy Bold)** 經典梗圖外觀，字型清楚飽滿。
   * 自由拖曳、放大縮小、旋轉，隨時微調字號、顏色與描邊粗細。
4. **絕對安全的 API Key 設計**：
   * API Key 僅儲存在您個人瀏覽器的 `localStorage` 中。
   * **程式碼中沒有任何寫死的 Key**，您可以安全地將整個專案 Git commit 並推送到 GitHub（甚至設為公開 Repo）。
5. **零依賴、純前端單檔**：
   * 無需安裝 Node.js、npm 或任何編譯環境，隨開隨用。

---

## 🚀 快速開始

### 方式 A：本機直接使用（最快）
1. 在 Mac Finder 中，直接對著 `index.html` 點擊滑鼠右鍵，選擇使用 Chrome、Safari 或 Edge 開啟。
2. （或在終端機啟動本地簡易伺服器）：
   ```bash
   python3 -m http.server 8000
   ```
   然後在瀏覽器打開 `http://localhost:8000`。
3. 點擊右上角 **「設定 API Key」**，貼上您的 OpenAI API Key（只需輸入一次，瀏覽器會自動記住）。

---

### 方式 B：部署至 GitHub Pages（在手機、平板與任何電腦使用）

您只要把本專案推送到 GitHub，就能免費獲得一個專屬的雲端 Web 應用：

1. **建立並推送到 GitHub**：
   ```bash
   git init
   git add index.html README.md
   git commit -m "feat: Add GPT Image 2.5 meme generator and inpainting studio"
   git branch -M main
   git remote add origin https://github.com/您的帳號/您的專案名稱.git
   git push -u origin main
   ```

2. **啟用 GitHub Pages**：
   * 進入您在 GitHub 上的專案儲存庫頁面。
   * 點擊上方 **「Settings」**（設定）分頁。
   * 在左側選單點擊 **「Pages」**。
   * 在 **Build and deployment** > **Branch** 下拉選單中，選擇 `main` 分支與 `/ (root)` 目錄，點擊 **Save**。
   * 約 1~2 分鐘後，上方會出現專屬網址（例如：`https://您的帳號.github.io/您的專案名稱/`）。

3. 打開該網址，在右上角輸入 API Key 即可開始創作！因為 API Key 是保存在您自己的瀏覽器端，他人開啟同一個網址也不會看到您的 Key。

---

## 🎨 梗圖創作操作指南

### 1. 全新生圖
* 在左側選擇 `gpt-image-2.5-flare`（快速）或 `sunburst`（精緻）。
* 選擇比例（1:1 正方、16:9 橫向文宣或 9:16 直式）。
* 輸入提示詞或點選快捷風格標籤（例如：諷刺漫畫、新聞快報、寫實攝影等）。
* 點擊「立即生成圖片」。

### 2. 局部修圖 (Inpainting)
* 圖片生成後（或點擊「開啟本機圖片」上傳現成圖片）。
* 切換左側至 **「局部遮罩修圖」** 分頁。
* 在畫布上用紅色筆刷塗抹想要修改的局部區塊。
* 在 Prompt 框描述塗抹區塊希望換成什麼（例如：「改成戴著黃色工程安全帽」）。
* 點擊「開始局部修圖」，AI 會保持其餘部分不變，僅重繪塗抹區塊！

### 3. 加入文字與下載
* 點擊工具列上的 **「+頂部文字」** 或 **「+底部文字」**。
* 雙擊文字框編輯字詞內容，拖曳控制點改變大小與位置。
* 點擊右上角 **「下載完成圖」**（直接存為 PNG 高清圖）或 **「複製圖片」** 直接貼到社群軟體發文！
