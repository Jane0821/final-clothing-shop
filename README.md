# 🛒 服飾即時篩選與品牌爬蟲系統原型專案

一個基於 Flask 架構開發的智慧服飾篩選與數據清洗引擎系統。本專案整合了前端動態不重刷新技術（Fetch API）與後端多層防禦備援機制，能即時搜羅、過濾各大主流品牌的服飾資料，並提供全雲端化的線上體驗。

## 🌐 線上展示 (Live Demo)

本專案已成功部署至雲端伺服器，可直接透過手機或電腦瀏覽器進行即時體驗：
👉 **[點此進入 Render 線上系統網站](https://final-clothing-shop.onrender.com)**

---

## ✨ 系統核心亮點與技術架構

### 1. 前端動態互動界面 (Responsive Frontend)
- **非同步無刷新技術**：採用 JavaScript **Fetch API (POST)** 與後端進行 JSON 資料交換，使用者篩選時網頁不需重新整理，體驗極其流暢。
- **現代化 UI/UX 視覺**：導入 **Bootstrap 5** 與 Google Font、FontAwesome 經典圖標，打造高質感、無人像干擾的純衣服平拍/掛拍卡片牆。
- **動態模擬加載**：貼心設計 `loadingSpinner` 轉圈圈動畫，增強即時爬蟲載入時的用戶反饋體驗。

### 2. 後端數據引擎 (Flask Backend Engine)
- **雙層備援防禦機制**：
  1. **優先權：即時網路爬蟲模組**（動態生成、過濾各大品牌如 UNIQLO、GU、ZARA、H&M 的價格 multipliers、品項 serial 與高品質圖片庫）。
  2. **備援權：本機 CSV 資料庫**（當爬蟲模組異常時，系統自動啟用 `os.path` 絕對路徑機制，無縫切換讀取 `data.csv` 備用資料庫）。
- **智慧推薦演算法**：當條件過於嚴苛導致搜尋結果為空時，後端將自動啟動「店長隨機推薦」功能，確保使用者永遠能看到商品。

---

## 📂 專案檔案結構 (Project Structure)

```text
final-clothing-shop/
├── app/
│   └── routes.py          # 後端核心路由與雙層備援篩選邏輯
├── static/
│   └── main.js            # 前端 Fetch API 請求、DOM 節點渲染與動畫控制
├── templates/
│   ├── base.html          # 全站基礎主版架構 (Navbar, Footer, CDN 載入)
│   └── index.html         # 智能篩選面板與商品展示格網 (Extends base)
├── data.csv               # 備援機制專用本機服飾資料庫
├── main.py                # 系統啟動進入點 (已優化雲端環境變數 PORT 偵測)
├── requirements.txt       # 專案套件依賴清單 (Flask, Pandas...)
└── README.md              # 專案說明文件 (本檔案)
