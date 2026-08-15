import streamlit as st
import sqlite3
from datetime import datetime, timedelta

# ============================================================
# CONFIGURAÇÃO DE TELA (NATIVA DO STREAMLIT)
# ============================================================
st.set_page_config(
    page_title="Escala Amazon",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# BANCO DE DADOS
# ============================================================
BANCO = "escala_amazon.db"

def conectar():
    return sqlite3.connect(BANCO, check_same_thread=False)

def criar_banco():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            funcao TEXT NOT NULL,
            turno TEXT NOT NULL,
            ativo INTEGER DEFAULT 1
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS escala (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operador_id INTEGER NOT NULL,
            semana_id TEXT NOT NULL,
            sexta TEXT NOT NULL,
            sabado TEXT NOT NULL,
            domingo TEXT NOT NULL,
            segunda TEXT NOT NULL,
            FOREIGN KEY (operador_id) REFERENCES operadores(id)
        )
    """)
    conn.commit()
    conn.close()

criar_banco()

HORARIOS = {
    "T1": "07:00 às 15:00",
    "T2": "15:00 às 23:00",
    "T3": "23:00 às 07:00"
}

NOMES_TURNOS = {
    "T1": "Turno 1",
    "T2": "Turno 2",
    "T3": "Turno 3"
}

# ============================================================
# INTERFACE CSS PREMIUM DARK MODE (ESTILO AMAZON CORE)
# ============================================================
st.markdown("""
<style>
/* Reset Total do Fundo para o Azul Escuro corporativo */
header[data-testid="stHeader"] { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDecoration { display: none !important; }
[data-testid="stSidebar"] { display: none; }

/* Fundo unificado Dark Corporativo */
[data-testid="stAppViewContainer"], .stApp { 
    background-color: #0F172A !important; 
}
.stMainBlockContainer { 
    padding-top: 25px !important; 
    padding-bottom: 40px !important; 
    max-width: 95% !important;
}

/* Tipografia e Títulos */
.titulo { 
    color: #FFFFFF; 
    font-family: 'Segoe UI', sans-serif; 
    font-size: 32px; 
    font-weight: 800; 
    letter-spacing: -0.5px;
}
.subtitulo { 
    color: #FF9900; 
    font-size: 12px; 
    font-weight: 700; 
    text-transform: uppercase;
    letter-spacing: 1.5px; 
    margin-bottom: 20px; 
}

/* Customização dos Inputs Padrão */
label[data-testid="stWidgetLabel"] p {
    color: #94A3B8 !important;
    font-weight: 600 !important;
    font-size: 12px !important;
}
div[data-baseweb="select"] > div {
    background-color: #1E293B !important;
    border: 1px solid #334155 !important;
    color: #FFFFFF !important;
    border-radius: 6px !important;
}
div[data-baseweb="select"] * {
    color: #FFFFFF !important;
}

/* Estilização Cirúrgica do Botão/Popover Gestor */
div[data-testid="stPopover"] > button {
    background-color: #1E293B !important;
    color: #FFFFFF !important;
    border: 1px solid #334155 !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
    font-size: 13px !important;
}
div[data-testid="stPopover"] > button:hover {
    background-color: #FF9900 !important;
    border-color: #FF9900 !important;
    color: #0F172A !important;
}
div[data-testid="stPopoverBody"] {
    background-color: #1E293B !important;
    border: 1px solid #334155 !important;
    color: #FFFFFF !important;
}

/* Grid de Métricas Avançado */
.metrics-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}
.metric-box {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
}
.metric-box.total { border-left: 4px solid #FF9900; }
.metric-box.turno { border-left: 4px solid #38BDF8; }
.metric-num { font-size: 28px; font-weight: 800; color: #FFFFFF; }
.metric-lab { font-size: 11px; color: #94A3B8; font-weight: 700; margin-top: 4px; letter-spacing: 0.5px; }

/* Tabs Modificadas para o Modo Escuro */
button[data-baseweb="tab"] {
    color: #94A3B8 !important;
    font-weight: 600 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #FF9900 !important;
    border-bottom-color: #FF9900 !important;
}

/* Banner do Turno Selecionado */
.turno-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 10px;
    margin-bottom: 20px;
    padding: 12px 18px;
    background-color: #1E293B;
    border-radius: 8px;
    border: 1px solid #334155;
}
.turno-titulo { font-size: 18px; font-weight: 700; color: #FFFFFF; }
.turno-horario {
    background-color: rgba(56, 189, 248, 0.1);
    color: #38BDF8;
    padding: 4px 12px;
    border-radius: 99px;
    font-size: 11px;
    font-weight: 700;
}

/* Cabeçalhos de Colunas da Tabela */
.header-col { 
    text-align: center; 
    font-weight: 700; 
    font-size: 11px; 
    color: #94A3B8; 
    letter-spacing: 0.5px;
    margin-bottom: 8px;
    text-transform: uppercase;
}
.header-esquerda { text-align: left; }
.nome-operador { padding-top: 10px; font-size: 13px; color: #FFFFFF; font-weight: 600; }
.funcao-operador { padding-top: 12px; font-size: 11px; color: #64748B; font-weight: 600; }
.separador { border: 0; border-top: 1px solid #334155; margin-top: 4px; margin-bottom: 12px; }

/* CARD STATUS - TRABALHO */
.card-trabalho {
    background-color: #FF9900;
    color: #0F172A;
    padding: 8px 4px;
    border-radius: 6px;
    text-align: center;
    font-weight: 800;
    font-size: 11px;
    letter-spacing: 0.5px;
    min-height: 44px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-shadow: 0 4px 10px rgba(255, 153, 0, 0.15);
}
.sub-info { color: #0F172A; opacity: 0.85; font-size: 9px; margin-top: 1px; font-weight: 700; }

/* CARD STATUS - FOLGA */
.card-folga {
    background-color: #1E293B;
    color: #64748B;
    padding: 8px 4px;
    border-radius: 6px;
    text-align: center;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.5px;
    min-height: 44px;
    border: 1px dashed #334155;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.sub-info-folga { color: #475569; font-size: 9px; margin-top: 1px; font-weight: 500; }

/* Alinhamento de Linhas e Botão Alternar Clean */
div[data-testid="column"] {
    padding: 0px 4px !important;
}
div[data-testid="column"] .stButton > button {
    border-radius: 4px !important;
    font-size: 10px !important;
    padding: 2px 0px !important;
    background-color: transparent !important;
    color: #94A3B8 !important;
    border: 1px solid #334155 !important;
    margin-top: 4px !important;
}
div[data-testid="column"] .stButton > button:hover {
    color: #FF9900 !important;
    border-color: #FF9900 !important;
    background-color: rgba(255,153,0,0.05) !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# GERENCIAMENTO DE ESTADO DE AUTENTICAÇÃO
# ============================================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# ============================================================
# FUNÇÕES DE PERSISTÊNCIA (SQLITE)
# ============================================================
def buscar_operadores():
    conn = conectar()
    dados = conn.execute("""
        SELECT id, nome, funcao, turno FROM operadores WHERE ativo = 1 ORDER BY turno, nome
    """).fetchall()
    conn.close()
    return dados

def cadastrar_operador(nome, funcao, turno):
    conn = conectar()
    conn.execute("INSERT INTO operadores (nome, funcao, turno) VALUES (?, ?, ?)", (nome, funcao, turno))
    conn.commit()
    conn.close()

def remover_operador(operador_id):
    conn = conectar()
    conn.execute("UPDATE operadores SET ativo = 0 WHERE id = ?", (operador_id,))
    conn.commit()
    conn.close()

def buscar_status(operador_id, semana_id):
    conn = conectar()
    resultado = conn.execute("""
        SELECT sexta, sabado, domingo, segunda FROM escala WHERE operador_id = ? AND semana_id = ?
    """, (operador_id, semana_id)).fetchone()
    conn.close()
    return resultado

def salvar_status(operador_id, semana_id, sexta, sabado, domingo, segunda):
    conn = conectar()
    existente = conn.execute(
        "SELECT id FROM escala WHERE operador_id = ? AND semana_id = ?", (operador_id, semana_id)
    ).fetchone()
    
    if existente:
        conn.execute("""
            UPDATE escala SET sexta = ?, sabado = ?, domingo = ?, segunda = ? WHERE operador_id = ? AND semana_id = ?
        """, (sexta, sabado, domingo, segunda, operador_id, semana_id))
    else:
        conn.execute("""
            INSERT INTO escala (operador_id, semana_id, sexta, sabado, domingo, segunda) VALUES (?, ?, ?, ?, ?, ?)
        """, (operador_id, semana_id, sexta, sabado, domingo, segunda))
    conn.commit()
    conn.close()

# Callback para gerenciar a alteração de status de forma síncrona e segura
def alternar_status_callback(operador_id, semana_id, lista_atual, index_dia, novo_valor):
    lista_atual[index_dia] = novo_valor
    salvar_status(operador_id, semana_id, *lista_atual)

# ============================================================
# INTEGRAÇÃO DE DATAS DINÂMICAS
# ============================================================
def obter_semana(deslocamento=0):
    hoje = datetime.now()
    dias_para_sexta = (hoje.weekday() - 4) % 7
    sexta = hoje - timedelta(days=dias_para_sexta) + timedelta(weeks=deslocamento)
    sabado = sexta + timedelta(days=1)
    domingo = sexta + timedelta(days=2)
    segunda = sexta + timedelta(days=3)

    return {
        "id": sexta.strftime("%Y-%m-%d"),
        "nome": f"{sexta.strftime('%d/%m')} até {segunda.strftime('%d/%m')}",
        "Sexta": sexta.strftime("%d/%m"),
        "Sábado": sabado.strftime("%d/%m"),
        "Domingo": domingo.strftime("%d/%m"),
        "Segunda": segunda.strftime("%d/%m")
    }

semanas = [obter_semana(i) for i in range(-2, 5)]

# ============================================================
# TOPBAR (HEADER + LOGIN ADM)
# ============================================================
col_tit, col_log = st.columns([4, 1], vertical_alignment="center")

with col_tit:
    st.markdown("<div class='titulo'>Escala Amazon</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitulo'>Monitoramento de Turnos e Operações</div>", unsafe_allow_html=True)

with col_log:
    if not st.session_state.autenticado:
        with st.popover("👤 Área do Gestor", use_container_width=True):
            with st.form("login_form", clear_on_submit=True):
                usuario = st.text_input("Usuário")
                senha = st.text_input("Senha", type="password")
                entrar = st.form_submit_button("Acessar", use_container_width=True)

                if entrar:
                    if usuario.lower().strip() == "admin" and senha == "Amazon123":
                        st.session_state.autenticado = True
                        st.rerun()
                    else:
                        st.error("Credenciais inválidas.")
    else:
        with st.popover("⚙️ Painel do Administrador", use_container_width=True):
            st.markdown("<span style='color:#4ADE80'>● Gestor Autenticado</span>", unsafe_allow_html=True)
            st.divider()
            
            menu_admin = st.selectbox("Ação rápida:", ["Adicionar Operador", "Remover Operador"])
            
            if menu_admin == "Adicionar Operador":
                novo_nome = st.text_input("Nome").strip().upper()
                nova_funcao = st.text_input("Função").strip().upper()
                novo_turno = st.selectbox("Turno", ["T1", "T2", "T3"], format_func=lambda x: f"{NOMES_TURNOS[x]} ({HORARIOS[x]})")
                if st.button("Salvar Registro", use_container_width=True):
                    if novo_nome and nova_funcao:
                        cadastrar_operador(novo_nome, nova_funcao, turno=novo_turno) # Ajustado aqui
                        st.success("Operador salvo!")
                        st.rerun()
                        
            elif menu_admin == "Remover Operador":
                operadores_lista = buscar_operadores()
                if operadores_lista:
                    opcoes_remocao = {f"{x[1]} [{x[2]}]": x[0] for x in operadores_lista}
                    selecionado = st.selectbox("Escolha quem remover:", list(opcoes_remocao.keys()))
                    if st.button("Remover Permanentemente", use_container_width=True):
                        remover_operador(opcoes_remocao[selecionado])
                        st.success("Operador removido.")
                        st.rerun()
            
            st.divider()
            if st.button("Sair do Modo Admin", use_container_width=True):
                st.session_state.autenticado = False
                st.rerun()

# ============================================================
# FILTROS PRINCIPAIS
# ============================================================
semana_labels = [x["nome"] for x in semanas]
semana_escolhida = st.selectbox("📅 Selecione a Janela da Escala", semana_labels, index=2)
semana = semanas[semana_labels.index(semana_escolhida)]
semana_id = semana["id"]

operadores = buscar_operadores()

# ============================================================
# CONTAINER DE METRICAS
# ============================================================
total = len(operadores)
t1 = len([x for x in operadores if x[3] == "T1"])
t2 = len([x for x in operadores if x[3] == "T2"])
t3 = len([x for x in operadores if x[3] == "T3"])

st.markdown(f"""
<div class='metrics-container'>
    <div class='metric-box total'>
        <div class='metric-num'>{total}</div>
        <div class='metric-lab'>TOTAL DE OPERADORES</div>
    </div>
    <div class='metric-box turno'>
        <div class='metric-num'>{t1}</div>
        <div class='metric-lab'>TURNO 1 (07H-15H)</div>
    </div>
    <div class='metric-box turno'>
        <div class='metric-num'>{t2}</div>
        <div class='metric-lab'>TURNO 2 (15H-23H)</div>
    </div>
    <div class='metric-box turno'>
        <div class='metric-num'>{t3}</div>
        <div class='metric-lab'>TURNO 3 (23H-07H)</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# CONSTRUÇÃO DA TABELA POR ABA DOS TURNOS
# ============================================================
DIAS = [("Sexta", "sexta"), ("Sábado", "sabado"), ("Domingo", "domingo"), ("Segunda", "segunda")]

aba_t1, aba_t2, aba_t3 = st.tabs(["🌅 Turno T1", "🌆 Turno T2", "🌌 Turno T3"])
abas_mapeamento = {"T1": aba_t1, "T2": aba_t2, "T3": aba_t3}

for turno in ["T1", "T2", "T3"]:
    with abas_mapeamento[turno]:
        operadores_turno = [x for x in operadores if x[3] == turno]

        if not operadores_turno:
            st.markdown("<p style='color:#64748B;font-size:13px;'>Nenhum operador vinculado a este turno.</p>", unsafe_allow_html=True)
            continue

        st.markdown(f"""
            <div class='turno-header'>
                <div class='turno-titulo'>🕒 {NOMES_TURNOS[turno]}</div>
                <div class='turno-horario'>Horário de Janela: {HORARIOS[turno]}</div>
            </div>
        """, unsafe_allow_html=True)

        headers = st.columns([2.5, 2, 1.8, 1.8, 1.8, 1.8])
        headers[0].markdown("<div class='header-col header-esquerda'>Operador</div>", unsafe_allow_html=True)
        headers[1].markdown("<div class='header-col header-esquerda'>Função</div>", unsafe_allow_html=True)
        
        for idx, (dia, _) in enumerate(DIAS, 2):
            headers[idx].markdown(f"<div class='header-col'>{dia} ({semana[dia]})</div>", unsafe_allow_html=True)

        st.markdown("<div class='separador'></div>", unsafe_allow_html=True)

        for operador in operadores_turno:
            operador_id, nome, funcao = operador[0], operador[1], operador[2]
            status = buscar_status(operador_id, semana_id)

            if status is None:
                horario = HORARIOS[turno]
                status = (horario, horario, horario, horario)
                salvar_status(operador_id, semana_id, *status)

            linha = st.columns([2.5, 2, 1.8, 1.8, 1.8, 1.8])
            linha[0].markdown(f"<div class='nome-operador'>{nome}</div>", unsafe_allow_html=True)
            linha[1].markdown(f"<div class='funcao-operador'>{funcao}</div>", unsafe_allow_html=True)

            status_lista = list(status)

            for idx, (dia, _) in enumerate(DIAS, 2):
                valor = status_lista[idx - 2]

                if valor != "FOLGA":
                    linha[idx].markdown(f"""
                        <div class='card-trabalho'>
                            TRABALHO
                            <div class='sub-info'>{HORARIOS[turno]}</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    linha[idx].markdown("""
                        <div class='card-folga'>
                            FOLGA
                            <div class='sub-info-folga'>Escala de Descanso</div>
                        </div>
                    """, unsafe_allow_html=True)

                if st.session_state.autenticado:
                    novo_valor = HORARIOS[turno] if valor == "FOLGA" else "FOLGA"
                    # Uso do on_click resolve o bug do botão fantasma que exige dois cliques
                    linha[idx].button(
                        "🔄 Alternar", 
                        key=f"{operador_id}_{semana_id}_{dia}_{turno}_d", 
                        use_container_width=True,
                        on_click=alternar_status_callback,
                        args=(operador_id, semana_id, status_lista.copy(), idx - 2, novo_valor)
                    )

st.divider()
st.caption("Amazon Control Center • Plataforma de Gestão Organizada")
