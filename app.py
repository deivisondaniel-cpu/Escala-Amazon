import streamlit as st
import sqlite3
from datetime import datetime, timedelta

# ============================================================
# CONFIGURAÇÃO
# ============================================================
st.set_page_config(
    page_title="Escala Amazon",
    page_icon="amazon.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# BANCO INTERNO
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

# ============================================================
# HORÁRIOS OFICIAIS
# ============================================================
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
# CSS IDENTIDADE AMAZON (CORREÇÃO DE ESPAÇOS E ALINHAMENTO)
# ============================================================
st.markdown("""
<style>
/* Reset de layout nativo do Streamlit */
header[data-testid="stHeader"] { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDecoration { display: none !important; }
[data-testid="stSidebar"] { display: none; }
[data-testid="stAppViewContainer"] { background-color: #F3F6F9; }
.stApp { background-color: #F3F6F9; }
.stMainBlockContainer { padding-top: 20px !important; padding-bottom: 30px !important; }

/* Identidade Visual - Cabeçalho */
.titulo { 
    color: #232F3E; 
    font-family: 'Segoe UI', sans-serif; 
    font-size: 34px; 
    font-weight: 800; 
    letter-spacing: -0.5px;
}
.subtitulo { 
    color: #146EB4; 
    font-size: 13px; 
    font-weight: 700; 
    text-transform: uppercase;
    letter-spacing: 0.8px; 
    margin-bottom: 20px; 
}

/* Forçar os botões Popover a ficarem no padrão Escuro Amazon */
div[data-testid="stPopover"] > button {
    background-color: #232F3E !important;
    color: #FFFFFF !important;
    border: 1px solid #232F3E !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
}
div[data-testid="stPopover"] > button:hover {
    background-color: #FF9900 !important;
    border-color: #FF9900 !important;
    color: #232F3E !important;
}

/* Alinhamento e Visual dos Cards de Escala (Ocupando 100% da coluna) */
.card-trabalho, .card-folga {
    width: 100% !important;
    box-sizing: border-box !important;
    padding: 10px 6px;
    border-radius: 6px;
    text-align: center;
    font-weight: 700;
    font-size: 11px;
    min-height: 48px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.card-trabalho {
    background-color: #232F3E;
    color: #FFFFFF;
    border-left: 4px solid #FF9900;
    box-shadow: 0 2px 4px rgba(35,47,62,0.1);
}
.sub-info { color: #FF9900; font-size: 10px; margin-top: 2px; font-weight: 700; }

.card-folga {
    background-color: #EAF3FB;
    color: #146EB4;
    border-left: 4px solid #146EB4;
}
.sub-info-folga { color: #6B8196; font-size: 10px; margin-top: 2px; font-weight: 600; }

/* Correção das colunas nativas do Streamlit para remover margens fantasmas */
div[data-testid="column"] {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    padding: 0px !important;
}

/* Estilização dos Mini Botões "Alternar" */
div[data-testid="column"] .stButton > button {
    border-radius: 5px !important;
    font-size: 10px !important;
    padding: 1px 4px !important;
    background-color: #FFFFFF !important;
    color: #232F3E !important;
    border: 1px solid #CBD5E1 !important;
    margin-top: 3px !important;
    height: auto !important;
}
div[data-testid="column"] .stButton > button:hover {
    border-color: #FF9900 !important;
    color: #FF9900 !important;
}

/* Banner de identificação de Turno */
.turno-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 15px;
    margin-bottom: 15px;
    padding: 10px 16px;
    background-color: #FFFFFF;
    border-left: 5px solid #FF9900;
    border-radius: 8px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}
.turno-titulo { font-size: 18px; font-weight: 800; color: #232F3E; }
.turno-horario {
    background-color: #EAF3FB;
    color: #146EB4;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 800;
}

/* Linhas e separadores */
.header-col { text-align: center; font-weight: 800; font-size: 11px; color: #232F3E; margin-bottom: 6px; }
.header-esquerda { text-align: left; }
.nome-operador { padding-top: 12px; font-size: 13px; color: #232F3E; }
.funcao-operador { padding-top: 14px; font-size: 11px; color: #617184; font-weight: 600; }
.separador { border: 0; border-top: 1px solid #CBD5E1; margin-top: 2px; margin-bottom: 12px; }

/* Grid de métricas customizado em HTML puro para evitar bugs do Streamlit */
.metrics-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
    margin-bottom: 20px;
}
.metric-box {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 14px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.metric-box.total { border-top: 4px solid #FF9900; }
.metric-box.turno { border-top: 4px solid #146EB4; }
.metric-num { font-size: 24px; font-weight: 800; color: #232F3E; }
.metric-lab { font-size: 11px; color: #617184; font-weight: 700; margin-top: 2px; }

@media (max-width: 800px) {
    .metrics-container { grid-template-columns: 1fr 1fr; }
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# LOGIN STATE
# ============================================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# ============================================================
# FUNÇÕES DE BANCO E CALLBACK REATIVO
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

def alternar_status_callback(operador_id, semana_id, lista_atual, index_dia, novo_valor):
    lista_atual[index_dia] = novo_valor
    salvar_status(operador_id, semana_id, *lista_atual)

# ============================================================
# GERAÇÃO DE DATAS
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
# CABEÇALHO DA APLICAÇÃO (TÍTULO + LOGIN GESTOR)
# ============================================================
col_tit, col_log = st.columns([4, 1], vertical_alignment="center")

with col_tit:
    st.markdown("<div class='titulo'>Escala Amazon</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitulo'>Monitoramento Amazon</div>", unsafe_allow_html=True)

with col_log:
    if not st.session_state.autenticado:
        with st.popover("👤 Área do Gestor", use_container_width=True):
            with st.form("login_form", clear_on_submit=True):
                usuario = st.text_input("Usuário")
                senha = st.text_input("Senha", type="password")
                entrar = st.form_submit_button("Entrar", use_container_width=True)

                if entrar:
                    if usuario.lower().strip() == "admin" and senha == "Amazon123":
                        st.session_state.autenticado = True
                        st.rerun()
                    else:
                        st.error("Dados incorretos.")
    else:
        with st.popover("⚙️ Painel de Gestão", use_container_width=True):
            st.markdown("🟢 **Modo Administrador**")
            st.divider()
            
            menu_admin = st.selectbox("O que deseja fazer?", ["Adicionar Operador", "Remover Operador"])
            
            if menu_admin == "Adicionar Operador":
                novo_nome = st.text_input("Nome").strip().upper()
                nova_funcao = st.text_input("Função").strip().upper()
                novo_turno = st.selectbox(
                    "Turno", ["T1", "T2", "T3"],
                    format_func=lambda x: f"{NOMES_TURNOS[x]} — {HORARIOS[x]}"
                )
                if st.button("Confirmar Cadastro", use_container_width=True):
                    if novo_nome and nova_funcao:
                        cadastrar_operador(novo_nome, nova_funcao, novo_turno)
                        st.success("Operador cadastrado!")
                        st.rerun()
                    else:
                        st.warning("Preencha todos os campos.")
                        
            elif menu_admin == "Remover Operador":
                operadores_lista = buscar_operadores()
                if operadores_lista:
                    opcoes_remocao = {f"{x[1]} — {x[2]}": x[0] for x in operadores_lista}
                    selecionado = st.selectbox("Selecione o operador", list(opcoes_remocao.keys()))
                    if st.button("Confirmar Remoção", use_container_width=True):
                        remover_operador(opcoes_remocao[selecionado])
                        st.success("Operador removido!")
                        st.rerun()
                else:
                    st.info("Nenhum operador cadastrado.")
                    
            st.divider()
            if st.button("🚪 Sair", use_container_width=True):
                st.session_state.autenticado = False
                st.rerun()

# ============================================================
# FILTRO DE SEMANA
# ============================================================
semana_labels = [x["nome"] for x in semanas]
semana_escolhida = st.selectbox("📅 Período da escala", semana_labels, index=2)
semana = semanas[semana_labels.index(semana_escolhida)]
semana_id = semana["id"]

operadores = buscar_operadores()

# ============================================================
# MÉTRICAS COM GRID CORRIGIDO EM HTML/CSS (FIM DO BUG DE ESPAÇO)
# ============================================================
total = len(operadores)
t1 = len([x for x in operadores if x[3] == "T1"])
t2 = len([x for x in operadores if x[3] == "T2"])
t3 = len([x for x in operadores if x[3] == "T3"])

st.markdown(f"""
<div class='metrics-container'>
    <div class='metric-box total'>
        <div class='metric-num'>{total}</div>
        <div class='metric-lab'>OPERADORES TOTAL</div>
    </div>
    <div class='metric-box turno'>
        <div class='metric-num'>{t1}</div>
        <div class='metric-lab'>T1 • 07h às 15h</div>
    </div>
    <div class='metric-box turno'>
        <div class='metric-num'>{t2}</div>
        <div class='metric-lab'>T2 • 15h às 23h</div>
    </div>
    <div class='metric-box turno'>
        <div class='metric-num'>{t3}</div>
        <div class='metric-lab'>T3 • 23h às 07h</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# ABAS DE NAVEGAÇÃO DOS TURNOS
# ============================================================
DIAS = [("Sexta", "sexta"), ("Sábado", "sabado"), ("Domingo", "domingo"), ("Segunda", "segunda")]

aba_t1, aba_t2, aba_t3 = st.tabs(["🌅 Turno 1 (07h às 15h)", "🌆 Turno 2 (15h às 23h)", "🌌 Turno 3 (23h às 07h)"])
abas_mapeamento = {"T1": aba_t1, "T2": aba_t2, "T3": aba_t3}

for turno in ["T1", "T2", "T3"]:
    with abas_mapeamento[turno]:
        operadores_turno = [x for x in operadores if x[3] == turno]

        if not operadores_turno:
            st.info(f"Nenhum operador alocado no {NOMES_TURNOS[turno]} para este período.")
            continue

        st.markdown(f"""
            <div class='turno-header'>
                <div class='turno-titulo'>🕒 {NOMES_TURNOS[turno]}</div>
                <div class='turno-horario'>{HORARIOS[turno]}</div>
            </div>
        """, unsafe_allow_html=True)

        headers = st.columns([2.5, 2, 1.8, 1.8, 1.8, 1.8])
        headers[0].markdown("<div class='header-col header-esquerda'>OPERADOR</div>", unsafe_allow_html=True)
        headers[1].markdown("<div class='header-col header-esquerda'>FUNÇÃO</div>", unsafe_allow_html=True)

        for i, (dia, _) in enumerate(DIAS, 2):
            headers[i].markdown(f"<div class='header-col'>{dia.upper()} ({semana[dia]})</div>", unsafe_allow_html=True)

        st.markdown("<div class='separador'></div>", unsafe_allow_html=True)

        for operador in operadores_turno:
            operador_id, nome, funcao = operador[0], operador[1], operador[2]
            status = buscar_status(operador_id, semana_id)

            if status is None:
                horario = HORARIOS[turno]
                status = (horario, horario, horario, horario)
                salvar_status(operador_id, semana_id, *status)

            linha = st.columns([2.5, 2, 1.8, 1.8, 1.8, 1.8])
            linha[0].markdown(f"<div class='nome-operador'><b>{nome}</b></div>", unsafe_allow_html=True)
            linha[1].markdown(f"<div class='funcao-operador'>{funcao}</div>", unsafe_allow_html=True)

            status_lista = list(status)

            for i, (dia, _) in enumerate(DIAS, 2):
                valor = status_lista[i - 2]

                if valor != "FOLGA":
                    linha[i].markdown(f"""
                        <div class='card-trabalho'>
                            TRABALHO
                            <div class='sub-info'>{HORARIOS[turno]}</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    linha[i].markdown("""
                        <div class='card-folga'>
                            FOLGA
                            <div class='sub-info-folga'>Descanso</div>
                        </div>
                    """, unsafe_allow_html=True)

                if st.session_state.autenticado:
                    novo_valor = HORARIOS[turno] if valor == "FOLGA" else "FOLGA"
                    linha[i].button(
                        "↔ Alternar", 
                        key=f"{operador_id}_{semana_id}_{dia}_{turno}", 
                        use_container_width=True,
                        on_click=alternar_status_callback,
                        args=(operador_id, semana_id, status_lista.copy(), i - 2, novo_valor)
                    )

st.divider()
st.caption("Escala Amazon • Sistema independente de gestão de escala")
