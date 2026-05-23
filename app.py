import streamlit as st
import requests
import pandas as pd
import hashlib
import os
import datetime
from datetime import timedelta

# Set page config for a wider, modern layout
st.set_page_config(
    page_title="RPA - Registro de Pensamentos Automáticos",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI / Serene Glassmorphic theme
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Title Styling */
    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #0f766e, #0284c7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2.5rem;
    }
    
    /* Fade-in Animation */
    @keyframes cardFadeIn {
        from {
            opacity: 0;
            transform: translateY(12px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Premium Thought Card */
    .thought-card-premium {
        background: #ffffff;
        border: 1.5px solid #f1f5f9;
        border-left: 6px solid #0f766e;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(15, 118, 110, 0.03), 0 2px 4px rgba(0, 0, 0, 0.01);
        animation: cardFadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .thought-card-premium:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 24px rgba(15, 118, 110, 0.08), 0 4px 8px rgba(15, 118, 110, 0.02);
        border-color: rgba(15, 118, 110, 0.2);
    }
    
    /* Dark Mode specific overrides for Premium Cards if detected or matching streamlit layout */
    @media (prefers-color-scheme: dark) {
        .thought-card-premium {
            background: rgba(30, 41, 59, 0.45);
            border: 1.5px solid rgba(255, 255, 255, 0.05);
            border-left: 6px solid #14b8a6;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        .thought-card-premium:hover {
            background: rgba(30, 41, 59, 0.6);
            border-color: rgba(20, 184, 166, 0.25);
            box-shadow: 0 16px 24px rgba(0, 0, 0, 0.3);
        }
    }

    /* Premium Badges */
    .badge-premium {
        display: inline-flex;
        align-items: center;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 10px;
        margin-bottom: 10px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
        border: 1px solid transparent;
        transition: all 0.2s ease;
    }
    
    .bp-date {
        background-color: #f0fdf4;
        color: #16a34a;
        border-color: #dcfce7;
    }
    .bp-location {
        background-color: #f0f9ff;
        color: #0284c7;
        border-color: #e0f2fe;
    }
    .bp-emotion {
        background-color: #fff1f2;
        color: #e11d48;
        border-color: #ffe4e6;
    }

    @media (prefers-color-scheme: dark) {
        .bp-date { background-color: rgba(22, 163, 74, 0.15); color: #4ade80; border-color: rgba(22, 163, 74, 0.2); }
        .bp-location { background-color: rgba(2, 132, 199, 0.15); color: #38bdf8; border-color: rgba(2, 132, 199, 0.2); }
        .bp-emotion { background-color: rgba(225, 29, 72, 0.15); color: #fb7185; border-color: rgba(225, 29, 72, 0.2); }
    }
    
    /* Layout Containers for thought sections */
    .thought-section {
        display: flex;
        gap: 16px;
        margin-top: 18px;
        align-items: flex-start;
    }
    .thought-section-icon {
        font-size: 1.4rem;
        padding: 6px;
        border-radius: 8px;
        background: #f8fafc;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.02);
    }
    @media (prefers-color-scheme: dark) {
        .thought-section-icon {
            background: rgba(15, 23, 42, 0.4);
        }
    }
    .thought-section-body {
        flex: 1;
    }

    .section-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #94a3b8;
        font-weight: 700;
        margin-bottom: 2px;
    }
    
    .section-content {
        font-size: 1.02rem;
        color: #334155;
        line-height: 1.5;
    }
    @media (prefers-color-scheme: dark) {
        .section-content {
            color: #cbd5e1;
        }
    }

    /* Core Thought Quote Box (RPA focal point) */
    .thought-quote-box {
        background-color: #f0fdf4;
        border-left: 4px solid #16a34a;
        border-radius: 4px 14px 14px 4px;
        padding: 16px 20px;
        margin: 16px 0;
        transition: all 0.3s ease;
    }
    .thought-quote-box-text {
        font-size: 1.15rem;
        font-weight: 600;
        color: #0f766e;
        font-style: italic;
        line-height: 1.4;
    }
    @media (prefers-color-scheme: dark) {
        .thought-quote-box {
            background-color: rgba(20, 184, 166, 0.08);
            border-left-color: #14b8a6;
        }
        .thought-quote-box-text {
            color: #2dd4bf;
        }
    }
    
    /* Glass Panel */
    .glass-panel {
        background: rgba(15, 118, 110, 0.03);
        border: 1.5px dashed rgba(15, 118, 110, 0.15);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to hash passwords (SHA-256 with Username as salt)
def hash_password(username, password):
    salt = username.strip().lower()
    return hashlib.sha256((salt + password).encode()).hexdigest()

# Helper to convert UTC ISO strings to local system formatted time
def convert_to_local(timestamp_str):
    if not timestamp_str:
        return ""
    try:
        # Standardize UTC formatting for older Python versions
        clean_str = timestamp_str.replace("Z", "+00:00")
        dt_utc = datetime.datetime.fromisoformat(clean_str)
        # astimezone() converts to system local timezone
        dt_local = dt_utc.astimezone()
        return dt_local.strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        # Fallback if string cannot be parsed
        return timestamp_str

# Try loading API configurations from st.secrets, otherwise look in session state or create them
def get_api_credentials():
    # 1. Check secrets safely to avoid StreamlitSecretNotFoundError when no secrets file exists
    try:
        if "api" in st.secrets:
            return st.secrets["api"].get("url", ""), st.secrets["api"].get("key", "")
    except Exception:
        # st.secrets raises an exception if there are no secrets defined at all
        pass
    
    # 2. Check session state (for dynamic setup)
    if "api_url" in st.session_state and "api_key" in st.session_state:
        return st.session_state["api_url"], st.session_state["api_key"]
    
    return "", ""

# Save credentials to .streamlit/secrets.toml
def save_credentials(url, key):
    try:
        # Define absolute path to ensure it goes inside the correct project directory
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
        return True
    except Exception as e:
        st.error(f"Erro ao salvar credenciais localmente: {e}")
        return False

# Base API client function
def call_api(action, method="GET", params=None, json_data=None):
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

# Define setup page if not configured
def render_setup_page():
    st.markdown("<h1 class='main-title'>🧠 Registro de Pensamentos Automáticos</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Configuração Inicial do Sistema com Google Sheets</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Configurar Conexão com Banco de Dados")
        st.info("O sistema utiliza o Google Sheets como banco de dados em nuvem através do Google Apps Script. Siga o guia passo a passo na lateral para obter as credenciais de acesso.")
        
        with st.form("setup_form"):
            url = st.text_input("URL do Web App do Google Apps Script:", placeholder="https://script.google.com/macros/s/.../exec")
            key = st.text_input("Chave da API (Definida no arquivo apps_script.js):", type="password", value="RPA_SECRET_SECURE_TOKEN_2026")
            
            submit = st.form_submit_button("Salvar e Testar Conexão")
            
            if submit:
                if not url:
                    st.error("Por favor, preencha a URL do Web App.")
                else:
                    # Test save
                    if save_credentials(url, key):
                        st.success("Configurações salvas localmente com sucesso!")
                        
                        # Test connection by running 'setup' action in Sheets
                        with st.spinner("Testando conexão com o Google Sheets..."):
                            res = call_api("setup", method="GET")
                            if res.get("success"):
                                st.success("Conexão estabelecida com sucesso! Google Sheets inicializado.")
                                st.balloons()
                                # Refresh app state
                                st.rerun()
                            else:
                                st.error(f"Não foi possível conectar à planilha. Detalhes: {res.get('error', 'Sem resposta')}")
    
    with col2:
        st.subheader("📋 Passo a Passo de Instalação")
        st.markdown("""
        1. **Crie uma Planilha Google**:
           - Vá para [Google Sheets](https://sheets.google.com) e crie uma nova planilha em branco.
        
        2. **Abra o Editor de Script**:
           - No menu superior, clique em **Extensões** > **Apps Script**.
        
        3. **Copie o Código**:
           - Substitua todo o conteúdo de `Código.gs` pelo código fornecido no arquivo `apps_script.js` do projeto.
        
        4. **Altere a Chave de Segurança (Opcional)**:
           - No início do script, mude o valor de `API_KEY` para uma chave forte e copie-a.
        
        5. **Execute a Inicialização**:
           - Selecione a função `setupSheets` no menu de seleção rápida superior e clique em **Executar**. Dê as permissões necessárias para o script acessar suas planilhas Google.
        
        6. **Publique como Web App**:
           - Clique em **Implantar** > **Nova implantação**.
           - Selecione o tipo **App da Web** (ícone de engrenagem).
           - **Executar como**: Escolha **Eu** (seu email).
           - **Quem tem acesso**: Escolha **Qualquer pessoa** (necessário para a API funcionar).
           - Clique em **Implantar** e copie a **URL do App da Web** gerada.
        
        7. **Cole as Informações aqui**:
           - Cole a URL e a Chave de API no formulário ao lado e clique em salvar!
        """)

# --- MAIN APP LOGIC ---

# Check if database is configured
api_url, api_key = get_api_credentials()
if not api_url:
    render_setup_page()
    st.stop()

# Initialize session states for auth
if "user" not in st.session_state:
    st.session_state.user = None

# Sidebar for logout / current user information
def render_sidebar():
    with st.sidebar:
        st.markdown("<div style='text-align: center; margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/3004/3004381.png", width=70) # Beautiful mind icon
        st.markdown("<h3>Sistema RPA</h3>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.session_state.user:
            user = st.session_state.user
            st.markdown(f"**Usuário:** `{user['username']}`")
            
            # Custom role badges in sidebar
            role_colors = {"Admin": "#3b82f6", "Mediador": "#0d9488", "Paciente": "#f59e0b"}
            role_color = role_colors.get(user['role'], "#6b7280")
            st.markdown(f"<span style='background-color: {role_color}; color: white; padding: 4px 10px; border-radius: 9999px; font-size: 0.85rem; font-weight: bold;'>{user['role']}</span>", unsafe_allow_html=True)
            
            if user['role'] == 'Paciente' and user['mediator']:
                st.caption(f"Mediador vinculado: **{user['mediator']}**")
                
            st.markdown("---")
            
            # Action to disconnect sheet/reset setup (useful if user wants to change sheet URL)
            with st.expander("⚙️ Conexão de Dados"):
                st.caption(f"URL: `{api_url[:25]}...`")
                if st.button("Desconectar Planilha", key="btn_disconnect"):
                    # Clear session credentials and file
                    st.session_state["api_url"] = ""
                    st.session_state["api_key"] = ""
                    if os.path.exists(".streamlit/secrets.toml"):
                        os.remove(".streamlit/secrets.toml")
                    st.session_state.user = None
                    st.rerun()
            
            if st.button("🚪 Sair / Logout", use_container_width=True, type="secondary"):
                st.session_state.user = None
                st.rerun()
        else:
            st.markdown("Por favor, faça login para acessar o sistema.")

# Render Login screen
def render_login_page():
    st.markdown("<h1 class='main-title'>🧠 Registro de Pensamentos Automáticos</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Terapia Cognitivo-Comportamental (TCC) em Nuvem</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.05); padding: 30px; border-radius: 16px; border: 1px solid rgba(226, 232, 240, 0.1); box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05);'>
            <h3 style='text-align: center; margin-bottom: 20px;'>Entrar no Sistema</h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Usuário", placeholder="Seu nome de usuário").strip()
            password = st.text_input("Senha", type="password", placeholder="Sua senha")
            
            submit = st.form_submit_button("Acessar Conta", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("Por favor, preencha o usuário e a senha.")
                else:
                    pass_hash = hash_password(username, password)
                    with st.spinner("Autenticando..."):
                        res = call_api("login", "GET", params={"username": username, "passwordHash": pass_hash})
                        
                        if res.get("success"):
                            st.session_state.user = res.get("user")
                            st.success("Login efetuado com sucesso!")
                            st.rerun()
                        else:
                            st.error(res.get("error", "Erro ao realizar o login."))

# --- PAGES ---

# Page: Admin
def render_admin_page():
    st.markdown("<h2>🛡️ Painel do Administrador</h2>", unsafe_allow_html=True)
    st.write("Gerencie os usuários do sistema, altere senhas, crie novas contas e atribua mediadores a pacientes.")
    
    tab_create, tab_manage = st.tabs(["🆕 Cadastrar Novo Usuário", "👥 Gerenciar Usuários"])
    
    # Fetch mediators to link patients to them
    mediators_res = call_api("getMediators", "GET")
    mediators = mediators_res.get("mediators", []) if mediators_res.get("success") else []
    
    with tab_create:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Registrar Novo Usuário")
            with st.form("create_user_form", clear_on_submit=True):
                new_username = st.text_input("Nome de Usuário (Ex: joaosilva)", placeholder="Usar letras minúsculas e sem espaços").strip().lower()
                new_password = st.text_input("Senha Inicial", type="password", placeholder="Mínimo 6 caracteres")
                new_role = st.selectbox("Cargo / Função", ["Paciente", "Mediador", "Admin"])
                
                # Dynamic dropdown to select mediator if user is a Paciente
                selected_mediator = ""
                if new_role == "Paciente":
                    if mediators:
                        selected_mediator = st.selectbox("Vincular a um Mediador (Terapeuta)", ["Nenhum"] + mediators)
                        if selected_mediator == "Nenhum":
                            selected_mediator = ""
                    else:
                        st.warning("Aviso: Nenhum mediador cadastrado no sistema ainda. Crie um Mediador primeiro para poder fazer o vínculo, ou cadastre o paciente sem vínculo inicial.")
                
                create_submit = st.form_submit_button("Salvar Usuário", use_container_width=True)
                
                if create_submit:
                    if not new_username or not new_password:
                        st.error("Nome de usuário e senha são obrigatórios.")
                    elif len(new_password) < 4:
                        st.error("A senha deve ter pelo menos 4 caracteres.")
                    else:
                        pass_hash = hash_password(new_username, new_password)
                        with st.spinner("Registrando usuário..."):
                            post_data = {
                                "username": new_username,
                                "passwordHash": pass_hash,
                                "role": new_role,
                                "mediator": selected_mediator
                            }
                            res = call_api("createUser", "POST", json_data=post_data)
                            if res.get("success"):
                                st.success(f"Usuário `{new_username}` cadastrado com sucesso!")
                                # Force reload of users
                                st.session_state["users_last_update"] = datetime.datetime.now()
                            else:
                                st.error(res.get("error", "Erro ao criar usuário."))
                                
        with col2:
            st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
            st.markdown("### ℹ️ Regras de Cargos")
            st.markdown("""
            - **Paciente**: Consegue fazer os registros do RPA. Só visualiza os próprios registros. Deve idealmente estar vinculado a um **Mediador**.
            - **Mediador (Terapeuta)**: Consegue visualizar os registros de todos os Pacientes que estão vinculados a ele, organizados de forma prática em abas. Não consegue ler registros de outros pacientes.
            - **Admin**: Tem controle total sobre criação, alteração e exclusão de contas no sistema. Não realiza registros clínicos.
            """)
            st.markdown("</div>", unsafe_allow_html=True)

    with tab_manage:
        st.subheader("Usuários Cadastrados")
        
        # Load user list
        with st.spinner("Carregando lista de usuários..."):
            users_res = call_api("getUsers", "GET")
            
        if users_res.get("success"):
            users = users_res.get("users", [])
            if not users:
                st.info("Nenhum usuário cadastrado além do administrador padrão.")
            else:
                # Convert to DataFrame for visualization and searching
                df_users = pd.DataFrame(users)
                # Convert UTC timestamp string safely to localized system timezone
                try:
                    df_users['created_at'] = pd.to_datetime(df_users['created_at'])
                    if df_users['created_at'].dt.tz is None:
                        df_users['created_at'] = df_users['created_at'].dt.tz_localize('UTC')
                    df_users['created_at'] = df_users['created_at'].dt.tz_convert(None).dt.strftime('%d/%m/%Y %H:%M')
                except Exception:
                    df_users['created_at'] = df_users['created_at'].astype(str)
                
                # Search filter
                search_q = st.text_input("🔍 Buscar usuário pelo nome:", "").strip().lower()
                if search_q:
                    df_users = df_users[df_users['username'].str.contains(search_q)]
                
                # Display dynamic dataframe with custom styling
                st.dataframe(
                    df_users.rename(columns={
                        'username': 'Nome de Usuário',
                        'role': 'Cargo',
                        'mediator': 'Mediador Vinculado',
                        'created_at': 'Data de Cadastro'
                    }), 
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown("---")
                st.subheader("✏️ Ações Rápidas de Usuário")
                
                # User selector for actions
                usernames = [u['username'] for u in users if u['username'].lower() != 'admin']
                if usernames:
                    selected_user = st.selectbox("Escolha um usuário para gerenciar:", usernames)
                    user_info = next((u for u in users if u['username'] == selected_user), None)
                    
                    if user_info:
                        col_pw, col_del = st.columns([1, 1])
                        
                        with col_pw:
                            st.write(f"**Alterar Senha de `{selected_user}`**")
                            new_pw = st.text_input("Nova Senha", type="password", key=f"pw_{selected_user}")
                            if st.button("Confirmar Nova Senha", key=f"btn_pw_{selected_user}"):
                                if not new_pw:
                                    st.error("Insira a nova senha.")
                                else:
                                    new_hash = hash_password(selected_user, new_pw)
                                    with st.spinner("Atualizando senha..."):
                                        res = call_api("updatePassword", "POST", json_data={"username": selected_user, "passwordHash": new_hash})
                                        if res.get("success"):
                                            st.success("Senha alterada com sucesso!")
                                        else:
                                            st.error(res.get("error", "Erro ao atualizar senha."))
                                            
                        with col_del:
                            st.write(f"**Excluir Usuário `{selected_user}`**")
                            st.warning("⚠️ Atenção: Esta ação é permanente e removerá o acesso deste usuário!")
                            confirm_del = st.checkbox(f"Estou ciente e desejo excluir o usuário `{selected_user}`", key=f"chk_del_{selected_user}")
                            if st.button("❌ Excluir Conta", key=f"btn_del_{selected_user}", type="primary", disabled=not confirm_del):
                                with st.spinner("Excluindo conta..."):
                                    res = call_api("deleteUser", "POST", json_data={"username": selected_user})
                                    if res.get("success"):
                                        st.success("Usuário excluído com sucesso!")
                                        st.rerun()
                                    else:
                                        st.error(res.get("error", "Erro ao excluir usuário."))
                else:
                    st.info("Nenhum outro usuário disponível para edição.")
        else:
            st.error(f"Erro ao carregar usuários: {users_res.get('error')}")

# Page: Paciente
def render_paciente_page():
    user = st.session_state.user
    
    st.markdown(f"<h2>🧠 Olá, {user['username'].capitalize()}!</h2>", unsafe_allow_html=True)
    st.write("Este é seu espaço seguro para registrar seus pensamentos automáticos e entender suas emoções.")
    
    tab_new, tab_history = st.tabs(["📝 Novo Registro (RPA)", "📊 Meus Registros"])
    
    with tab_new:
        st.subheader("Registrar Pensamento Automático")
        st.write("Preencha as informações abaixo seguindo a técnica clássica do RPA da Terapia Cognitivo-Comportamental.")
        
        with st.form("rpa_form", clear_on_submit=True):
            col_d, col_l = st.columns([1, 1])
            with col_d:
                date_input = st.date_input("Data do Ocorrido", datetime.date.today())
            with col_l:
                location_input = st.text_input("Local", placeholder="Ex: No trabalho, em casa, no trânsito...")
                
            situation = st.text_area("1. Situação", 
                                    placeholder="O que aconteceu? Quem estava com você? O que você estava fazendo?",
                                    help="Descreva o fato concreto objetivamente, sem julgamentos.")
            
            thought = st.text_area("2. Pensamento Automático", 
                                   placeholder="O que passou pela sua cabeça naquele momento? O que isso diz sobre você?",
                                   help="Escreva as palavras exatas ou imagens mentais que surgiram na sua mente.")
            
            emotion = st.text_input("3. Emoção Associada (e intensidade)", 
                                    placeholder="Ex: Ansiedade (80%), Tristeza (60%), Raiva (40%)",
                                    help="Identifique as emoções sentidas e coloque uma nota de 0 a 100% para cada uma.")
            
            behavior = st.text_area("4. Comportamento Resposta", 
                                    placeholder="O que você fez após o pensamento? Qual foi a sua reação física?",
                                    help="Descreva suas ações físicas ou reações fisiológicas (ex: tremores, suor, fuga).")
            
            submit_rpa = st.form_submit_button("Gravar Registro de Pensamento", use_container_width=True)
            
            if submit_rpa:
                if not situation or not thought or not emotion or not behavior:
                    st.error("Todos os campos do RPA são muito importantes e devem ser preenchidos!")
                else:
                    date_local = f"{date_input.strftime('%d/%m/%Y')} - {location_input}"
                    with st.spinner("Gravando seu registro no banco de dados..."):
                        record_data = {
                            "patient": user['username'],
                            "dateLocal": date_local,
                            "situation": situation,
                            "thought": thought,
                            "emotion": emotion,
                            "behavior": behavior
                        }
                        res = call_api("addRecord", "POST", json_data=record_data)
                        if res.get("success"):
                            st.success("Seu pensamento foi registrado e guardado com sucesso!")
                            st.balloons()
                        else:
                            st.error(res.get("error", "Erro ao gravar pensamento."))
                            
    with tab_history:
        st.subheader("Histórico de Pensamentos Registrados")
        
        # Load patient's own records
        with st.spinner("Carregando seus registros..."):
            records_res = call_api("getPatientRecords", "GET", params={"patient": user['username']})
            
        if records_res.get("success"):
            records = records_res.get("records", [])
            
            if not records:
                st.info("Você ainda não possui pensamentos automáticos registrados. Que tal fazer o seu primeiro agora?")
            else:
                # Reverse chronological order
                records.reverse()
                
                # Metricas rapidas
                st.markdown("<div style='display: flex; gap: 15px; margin-bottom: 20px;'>", unsafe_allow_html=True)
                st.metric("Total de Registros", len(records))
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Display cards
                for r in records:
                    local_time_str = convert_to_local(r["timestamp"])
                    card_html = (
                        f'<div class="thought-card-premium">'
                        f'<div style="display: flex; flex-wrap: wrap; margin-bottom: 8px;">'
                        f'<span class="badge-premium bp-date">📅 Registro: {local_time_str}</span>'
                        f'<span class="badge-premium bp-location">📍 Local: {r["date_local"]}</span>'
                        f'<span class="badge-premium bp-emotion">❤️ Emoção: {r["emotion"]}</span>'
                        f'</div>'
                        f'<div class="thought-section">'
                        f'<div class="thought-section-icon">🔍</div>'
                        f'<div class="thought-section-body">'
                        f'<div class="section-label">1. Situação</div>'
                        f'<div class="section-content">{r["situation"]}</div>'
                        f'</div>'
                        f'</div>'
                        f'<div class="thought-quote-box">'
                        f'<div class="section-label" style="color: inherit; opacity: 0.8;">2. Pensamento Automático</div>'
                        f'<div class="thought-quote-box-text">"{r["thought"]}"</div>'
                        f'</div>'
                        f'<div class="thought-section" style="margin-top: 10px;">'
                        f'<div class="thought-section-icon">⚡</div>'
                        f'<div class="thought-section-body">'
                        f'<div class="section-label">3. Comportamento Resposta</div>'
                        f'<div class="section-content">{r["behavior"]}</div>'
                        f'</div>'
                        f'</div>'
                        f'</div>'
                    )
                    st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.error(f"Erro ao carregar registros: {records_res.get('error')}")

# Page: Mediador
def render_mediador_page():
    user = st.session_state.user
    
    st.markdown(f"<h2>🩺 Painel Clínico - Mediador {user['username'].capitalize()}</h2>", unsafe_allow_html=True)
    st.write("Acompanhe o registro de pensamentos automáticos dos seus pacientes de forma rápida e dinâmica.")
    
    # Fetch patients linked to this mediator along with their records in a single fast request!
    with st.spinner("Carregando dados dos pacientes vinculados..."):
        res = call_api("getMediatorPatients", "GET", params={"mediator": user['username']})
        
    if not res.get("success"):
        st.error(f"Erro ao carregar informações dos pacientes: {res.get('error')}")
        return
        
    patients = res.get("patients", [])
    all_records = res.get("records", {})
    
    if not patients:
        st.markdown("""
        <div class="glass-panel" style="text-align: center; padding: 40px;">
            <h3>Nenhum paciente vinculado</h3>
            <p>Você não possui pacientes vinculados ao seu usuário atualmente.</p>
            <p style="color: #64748b;">Solicite ao <b>Administrador</b> do sistema que vincule novos pacientes ao seu perfil de mediador.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Divisão por abas (Dynamic Patient Tabs as requested by user)
    tabs = st.tabs([f"👤 {patient_name.capitalize()}" for patient_name in patients])
    
    for i, patient_name in enumerate(patients):
        with tabs[i]:
            records = all_records.get(patient_name, [])
            
            col_p_title, col_p_actions = st.columns([2, 1])
            with col_p_title:
                st.subheader(f"Registros de {patient_name.capitalize()}")
            
            # If patient has records
            if records:
                # Chronological sort (descending timestamp by default)
                records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                
                # Load them into a clean DataFrame for date calculations
                df = pd.DataFrame(records)
                # Parse timestamps for filtering
                df['parsed_date'] = pd.to_datetime(df['timestamp']).dt.date
                
                # Filters row
                with st.expander("🔍 Filtros de Visualização", expanded=True):
                    col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
                    
                    with col_f1:
                        # Date Range Selector
                        min_date = df['parsed_date'].min()
                        max_date = df['parsed_date'].max()
                        
                        # Fallback for date_input defaults
                        start_d = min_date - timedelta(days=1)
                        end_d = max_date + timedelta(days=1)
                        
                        date_range = st.date_input(
                            "Filtrar por Período de Registro:",
                            value=(min_date, max_date),
                            min_value=min_date,
                            max_value=max_date,
                            key=f"date_filter_{patient_name}"
                        )
                    
                    with col_f2:
                        # Emotion search
                        search_emotion = st.text_input("Filtrar por Emoção:", "", key=f"emo_filter_{patient_name}").strip().lower()
                        
                    with col_f3:
                        # Text search
                        search_text = st.text_input("Buscar nas descrições:", "", key=f"text_filter_{patient_name}").strip().lower()
                
                # Apply Date Range filter
                filtered_records = records.copy()
                if isinstance(date_range, tuple) and len(date_range) == 2:
                    start_date, end_date = date_range
                    filtered_records = [r for r in filtered_records if start_date <= pd.to_datetime(r['timestamp']).date() <= end_date]
                elif isinstance(date_range, datetime.date):
                    # Single date selected
                    filtered_records = [r for r in filtered_records if pd.to_datetime(r['timestamp']).date() == date_range]
                
                # Apply Emotion search filter
                if search_emotion:
                    filtered_records = [r for r in filtered_records if search_emotion in r['emotion'].lower()]
                    
                # Apply Text search filter
                if search_text:
                    filtered_records = [r for r in filtered_records if (search_text in r['situation'].lower() or search_text in r['thought'].lower() or search_text in r['behavior'].lower())]
                
                # Action Buttons
                with col_p_actions:
                    if filtered_records:
                        df_export = pd.DataFrame(filtered_records)
                        # Clean columns for export
                        if 'parsed_date' in df_export.columns:
                            df_export = df_export.drop(columns=['parsed_date'])
                        csv_data = df_export.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label="📥 Exportar Dados (CSV)",
                            data=csv_data,
                            file_name=f"RPA_{patient_name}_{datetime.date.today()}.csv",
                            mime="text/csv",
                            key=f"dl_{patient_name}",
                            use_container_width=True
                        )
                
                # Visual Metrics Row
                st.markdown("<div style='display: flex; gap: 15px; margin-bottom: 20px;'>", unsafe_allow_html=True)
                col_m1, col_m2 = st.columns([1, 1])
                with col_m1:
                    st.metric("Registros Encontrados (Filtro)", len(filtered_records), delta=f"Total: {len(records)}")
                with col_m2:
                    last_record_date = convert_to_local(records[0]['timestamp']) if records else "Sem registros"
                    st.metric("Última Atividade", last_record_date)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Render records dynamically
                if not filtered_records:
                    st.warning("Nenhum registro corresponde aos filtros selecionados.")
                else:
                    for r in filtered_records:
                        local_time_str = convert_to_local(r["timestamp"])
                        card_html = (
                            f'<div class="thought-card-premium">'
                            f'<div style="display: flex; flex-wrap: wrap; margin-bottom: 8px;">'
                            f'<span class="badge-premium bp-date">📅 Registro: {local_time_str}</span>'
                            f'<span class="badge-premium bp-location">📍 Local: {r["date_local"]}</span>'
                            f'<span class="badge-premium bp-emotion">❤️ Emoção: {r["emotion"]}</span>'
                            f'</div>'
                            f'<div class="thought-section">'
                            f'<div class="thought-section-icon">🔍</div>'
                            f'<div class="thought-section-body">'
                            f'<div class="section-label">1. Situação</div>'
                            f'<div class="section-content">{r["situation"]}</div>'
                            f'</div>'
                            f'</div>'
                            f'<div class="thought-quote-box">'
                            f'<div class="section-label" style="color: inherit; opacity: 0.8;">2. Pensamento Automático</div>'
                            f'<div class="thought-quote-box-text">"{r["thought"]}"</div>'
                            f'</div>'
                            f'<div class="thought-section" style="margin-top: 10px;">'
                            f'<div class="thought-section-icon">⚡</div>'
                            f'<div class="thought-section-body">'
                            f'<div class="section-label">3. Comportamento Resposta</div>'
                            f'<div class="section-content">{r["behavior"]}</div>'
                            f'</div>'
                            f'</div>'
                            f'</div>'
                        )
                        st.markdown(card_html, unsafe_allow_html=True)
            else:
                st.info(f"O paciente {patient_name.capitalize()} ainda não registrou nenhum pensamento automático.")

# --- RENDER LAYOUT FLOW ---

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
        st.error("Cargo desconhecido no sistema. Contate o administrador.")
        st.session_state.user = None
        if st.button("Voltar ao Login"):
            st.rerun()
