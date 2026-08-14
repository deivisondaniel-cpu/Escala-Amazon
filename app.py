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
# CSS PROFISSIONAL: ULTRA COMPACTO & ALTO CONTRASTE
# ============================================================
st.markdown("""
<style>
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDecoration { display: none !important; }
[data-testid="stSidebar"] { display: none; }

/* Correção do topo e redução drástica do espaçamento global */
[data-testid="stAppViewContainer"], .stApp {
    background-color: #0A121C !important;
}
.stMainBlockContainer {
    padding-top: 5px !important;
    padding-bottom: 10px !important;
    max-width: 98% !important;
}

/* Títulos corrigidos (sem cortes) e menores */
.titulo {
    color: #FFFFFF;
    font-family: 'Segoe UI', sans-serif;
    font-size: 24px;
    font-weight: 800;
    line-height: 1.2;
}
.subtitulo {
    color: #FF5500;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 10px;
}

/* Filtro de período super enxuto */
div[data-baseweb="select"] > div {
    border: 1px solid #1A2635 !important;
    border-radius: 6px !important;
    background-color: #121E2B !important;
    min-height: 30px !important;
}
div[data-baseweb="select"] span {
    color: #FFFFFF !important;
    font-size: 12px !important;
}

/* Área do Gestor - Botão Branco Clean */
div[data-testid="stPopover"] > button {
    background-color: #FFFFFF !important;
    color: #0A121C !important;
    border: 1px solid #E2E8F0 !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
    padding: 2px 10px !important;
    font-size: 12px !important;
}
div[data-testid="stPopover"] > button:hover {
    color: #FF5500 !important;
    background-color: #F8FAFC !important;
}

/* Balão do Popover 100% Branco Interno */
div[data-testid="stPopoverBody"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 6px !important;
    box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2) !important;
    padding: 10px !important;
}
div[data-testid="stPopoverBody"] label p { color: #334155 !important; font-weight: 600; font-size: 12px; }
div[data-testid="stPopoverBody"] input { background-color: #F8FAFC !important; color: #0F172A !important; border: 1px solid #CBD5E1 !important; height: 30px; }
div[data-testid="stPopoverBody"] button[type="submit"] { background-color: #0F172A !important; color: #FFFFFF !important; font-weight: 700; border: none !important; }
div[data-testid="stPopoverBody"] p, div[data-testid="stPopoverBody"] span { color: #334155 !important; }

/* Mini Cards de Métricas (Ganho de espaço vertical) */
.metric-card {
    background-color: #121E2B;
    border: 1px solid #1A2635;
    border-radius: 6px;
    padding: 6px 10px;
    text-align: center;
}
.metric-numero { font-size: 18px; font-weight: 800; color: #FFFFFF; line-height: 1.1; }
.metric-label { font-size: 10px; color: #8FA0B5; font-weight: 700; letter-spacing: 0.5px; }

/* Abas (Tabs) compactas e com alto contraste nas inativas */
.stTabs [data-baseweb="tab-list"] { background-color: #121E2B; border-radius: 6px; padding: 2px; gap: 4px; }
.stTabs [data-baseweb="tab"] { color: #A0AEC0 !important; font-weight: 700; font-size: 12px !important; padding: 6px 12px !important; }
.stTabs [aria-selected="true"] { color: #FFFFFF !important; background-color: #FF5500; border-radius: 4px; }

/* Faixa informativa do turno mais fina */
.turno-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 8px;
    margin-bottom: 10px;
    padding: 4px 10px;
    background-color: #121E2B;
    border-left: 4px solid #FF5500;
    border-radius: 4px;
}
.turno-titulo { font-size: 14px; font-weight: 800; color: #FFFFFF; }
.turno-horario {
    background-color: #0A121C;
    color: #FF5500;
    border: 1px solid #FF5500;
    padding: 1px 8px;
    border-radius: 12px;
    font-size: 10px;
    font-weight: 800;
}

/* Estrutura da Tabela de Operadores de Alta Densidade */
.header-col { text-align: center; font-weight: 800; font-size: 10px; color: #FF5500; margin-bottom: 4px; letter-spacing: 0.5px; }
.header-esquerda { text-align: left; }
.nome-operador { padding-top: 6px; font-size: 12px; color: #FFFFFF; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.funcao-operador { padding-top: 6px; font-size: 11px; color: #8FA0B5; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* CARD FOLGA (Destaque Laranja Vibrante) */
.card-folga {
    background-color: #FF5500;
    color: #FFFFFF;
    padding: 4px;
    border-radius: 6px;
    text-align: center;
    font-weight: 800;
    font-size: 11px;
    min-height: 32px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-shadow: 0px 2px 6px rgba(255, 85, 0, 0.2);
}
.sub-info-folga { color: #FFFFFF; font-size: 9px; font-weight: 700; opacity: 0.9; }

/* CARD TRABALHO (Ajustado com ALTO CONTRASTE nas letras) */
.card-trabalho {
    background-color: #121E2B;
    color: #FFFFFF;
    padding: 4px;
    border-radius: 6px;
    text-align: center;
    font-weight: 700;
    font-size: 11px;
    border: 1px solid #1A2635;
    min-height: 32px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.sub-info { color: #E2E8F0 !important; font-size: 9px; font-weight: 600; opacity: 1; } /* Cinza claro totalmente visível */

/* Reduzir o tamanho dos botões de alternar para os gestores */
.stButton > button {
    padding: 1px 4px !important;
    font-size: 10px !important;
    min-height: 20px !important;
    height: 22px !important;
    background-color: #121E2B !important;
    color: #E2E8F0 !important;
    border: 1px solid #1A2635 !important;
}
.stButton > button:hover { border-color: #FF5500 !important; color: #FF5500 !important; }

[data-testid="stForm"] { background-color: transparent; border: none; padding: 0px; }
.separador { border: 0; border-top: 1px solid #121E2B; margin-top: 2px; margin-bottom: 6px; }
.stMarkdown div p { margin-bottom: 0px !important; }
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
        """, (sexta, sabado, domingo, segunda, operador_id, semana_id))
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
# CABEÇALHO COMPACTO ALINHADO
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
# FILTRO DE SEMANA COMPACTO
# ============================================================
semana_labels = [x["nome"] for x in semanas]
semana_escolhida = st.selectbox("📅 Período da escala", semana_labels, index=2)
semana = semanas[semana_labels.index(semana_escolhida)]
semana_id = semana["id"]

operadores = buscar_operadores()

# ============================================================
# MINI PAINEL DE MÉTRICAS (MUITO MAIS FINO)
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

# ============================================================
# ABAS DE TURNO COMPACTAS
# ============================================================
DIAS = [("Sexta", "sexta"), ("Sábado", "sabado"), ("Domingo", "domingo"), ("Segunda", "segunda")]

aba_t1, aba_t2, aba_t3 = st.tabs(["🌅 Turno 1", "🌆 Turno 2", "🌌 Turno 3"])
abas_mapeamento = {"T1": aba_t1, "T2": aba_t2, "T3": aba_t3}

for turno in ["T1", "T2", "T3"]:
    with abas_mapeamento[turno]:
        operadores_turno = [x for x in operadores if x[3] == turno]

        if not operadores_turno:
            st.info(f"Nenhum operador alocado no {NOMES_TURNOS[turno]}.")
            continue

        st.markdown(f"""
            <div class='turno-header'>
                <div class='turno-titulo'>🕒 {NOMES_TURNOS[turno]}</div>
                <div class='turno-horario'>{HORARIOS[turno]}</div>
            </div>
        """, unsafe_allow_html=True)

        # Montagem da Grid compacta
        headers = st.columns([2.2, 1.8, 2, 2, 2, 2])
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

            linha = st.columns([2.2, 1.8, 2, 2, 2, 2])
            linha[0].markdown(f"<div class='nome-operador'><b>{nome}</b></div>", unsafe_allow_html=True)
            linha[1].markdown(f"<div class='funcao-operador'>{funcao}</div>", unsafe_allow_html=True)

            status_lista = list(status)

            for i, (dia, _) in enumerate(DIAS, 2):
                valor = status_lista[i - 2]

                if valor == "FOLGA":
                    linha[i].markdown("""
                        <div class='card-folga'>
                            FOLGA
                            <div class='sub-info-folga'>Descanso</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    linha[i].markdown(f"""
                        <div class='card-trabalho'>
                            TRABALHO
                            <div class='sub-info'>{HORARIOS[turno]}</div>
                        </div>
                    """, unsafe_allow_html=True)

                # Botão administrativo alinhado e enxuto embaixo do card se logado
                if st.session_state.autenticado:
                    novo_valor = HORARIOS[turno] if valor == "FOLGA" else "FOLGA"
                    if linha[i].button("Alternar", key=f"{operador_id}_{semana_id}_{dia}_{turno}", use_container_width=True):
                        status_lista[i - 2] = novo_valor
                        salvar_status(operador_id, semana_id, *status_lista)
                        st.rerun()
