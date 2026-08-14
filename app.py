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
# CSS REFORMULADO (DARK COMPACTO E POPOVER INTEGRADO)
# ============================================================
st.markdown("""
<style>
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDecoration { display: none !important; }

/* Remove a barra lateral */
[data-testid="stSidebar"] { display: none; }

/* Fundo Principal Dark Corporativo */
[data-testid="stAppViewContainer"], .stApp {
    background-color: #131A22 !important;
}

/* Títulos principais */
.titulo {
    color: #FFFFFF;
    font-family: 'Segoe UI', sans-serif;
    font-size: 32px;
    font-weight: 800;
}
.subtitulo {
    color: #FF9900;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 20px;
}

/* Filtro de período */
div[data-baseweb="select"] > div {
    border: 1px solid #232F3E !important;
    border-radius: 6px !important;
    background-color: #232F3E !important;
}
div[data-baseweb="select"] span {
    color: #FFFFFF !important;
}

/* Botão de Área do Gestor (Superior Direito) */
div[data-testid="stPopover"] > button {
    background-color: #232F3E !important;
    color: #FFFFFF !important;
    border: 1px solid #37475A !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
    padding: 6px 16px !important;
}
div[data-testid="stPopover"] > button:hover {
    background-color: #37475A !important;
    border-color: #FF9900 !important;
    color: #FF9900 !important;
}

/* FIX CRÍTICO: Força o Balão do Popover a ficar escuro */
div[data-testid="stPopoverBody"] {
    background-color: #232F3E !important;
    border: 1px solid #37475A !important;
    border-radius: 8px !important;
    box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.5) !important;
}
div[data-testid="stPopoverBody"] label p {
    color: #FFFFFF !important;
}
div[data-testid="stPopoverBody"] input {
    background-color: #131A22 !important;
    color: #FFFFFF !important;
    border: 1px solid #37475A !important;
}

/* Botão de Entrar interno do formulário */
div[data-testid="stPopoverBody"] button[type="submit"] {
    background-color: #FF9900 !important;
    color: #131A22 !important;
    font-weight: 700 !important;
    border: none !important;
}

/* Métricas do Painel */
.metric-card {
    background-color: #232F3E;
    border: 1px solid #37475A;
    border-radius: 8px;
    padding: 14px;
    text-align: center;
}
.metric-numero { font-size: 26px; font-weight: 800; color: #FFFFFF; }
.metric-label { font-size: 11px; color: #99AAB5; font-weight: 700; letter-spacing: 0.5px; }

/* Abas (Tabs) customizadas */
.stTabs [data-baseweb="tab-list"] { background-color: #232F3E; border-radius: 6px; padding: 4px; }
.stTabs [data-baseweb="tab"] { color: #99AAB5 !important; font-weight: 700; }
.stTabs [aria-selected="true"] { color: #FF9900 !important; background-color: #131A22; border-radius: 4px; }

/* Cabeçalho do Turno Ativo */
.turno-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 15px;
    margin-bottom: 20px;
    padding: 10px 14px;
    background-color: #232F3E;
    border-left: 5px solid #FF9900;
    border-radius: 6px;
}
.turno-titulo { font-size: 20px; font-weight: 800; color: #FFFFFF; }
.turno-horario {
    background-color: #131A22;
    color: #FF9900;
    border: 1px solid #FF9900;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 800;
}

/* Colunas da tabela */
.header-col { text-align: center; font-weight: 800; font-size: 11px; color: #FF9900; margin-bottom: 10px; letter-spacing: 0.5px; }
.header-esquerda { text-align: left; }
.nome-operador { padding-top: 10px; font-size: 13px; color: #FFFFFF; font-weight: 700; }
.funcao-operador { padding-top: 10px; font-size: 11px; color: #99AAB5; font-weight: 600; }

/* CARDS DE STATUS (Trabalho vs Folga) */
.card-trabalho {
    background-color: #FF9900;
    color: #131A22;
    padding: 8px;
    border-radius: 6px;
    text-align: center;
    font-weight: 800;
    font-size: 11px;
    min-height: 44px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.sub-info { color: #131A22; font-size: 10px; font-weight: 700; opacity: 0.8; }

.card-folga {
    background-color: #232F3E;
    color: #8494A5;
    padding: 8px;
    border-radius: 6px;
    text-align: center;
    font-weight: 700;
    font-size: 11px;
    border: 1px solid #37475A;
    min-height: 44px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.sub-info-folga { color: #526273; font-size: 10px; }

.separador { border: 0; border-top: 1px solid #232F3E; margin-top: 4px; margin-bottom: 15px; }
.stMainBlockContainer { padding-top: 20px !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# LOGIN STATE
# ============================================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# ============================================================
# FUNÇÕES DE BANCO
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
# DATAS
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
# CABEÇALHO DA APLICAÇÃO (TÍTULO + LOGIN ALINHADOS)
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
            st.markdown("<span style='color:#FF9900; font-weight:bold;'>🟢 Modo Administrador</span>", unsafe_allow_html=True)
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
# MÉTRICAS DO PAINEL
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
# ABAS DE NAVEGAÇÃO DOS TURNOS
# ============================================================
DIAS = [("Sexta", "sexta"), ("Sábado", "sabado"), ("Domingo", "domingo"), ("Segunda", "segunda")]

aba_t1, aba_t2, aba_t3 = st.tabs(["🌅 Turno 1", "🌆 Turno 2", "🌌 Turno 3"])
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
