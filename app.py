import streamlit as st
import sqlite3
from datetime import datetime, timedelta

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Escala Monitoramento - Amazon",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# BANCO DE DADOS INTEGRADO
# ============================================================
BANCO = "escala_amazon_v2.db"

def conectar():
    return sqlite3.connect(BANCO, check_same_thread=False)

def criar_banco_do_zero():
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
    
    dados_existentes = cursor.execute("SELECT COUNT(*) FROM operadores WHERE ativo = 1").fetchone()[0]
    if dados_existentes == 0:
        funcionarios_oficiais = [
            ("ALAN ARAÚJO", "ANALISTA", "T1"),
            ("MARGARIDA", "PICKUP", "T1"),
            ("JOSÉ BRUNO PALHANO", "PICKUP", "T1"),
            ("CRISTOVÃO MIKELLYS", "DEPART", "T1"),
            ("PEDRO LUCAS", "DROPOFF", "T1"),
            ("FELIPE ALLAN", "DROPOFF", "T1"),
            ("BRUNA BLENDA", "DROPOFF", "T1"),
            ("CONCEIÇÃO DAIANE", "SEGURANÇA (ONISYS)", "T1"),
            ("MATHEUS LUSTOSA", "SEGURANÇA/ELOG", "T1"),
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
            ("WESLEY", "LÍDER", "T3"),
            ("JOÃO", "LÍDER/SEGURANÇA", "T3"),
            ("RILDOMAR", "PICKUP", "T3"),
            ("LUCIANA", "PICKUP", "T3"),
            ("GLAYLDSON", "SEGURANÇA", "T3"),
            ("TAYANARA", "DEPART", "T3"),
            ("RUAN", "DROPOFF", "T3"),
            ("BÁRBARA", "DROPOFF", "T3")
        ]
        cursor.executemany("INSERT INTO operadores (nome, funcao, turno) VALUES (?, ?, ?)", funcionarios_oficiais)
        conn.commit()
    conn.close()

criar_banco_do_zero()

HORARIOS = {"T1": "07:00 às 15:00", "T2": "15:00 às 23:00", "T3": "23:00 às 07:00"}
NOMES_TURNOS = {"T1": "Turno 1", "T2": "Turno 2", "T3": "Turno 3"}

# ============================================================
# CSS INJETADO (OTIMIZAÇÃO DE ESPAÇO E DESIGN AMAZON)
# ============================================================
st.markdown("""
<style>
header[data-testid="stHeader"], .stAppDeployButton, div[data-testid="stViewerBadge"], footer, #MainMenu, .stDecoration { 
    display: none !important; visibility: hidden !important; width: 0 !important; height: 0 !important; opacity: 0 !important;
}
[data-testid="stSidebar"] { display: none; }
.stApp { background-color: #FAFAFA; }
.stMainBlockContainer { padding: 15px 20px !important; max-width: 100% !important; }

/* Título Premium */
.titulo-container { margin-bottom: 10px; }
.titulo { color: #232F3E; font-family: 'Segoe UI', sans-serif; font-size: 26px; font-weight: 800; display: inline-block; }
.subtitulo { color: #FF9900; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }

/* Filtros Menores */
div[data-baseweb="select"] > div { border: 1px solid #D5D9D9 !important; border-radius: 4px !important; min-height: 34px !important; }

/* Métricas Compactas */
.metric-grid { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 15px; }
.metric-card { flex: 1; min-width: 140px; background: #FFFFFF; border: 1px solid #D5D9D9; border-radius: 4px; padding: 8px 12px; text-align: left; border-top: 3px solid #232F3E; }
.metric-card.total { border-top-color: #FF9900; }
.metric-numero { font-size: 20px; font-weight: 800; color: #111111; line-height: 1.1; }
.metric-label { font-size: 11px; color: #565959; font-weight: 600; margin-top: 2px; }

/* Headers e Abas */
.stTabs [data-baseweb="tab"] { font-size: 13px !important; font-weight: 700 !important; padding: 6px 12px !important; color: #565959 !important; }
.stTabs [aria-selected="true"] { color: #232F3E !important; border-bottom-color: #FF9900 !important; }
.turno-header { display: flex; align-items: center; gap: 8px; margin: 10px 0; padding: 6px 12px; background-color: #232F3E; color: white; border-radius: 4px; }
.turno-titulo { font-size: 14px; font-weight: 700; }
.turno-horario { background-color: rgba(255,153,0,0.2); color: #FF9900; padding: 2px 8px; border-radius: 2px; font-size: 11px; font-weight: 700; }

/* Grid de Escala Compacto */
.header-col { font-weight: 700; font-size: 11px; color: #565959; text-transform: uppercase; padding-bottom: 4px; border-bottom: 1px solid #E7E9E9; }
.nome-operador { font-size: 13px; font-weight: 700; color: #111111; line-height: 1.2; }
.funcao-operador { font-size: 11px; color: #565959; font-weight: 500; }

/* Cards de Status Otimizados */
.card-status { padding: 4px 6px; border-radius: 4px; text-align: center; font-size: 11px; font-weight: 700; display: flex; flex-direction: column; justify-content: center; min-height: 38px; }
.status-trabalho { background-color: #FFF8F2; color: #C45500; border: 1px solid #FBD8B4; }
.status-folga { background-color: #F0F2F2; color: #565959; border: 1px solid #D5D9D9; }
.sub-status { font-size: 9px; font-weight: 500; opacity: 0.8; }

/* Mobile Card Layout */
.mobile-operator-card { background: white; border: 1px solid #E7E9E9; border-radius: 6px; padding: 12px; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.mobile-day-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px dashed #F3F3F3; }
.mobile-day-row:last-child { border-bottom: none; }

div[data-testid="stForm"] { background-color: transparent; }
.stButton > button { font-size: 11px !important; padding: 2px 8px !important; border-radius: 4px !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNÇÕES DE BANCO E CONSULTAS
# ============================================================
def buscar_operadores():
    conn = conectar()
    dados = conn.execute("SELECT id, nome, funcao, turno FROM operadores WHERE ativo = 1 ORDER BY turno, nome").fetchall()
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
    resultado = conn.execute("SELECT sexta, sabado, domingo, segunda FROM escala WHERE operador_id = ? AND semana_id = ?", (operador_id, semana_id)).fetchone()
    conn.close()
    return resultado

def salvar_status(operador_id, semana_id, sexta, sabado, domingo, segunda):
    conn = conectar()
    existente = conn.execute("SELECT id FROM escala WHERE operador_id = ? AND semana_id = ?", (operador_id, semana_id)).fetchone()
    if existente:
        conn.execute("UPDATE escala SET sexta = ?, sabado = ?, domingo = ?, segunda = ? WHERE operador_id = ? AND semana_id = ?", (sexta, sabado, domingo, segunda, operador_id, semana_id))
    else:
        conn.execute("INSERT INTO escala (operador_id, semana_id, sexta, sabado, domingo, segunda) VALUES (?, ?, ?, ?, ?, ?)", (operador_id, semana_id, sexta, sabado, domingo, segunda))
    conn.commit()
    conn.close()

def obter_semana(deslocamento=0):
    hoje = datetime.now()
    dias_para_sexta = (hoje.weekday() - 4) % 7
    sexta = hoje - timedelta(days=dias_para_sexta) + timedelta(weeks=deslocamento)
    return {
        "id": sexta.strftime("%Y-%m-%d"),
        "nome": f"{sexta.strftime('%d/%m')} até {(sexta + timedelta(days=3)).strftime('%d/%m')}",
        "Sexta": sexta.strftime("%d/%m"), "Sábado": (sexta + timedelta(days=1)).strftime("%d/%m"),
        "Domingo": (sexta + timedelta(days=2)).strftime("%d/%m"), "Segunda": (sexta + timedelta(days=3)).strftime("%d/%m")
    }

semanas = [obter_semana(i) for i in range(-2, 5)]

# ============================================================
# RENDERIZAÇÃO DO TOP BAR
# ============================================================
col_tit, col_log = st.columns([3, 1], vertical_alignment="center")
with col_tit:
    st.markdown("<div class='titulo-container'><div class='titulo'>Monitoramento Amazon</div><br><div class='subtitulo'>Escala Operacional Interna</div></div>", unsafe_allow_html=True)

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

with col_log:
    if not st.session_state.autenticado:
        with st.popover("👤 Gestor", use_container_width=True):
            with st.form("login_form", clear_on_submit=True):
                usuario = st.text_input("Usuário")
                senha = st.text_input("Senha", type="password")
                if st.form_submit_button("Entrar", use_container_width=True):
                    if usuario.lower().strip() == "admin" and senha == "Amazon123":
                        st.session_state.autenticado = True
                        st.rerun()
                    else:
                        st.error("Incorreto.")
    else:
        with st.popover("⚙️ Painel", use_container_width=True):
            menu_admin = st.selectbox("Ação", ["Adicionar Operador", "Remover Operador"])
            if menu_admin == "Adicionar Operador":
                novo_nome = st.text_input("Nome").strip().upper()
                nova_funcao = st.text_input("Função").strip().upper()
                novo_turno = st.selectbox("Turno", ["T1", "T2", "T3"])
                if st.button("Salvar", use_container_width=True):
                    if novo_nome and nova_funcao:
                        cadastrar_operador(novo_nome, nova_funcao, novo_turno)
                        st.rerun()
            elif menu_admin == "Remover Operador":
                operadores_lista = buscar_operadores()
                opcoes = {f"{x[1]} [{x[3]}]": x[0] for x in operadores_lista}
                sel = st.selectbox("Selecione", list(opcoes.keys()))
                if st.button("Remover", use_container_width=True):
                    remover_operador(opcoes[sel])
                    st.rerun()
            if st.button("🚪 Sair", use_container_width=True):
                st.session_state.autenticado = False
                st.rerun()

# ============================================================
# FILTROS E MÉTRICAS
# ============================================================
semana_labels = [x["nome"] for x in semanas]
col_filtro = st.columns([1, 2])
with col_filtro[0]:
    semana_escolhida = st.selectbox("📅 Período", semana_labels, index=2, label_visibility="collapsed")
semana = semanas[semana_labels.index(semana_escolhida)]
semana_id = semana["id"]

operadores = buscar_operadores()
total = len(operadores)
t1 = len([x for x in operadores if x[3] == "T1"])
t2 = len([x for x in operadores if x[3] == "T2"])
t3 = len([x for x in operadores if x[3] == "T3"])

st.markdown(f"""
<div class='metric-grid'>
    <div class='metric-card total'><div class='metric-numero'>{total}</div><div class='metric-label'>OPERADORES</div></div>
    <div class='metric-card'><div class='metric-numero'>{t1}</div><div class='metric-label'>T1 (07h-15h)</div></div>
    <div class='metric-card'><div class='metric-numero'>{t2}</div><div class='metric-label'>T2 (15h-23h)</div></div>
    <div class='metric-card'><div class='metric-numero'>{t3}</div><div class='metric-label'>T3 (23h-07h)</div></div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# ESTRUTURA VISUAL DAS ABAS
# ============================================================
DIAS = [("Sexta", "sexta"), ("Sábado", "sabado"), ("Domingo", "domingo"), ("Segunda", "segunda")]

aba_t1, aba_t2, aba_t3 = st.tabs(["🌅 Turno 1", "🌆 Turno 2", "🌌 Turno 3"])
abas_mapeamento = {"T1": aba_t1, "T2": aba_t2, "T3": aba_t3}

# Checkbox discreto para alternar a visualização se necessário
is_mobile = st.checkbox("📱 Otimizar visualização para Celular / Tela Pequena", value=False)

for turno in ["T1", "T2", "T3"]:
    with abas_mapeamento[turno]:
        operadores_turno = [x for x in operadores if x[3] == turno]
        
        if not operadores_turno:
            st.info("Nenhum operador alocado.")
            continue

        st.markdown(f"<div class='turno-header'><div class='turno-titulo'>🕒 {NOMES_TURNOS[turno]}</div><div class='turno-horario'>{HORARIOS[turno]}</div></div>", unsafe_allow_html=True)
        
        if not is_mobile:
            # --- MODO DESKTOP (TABELA COMPACTADA) ---
            headers = st.columns([1.8, 1.2, 1, 1, 1, 1])
            headers[0].markdown("<div class='header-col'>Operador</div>", unsafe_allow_html=True)
            headers[1].markdown("<div class='header-col'>Função</div>", unsafe_allow_html=True)
            for idx, (dia, _) in enumerate(DIAS, 2):
                headers[idx].markdown(f"<div class='header-col' style='text-align:center;'>{dia} ({semana[dia]})</div>", unsafe_allow_html=True)
            
            for op in operadores_turno:
                op_id, nome, funcao = op[0], op[1], op[2]
                status = buscar_status(op_id, semana_id) or (HORARIOS[turno],)*4
                if not buscar_status(op_id, semana_id):
                    salvar_status(op_id, semana_id, *status)
                
                linha = st.columns([1.8, 1.2, 1, 1, 1, 1], vertical_alignment="center")
                linha[0].markdown(f"<div class='nome-operador'>{nome}</div>", unsafe_allow_html=True)
                linha[1].markdown(f"<div class='funcao-operador'>{funcao}</div>", unsafe_allow_html=True)
                
                status_lista = list(status)
                for idx, (dia, _) in enumerate(DIAS, 2):
                    valor = status_lista[idx - 2]
                    if valor != "FOLGA":
                        linha[idx].markdown(f"<div class='card-status status-trabalho'>TRABALHO<span class='sub-status'>{HORARIOS[turno]}</span></div>", unsafe_allow_html=True)
                    else:
                        linha[idx].markdown("<div class='card-status status-folga'>FOLGA<span class='sub-status'>Descanso</span></div>", unsafe_allow_html=True)
                    
                    if st.session_state.autenticado:
                        novo_valor = HORARIOS[turno] if valor == "FOLGA" else "FOLGA"
                        if linha[idx].button("Alternar", key=f"d_{op_id}_{semana_id}_{dia}_{turno}"):
                            status_lista[idx - 2] = novo_valor
                            salvar_status(op_id, semana_id, *status_lista)
                            st.rerun()
        else:
            # --- MODO MOBILE (LISTA DE CARDS ENXUTOS) ---
            for op in operadores_turno:
                op_id, nome, funcao = op[0], op[1], op[2]
                status = buscar_status(op_id, semana_id) or (HORARIOS[turno],)*4
                status_lista = list(status)
                
                st.markdown(f"""
                <div class='mobile-operator-card'>
                    <div style='border-bottom: 2px solid #FF9900; padding-bottom:4px; margin-bottom:8px;'>
                        <span class='nome-operador'>{nome}</span><br>
                        <span class='funcao-operador'>{funcao}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                for idx, (dia, _) in enumerate(DIAS):
                    valor = status_lista[idx]
                    col_dia, col_status, col_acao = st.columns([1.5, 2, 1.5])
                    
                    col_dia.markdown(f"<b style='font-size:12px; color:#232F3E;'>{dia} ({semana[dia]})</b>", unsafe_allow_html=True)
                    
                    if valor != "FOLGA":
                        col_status.markdown(f"<div class='card-status status-trabalho' style='min-height:28px; padding:2px;'>TRABALHO ({HORARIOS[turno]})</div>", unsafe_allow_html=True)
                    else:
                        col_status.markdown("<div class='card-status status-folga' style='min-height:28px; padding:2px;'>FOLGA</div>", unsafe_allow_html=True)
                    
                    if st.session_state.autenticado:
                        novo_valor = HORARIOS[turno] if valor == "FOLGA" else "FOLGA"
                        if col_acao.button("Mudar ↔", key=f"m_{op_id}_{semana_id}_{dia}_{turno}", use_container_width=True):
                            status_lista[idx] = novo_valor
                            salvar_status(op_id, semana_id, *status_lista)
                            st.rerun()
                st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)

st.divider()
st.caption("Escala Amazon • Dashboard Otimizado Independente")
