import streamlit as st
import requests
import pandas as pd
import hashlib
import os
import datetime
import json
import base64
from datetime import timedelta
from cryptography.fernet import Fernet

# Set page config for a wider, modern layout
st.set_page_config(
    page_title="RPA - Registro de Pensamentos Automáticos",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== INICIALIZAÇÃO DO SESSION STATE ==========
if 'user' not in st.session_state:
    st.session_state.user = None
if 'api_url' not in st.session_state:
    st.session_state.api_url = ""
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'encryption_key' not in st.session_state:
    st.session_state.encryption_key = None

# Custom CSS with refined color system for light and dark themes
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* ========== SISTEMA DE CORES PADRONIZADO ========== */
    /* Light Theme Cores */
    :root {
        --primary: #0f766e;
        --primary-dark: #0d5c56;
        --primary-light: #14b8a6;
        --primary-gradient: linear-gradient(135deg, #0f766e, #0284c7);
        --secondary: #0284c7;
        --secondary-dark: #0369a1;
        --success: #16a34a;
        --warning: #d97706;
        --danger: #dc2626;
        --info: #06b6d4;
        
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --bg-tertiary: #f1f5f9;
        --surface: #ffffff;
        
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-tertiary: #64748b;
        --text-muted: #94a3b8;
        
        --border-light: #e2e8f0;
        --border-medium: #cbd5e1;
        
        --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.03), 0 1px 2px rgba(0, 0, 0, 0.05);
        --card-hover-shadow: 0 20px 25px -12px rgba(0, 0, 0, 0.1);
    }
    
    /* Dark Theme Cores - Automático via media query */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-tertiary: #334155;
            --surface: #1e293b;
            
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
            --text-tertiary: #94a3b8;
            --text-muted: #64748b;
            
            --border-light: #334155;
            --border-medium: #475569;
            
            --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            --card-hover-shadow: 0 20px 25px -12px rgba(0, 0, 0, 0.3);
        }
    }
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* ========== BARRA DE NAVEGAÇÃO (TABS) ========== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 40px;
        padding: 8px 24px;
        font-weight: 600;
        transition: all 0.2s ease;
        background-color: var(--bg-tertiary);
        color: var(--text-secondary);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: var(--border-light);
        color: var(--primary-light);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0f766e, #0284c7);
        color: white !important;
    }
    
    /* ========== SIDEBAR ========== */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-light);
    }
    
    /* ========== TÍTULOS ========== */
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #0f766e, #0284c7, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: var(--text-tertiary);
        text-align: center;
        margin-bottom: 2rem;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary);
    }
    
    p {
        color: var(--text-secondary);
    }
    
    /* ========== ANIMAÇÕES ========== */
    @keyframes cardFadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* ========== CARDS DE PENSAMENTO ========== */
    .thought-card-premium {
        background: var(--surface);
        border: 1px solid var(--border-light);
        border-left: 6px solid var(--primary);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 24px;
        box-shadow: var(--card-shadow);
        animation: cardFadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) both;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .thought-card-premium::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 100px;
        height: 100px;
        background: radial-gradient(circle, rgba(15, 118, 110, 0.03) 0%, transparent 70%);
        pointer-events: none;
    }
    
    .thought-card-premium:hover {
        transform: translateY(-4px);
        box-shadow: var(--card-hover-shadow);
        border-color: var(--border-medium);
    }
    
    /* ========== BADGES ========== */
    .badge-premium {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 10px;
        margin-bottom: 10px;
        letter-spacing: 0.3px;
        transition: transform 0.2s ease;
    }
    
    .badge-premium:hover {
        transform: scale(1.05);
    }
    
    .bp-date {
        background: rgba(22, 163, 74, 0.1);
        color: var(--success);
        border: 1px solid rgba(22, 163, 74, 0.2);
    }
    
    .bp-location {
        background: rgba(2, 132, 199, 0.1);
        color: var(--secondary);
        border: 1px solid rgba(2, 132, 199, 0.2);
    }
    
    .bp-emotion {
        background: rgba(220, 38, 38, 0.1);
        color: var(--danger);
        border: 1px solid rgba(220, 38, 38, 0.2);
    }
    
    @media (prefers-color-scheme: dark) {
        .bp-date { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
        .bp-location { background: rgba(14, 165, 233, 0.15); color: #38bdf8; }
        .bp-emotion { background: rgba(244, 63, 94, 0.15); color: #fb7185; }
    }
    
    /* ========== SEÇÕES DE PENSAMENTO ========== */
    .thought-section {
        display: flex;
        gap: 16px;
        margin-top: 20px;
        align-items: flex-start;
        animation: slideIn 0.3s ease;
    }
    
    .thought-section-icon {
        font-size: 1.5rem;
        padding: 8px;
        border-radius: 12px;
        background: var(--bg-tertiary);
        width: 44px;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
    }
    
    .thought-section-icon:hover {
        transform: scale(1.1);
        background: var(--border-light);
    }
    
    .thought-section-body {
        flex: 1;
    }
    
    .section-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-muted);
        font-weight: 700;
        margin-bottom: 6px;
    }
    
    .section-content {
        font-size: 1rem;
        color: var(--text-secondary);
        line-height: 1.6;
    }
    
    /* ========== QUOTE BOX ========== */
    .thought-quote-box {
        background: rgba(22, 163, 74, 0.05);
        border-left: 4px solid var(--success);
        border-radius: 12px;
        padding: 20px 24px;
        margin: 20px 0;
        transition: all 0.3s ease;
    }
    
    .thought-quote-box:hover {
        transform: translateX(4px);
        background: rgba(22, 163, 74, 0.08);
    }
    
    .thought-quote-box-text {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--primary);
        font-style: italic;
        line-height: 1.5;
    }
    
    /* ========== GLASS PANEL ========== */
    .glass-panel {
        background: rgba(15, 118, 110, 0.04);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(15, 118, 110, 0.1);
        border-radius: 24px;
        padding: 28px;
        margin-bottom: 24px;
    }
    
    /* ========== ENCRYPTED BADGE ========== */
    .encrypted-badge {
        background: rgba(217, 119, 6, 0.1);
        color: var(--warning);
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        letter-spacing: 0.5px;
        transition: all 0.2s ease;
    }
    
    .encrypted-badge:hover {
        transform: scale(1.05);
        background: rgba(217, 119, 6, 0.15);
    }
    
    /* ========== METRIC CARDS ========== */
    .metric-card {
        background: var(--surface);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        border: 1px solid var(--border-light);
        transition: all 0.3s ease;
        animation: cardFadeIn 0.4s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--card-shadow);
        border-color: var(--primary-light);
    }
    
    .metric-card h3 {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* ========== PAGE HEADER ========== */
    .page-header {
        background: linear-gradient(135deg, rgba(15, 118, 110, 0.05), rgba(2, 132, 199, 0.05));
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 24px;
        border: 1px solid rgba(15, 118, 110, 0.1);
    }
    
    /* ========== BOTÕES ========== */
    .stButton > button {
        border-radius: 40px;
        font-weight: 600;
        transition: all 0.2s ease;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        border: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(15, 118, 110, 0.3);
    }
    
    /* Botão secundário */
    .stButton > button[data-baseweb="button"][kind="secondary"] {
        background: transparent;
        border: 1px solid var(--border-medium);
        color: var(--text-secondary);
    }
    
    /* ========== FORM CONTAINER ========== */
    .form-container {
        background: var(--surface);
        border-radius: 24px;
        padding: 24px;
        border: 1px solid var(--border-light);
    }
    
    /* ========== EMPTY STATE ========== */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        background: var(--bg-secondary);
        border-radius: 24px;
        border: 2px dashed var(--border-light);
    }
    
    .empty-state h3 {
        color: var(--text-primary);
        margin: 16px 0 8px 0;
    }
    
    /* ========== FILTER SECTION ========== */
    .filter-section {
        background: var(--bg-tertiary);
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 24px;
        border: 1px solid var(--border-light);
    }
    
    /* ========== INFO BOXES ========== */
    .stAlert {
        border-radius: 12px;
    }
    
    /* ========== DIVIDERS ========== */
    hr {
        border-color: var(--border-light);
    }
    
    /* ========== EXPANDER ========== */
    .streamlit-expanderHeader {
        background: var(--bg-tertiary);
        border-radius: 12px;
        color: var(--text-primary);
    }
    
    /* ========== DATAFRAME ========== */
    .stDataFrame {
        border-radius: 12px;
        border: 1px solid var(--border-light);
    }
    
    /* ========== INPUT FIELDS ========== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        border-radius: 12px;
        border-color: var(--border-light);
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 2px rgba(15, 118, 110, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# ========== FUNÇÕES DE CRIPTOGRAFIA ==========
def get_encryption_key():
    """Gera ou recupera a chave de criptografia baseada na API Key"""
    if st.session_state.encryption_key is not None:
        return st.session_state.encryption_key
    
    _, api_key = get_api_credentials()
    if not api_key:
        return None
    
    key_material = api_key.encode()
    key_bytes = hashlib.sha256(key_material).digest()
    key_b64 = base64.urlsafe_b64encode(key_bytes)
    fernet_key = Fernet(key_b64)
    
    st.session_state.encryption_key = fernet_key
    return fernet_key

def encrypt_record(record_dict: dict) -> str:
    """Criptografa um registro e retorna string base64"""
    fernet = get_encryption_key()
    if not fernet:
        raise Exception("Chave de criptografia não disponível")
    
    record_dict['encrypted_at'] = datetime.datetime.now().isoformat()
    
    json_str = json.dumps(record_dict, ensure_ascii=False)
    encrypted = fernet.encrypt(json_str.encode())
    return encrypted.decode()

def decrypt_record(encrypted_str: str) -> dict:
    """Descriptografa um registro e retorna o dicionário"""
    fernet = get_encryption_key()
    if not fernet:
        raise Exception("Chave de criptografia não disponível")
    
    decrypted = fernet.decrypt(encrypted_str.encode())
    return json.loads(decrypted.decode())

# ========== FUNÇÕES AUXILIARES ==========
def hash_password(username, password):
    """Hashes password using SHA-256 with username as salt"""
    salt = username.strip().lower()
    return hashlib.sha256((salt + password).encode()).hexdigest()

def convert_to_local(timestamp_str):
    if not timestamp_str:
        return ""
    try:
        clean_str = timestamp_str.replace("Z", "+00:00")
        dt_utc = datetime.datetime.fromisoformat(clean_str)
        dt_local = dt_utc.astimezone()
        return dt_local.strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        return timestamp_str

# ========== API CREDENTIALS MANAGEMENT ==========
def get_api_credentials():
    try:
        if "api" in st.secrets:
            return st.secrets["api"].get("url", ""), st.secrets["api"].get("key", "")
    except Exception:
        pass
    
    if "api_url" in st.session_state and "api_key" in st.session_state:
        return st.session_state["api_url"], st.session_state["api_key"]
    
    return "", ""

def save_credentials(url, key):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        secrets_dir = os.path.join(base_dir, ".streamlit")
        os.makedirs(secrets_dir, exist_ok=True)
        
        secrets_file = os.path.join(secrets_dir, "secrets.toml")
        with open(secrets_file, "w", encoding="utf-8") as f:
            f.write("[api]\n")
            f.write(f'url = "{url}"\n')
            f.write(f'key = "{key}"\n')
            
        st.session_state["api_url"] = url
        st.session_state["api_key"] = key
        st.session_state.encryption_key = None
        return True
    except Exception as e:
        st.error(f"Erro ao salvar credenciais: {e}")
        return False

def call_api(action, method="GET", params=None, json_data=None):
    """Generic API caller for Google Apps Script Web App"""
    api_url, api_key = get_api_credentials()
    if not api_url:
        return {"success": False, "error": "URL da API não configurada."}
    
    if params is None:
        params = {}
    params["apiKey"] = api_key
    params["action"] = action
    
    if json_data is None:
        json_data = {}
    json_data["apiKey"] = api_key
    json_data["action"] = action
    
    try:
        if method == "GET":
            response = requests.get(api_url, params=params, timeout=15)
        else:
            response = requests.post(api_url, json=json_data, timeout=15)
            
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "error": f"Erro HTTP {response.status_code}: {response.text}"}
    except Exception as e:
        return {"success": False, "error": f"Falha na conexão: {str(e)}"}

# ========== PÁGINAS ==========
def render_setup_page():
    st.markdown("<h1 class='main-title'>🧠 RPA</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Registro de Pensamentos Automáticos</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.container():
            st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
            st.subheader("⚙️ Configurar Conexão")
            st.info("🔐 O sistema utiliza Google Sheets como banco de dados com criptografia de ponta a ponta.")
            
            with st.form("setup_form"):
                url = st.text_input("URL do Web App", 
                                   placeholder="https://script.google.com/macros/s/.../exec",
                                   help="Cole a URL gerada após o deploy do Apps Script")
                key = st.text_input("Chave da API", type="password", 
                                   value="RPA_SECRET_SECURE_TOKEN_2026",
                                   help="Use a mesma chave definida no const API_KEY do Apps Script")
                
                submit = st.form_submit_button("🔌 Conectar", use_container_width=True, type="primary")
                
                if submit:
                    if not url:
                        st.error("❌ Preencha a URL do Web App")
                    else:
                        if save_credentials(url, key):
                            st.success("✅ Configurações salvas!")
                            with st.spinner("🔄 Testando conexão..."):
                                res = call_api("setup", method="GET")
                                if res.get("success"):
                                    st.success("🎉 Conexão estabelecida com sucesso!")
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error(f"❌ Erro: {res.get('error', 'Sem resposta')}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown("### 📋 Guia Rápido")
        st.markdown("""
        1. 📊 Crie uma planilha Google
        2. 📝 Abra o Editor de Script
        3. 💻 Cole o código do Apps Script
        4. 🔑 Execute `setupSheets`
        5. 🚀 Publique como Web App
        6. 🔗 Cole a URL aqui
        
        ---
        
        **🔒 Segurança**  
        Dados são criptografados antes do envio
        
        ---
        
        **👤 Credenciais padrão**  
        `admin` / `admin123`
        """)
        st.markdown('</div>', unsafe_allow_html=True)

def render_login_page():
    st.markdown("<h1 class='main-title'>🧠 RPA</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Registro de Pensamentos Automáticos</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; margin-bottom: 24px;'>🔐 Acesso ao Sistema</h3>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("👤 Usuário", placeholder="Seu nome de usuário").strip()
            password = st.text_input("🔒 Senha", type="password", placeholder="Sua senha")
            
            submit = st.form_submit_button("🚀 Entrar", use_container_width=True, type="primary")
            
            if submit:
                if not username or not password:
                    st.error("❌ Preencha usuário e senha")
                else:
                    pass_hash = hash_password(username, password)
                    with st.spinner("🔄 Autenticando..."):
                        res = call_api("login", "GET", params={"username": username, "passwordHash": pass_hash})
                        
                        if res.get("success"):
                            st.session_state.user = res.get("user")
                            st.success(f"✨ Bem-vindo, {username}!")
                            st.rerun()
                        else:
                            st.error(f"❌ {res.get('error', 'Erro ao realizar login')}")
        
        st.markdown("---")
        st.caption("🔒 Todos os dados são criptografados antes de serem transmitidos")
        st.markdown('</div>', unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.markdown("<div style='text-align: center; padding: 16px 0;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='margin: 8px 0;'>RPA</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b; font-size: 0.8rem;'>Registro de Pensamentos</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.session_state.user is not None:
            user = st.session_state.user
            st.markdown("---")
            
            # User info card
            st.markdown(f"""
            <div style='background: rgba(15, 118, 110, 0.1); border-radius: 16px; padding: 16px; margin: 8px 0;'>
                <p style='margin: 0; font-size: 0.75rem; color: #64748b;'>USUÁRIO</p>
                <p style='margin: 4px 0 0 0; font-weight: 600; font-size: 1rem;'>@{user['username']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            role_colors = {"Admin": "#3b82f6", "Mediador": "#0d9488", "Paciente": "#f59e0b"}
            role_color = role_colors.get(user['role'], "#6b7280")
            st.markdown(f"""
            <div style='background: {role_color}15; border-radius: 12px; padding: 8px 12px; margin: 8px 0; text-align: center;'>
                <span style='color: {role_color}; font-weight: 700; font-size: 0.85rem;'>{user['role']}</span>
            </div>
            """, unsafe_allow_html=True)
            
            if user['role'] == 'Paciente' and user.get('mediator'):
                st.info(f"👨‍⚕️ Mediador: **{user['mediator']}**")
            
            st.markdown("---")
            st.markdown('<div style="text-align: center;"><span class="encrypted-badge">🔒 Criptografia Ativa</span></div>', unsafe_allow_html=True)
            st.markdown("---")
            
            with st.expander("⚙️ Configurações", expanded=False):
                api_url, _ = get_api_credentials()
                st.caption(f"📡 URL: `{api_url[:35]}...`" if api_url else "⚡ Não configurada")
                if st.button("🔌 Desconectar Planilha", use_container_width=True):
                    st.session_state["api_url"] = ""
                    st.session_state["api_key"] = ""
                    st.session_state.encryption_key = None
                    secrets_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".streamlit", "secrets.toml")
                    if os.path.exists(secrets_file):
                        os.remove(secrets_file)
                    st.session_state.user = None
                    st.rerun()
            
            if st.button("🚪 Sair", use_container_width=True, type="secondary"):
                st.session_state.user = None
                st.rerun()
        else:
            st.markdown("---")
            st.info("🔐 Faça login para acessar o sistema")

def render_admin_page():
    st.markdown("<h2>🛡️ Painel do Administrador</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; margin-bottom: 24px;'>Gerencie usuários, vínculos e permissões do sistema</p>", unsafe_allow_html=True)
    
    tab_create, tab_manage, tab_link = st.tabs(["➕ Criar Usuário", "📋 Gerenciar", "🔗 Vincular Mediador"])
    
    mediators_res = call_api("getMediators", "GET")
    mediators = mediators_res.get("mediators", []) if mediators_res.get("success") else []
    
    users_res = call_api("getUsers", "GET")
    users = users_res.get("users", []) if users_res.get("success") else []
    patients = [u for u in users if u.get('role') == 'Paciente']
    
    with tab_create:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            with st.form("create_user_form", clear_on_submit=True):
                st.subheader("📝 Dados do Usuário")
                new_username = st.text_input("Nome de Usuário", placeholder="ex: joaosilva").strip().lower()
                new_password = st.text_input("Senha Inicial", type="password", placeholder="Mínimo 4 caracteres")
                new_role = st.selectbox("Cargo", ["Paciente", "Mediador", "Admin"])
                
                selected_mediator = ""
                if new_role == "Paciente":
                    mediator_options = ["Nenhum"] + mediators
                    selected_mediator = st.selectbox("Vincular a Mediador", mediator_options)
                    if selected_mediator == "Nenhum":
                        selected_mediator = ""
                
                create_submit = st.form_submit_button("✅ Salvar Usuário", use_container_width=True, type="primary")
                
                if create_submit:
                    if not new_username or not new_password:
                        st.error("❌ Nome e senha obrigatórios")
                    elif len(new_password) < 4:
                        st.error("❌ Senha deve ter pelo menos 4 caracteres")
                    else:
                        pass_hash = hash_password(new_username, new_password)
                        post_data = {
                            "username": new_username,
                            "passwordHash": pass_hash,
                            "role": new_role,
                            "mediator": selected_mediator
                        }
                        res = call_api("createUser", "POST", json_data=post_data)
                        if res.get("success"):
                            st.success(f"✅ Usuário `{new_username}` criado com sucesso!")
                            st.rerun()
                        else:
                            st.error(f"❌ {res.get('error', 'Erro ao criar usuário')}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
            st.markdown("### ℹ️ Regras de Cargos")
            st.markdown("""
            | Cargo | Função |
            |-------|--------|
            | 🧠 **Paciente** | Registra pensamentos automáticos |
            | 👨‍⚕️ **Mediador** | Visualiza registros dos pacientes |
            | 🛡️ **Admin** | Gerencia todos os usuários |
            
            ---
            
            **🔒 Segurança**  
            Todos os registros são criptografados antes do envio ao servidor.
            """)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab_manage:
        if users_res.get("success"):
            if not users:
                st.info("📭 Nenhum usuário cadastrado.")
            else:
                df_users = pd.DataFrame(users)
                try:
                    if 'created_at' in df_users.columns:
                        df_users['created_at'] = pd.to_datetime(df_users['created_at'])
                        df_users['created_at'] = df_users['created_at'].dt.strftime('%d/%m/%Y %H:%M')
                except:
                    pass
                
                search_q = st.text_input("🔍 Buscar usuário", placeholder="Digite o nome...", value="").strip().lower()
                if search_q:
                    df_users = df_users[df_users['username'].str.contains(search_q)]
                
                st.dataframe(
                    df_users.rename(columns={
                        'username': 'Usuário',
                        'role': 'Cargo',
                        'mediator': 'Mediador Vinculado',
                        'created_at': 'Cadastro'
                    }), 
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown("---")
                st.subheader("✏️ Ações Rápidas")
                
                usernames = [u['username'] for u in users if u['username'].lower() != 'admin']
                if usernames:
                    selected_user = st.selectbox("Selecione um usuário", usernames)
                    
                    col_pw, col_del = st.columns(2)
                    
                    with col_pw:
                        with st.expander("🔑 Alterar Senha", expanded=True):
                            new_pw = st.text_input("Nova Senha", type="password", key=f"pw_{selected_user}")
                            if st.button("✅ Confirmar", key=f"btn_pw_{selected_user}", use_container_width=True):
                                if not new_pw:
                                    st.error("❌ Insira a nova senha")
                                elif len(new_pw) < 4:
                                    st.error("❌ Mínimo 4 caracteres")
                                else:
                                    new_hash = hash_password(selected_user, new_pw)
                                    with st.spinner("🔄 Atualizando..."):
                                        res = call_api("updatePassword", "POST", json_data={"username": selected_user, "passwordHash": new_hash})
                                        if res.get("success"):
                                            st.success("✅ Senha alterada com sucesso!")
                                        else:
                                            st.error(f"❌ {res.get('error')}")
                    
                    with col_del:
                        with st.expander("⚠️ Excluir Usuário", expanded=True):
                            st.warning("Esta ação é permanente!")
                            confirm_del = st.checkbox(f"Confirmo exclusão de `{selected_user}`", key=f"chk_del_{selected_user}")
                            if st.button("🗑️ Excluir", key=f"btn_del_{selected_user}", disabled=not confirm_del, use_container_width=True):
                                with st.spinner("🔄 Excluindo..."):
                                    res = call_api("deleteUser", "POST", json_data={"username": selected_user})
                                    if res.get("success"):
                                        st.success("✅ Usuário excluído com sucesso!")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {res.get('error')}")
                else:
                    st.info("📭 Nenhum outro usuário disponível")
        else:
            st.error(f"❌ {users_res.get('error')}")
    
    with tab_link:
        st.subheader("🔗 Vincular Mediador a Paciente")
        
        if not patients:
            st.warning("📭 Nenhum paciente cadastrado. Crie pacientes primeiro.")
        elif not mediators:
            st.warning("📭 Nenhum mediador cadastrado. Crie mediadores primeiro.")
        else:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                patient_options = {p['username']: p for p in patients}
                selected_patient = st.selectbox("👤 Paciente", list(patient_options.keys()))
                patient_data = patient_options[selected_patient]
                mediator_atual = patient_data.get('mediator', '')
                
                st.info(f"📌 Mediador atual: **{mediator_atual if mediator_atual else 'Nenhum'}**")
            
            with col2:
                mediator_options = ["Nenhum"] + mediators
                current_index = 0 if mediator_atual == '' else (mediator_options.index(mediator_atual) if mediator_atual in mediator_options else 0)
                new_mediator = st.selectbox("👨‍⚕️ Novo Mediador", mediator_options, index=current_index)
                if new_mediator == "Nenhum":
                    new_mediator = ""
            
            if st.button("🔄 Atualizar Vínculo", type="primary", use_container_width=True):
                with st.spinner("🔄 Atualizando..."):
                    update_res = call_api("updateUserMediator", "POST", json_data={
                        "username": selected_patient,
                        "mediator": new_mediator
                    })
                    if update_res.get("success"):
                        st.success(f"✅ Paciente {selected_patient} agora vinculado a {new_mediator or 'nenhum mediador'}")
                        st.rerun()
                    else:
                        st.error(f"❌ {update_res.get('error', 'Erro ao atualizar vínculo')}")

def render_paciente_page():
    user = st.session_state.user
    
    # Header estilizado
    st.markdown(f"""
    <div class="page-header">
        <h2 style="margin: 0; color: var(--primary);">🧠 Olá, {user['username'].capitalize()}!</h2>
        <p style="margin: 8px 0 0 0; color: var(--text-tertiary);">Registre e acompanhe seus pensamentos automáticos de forma segura</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<p><span class='encrypted-badge'>🔒 Seus dados são criptografados antes do envio</span></p>", unsafe_allow_html=True)
    
    tab_new, tab_history = st.tabs(["📝 Novo Registro", "📊 Meus Registros"])
    
    with tab_new:
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.subheader("📝 Registro de Pensamento Automático")
        st.caption("Preencha todos os campos abaixo seguindo a técnica RPA da TCC")
        
        with st.form("rpa_form", clear_on_submit=True):
            col_d, col_l = st.columns(2)
            with col_d:
                date_input = st.date_input("📅 Data do Ocorrido", datetime.date.today())
            with col_l:
                location_input = st.text_input("📍 Local", placeholder="Ex: No trabalho, em casa...")
                
            situation = st.text_area("1️⃣ Situação", 
                                    placeholder="O que aconteceu? Quem estava com você? O que você estava fazendo?",
                                    height=100,
                                    help="Descreva o fato concreto objetivamente")
            
            thought = st.text_area("2️⃣ Pensamento Automático", 
                                   placeholder="O que passou pela sua cabeça naquele momento? O que isso diz sobre você?",
                                   height=100,
                                   help="Escreva as palavras exatas que surgiram na sua mente")
            
            emotion = st.text_input("3️⃣ Emoção e Intensidade", 
                                    placeholder="Ex: Ansiedade (80%), Tristeza (60%), Raiva (40%)",
                                    help="Identifique as emoções e dê uma nota de 0 a 100%")
            
            behavior = st.text_area("4️⃣ Comportamento Resposta", 
                                    placeholder="O que você fez após o pensamento? Qual foi sua reação?",
                                    height=80,
                                    help="Descreva suas ações físicas ou reações fisiológicas")
            
            submit_rpa = st.form_submit_button("🔒 Salvar Registro (Criptografado)", use_container_width=True, type="primary")
            
            if submit_rpa:
                if not all([situation, thought, emotion, behavior]):
                    st.error("❌ Todos os campos são obrigatórios!")
                else:
                    date_local = f"{date_input.strftime('%d/%m/%Y')} - {location_input}" if location_input else date_input.strftime('%d/%m/%Y')
                    record_data = {
                        "patient": user['username'],
                        "dateLocal": date_local,
                        "situation": situation,
                        "thought": thought,
                        "emotion": emotion,
                        "behavior": behavior
                    }
                    
                    try:
                        encrypted_data = encrypt_record(record_data)
                        
                        with st.spinner("🔒 Criptografando e salvando..."):
                            res = call_api("addRecordEncrypted", "POST", json_data={
                                "encryptedData": encrypted_data,
                                "patient": user['username'],
                                "dateLocal": date_local
                            })
                            
                            if res.get("success"):
                                st.success("✅ Registro salvo com segurança!")
                                st.balloons()
                            else:
                                st.error(f"❌ {res.get('error', 'Erro ao gravar registro')}")
                    except Exception as e:
                        st.error(f"❌ Erro na criptografia: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab_history:
        # Header com estatísticas
        st.markdown('<div class="page-header" style="padding: 16px;">', unsafe_allow_html=True)
        st.subheader("📋 Seus Pensamentos Registrados")
        st.markdown('<p style="color: var(--text-tertiary); margin: 0;">Aqui está o histórico completo dos seus registros de pensamentos automáticos</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.spinner("🔄 Carregando seus registros..."):
            res = call_api("getPatientRecordsEncrypted", "GET", params={"patient": user['username']})
            
        if res.get("success"):
            records = res.get("records", [])
            
            if not records:
                # Empty state melhorado
                st.markdown("""
                <div class="empty-state">
                    <p style="font-size: 3rem; margin: 0;">📭</p>
                    <h3>Nenhum registro encontrado</h3>
                    <p>Você ainda não possui pensamentos automáticos registrados.</p>
                    <p>Que tal fazer o seu primeiro registro agora?</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Métricas em cards
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>{len(records)}</h3>
                        <p>Total de Registros</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Processar registros
                decrypted_records = []
                decryption_errors = 0
                
                for record in records:
                    try:
                        if isinstance(record, dict):
                            encrypted_data = record.get('encrypted_data', '')
                        else:
                            encrypted_data = record
                            
                        if encrypted_data:
                            dec = decrypt_record(encrypted_data)
                            decrypted_records.append(dec)
                    except Exception as e:
                        decryption_errors += 1
                
                if decryption_errors > 0:
                    st.warning(f"⚠️ {decryption_errors} registro(s) não puderam ser descriptografados")
                
                if decrypted_records:
                    # Filtros melhorados
                    with st.expander("🔍 Filtrar Registros", expanded=False):
                        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
                        col_f1, col_f2 = st.columns(2)
                        with col_f1:
                            search_emotion = st.text_input("Filtrar por Emoção", placeholder="Digite a emoção...", key="filter_emotion").strip().lower()
                        with col_f2:
                            search_date = st.text_input("Filtrar por Data", placeholder="DD/MM/AAAA", key="filter_date").strip()
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    filtered_records = decrypted_records.copy()
                    
                    if search_emotion:
                        filtered_records = [r for r in filtered_records if search_emotion in r.get('emotion', '').lower()]
                    
                    if search_date:
                        filtered_records = [r for r in filtered_records if search_date in r.get('dateLocal', '')]
                    
                    # Mostrar contagem filtrada
                    if len(filtered_records) != len(decrypted_records):
                        st.info(f"📊 Mostrando {len(filtered_records)} de {len(decrypted_records)} registros")
                    
                    # Timeline de registros
                    for idx, r in enumerate(reversed(filtered_records)):
                        # Ícone diferente para cada tipo de emoção
                        emotion_lower = r.get('emotion', '').lower()
                        if "feliz" in emotion_lower or "alegre" in emotion_lower:
                            emotion_icon = "😊"
                        elif "triste" in emotion_lower:
                            emotion_icon = "😢"
                        elif "raiva" in emotion_lower or "raivoso" in emotion_lower:
                            emotion_icon = "😠"
                        elif "ansiedade" in emotion_lower or "ansioso" in emotion_lower:
                            emotion_icon = "😰"
                        elif "medo" in emotion_lower:
                            emotion_icon = "😨"
                        elif "calma" in emotion_lower or "tranquilo" in emotion_lower:
                            emotion_icon = "😌"
                        else:
                            emotion_icon = "🧠"
                        
                        card_html = f'''
                        <div class="thought-card-premium" style="animation-delay: {idx * 0.05}s;">
                            <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; align-items: center;">
                                <span class="badge-premium bp-date">📅 {r.get('dateLocal', 'Data não informada')}</span>
                                <span class="badge-premium bp-emotion">{emotion_icon} {r.get('emotion', 'Emoção não informada')}</span>
                                <span class="encrypted-badge" style="margin-left: auto;">🔒 Criptografado</span>
                            </div>
                            <div class="thought-section">
                                <div class="thought-section-icon">🔍</div>
                                <div class="thought-section-body">
                                    <div class="section-label">1. Situação</div>
                                    <div class="section-content">{r.get('situation', '')}</div>
                                </div>
                            </div>
                            <div class="thought-quote-box">
                                <div class="section-label">2. Pensamento Automático</div>
                                <div class="thought-quote-box-text">"{r.get('thought', '')}"</div>
                            </div>
                            <div class="thought-section">
                                <div class="thought-section-icon">⚡</div>
                                <div class="thought-section-body">
                                    <div class="section-label">3. Comportamento Resposta</div>
                                    <div class="section-content">{r.get('behavior', '')}</div>
                                </div>
                            </div>
                        </div>
                        '''
                        st.markdown(card_html, unsafe_allow_html=True)
                    
                    # Botão para exportar
                    if filtered_records:
                        st.markdown("---")
                        df_export = pd.DataFrame(filtered_records)
                        csv_data = df_export.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label="📥 Exportar todos os registros (CSV)",
                            data=csv_data,
                            file_name=f"RPA_{user['username']}_{datetime.date.today()}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
        else:
            st.error(f"❌ {res.get('error')}")

def render_mediador_page():
    user = st.session_state.user
    
    st.markdown(f"<h2>🩺 Painel Clínico - Dr(a). {user['username'].capitalize()}</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: var(--text-tertiary); margin-bottom: 24px;'>Acompanhe os registros de pensamentos automáticos dos seus pacientes</p>", unsafe_allow_html=True)
    
    with st.spinner("🔄 Carregando dados dos pacientes..."):
        res = call_api("getMediatorPatientsEncrypted", "GET", params={"mediator": user['username']})
        
    if not res.get("success"):
        st.error(f"❌ {res.get('error')}")
        return
        
    patients = res.get("patients", [])
    all_encrypted_records = res.get("records", {})
    
    if not patients:
        st.markdown("""
        <div class="glass-panel" style="text-align: center; padding: 48px;">
            <h3>📭 Nenhum paciente vinculado</h3>
            <p>Você não possui pacientes vinculados ao seu perfil.</p>
            <p style="color: var(--text-tertiary);">Solicite ao <b>Administrador</b> que vincule pacientes a você.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    tabs = st.tabs([f"👤 {patient_name.capitalize()}" for patient_name in patients])
    
    for i, patient_name in enumerate(patients):
        with tabs[i]:
            encrypted_records = all_encrypted_records.get(patient_name, [])
            
            if encrypted_records:
                records = []
                for enc in encrypted_records:
                    try:
                        dec = decrypt_record(enc)
                        records.append(dec)
                    except Exception as e:
                        st.error(f"❌ Erro ao descriptografar: {e}")
                
                if records:
                    records.sort(key=lambda x: x.get('encrypted_at', ''), reverse=True)
                    
                    with st.expander("🔍 Filtros", expanded=False):
                        col_f1, col_f2 = st.columns(2)
                        with col_f1:
                            search_emotion = st.text_input("Emoção", "", key=f"emo_{patient_name}").strip().lower()
                        with col_f2:
                            search_text = st.text_input("Buscar texto", "", key=f"text_{patient_name}").strip().lower()
                    
                    filtered_records = records.copy()
                    
                    if search_emotion:
                        filtered_records = [r for r in filtered_records if search_emotion in r.get('emotion', '').lower()]
                    
                    if search_text:
                        filtered_records = [r for r in filtered_records if 
                                          search_text in r.get('situation', '').lower() or 
                                          search_text in r.get('thought', '').lower() or 
                                          search_text in r.get('behavior', '').lower()]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>{len(records)}</h3>
                            <p>Total</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>{len(filtered_records)}</h3>
                            <p>Filtrados</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        st.markdown('<div class="metric-card"><span class="encrypted-badge">🔒 Criptografados</span></div>', unsafe_allow_html=True)
                    
                    if filtered_records:
                        df_export = pd.DataFrame(filtered_records)
                        csv_data = df_export.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label="📥 Exportar CSV",
                            data=csv_data,
                            file_name=f"RPA_{patient_name}_{datetime.date.today()}.csv",
                            mime="text/csv",
                            key=f"dl_{patient_name}",
                            use_container_width=True
                        )
                    
                    if not filtered_records:
                        st.warning("📭 Nenhum registro corresponde aos filtros")
                    else:
                        for r in filtered_records:
                            emotion_lower = r.get('emotion', '').lower()
                            if "feliz" in emotion_lower:
                                emotion_icon = "😊"
                            elif "triste" in emotion_lower:
                                emotion_icon = "😢"
                            elif "raiva" in emotion_lower:
                                emotion_icon = "😠"
                            elif "ansiedade" in emotion_lower:
                                emotion_icon = "😰"
                            else:
                                emotion_icon = "🧠"
                            
                            card_html = f'''
                                <div class="thought-card-premium">
                                    <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px;">
                                        <span class="badge-premium bp-date">📅 {r.get('dateLocal', '')}</span>
                                        <span class="badge-premium bp-emotion">{emotion_icon} {r.get('emotion', '')}</span>
                                        <span class="encrypted-badge" style="margin-left: auto;">🔒 Criptografado</span>
                                    </div>
                                    <div class="thought-section">
                                        <div class="thought-section-icon">🔍</div>
                                        <div class="thought-section-body">
                                            <div class="section-label">1. Situação</div>
                                            <div class="section-content">{r.get('situation', '')}</div>
                                        </div>
                                    </div>
                                    <div class="thought-quote-box">
                                        <div class="section-label">2. Pensamento Automático</div>
                                        <div class="thought-quote-box-text">"{r.get('thought', '')}"</div>
                                    </div>
                                    <div class="thought-section">
                                        <div class="thought-section-icon">⚡</div>
                                        <div class="thought-section-body">
                                            <div class="section-label">3. Comportamento Resposta</div>
                                            <div class="section-content">{r.get('behavior', '')}</div>
                                        </div>
                                    </div>
                                </div>
                            '''
                            st.markdown(card_html, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Não foi possível descriptografar os registros")
            else:
                st.info(f"📭 O paciente {patient_name.capitalize()} ainda não registrou nenhum pensamento")

# ========== MAIN EXECUTION ==========
api_url, api_key = get_api_credentials()
if not api_url:
    render_setup_page()
    st.stop()

render_sidebar()

if st.session_state.user is None:
    render_login_page()
else:
    role = st.session_state.user['role']
    
    if role == "Admin":
        render_admin_page()
    elif role == "Mediador":
        render_mediador_page()
    elif role == "Paciente":
        render_paciente_page()
    else:
        st.error("❌ Cargo desconhecido no sistema")
        st.session_state.user = None
        if st.button("🔄 Voltar ao Login"):
            st.rerun()