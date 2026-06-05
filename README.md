# **🌌 Cosmos3-Super-Text2Image-Mobile (雙引擎文字生圖 App)**

這是一個基於 **Gemini Canvas** 輔助開發、專為行動端（手機版優先）設計的 **AI 圖像生成 Web App**。

本專案同時整合了 **NVIDIA Cosmos 基礎世界模型**（透過 Hugging Face Inference API）與 **Google Gemini 3.1 直連影像生成模型**，並提供一鍵智能容錯、自動 Prompt 優化與精美畫廊功能，非常適合部署在 **Streamlit Community Cloud (streamlit.io)** 上，作為您的個人作品集或作業成果繳交。

## **🌟 專案核心特色**

* **⚡ 雙圖像生成引擎自由切換**：  
  * **NVIDIA Cosmos 引擎 (HF)**：支援 nvidia/Cosmos-1.0-Diffusion-7B-Text2World 等高精度物理反射大模型，可自訂步數 (Steps)、引導強度 (CFG) 與 Hugging Face Token。  
  * **Google Gemini 3.1 引擎**：直連 Google 最新高速生圖模型 gemini-3.1-flash-image-preview，免 Token 且 100% 穩定，可避開 Hugging Face 免費端常發生的 CORS 阻擋與冷啟動延遲。  
* **💡 Gemini 2.5 智慧提示詞優化**：  
  * 內建一鍵優化按鈕。利用 Gemini 大型語言模型，將簡單的基礎字詞智慧擴展為極具電影質感（Cinematic）、光影細緻且符合物理運作規律的英文進階 Prompt。  
* **🛡️ 智能連線異常容錯機制**：  
  * 偵測到 Hugging Face 連線受阻（如模型載入過久、無 Token 或連線異常）時，系統會自動在畫面上方彈出精美的**容錯提醒視窗**，引導使用者「一鍵切換至穩定的 Gemini 3.1 引擎」重試，保證 Demo 展示過程不中斷！  
* **📱 極致的手機自適應介面**：  
  * 採用完美的深色科技風（Deep Blue / Dark mode）UI，優化圓角卡片、滑動頁籤（Tabs）與快速風格推薦標籤。  
* **🎨 精選展示畫廊**：  
  * 預設多組 NVIDIA Cosmos 生成的高品質物理世界圖像與對應 Prompt，點選即可秒速複製或直接載入套用。

## **🛠️ 快速開始 (本地端執行)**

請依照以下步驟在您本地的電腦上運行本專案：

### **1\. 複製專案 (Clone Repository)**

git clone \[https://github.com/您的用戶名/Cosmos3-Super-Text2Image-Mobile.git\](https://github.com/您的用戶名/Cosmos3-Super-Text2Image-Mobile.git)  
cd Cosmos3-Super-Text2Image-Mobile

### **2\. 安裝依賴套件**

我們建議使用 Python 3.9+。請先安裝 requirements.txt 中指定的套件：

pip install \-r requirements.txt

*(註：您的 requirements.txt 僅需包含 streamlit 與 requests 即可。)*

### **3\. 本地執行 App**

streamlit run app.py

執行後，瀏覽器將自動開啟 http://localhost:8501。

## **🚀 部署至 Streamlit Community Cloud (streamlit.io)**

本專案完全適配並推薦部署至 Streamlit Cloud。

### **步驟 1：上傳程式碼**

將您的 app.py 與 requirements.txt 上傳/Push 至您的 GitHub 公開或私人 Repository 中。

### **步驟 2：建立 App**

1. 前往 [Streamlit Community Cloud](https://share.streamlit.io/) 並使用您的 GitHub 帳號登入。  
2. 點擊右上角的 **"New App"**。  
3. 選擇您剛才上傳的 Repository、Branch 以及主要檔案路徑 (app.py)。

### **步驟 3：配置 Secrets 安全變數（推薦，極重要！）**

為了避免使用者每次進入網頁都需要手動填寫 API 金鑰與 Token，強烈建議在部署前配置 **Streamlit Secrets**：

1. 在 Streamlit 部署頁面的右下角點擊 **"Advanced settings..."**。  
2. 在 **"Secrets"** 的輸入框中，以 TOML 格式貼上您的金鑰（系統會自動載入）：

\# Google Gemini API Key  
GEMINI\_API\_KEY \= "您的\_GEMINI\_API\_金鑰"

\# Hugging Face Read 權限 Token (用於 Cosmos 實時生成)  
HF\_TOKEN \= "您的\_HUGGING\_FACE\_TOKEN"

3. 點擊 **"Save"** 儲存，接著點擊 **"Deploy\!"** 開始部署。幾分鐘後，您的 T2I 生圖 App 即可全網順暢運行！

## **📂 專案檔案結構**

├── app.py              \# 主要的 Streamlit 應用程式 Python 程式碼  
├── requirements.txt    \# 專案依賴套件 (包含 streamlit, requests)  
└── README.md           \# 本說明文件

## **🎯 繳交作業與演示指引**

1. **基本測試**：直接在輸入框輸入提示詞，切換為 **"Gemini 3.1 直連"**，並點擊「立即生成影像」即可 100% 成功秒級生圖，用作基本功能展示。  
2. **NVIDIA Cosmos3 真實連線測試**：  
   * 在頂部「⚙️ API 部署與進階設定」填入您的 HF\_TOKEN。  
   * 將引擎切換至 **"Cosmos (NVIDIA 物理世界模型)"**，模型下拉選單選擇 NVIDIA Cosmos 1.0 Diffusion 7B。  
   * 輸入提示詞進行真實的物理世界模擬生成。  
3. **一鍵容錯展示**：在未設定 HF\_TOKEN 的情況下，Cosmos 的真實連線若遭遇錯誤，頁面將會完美彈出「智能連線異常容錯」小幫手，展示在網路或 API 異常時，產品如何快速無縫切換到 Gemini 引擎進行體驗，這是一大加分亮點！

## **📜 授權許可**

本專案基於 [MIT License](http://docs.google.com/LICENSE) 進行開源。
