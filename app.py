import streamlit as st
import sqlite3
from datetime import datetime, timedelta

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Escala-Monitoramento-Amazon",
    page_icon="amazon.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# NOVO BANCO DE DADOS INTEGRADO (ZURADO - V2)
# ============================================================
BANCO = "escala_amazon_v2.db"

def conectar():
    return sqlite3.connect(BANCO, check_same_thread=False)

def criar_banco_do_zero():
    conn = conectar()
    cursor = conn.cursor()
    
    # Criação das tabelas estruturais
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
    
    # Injeção inicial forçada da lista oficial extraída das imagens
    dados_existentes = cursor.execute("SELECT COUNT(*) FROM operadores WHERE ativo = 1").fetchone()[0]
    if dados_existentes == 0:
        funcionarios_oficiais = [
            # 🌅 TURNO 1 (T1)
            ("ALAN ARAÚJO", "ANALISTA", "T1"),
            ("MARGARIDA", "PICKUP", "T1"),
            ("JOSÉ BRUNO PALHANO", "PICKUP", "T1"),
            ("CRISTOVÃO MIKELLYS", "DEPART", "T1"),
            ("PEDRO LUCAS", "DROPOFF", "T1"),
            ("FELIPE ALLAN", "DROPOFF", "T1"),
            ("BRUNA BLENDA", "DROPOFF", "T1"),
            ("CONCEIÇÃO DAIANE", "SEGURANÇA (ONISYS)", "T1"),
            ("MATHEUS LUSTOSA", "SEGURANÇA/ELOG", "T1"),

            # 🌆 TURNO 2 (T2)
            ("MANUELA PINHEIRO", "LÍDER", "T2"),
            ("ISABEL", "LÍDER/SEGURANÇA", "T2"),
            ("ANDREZA OLIVEIRA", "PICKUP", "T2"),
            ("ROZIANE DA SILVA", "PICKUP", "T2"),
            ("DAIANE", "SEGURANÇA", "T2"),
            ("EMANUEL ROBERTO", "DEPART", "T2"),
            ("TAMMYRIS DA SILVA", "DROPOFF", "T2"),
            ("RAPHAEL DO NASCIMENTO", "DROPOFF", "T2"),
            ("LUDMILLA RODRIGUES", "DROPOFF", "T2"),
            ("MARIA NATHALIA", "SEGURANÇA", "T2"),
            ("CINAMOR", "ELOG", "T2"),

            # 🌌 TURNO 3 (T3)
            ("WESLEY", "LÍDER", "T3"),
            ("JOÃO", "LÍDER/SEGURANÇA", "T3"),
            ("RILDOMAR", "PICKUP", "T3"),
            ("LUCIANA", "PICKUP", "T3"),
            ("GLAYLDSON", "SEGURANÇA", "T3"),
            ("TAYANARA", "DEPART", "T3"),
            ("RUAN", "DROPOFF", "T3"),
            ("BÁRBARA", "DROPOFF", "T3")
        ]
        cursor.executemany("""
            INSERT INTO operadores (nome, funcao, turno) VALUES (?, ?, ?)
        """, funcionarios_oficiais)
        conn.commit()
        
    conn.close()

# Executa a montagem limpa do projeto
criar_banco_do_zero()

# ============================================================
# HORÁRIOS E CONSTANTES
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
# CSS INJETADO (REMOÇÃO DA BARRA AZUL/COROA DO STREAMLIT)
# ============================================================
st.markdown("""
<style>
/* Oculta completamente os elementos nativos da Cloud do Streamlit */
header[data-testid="stHeader"], 
.stAppDeployButton, 
div[data-testid="stViewerBadge"],
footer,
#MainMenu,
.stDecoration { 
    display: none !important; 
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
    opacity: 0 !important;
}

[data-testid="stSidebar"] { display: none; }
[data-testid="stAppViewContainer"] { background-color: #F3F6F9; }
.stApp { background-color: #F3F6F9; }

.titulo {
    color: #232F3E;
    font-family: 'Segoe UI', sans-serif;
    font-size: 32px;
    font-weight: 800;
}

.subtitulo {
    color: #146EB4;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.2px;
    margin-bottom: 25px;
}

div[data-baseweb="select"] > div {
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    background-color: #FFFFFF !important;
}

.turno-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 15px;
    margin-bottom: 20px;
    padding: 10px 14px;
    background-color: #FFFFFF;
    border-left: 5px solid #FF9900;
    border-bottom: 1px solid #D7DEE7;
    border-radius: 8px;
    box-shadow: 0 2px 7px rgba(35,47,62,0.06);
}

.turno-titulo { font-size: 21px; font-weight: 800; color: #232F3E; }
.turno-horario {
    background-color: #EAF3FB;
    color: #146EB4;
    border: 1px solid #B9D7EE;
    padding: 4px 11px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 800;
}

.header-col { text-align: center; font-weight: 800; font-size: 12px; color: #232F3E; margin-bottom: 8px; }
.header-esquerda { text-align: left; }
.nome-operador { padding-top: 9px; font-size: 13px; color: #232F3E; }
.funcao-operador { padding-top: 9px; font-size: 11px; color: #617184; font-weight: 600; }

.card-trabalho {
    background-color: #232F3E;
    color: #FFFFFF;
    padding: 8px 5px;
    border-radius: 7px;
    text-align: center;
    font-weight: 700;
    font-size: 11px;
    border-left: 4px solid #FF9900;
    margin-bottom: 4px;
    min-height: 43px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.sub-info { color: #FFB84D; font-size: 10px; margin-top: 3px; font-weight: 700; }

.card-folga {
    background-color: #EAF3FB;
    color: #232F3E;
    padding: 8px 5px;
    border-radius: 7px;
    text-align: center;
    font-weight: 800;
    font-size: 11px;
    border-left: 4px solid #146EB4;
    margin-bottom: 4px;
    min-height: 43px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.sub-info-folga { color: #6B8196; font-size: 10px; margin-top: 3px; font-weight: 600; }

.separador { border: 0; border-top: 1px solid #D7DEE7; margin-top: 2px; margin-bottom: 15px; }

.metric-card {
    background-color: #FFFFFF;
    border: 1px solid #D7DEE7;
    border-top: 4px solid #146EB4;
    border-radius: 10px;
    padding: 12px;
    text-align: center;
    box-shadow: 0 2px 7px rgba(35,47,62,0.06);
}
.metric-numero { font-size: 22px; font-weight: 800; color: #232F3E; }
.metric-label { font-size: 11px; color: #617184; font-weight: 700; }
.metric-card:first-child { border-top-color: #FF9900; }

[data-testid="stForm"] { background-color: #FFFFFF; border: none; padding: 0px; }
.stButton > button { border-radius: 7px; font-weight: 700; border: 1px solid #D7DEE7; }
div[data-testid="column"] .stButton > button { color: #232F3E; }
div[data-baseweb="input"] { border-radius: 7px; }
.stMainBlockContainer { padding-top: 25px !important; padding-bottom: 30px !important; }
.stCaption { color: #617184 !important; }

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

@media (max-width: 800px) {
    .titulo { font-size: 24px; }
    .turno-titulo { font-size: 18px; }
    .turno-horario { font-size: 10px; }
    .metric-numero { font-size: 18px; }
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSÃO DE AUTENTICAÇÃO
# ============================================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# ============================================================
# OPERAÇÕES DE CONSULTA BANCO
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

# ============================================================
# MONITORAMENTO DE DATAS DA ESCALA
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
# CORE - RENDERIZAÇÃO DO TOP BAR
# ============================================================
col_tit, col_log = st.columns([4, 1], vertical_alignment="center")

with col_tit:
    st.markdown("<div class='titulo'>Monitoramento Amazon</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitulo'>Escala do turno</div>", unsafe_allow_html=True)

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
            st.markdown("🟢 **Modo Gestor ativo**")
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
# FILTRO DE SELEÇÃO GLOBAL
# ============================================================
semana_labels = [x["nome"] for x in semanas]
semana_escolhida = st.selectbox("📅 Período da escala", semana_labels, index=2)
semana = semanas[semana_labels.index(semana_escolhida)]
semana_id = semana["id"]

operadores = buscar_operadores()

# ============================================================
# RECONSTRUÇÃO DAS MÉTRICAS EM TEMPO REAL
# ============================================================
total = len(operadores)
t1 = len([x for x in operadores if x[3] == "T1"])
t2 = len([x for x in operadores if x[3] == "T2"])
t3 = len([x for x in operadores if x[3] == "T3"])

m1, m2, m3, m4 = st.columns(4)
with m1: st.markdown(f"<div class='metric-card'><div class='metric-numero'>{total}</div><div class='metric-label'>OPERADORES TOTAL</div></div>", unsafe_allow_html=True)
with m2: st.markdown(f"<div class='metric-card'><div class='metric-numero'>{t1}</div><div class='metric-label'>T1 • 07h às 15h</div></div>", unsafe_allow_html=True)
with m3: st.markdown(f"<div class='metric-card'><div class='metric-numero'>{t2}</div><div class='metric-label'>T2 • 15h às 23h</div></div>", unsafe_allow_html=True)
with m4: st.markdown(f"<div class='metric-card'><div class='metric-numero'>{t3}</div><div class='metric-label'>T3 • 23h às 07h</div></div>", unsafe_allow_html=True)

st.write("")

# ============================================================
# CONSTRUÇÃO DO GRID DE TURNOS (ABAS INDEPENDENTES)
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
                    if linha[i].button("↔ Alternar", key=f"{operador_id}_{semana_id}_{dia}_{turno}", use_container_width=True):
                        status_lista[i - 2] = novo_valor
                        salvar_status(operador_id, semana_id, *status_lista)
                        st.rerun()

st.divider()
st.caption("Escala Amazon • Sistema independente de gestão de escala")
