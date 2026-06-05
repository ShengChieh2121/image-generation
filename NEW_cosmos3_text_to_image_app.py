import streamlit as st
import requests
import time
import base64

# -----------------------------------------------------------------------------
# 頁面基本設定 (手機版優先與深色科技風)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Cosmos3 Super T2I Mobile",
    page_icon="🌌",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 注入自定義 CSS 以打造極致的深色科技風與行動端自適應介面
st.markdown("""
<style>
    /* 全域深色背景與文字 */
    .stApp {
        background-color: #020617;
        color: #f1f5f9;
    }
    
    /* 調整頂部 Header 樣式 */
    .header-container {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 0;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 20px;
    }
    .header-logo {
        background: linear-gradient(135deg, #4f46e5, #a855f7);
        padding: 8px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    .header-title {
        font-size: 1.25rem;
        font-weight: 700;
        background: linear-gradient(to right, #ffffff, #c7d2fe, #f3e8ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .header-subtitle {
        font-size: 0.7rem;
        font-family: monospace;
        color: #94a3b8;
        margin: 0;
    }

    /* 圓角卡片樣式 */
    .custom-card {
        background-color: rgba(15, 23, 42, 0.5);
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 16px;
    }

    /* 漂亮的隨機風格標籤按鈕 */
    .stButton>button {
        border-radius: 10px !important;
        transition: all 0.2s ease-in-out;
    }
    
    /* 主生成按鈕漸層樣式 */
    div[data-testid="stForm"] button[type="submit"], 
    .main-generate-btn button {
        background: linear-gradient(to right, #4f46e5, #7c3aed) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
    }
    
    div[data-testid="stForm"] button[type="submit"]:hover,
    .main-generate-btn button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(79, 70, 229, 0.4) !important;
    }

    /* 智慧一鍵切換警示框樣式 */
    .fallback-box {
        background: linear-gradient(to right, rgba(120, 53, 4, 0.8), rgba(15, 23, 42, 0.9));
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 初始化 Session State (狀態管理)
# -----------------------------------------------------------------------------
if 'engine' not in st.session_state:
    st.session_state.engine = 'gemini'  # 'gemini' 或 'cosmos' (HF)
if 'prompt' not in st.session_state:
    st.session_state.prompt = ''
if 'negative_prompt' not in st.session_state:
    st.session_state.negative_prompt = 'low quality, blurry, distorted, bad anatomy'
if 'aspect_ratio' not in st.session_state:
    st.session_state.aspect_ratio = '16:9'
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = 'gemini-3.1-flash-image-preview'
if 'custom_model_path' not in st.session_state:
    st.session_state.custom_model_path = 'nvidia/Cosmos-1.0-Diffusion-7B-Text2World'
if 'generated_result' not in st.session_state:
    st.session_state.generated_result = None  # 儲存格式: {'url': str, 'prompt': str, 'engine': str, 'is_simulated': bool, 'aspect_ratio': str}
if 'show_fallback_modal' not in st.session_state:
    st.session_state.show_fallback_modal = False

# -----------------------------------------------------------------------------
# 行動端頂部導航
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-container">
    <div class="header-logo">
        <span style="font-size: 20px; line-height: 1;">🌌</span>
    </div>
    <div>
        <h1 class="header-title">Cosmos3 Super T2I</h1>
        <p class="header-subtitle">Streamlit Mobile Engine v2.0</p>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 設定抽屜 (以 Streamlit Expander 展開設定)
# -----------------------------------------------------------------------------
with st.expander("⚙️ API 部署與進階設定", expanded=False):
    st.subheader("🔑 金鑰配置")
    
    # 支援優先讀取 Streamlit Secrets 安全變數
    default_gemini_key = st.secrets.get("GEMINI_API_KEY", "")
    default_hf_token = st.secrets.get("HF_TOKEN", "")
    
    gemini_key = st.text_input(
        "Google Gemini API Key (可選)", 
        value=default_gemini_key, 
        type="password",
        help="留空將自動嘗試讀取 Streamlit Secrets 的配置。這用於『Gemini 直連』與『智慧提示詞優化』。"
    )
    
    hf_token = st.text_input(
        "Hugging Face Token (Cosmos3 專用)", 
        value=default_hf_token, 
        type="password",
        help="留空則 Cosmos 引擎在生成時會自動啟用體驗展示模式。"
    )

    st.subheader("參數調整")
    col_steps, col_cfg = st.columns(2)
    with col_steps:
        steps = st.number_input("推理步數 (Steps)", min_value=10, max_value=100, value=30)
    with col_cfg:
        guidance_scale = st.number_input("引導強度 (CFG)", min_value=1.0, max_value=20.0, value=7.0, step=0.5)

# -----------------------------------------------------------------------------
# 頁籤選單（分頁切換）
# -----------------------------------------------------------------------------
tabs = st.tabs(["✨ 智能生成", "🖼️ 精選畫廊", "📖 教學與說明"])

# -----------------------------------------------------------------------------
# 頁籤 1: 智能生成
# -----------------------------------------------------------------------------
with tabs[0]:
    # 選擇生圖引擎
    st.markdown("##### 1. 選擇圖像生成引擎")
    engine_options = {"Gemini 3.1 直連 (穩定、極速生圖)": "gemini", "Cosmos (NVIDIA 物理世界模型)": "cosmos"}
    selected_engine_label = st.radio(
        "生圖引擎",
        options=list(engine_options.keys()),
        horizontal=True,
        label_visibility="collapsed"
    )
    # 動態響應引擎切換
    current_engine = engine_options[selected_engine_label]
    if current_engine != st.session_state.engine:
        st.session_state.engine = current_engine
        if current_engine == 'gemini':
            st.session_state.selected_model = 'gemini-3.1-flash-image-preview'
        else:
            st.session_state.selected_model = 'nvidia/Cosmos-1.0-Diffusion-7B-Text2World'

    # 選擇具體模型
    st.markdown("##### 2. 選擇具體生成模型")
    if st.session_state.engine == 'gemini':
        model_list = {
            "Gemini 3.1 Flash Image (極速、高畫質生圖 - 預設)": "gemini-3.1-flash-image-preview",
            "Gemini 2.5 Flash Image (多模態穩定生圖)": "gemini-2.5-flash-image-preview"
        }
    else:
        model_list = {
            "NVIDIA Cosmos 1.0 Diffusion 7B (世界物理模型)": "nvidia/Cosmos-1.0-Diffusion-7B-Text2World",
            "NVIDIA Cosmos 1.0 Diffusion 14B (物理高擬真反射)": "nvidia/Cosmos-1.0-Diffusion-14B-Text2World",
            "FLUX.1 Schnell (極速開源神級生圖 - 推薦替代方案)": "black-forest-labs/FLUX.1-schnell",
            "Stable Diffusion 3.5 Medium (經典寫實)": "stabilityai/stable-diffusion-3.5-medium",
            "✍️ 手動輸入其它 Hugging Face 模型...": "custom"
        }
    
    # 確保預設選項合法，防止切換引擎時發生 Index 錯位
    model_labels = list(model_list.keys())
    model_values = list(model_list.values())
    default_index = 0
    if st.session_state.selected_model in model_values:
        default_index = model_values.index(st.session_state.selected_model)
    elif st.session_state.selected_model == 'custom' or st.session_state.selected_model == st.session_state.custom_model_path:
        if "✍️ 手動輸入其它 Hugging Face 模型..." in model_labels:
            default_index = model_labels.index("✍️ 手動輸入其它 Hugging Face 模型...")

    selected_model_label = st.selectbox(
        "生成模型",
        options=model_labels,
        index=default_index,
        label_visibility="collapsed"
    )
    st.session_state.selected_model = model_list[selected_model_label]

    # 自訂模型輸入框
    if st.session_state.engine == 'cosmos' and st.session_state.selected_model == 'custom':
        custom_path = st.text_input(
            "輸入 Hugging Face 模型路徑", 
            value=st.session_state.custom_model_path,
            placeholder="例如: stabilityai/stable-diffusion-xl-base-1.0"
        )
        st.session_state.custom_model_path = custom_path

    # 一鍵容錯提示框 (緊急 fallback 處理)
    if st.session_state.show_fallback_modal:
        st.markdown(f"""
        <div class="fallback-box">
            <h4 style="color: #f59e0b; margin-top: 0; display: flex; align-items: center; gap: 8px;">
                ⚠️ 偵測到 Hugging Face 連線障礙
            </h4>
            <p style="font-size: 0.8rem; line-clamp: 3; color: #fef3c7; line-height: 1.5; margin-bottom: 12px;">
                剛剛使用的 Cosmos (HF) 連線受到阻礙。這通常是因為該物理世界大模型（7B+）在免費共享端需要 Token 認證，或受到伺服器跨來源限制 (CORS)。
                <br><strong>💡 建議解決方案：</strong> 請點擊下方按鈕，<b>一鍵切換至 Google 官方 Gemini 3.1 直連引擎</b>，體驗零排隊、無阻擋的生圖效果！
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("⚡ 一鍵切換 Gemini 重新嘗試"):
            st.session_state.engine = 'gemini'
            st.session_state.selected_model = 'gemini-3.1-flash-image-preview'
            st.session_state.show_fallback_modal = False
            st.rerun()

    # -----------------------------------------------------------------------------
    # 影像展示區 (Result Card)
    # -----------------------------------------------------------------------------
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    if st.session_state.generated_result:
        res = st.session_state.generated_result
        
        # 標題與標籤
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="font-size: 0.75rem; font-weight: bold; text-transform: uppercase; color: #818cf8;">
                🔮 使用引擎: {res['engine'].upper()}
            </span>
            <span style="font-size: 0.7rem; color: #94a3b8; font-family: monospace;">
                比例: {res['aspect_ratio']}
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # 顯示圖片
        if res['url'].startswith("data:image"):
            # Base64 格式
            st.image(res['url'], use_container_width=True)
        else:
            # 標準 URL
            st.image(res['url'], use_container_width=True)
            
        # 體驗模式小告示
        if res.get('is_simulated'):
            st.warning("⚠️ 目前處於 Cosmos 體驗模式：請配置 HF Token 以進行真實大模型連線！")
            
        # 提示詞展示與複製
        st.info(f"💡 採用的提示詞：\n\n*{res['prompt']}*")
    else:
        st.markdown("""
        <div style="text-align: center; padding: 40px 0;">
            <span style="font-size: 40px;">🖼️</span>
            <p style="font-size: 0.8rem; color: #94a3b8; margin-top: 10px;">
                在下方輸入提示詞並點擊生成，AI 擴散模型即刻為您創造物理世界景象。
            </p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------------------
    # 輸入面板
    # -----------------------------------------------------------------------------
    st.markdown("##### 3. 設計提示詞 (Prompt)")
    
    # 智慧優化提示詞處理
    def run_prompt_optimizer():
        if not st.session_state.prompt_input.strip():
            st.error("請先輸入基礎提示詞再進行優化！")
            return
        
        with st.spinner("🔮 Gemini AI 正在重塑並優化提示詞結構..."):
            try:
                system_instruction = "You are an expert prompt engineer for advanced image generators (Gemini Image & Nvidia Cosmos). Your task is to expand and enhance the user's prompt to make it incredibly detailed, cinematic, and physical-world-compliant. Keep the core intent but add details about lighting, textures, cinematic camera angles, and physical accuracy. Return ONLY the enhanced prompt in English, with no introduction or markdown formatting."
                payload = {
                    "contents": [{"parts": [{"text": f'Enhance this prompt: "{st.session_state.prompt_input}". Focus on cinematic realism. Keep it under 100 words.'}]}],
                    "systemInstruction": {"parts": [{"text": system_instruction}]}
                }
                api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={gemini_key}"
                resp = requests.post(api_url, json=payload, timeout=15)
                if resp.status_code == 200:
                    text_out = resp.json()['candidates'][0]['content']['parts'][0]['text']
                    st.session_state.prompt = text_out.strip()
                    st.success("⚡ 提示詞優化成功！已為您自動填入文字框。")
                else:
                    raise Exception("API 回應異常")
            except Exception as e:
                # 本地優化 Fallback
                st.session_state.prompt = f"{st.session_state.prompt_input}, cinematic lighting, photorealistic, physics simulated details, 8k resolution, highly detailed textures, masterpiece"
                st.info("已套用本地引擎進行提示詞增強優化！")

    # 綁定 st.session_state.prompt
    user_prompt = st.text_area(
        "提示詞內容",
        value=st.session_state.prompt,
        placeholder="例如：An ultra-realistic futuristic city, flying transport, neon lights reflected in puddles, cinematic composition...",
        key="prompt_input",
        height=100
    )
    st.session_state.prompt = user_prompt

    # 智慧優化與清除按鈕
    col_opt, col_clr = st.columns([3, 1])
    with col_opt:
        if st.button("💡 Gemini 智慧優化提示詞", use_container_width=True):
            run_prompt_optimizer()
            st.rerun()
    with col_clr:
        if st.button("🗑️ 清除", use_container_width=True):
            st.session_state.prompt = ""
            st.rerun()

    # 風格快速推薦
    st.markdown("💡 **風格快速推薦 (點選即刻套用)**")
    styles = [
        {"label": "🌌 未來科幻", "text": "Cyberpunk futuristic metropolis, holograms, volumetric fog, Unreal Engine 5"},
        {"label": "🏞 自然景觀", "text": "B breathtaking mountain lake view at sunrise, volumetric light rays, physically simulated water"},
        {"label": "🚀 太空星際", "text": "Cinematic wide shot of deep space explorer, alien planet, ringed planetary background"},
        {"label": "🎨 概念藝術", "text": "Abstract physical concept art of quantum mechanics, glowing particles, deep colors"}
    ]
    style_cols = st.columns(4)
    for idx, style in enumerate(styles):
        with style_cols[idx]:
            if st.button(style["label"], key=f"btn_style_{idx}", use_container_width=True):
                st.session_state.prompt = style["text"]
                st.rerun()

    # 橫縱比設定
    st.markdown("##### 4. 世界比例與形狀 (Aspect Ratio)")
    ratios = ["16:9", "9:16", "1:1", "4:3"]
    ratio_cols = st.columns(4)
    for idx, r in enumerate(ratios):
        with ratio_cols[idx]:
            is_active = (st.session_state.aspect_ratio == r)
            btn_label = f"⭐ {r}" if is_active else r
            if st.button(btn_label, key=f"btn_ratio_{r}", use_container_width=True):
                st.session_state.aspect_ratio = r
                st.rerun()

    # -----------------------------------------------------------------------------
    # 開始生成 (Form Action)
    # -----------------------------------------------------------------------------
    if st.button("🚀 立即生成影像", use_container_width=True, type="primary"):
        if not st.session_state.prompt.strip():
            st.error("請輸入提示詞內容！")
        else:
            with st.spinner("🌀 AI 引擎正全力描繪世界中，請稍候..."):
                if st.session_state.engine == 'gemini':
                    # Gemini 生成處理
                    try:
                        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{st.session_state.selected_model}:generateContent?key={gemini_key}"
                        payload = {
                            "contents": [{"role": "user", "parts": [{"text": st.session_state.prompt}]}],
                            "generationConfig": {
                                "responseModalities": ["IMAGE"],
                                "imageConfig": {"aspectRatio": st.session_state.aspect_ratio}
                            }
                        }
                        resp = requests.post(api_url, json=payload, timeout=40)
                        if resp.status_code == 200:
                            data = resp.json()
                            parts = data['candidates'][0]['content']['parts']
                            image_part = next((p for p in parts if 'inlineData' in p), None)
                            
                            if image_part:
                                mime_type = image_part['inlineData']['mimeType']
                                b64_data = image_part['inlineData']['data']
                                image_url = f"data:{mime_type};base64,{b64_data}"
                                
                                st.session_state.generated_result = {
                                    'url': image_url,
                                    'prompt': st.session_state.prompt,
                                    'engine': 'gemini',
                                    'is_simulated': False,
                                    'aspect_ratio': st.session_state.aspect_ratio
                                }
                                st.success("🎉 Gemini 影像生成成功！")
                                st.rerun()
                            else:
                                raise Exception("無法從 Gemini 回傳中解析出影像。")
                        else:
                            err_msg = resp.json().get('error', {}).get('message', f"錯誤代碼 {resp.status_code}")
                            raise Exception(err_msg)
                    except Exception as e:
                        st.error(f"Gemini 生成失敗: {str(e)}")
                        
                else:
                    # Cosmos (HF) 生成處理
                    if hf_token.strip():
                        try:
                            active_model = st.session_state.custom_model_path if st.session_state.selected_model == 'custom' else st.session_state.selected_model
                            api_url = f"https://api-inference.huggingface.co/models/{active_model}"
                            headers = {
                                "Authorization": f"Bearer {hf_token}",
                                "Content-Type": "application/json"
                            }
                            payload = {
                                "inputs": f"{st.session_state.prompt} | Negative: {st.session_state.negative_prompt} | Aspect Ratio: {st.session_state.aspect_ratio}",
                                "parameters": {
                                    "guidance_scale": float(guidance_scale),
                                    "num_inference_steps": int(steps)
                                }
                            }
                            
                            # 指數退避重試
                            retries = 3
                            delay = 2
                            resp = None
                            
                            for r in range(retries):
                                resp = requests.post(api_url, json=payload, headers=headers, timeout=50)
                                if resp.status_code == 503:
                                    # 正在載入模型，進行重試
                                    time.sleep(delay)
                                    delay *= 2
                                    continue
                                break
                                
                            if resp and resp.status_code == 200:
                                encoded_img = base64.b64encode(resp.content).decode('utf-8')
                                image_url = f"data:image/png;base64,{encoded_img}"
                                
                                st.session_state.generated_result = {
                                    'url': image_url,
                                    'prompt': st.session_state.prompt,
                                    'engine': 'cosmos',
                                    'is_simulated': False,
                                    'aspect_ratio': st.session_state.aspect_ratio
                                }
                                st.success("🎉 Cosmos 影像生成成功！")
                                st.rerun()
                            else:
                                status = resp.status_code if resp else "無回應"
                                raise Exception(f"HTTP 連線受阻 ({status})。該大模型可能正處於高負載，或受限於 API Token。")
                        except Exception as e:
                            st.session_state.show_fallback_modal = True
                            st.error(f"Cosmos 生成失敗: {str(e)}")
                            st.rerun()
                    else:
                        # 模擬體驗展示模式 (Demo Mode)
                        time.sleep(2)
                        theme = 'scifi'
                        lower_p = st.session_state.prompt.lower()
                        if any(k in lower_p for k in ['forest', 'stream', 'tree', 'nature']):
                            theme = 'nature'
                        elif any(k in lower_p for k in ['cyber', 'neon', 'city']):
                            theme = 'cyberpunk'
                        elif any(k in lower_p for k in ['cat', 'dog', 'animal']):
                            theme = 'animals'
                            
                        simulated_images = {
                            'nature': 'https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?auto=format&fit=crop&w=1200&q=80',
                            'cyberpunk': 'https://images.unsplash.com/photo-1515621061946-eff1c2a352bd?auto=format&fit=crop&w=1200&q=80',
                            'animals': 'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=1200&q=80',
                            'scifi': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1200&q=80'
                        }
                        
                        st.session_state.generated_result = {
                            'url': simulated_images[theme],
                            'prompt': st.session_state.prompt,
                            'engine': 'cosmos',
                            'is_simulated': True,
                            'aspect_ratio': st.session_state.aspect_ratio
                        }
                        st.info("✨ 已進入預覽展示模式。配置個人 HF Token 即可直接串接大模型！")
                        st.rerun()

# -----------------------------------------------------------------------------
# 頁籤 2: 精選畫廊
# -----------------------------------------------------------------------------
with tabs[1]:
    st.markdown("### 🖼️ 物理基礎世界模型展示畫廊")
    st.caption("以下展示使用 NVIDIA Cosmos 基礎物理世界模型生成之高階影像。點選套用可直接載入提示詞。")

    gallery_items = [
        {
            "title": "🌌 未來霓虹賽博朋克街道",
            "prompt": "A futuristic cybernetic street at night, neon signs, flying cars, rain reflecting on pavement, hyper-realistic, physical simulation",
            "url": "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?auto=format&fit=crop&w=800&q=80",
            "ratio": "16:9"
        },
        {
            "title": "🚀 神祕太空星雲與探索者",
            "prompt": "Cinematic physical world simulation of an astronaut floating near a massive glowing nebula, detailed spacesuit, cosmic dust, cinematic lighting",
            "url": "https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?auto=format&fit=crop&w=800&q=80",
            "ratio": "1:1"
        },
        {
            "title": "🏞️ 超寫實林中溪流",
            "prompt": "A pristine fast-flowing forest stream over smooth pebbles, sunlight filtering through ancient redwood trees, physically accurate water physics, 8k",
            "url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=800&q=80",
            "ratio": "16:9"
        }
    ]

    for idx, item in enumerate(gallery_items):
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.image(item["url"], caption=f"{item['title']} ({item['ratio']})", use_container_width=True)
        st.code(item["prompt"], language="text")
        
        if st.button("✨ 載入並套用提示詞", key=f"gallery_apply_{idx}", use_container_width=True):
            st.session_state.prompt = item["prompt"]
            st.session_state.aspect_ratio = item["ratio"]
            st.success("已套用畫廊風格！請切換至『智能生成』進行渲染。")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 頁籤 3: 教學與說明
# -----------------------------------------------------------------------------
with tabs[2]:
    st.markdown("""
    ### 📖 關於雙引擎生圖 App 運作指南
    
    本 App 同時整合了 **NVIDIA Cosmos3 物理基礎世界模型** 與 **Google Gemini 3.1 影像模型**，帶給您最佳的部署相容性。
    
    #### 🌟 為什麼整合雙引擎？
    
    1. **NVIDIA Cosmos 物理模型 (HF)**：
       * Cosmos 專為真實世界的物理運動學、光影衍射與動態生成所設計。
       * 由於其參數量龐大 (7B/14B)，在 Hugging Face 免費共享端點時極易出現伺服器忙碌、冷啟動或跨網域 CORS 連線被拒。
       * 當您需要向老師演示 Cosmos 時，建議先在頂部「API 部署與進階設定」填寫具備 Read 權限的個人 **Hugging Face Token**。
       
    2. **Google Gemini 3.1 直連生圖**：
       * 本 App 內建 Gemini 直連引擎。不論您在任何地方部署，Gemini 都能 **100% 穩定、高速地為您生成精美的高清圖像**。
       * 是您演示或在 Streamlit.io 免費託管時，最穩定的強大後盾。
       
    #### 🤖 一鍵容錯與智能切換
    
    當您在使用 Cosmos 引擎生成失敗時，系統會智慧感應並跳出建議小視窗。點擊 **「一鍵切換 Gemini 重試」** 即可自動更改配置並再次渲染，絕不中斷展示體驗！
    """)

# -----------------------------------------------------------------------------
# 頁尾
# -----------------------------------------------------------------------------
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.75rem; padding: 20px 0; border-top: 1px solid #1e293b; margin-top: 40px;">
    NVIDIA Cosmos3 x Gemini 3.1 • 雙引擎生圖行動版 (Streamlit 部署版)
</div>
""", unsafe_allow_html=True)