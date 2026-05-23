# 🧠 Sistema de Registro de Pensamentos Automáticos (RPA)

Este é um sistema moderno, rápido e dinâmico para Registro de Pensamentos Automáticos (RPA), um instrumento clássico da Terapia Cognitivo-Comportamental (TCC). 

O sistema é construído em **Python** usando **Streamlit** no frontend, integrado diretamente com o **Google Sheets** na nuvem como banco de dados através de uma API segura criada no **Google Apps Script**.

---

## 🚀 Arquitetura e Recursos

O sistema é dividido em três perfis de usuários com permissões específicas:
1. **Administrador**:
   - Cadastra novos usuários (definindo cargo e dados).
   - Gerencia cargos e altera senhas.
   - Vincula pacientes a seus respectivos mediadores (terapeutas).
2. **Mediador (Terapeuta)**:
   - Acompanha de forma centralizada e dinâmica os registros de seus pacientes vinculados.
   - Visualização organizada **por abas de pacientes**.
   - Filtros dinâmicos por **Período (Data)**, **Emoções** e busca textual livre.
   - Exportação de relatórios clínicos em formato CSV.
3. **Paciente**:
   - Registra novos pensamentos com os campos estruturados da TCC: "Data e Local", "Situação", "Pensamento Automático", "Emoção Associada (e intensidade)", e "Comportamento Resposta".
   - Histórico em formato de cartões visuais elegantes (timeline).

---

## 🛠️ Passo a Passo de Instalação e Configuração

### Passo 1: Configurar a Planilha e o Google Apps Script (Banco de Dados)

1. Crie uma nova planilha vazia no [Google Sheets](https://sheets.google.com).
2. No menu superior da planilha, acesse **Extensões** > **Apps Script**.
3. Apague todo o código padrão e cole o conteúdo do arquivo [apps_script.js](file:///c:/Users/Joaom/Documents/Psych/apps_script.js) do projeto.
4. **Segurança**: Na linha 16 de `apps_script.js`, você verá a variável `const API_KEY = "RPA_SECRET_SECURE_TOKEN_2026";`. Se desejar, altere esse valor para uma chave secreta de sua escolha. Lembre-se dessa chave.
5. No menu superior do Apps Script, selecione a função `setupSheets` e clique em **Executar** (botão de play).
   - O Google solicitará permissão para que o script acesse a planilha. Autorize todas as permissões.
   - Essa execução criará automaticamente as abas `users` e `records` na planilha, além de cadastrar o usuário administrador padrão (`admin` / `admin123`).
6. No canto superior direito, clique em **Implantar** > **Nova implantação**.
   - Clique no ícone de engrenagem (Tipo de implantação) e escolha **App da Web**.
   - **Descrição**: "API RPA"
   - **Executar como**: Selecione **Eu (seu-email@gmail.com)**.
   - **Quem tem acesso**: Selecione **Qualquer pessoa** (isso é fundamental para que o Streamlit consiga enviar dados para a API).
   - Clique em **Implantar**.
7. Copie a **URL do App da Web** gerada (ex: `https://script.google.com/macros/s/.../exec`).

---

### Passo 2: Configurar e Rodar o App Streamlit (Interface Visual)

1. **Instale os requisitos**:
   Abra seu terminal na pasta do projeto e instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. **Inicie o Streamlit**:
   Execute o comando abaixo para iniciar o servidor de desenvolvimento:
   ```bash
   streamlit run app.py
   ```

3. **Configuração Automática Onboarding**:
   - Na primeira execução, o Streamlit abrirá uma tela de onboarding amigável.
   - Cole a **URL do Web App** obtida no Apps Script e informe a **Chave de API** (por padrão `RPA_SECRET_SECURE_TOKEN_2026`).
   - Clique em **Salvar e Testar Conexão**. O sistema fará um teste de conexão em tempo real e criará o arquivo `.streamlit/secrets.toml` automaticamente.

---

## 🔑 Credenciais Padrão e Primeiros Passos

1. Acesse o sistema utilizando o login de Administrador padrão:
   - **Usuário**: `admin`
   - **Senha**: `admin123`
2. **Cadastre um Mediador**:
   - Vá no painel do administrador, aba "Cadastrar Novo Usuário", defina o usuário (ex: `terapeuta1`), senha, cargo como **Mediador** e salve.
3. **Cadastre um Paciente**:
   - No mesmo formulário, defina o usuário (ex: `paciente1`), senha, cargo como **Paciente**.
   - Na caixa de seleção "Vincular a um Mediador", selecione o mediador que você criou (`terapeuta1`). Salve.
4. **Registre Pensamentos**:
   - Faça logout (`Sair` no painel lateral) e logue como o paciente (`paciente1` / senha escolhida).
   - Faça alguns registros de pensamentos na aba de cadastro.
5. **Monitore Clinicamente**:
   - Faça logout e logue como o mediador (`terapeuta1` / senha escolhida).
   - O painel exibirá as abas para cada um dos seus pacientes, contendo os pensamentos registrados, filtros avançados de data e exportação em CSV!

---

## 🔒 Segurança de Senhas

As senhas são protegidas no lado do cliente (Streamlit) utilizando criptografia unidirecional **SHA-256** com *salting* automático (baseado no nome do usuário). Isso garante que:
- Senhas em texto plano nunca trafeguem pela rede.
- Senhas armazenadas na planilha Google permaneçam criptografadas e protegidas contra vazamentos.
