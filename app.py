import streamlit as st
import sqlite3
from datetime import datetime, timedelta

# ============================================================
# CONFIGURAÇÃO DA PÁGINA (ESTILO PREMIUM CORPORATIVO)
# ============================================================
st.set_page_config(
    page_title="LosungWeb - Amazon Escala",
    page_icon="🧡",
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
            ("ALAN ARAÚJO", "ANALISTA", "T1"), ("MARGARIDA", "PICKUP", "T1"),
            ("JOSÉ BRUNO PALHANO", "PICKUP", "T1"), ("CRISTOVÃO MIKELLYS", "DEPART", "T1"),
            ("PEDRO LUCAS", "DROPOFF", "T1"), ("FELIPE ALLAN", "DROPOFF", "T1"),
            ("BRUNA BLENDA", "DROPOFF", "T1"), ("CONCEIÇÃO DAIANE", "SEGURANÇA (ONISYS)", "T1"),
            ("MATHEUS LUSTOSA", "SEGURANÇA/ELOG", "T1"), ("MANUELA PINHEIRO", "LÍDER", "T2"),
            ("ISABEL", "LÍDER/SEGURANÇA", "T2"), ("ANDREZA OLIVEIRA", "PICKUP", "T2"),
            ("ROZIANE DA SILVA", "PICKUP", "T2"), ("DAIANE", "SEGURANÇA", "T2"),
            ("EMANUEL ROBERTO", "DEPART", "T2"), ("TAMMYRIS DA SILVA", "DROPOFF", "T2"),
            ("RAPHAEL DO NASCIMENTO", "DROPOFF", "T2"), ("LUDMILLA RODRIGUES", "DROPOFF", "T2"),
            ("MARIA NATHALIA", "SEGURANÇA", "T2"), ("CINAMOR", "ELOG", "T2"),
            ("WESLEY", "LÍDER", "T3"), ("JOÃO", "LÍDER/SEGURANÇA", "T3"),
            ("RILDOMAR", "PICKUP", "T3"), ("LUCIANA", "PICKUP", "T3"),
            ("GLAYLDSON", "SEGURANÇA", "T3"), ("TAYANARA", "DEPART", "T3"),
            ("RUAN", "DROPOFF", "T3"), ("BÁRBARA", "DROPOFF", "T3")
        ]
        cursor.executemany("INSERT INTO operadores (nome, funcao, turno) VALUES (?, ?, ?)", funcionarios_oficiais)
        conn.commit()
    conn.close()

criar_banco_do_zero()

HORARIOS = {"T1": "07:00 às 15:00", "T2": "15:00 às 23:00", "T3": "23:00 às 07:00"}
NOMES_TURNOS = {"T1": "Turno 1", "T2": "Turno 2", "T3": "Turno 3"}

# ============================================================
# CSS APURADO: AZUL VIVO, CAIXAS COMPACTAS E INDEPENDENTES
# ============================================================
st.markdown("""
<style>
header[data-testid="stHeader"], .stAppDeployButton, div[data-testid="stViewerBadge"], footer, #MainMenu, .stDecoration { 
    display: none !important; visibility: hidden !important; width: 0 !important; height: 0 !important; opacity: 0 !important;
}
[data-testid="stSidebar"] { display: none; }

/* Fundo Geral do Sistema */
.stApp { background-color: #0B1320; color: #F1F5F9; }
.stMainBlockContainer { padding: 12px 20px !important; max-width: 100% !important; }

/* Ajuste milimétrico de espaços vazios */
[data-testid="stVerticalBlock"] { gap: 0px !important; }
[data-testid="stHorizontalBlock"] { padding: 0px !important; margin-bottom: 5px !important; align-items: center !important; }

/* Abas Customizadas - Sem Ícones e Cores Ajustadas */
button[data-baseweb="tab"] { font-size: 13px !important; font-weight: 700 !important; color: #64748B !important; }
button[aria-selected="true"] { color: #FF5500 !important; border-bottom-color: #FF5500 !important; }

/* Cabeçalho Superior */
.titulo-container { margin-bottom: 8px; }
.titulo { color: #FFFFFF; font-family: 'Segoe UI', sans-serif; font-size: 24px; font-weight: 800; }
.subtitulo { color: #FF5500; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }

/* Painel de Métricas Reduzido */
.metric-grid { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }
.metric-card { flex: 1; min-width: 110px; background: #141E30; border: 1px solid #1E293B; border-radius: 6px; padding: 6px 10px; text-align: left; }
.metric-card.total { border-left: 4px solid #FF5500; }
.metric-numero { font-size: 18px; font-weight: 800; color: #FFFFFF; line-height: 1.1; }
.metric-label { font-size: 10px; color: #38BDF8; font-weight: 600; margin-top: 1px; }

/* Header de Turno Limpo apenas com o Relógio */
.turno-header { display: flex; align-items: center; gap: 8px; margin: 8px 0; padding: 6px 12px; background-color: #141E30; color: white; border-radius: 6px; border: 1px solid #1E293B; }
.turno-titulo { font-size: 13px; font-weight: 700; color: #FFFFFF; }
.turno-horario { background-color: rgba(255,85,0,0.15); color: #FF5500; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; border: 1px solid rgba(255,85,0,0.3); }

/* Colunas de Títulos */
.header-col { font-weight: 700; font-size: 11px; color: #38BDF8; text-transform: uppercase; padding-bottom: 4px; border-bottom: 1px solid #1E293B; margin-bottom: 6px; }

/* Textos da Tabela com o Azul Mais Vivo */
.nome-operador { font-size: 12px; font-weight: 700; color: #FFFFFF; display: flex; align-items: center; min-height: 42px; }
.funcao-operador { font-size: 11px; color: #38BDF8; font-weight: 600; display: flex; align-items: center; min-height: 42px; }

/* CARDS DE STATUS INDEPENDENTES ESTILO REQUADRO */
.card-status { 
    background-color: #141E30;
    border: 1px solid #1E293B;
    border-radius: 6px; 
    text-align: center; 
    font-size: 11px; 
    font-weight: 700; 
    display: flex; 
    flex-direction: column; 
    justify-content: center; 
    min-height: 42px; 
    box-sizing: border-box; 
    width: 100%;
}

/* Trabalho: Borda Laranja da Amazon */
.status-trabalho { 
    border-left: 4px solid #FF5500 !important;
    color: #FF5500;
}
.status-trabalho .sub-status { color: #38BDF8; }

/* Folga: Preenchimento Amarelo Sólido Conforme Solicitado */
.status-folga { 
    background-color: #FFCC00 !important;
    border: none !important;
    color: #0B1320 !important;
}
.status-folga .sub-status { color: rgba(11, 19, 32, 0.7) !important; }

.sub-status { font-size: 9px; font-weight: 600; margin-top: 1px; }

/* Botão invisível perfeitamente cobrindo a caixa independente */
.stButton > button {
    background-color: transparent !important;
    color: transparent !important;
    border: none !important;
    position: absolute !important;
    top: 0; left: 0; width: 100% !important; height: 42px !important;
    z-index: 10;
    cursor: pointer;
}
.stButton { position: relative !important; margin: 0 !important; padding: 0 !important; height: 42px; }

/* Mobile Otimizado */
.mobile-operator-card { background: #141E30; border: 1px solid #1E293B; border-radius: 6px; padding: 10px; margin-bottom: 6px; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNÇÕES DE BANCO DE DADOS
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
# LAYOUT TOP BAR
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
                        cadastrar_operador(novo_nome, nova_funcao,
