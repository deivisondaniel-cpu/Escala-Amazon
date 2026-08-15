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
# CSS APURADO: AZUL VIVO, CAIXAS INDEPENDENTES SEM ESPAÇO VAZIO
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

/* Remove espaçamentos e margens gigantescas nativas do Streamlit */
div[data-testid="stVerticalBlock"] { gap: 4px !important; padding: 0px !important; }
div[data-testid="stHorizontalBlock"] { gap: 8px !important; padding: 0px !important; margin: 0px 0px 4px 0px !important; align-items: center !important; }

/* Abas Customizadas - Sem Ícones */
button[data-baseweb="tab"] { font-size: 13px !important; font-weight: 700 !important; color: #64748B !important; }
button[aria-selected="true"] { color: #FF5500 !important; border-bottom-color: #FF5500 !important; }

/* Cabeçalho Superior */
.titulo-container { margin-bottom: 8px; }
.titulo { color: #FFFFFF; font-family: 'Segoe UI', sans-serif; font-size: 24px; font-weight: 800; }
.subtitulo { color: #FF5500; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }

/* Header de Turno Limpo apenas com o Relógio */
.turno-header { display: flex; align-items: center; gap: 8px; margin: 8px 0px; padding: 6px 12px; background-color: #141E30; color: white; border-radius: 6px; border: 1px solid #1E293B; }
.turno-titulo { font-size: 13px; font-weight: 700; color: #FFFFFF; }
.turno-horario { background-color: rgba(255,85,0,0.15); color: #FF5500; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; border: 1px solid rgba(255,85,0,0.3); }

/* Colunas de Títulos com o Azul Mais Vivo */
.header-col { font-weight: 700; font-size: 11px; color: #38BDF8 !important; text-transform: uppercase; padding-bottom: 4px; border-bottom: 1px solid #1E293B; margin-bottom: 6px; }

/* Textos com o Azul Mais Vivo solicitado */
.nome-operador { font-size: 12px; font-weight: 700; color: #FFFFFF; display: flex; align-items: center; height: 38px; }
.funcao-operador { font-size: 11px; color: #38BDF8 !important; font-weight: 600; display: flex; align-items: center; height: 38px; }

/* ==========================================
   CAIXAS INDEPENDENTES ESTILO PAINEL GESTOR
   ========================================== */
.stButton > button {
    width: 100% !important;
    height: 38px !important;
    border-radius: 6px !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    padding: 0px !important;
    margin: 0px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    transition: all 0.2s ease;
}

/* CAIXA DE TRABALHO: Borda Laranja, Fundo Escuro, Subtexto em Azul Vivo */
.btn-trabalho > div [data-testid="stMarkdownContainer"] p { color: transparent !important; height: 0px; margin:0; } /* Esconde o texto padrão do streamlit button */
.btn-trabalho button {
    background-color: #141E30 !important;
    border: 1px solid #1E293B !important;
    border-left: 4px solid #FF5500 !important;
    color: #FF5500 !important;
}
.btn-trabalho button::before {
    content: "TRABALHO";
    display: block;
    font-size: 11px;
    font-weight: 700;
}
.btn-trabalho button::after {
    content: "07:00 às 15:00"; /* Dinâmico via CSS injetado ou fixo base */
    display: block;
    font-size: 9px;
    color: #38BDF8 !important; /* Letras azul vivo */
    font-weight: 600;
    margin-top: 1px;
}

/* CAIXA DE FOLGA AMARELA SÓLIDA CONFORME SOLICITADO */
.btn-folga > div [data-testid="stMarkdownContainer"] p { color: transparent !important; height: 0px; margin:0; }
.btn-folga button {
    background-color: #FFCC00 !important;
    border: none !important;
    color: #0B1320 !important;
}
.btn-folga button::before {
    content: "FOLGA";
    display: block;
    font-size: 11px;
    font-weight: 800;
}
.btn-folga button::after {
    content: "INTERNA";
    display: block;
    font-size: 9px;
    color: rgba(11, 19, 32, 0.7) !important;
    font-weight: 600;
    margin-top: 1px;
}

/* Efeito de Hover nas caixas */
.stButton > button:hover {
    filter: brightness(1.2);
    transform: scale(1.01);
}
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
        with st.popover("⚙️ Painel Gestão", use_container_width=True):
            menu_admin = st.selectbox("Ação", ["Adicionar Operador", "Remover Operador"])
            if menu_admin == "Adicionar Operador":
                novo_nome = st.text_input("Nome").strip().upper()
                nova_funcao = st.text_input("Função").strip().upper()
                novo_turno = st.selectbox("Turno", ["T1", "T2", "T3"])
                if st.button("Salvar", use_container_width=True):
                    if novo_nome and nova_funcao:
                        cadastrar_operador(novo_nome, nova_funcao, novo_turno)
                        st.success("Adicionado!")
                        st.rerun()
            elif menu_admin == "Remover Operador":
                ops = buscar_operadores()
                if ops:
                    op_remover = st.selectbox("Selecionar Operador", options=ops, format_func=lambda x: f"{x[1]} ({x[3]})")
                    if st.button("Remover Permanentemente", use_container_width=True):
                        remover_operador(op_remover[0])
                        st.warning("Removido.")
                        st.rerun()
            if st.button("Sair do Modo Gestor", use_container_width=True):
                st.session_state.autenticado = False
                st.rerun()

# Seleção de semana
semana_selecionada = st.selectbox("Selecione o período da Escala", options=semanas, format_func=lambda x: x["nome"], index=2)
todos_operadores = buscar_operadores()

# ============================================================
# EXIBIÇÃO EM ABAS (SEM ÍCONES DE SOL/NOITE - SÓ RELÓGIO)
# ============================================================
abas_turnos = st.tabs([NOMES_TURNOS["T1"], NOMES_TURNOS["T2"], NOMES_TURNOS["T3"]])

for idx_turno, cod_turno in enumerate(["T1", "T2", "T3"]):
    with abas_turnos[idx_turno]:
        st.markdown(f"""
        <div class='turno-header'>
            <span style='font-size:14px;'>🕒</span>
            <div class='turno-titulo'>{NOMES_TURNOS[cod_turno]}</div>
            <div class='turno-horario'>{HORARIOS[cod_turno]}</div>
        </div>
        """, unsafe_allow_html=True)
        
        ops_do_turno = [o for o in todos_operadores if o[3] == cod_turno]
        
        if not ops_do_turno:
            st.info("Nenhum operador alocado.")
            continue
            
        # Títulos das Colunas
        c_op, c_fun, c_sex, c_sab, c_dom, c_seg = st.columns([2.5, 2.2, 1.5, 1.5, 1.5, 1.5])
        c_op.markdown("<div class='header-col'>Operador</div>", unsafe_allow_html=True)
        c_fun.markdown("<div class='header-col'>Função</div>", unsafe_allow_html=True)
        c_sex.markdown(f"<div class='header-col' style='text-align:center;'>Sexta ({semana_selecionada['Sexta']})</div>", unsafe_allow_html=True)
        c_sab.markdown(f"<div class='header-col' style='text-align:center;'>Sábado ({semana_selecionada['Sábado']})</div>", unsafe_allow_html=True)
        c_dom.markdown(f"<div class='header-col' style='text-align:center;'>Domingo ({semana_selecionada['Domingo']})</div>", unsafe_allow_html=True)
        c_seg.markdown(f"<div class='header-col' style='text-align:center;'>Segunda ({semana_selecionada['Segunda']})</div>", unsafe_allow_html=True)
        
        # Renderização das Caixas/Linhas por Operador
        for op in ops_do_turno:
            op_id, nome, funcao, _ = op
            status_banco = buscar_status(op_id, semana_selecionada["id"])
            
            status_dias = list(status_banco) if status_banco else ["TRABALHO", "TRABALHO", "TRABALHO", "TRABALHO"]
                
            row_op, row_fun, row_sex, row_sab, row_dom, row_seg = st.columns([2.5, 2.2, 1.5, 1.5, 1.5, 1.5])
            
            row_op.markdown(f"<div class='nome-operador'>{nome}</div>", unsafe_allow_html=True)
            row_fun.markdown(f"<div class='funcao-operador'>{funcao}</div>", unsafe_allow_html=True)
            
            dias_cols = [row_sex, row_sab, row_dom, row_seg]
            dias_nomes = ["sexta", "sabado", "domingo", "segunda"]
            
            for i in range(4):
                coluna_dia = dias_cols[i]
                status_atual = status_dias[i]
                classe_css = "btn-trabalho" if status_atual == "TRABALHO" else "btn-folga"
                
                with coluna_dia:
                    # Injeta o botão nativo envelopado no container CSS para se transformar no Card customizado
                    st.markdown(f"<div class='{classe_css}'>", unsafe_allow_html=True)
                    
                    # O botão agora exibe o texto e altera o status ao clique direto (Modo Gestor logado)
                    if st.session_state.autenticado:
                        if st.button(f"{status_atual}_{op_id}_{dias_nomes[i]}", key=f"b_{op_id}_{semana_selecionada['id']}_{dias_nomes[i]}"):
                            status_dias[i] = "FOLGA" if status_atual == "TRABALHO" else "TRABALHO"
                            salvar_status(op_id, semana_selecionada["id"], status_dias[0], status_dias[1], status_dias[2], status_dias[3])
                            st.rerun()
                    else:
                        # Se não logado, gera um botão desabilitado que apenas renderiza o card visual idêntico
                        st.button(f"{status_atual}_{op_id}_{dias_nomes[i]}", key=f"b_{op_id}_{semana_selecionada['id']}_{dias_nomes[i]}", disabled=True)
                        
                    st.markdown("</div>", unsafe_allow_html=True)
