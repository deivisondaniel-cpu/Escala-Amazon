import streamlit as st
import sqlite3
from datetime import datetime, timedelta

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Escala Amazon",
    page_icon="amazon.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# BANCO DE DADOS
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

    # --------------------------------------------------------
    # CARGA INICIAL
    # --------------------------------------------------------

    dados_existentes = cursor.execute(
        "SELECT COUNT(*) FROM operadores WHERE ativo = 1"
    ).fetchone()[0]

    if dados_existentes == 0:

        funcionarios_oficiais = [

            # 🌅 TURNO 1
            ("ALAN ARAÚJO", "ANALISTA", "T1"),
            ("MARGARIDA", "PICKUP", "T1"),
            ("JOSÉ BRUNO PALHANO", "PICKUP", "T1"),
            ("CRISTOVÃO MIKELLYS", "DEPART", "T1"),
            ("PEDRO LUCAS", "DROPOFF", "T1"),
            ("FELIPE ALLAN", "DROPOFF", "T1"),
            ("BRUNA BLENDA", "DROPOFF", "T1"),
            ("CONCEIÇÃO DAIANE", "SEGURANÇA (ONISYS)", "T1"),
            ("MATHEUS LUSTOSA", "SEGURANÇA/ELOG", "T1"),

            # 🌆 TURNO 2
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

            # 🌌 TURNO 3
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
            INSERT INTO operadores (nome, funcao, turno)
            VALUES (?, ?, ?)
        """, funcionarios_oficiais)

        conn.commit()

    conn.close()


criar_banco_do_zero()


# ============================================================
# HORÁRIOS E CONSTANTES
# ============================================================

HORARIOS = {
    "T1": "07:00 às 15:00",
    "T2": "15:00 às 23:00",
    "T3": "23:00 às 07:00"
}

HORARIOS_CURTOS = {
    "T1": "07h — 15h",
    "T2": "15h — 23h",
    "T3": "23h — 07h"
}

NOMES_TURNOS = {
    "T1": "Turno 1",
    "T2": "Turno 2",
    "T3": "Turno 3"
}

ICONS_TURNOS = {
    "T1": "🌅",
    "T2": "🌆",
    "T3": "🌌"
}

DIAS = [
    ("Sexta", "sexta"),
    ("Sábado", "sabado"),
    ("Domingo", "domingo"),
    ("Segunda", "segunda")
]


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

/* ============================================================
   RESET / FUNDO
   ============================================================ */

header[data-testid="stHeader"],
.stAppDeployButton,
div[data-testid="stViewerBadge"],
footer,
#MainMenu,
.stDecoration {
    display: none !important;
}

[data-testid="stSidebar"] {
    display: none !important;
}

.stApp {
    background: #F4F6F8 !important;
}

[data-testid="stAppViewContainer"] {
    background: #F4F6F8 !important;
}

.stMainBlockContainer {
    max-width: 1480px !important;
    padding-top: 16px !important;
    padding-bottom: 22px !important;
}


/* ============================================================
   CABEÇALHO
   ============================================================ */

.top-title {
    color: #232F3E;
    font-family: "Segoe UI", sans-serif;
    font-size: 28px;
    font-weight: 850;
    line-height: 1.05;
    letter-spacing: -0.7px;
    margin: 0;
}

.top-subtitle {
    color: #667085;
    font-size: 11px;
    font-weight: 650;
    margin-top: 4px;
}

.brand-line {
    display: flex;
    align-items: center;
    gap: 9px;
}

.brand-dot {
    width: 9px;
    height: 9px;
    background: #FF9900;
    border-radius: 50%;
    box-shadow: 0 0 0 4px rgba(255,153,0,.12);
}


/* ============================================================
   POPOVER GESTOR
   ============================================================ */

div[data-testid="stPopover"] > button {
    background: #FFFFFF !important;
    color: #232F3E !important;
    border: 1px solid #D7DEE7 !important;
    border-radius: 8px !important;
    min-height: 35px !important;
    font-size: 11px !important;
    font-weight: 750 !important;
    box-shadow: none !important;
}

div[data-testid="stPopover"] > button:hover {
    background: #FFF8ED !important;
    border-color: #FF9900 !important;
}


/* ============================================================
   ÁREA DO PERÍODO
   ============================================================ */

.period-label {
    color: #667085;
    font-size: 9px;
    font-weight: 850;
    text-transform: uppercase;
    letter-spacing: .5px;
    margin-bottom: 3px;
}

div[data-baseweb="select"] > div {
    min-height: 36px !important;
    height: 36px !important;
    border: 1px solid #D8E0E7 !important;
    border-radius: 8px !important;
    background: #FFFFFF !important;
    box-shadow: none !important;
}

div[data-baseweb="select"] span {
    font-size: 11px !important;
    font-weight: 650 !important;
}


/* ============================================================
   MÉTRICAS
   ============================================================ */

.metric-card {
    background: #FFFFFF;
    border: 1px solid #DDE4EA;
    border-radius: 9px;
    padding: 7px 10px;
    min-height: 54px;
    box-shadow: 0 1px 4px rgba(35,47,62,.035);
    text-align: center;
}

.metric-numero {
    color: #232F3E;
    font-size: 20px;
    line-height: 21px;
    font-weight: 850;
}

.metric-label {
    color: #667085;
    font-size: 8px;
    line-height: 11px;
    font-weight: 850;
    text-transform: uppercase;
    letter-spacing: .25px;
}

.metric-card:first-child {
    border-top: 3px solid #FF9900;
}

.metric-card:nth-child(2) {
    border-top: 3px solid #FFB84D;
}

.metric-card:nth-child(3) {
    border-top: 3px solid #8B5CF6;
}

.metric-card:nth-child(4) {
    border-top: 3px solid #64748B;
}


/* ============================================================
   TABS
   ============================================================ */

div[data-testid="stTabs"] {
    margin-top: 4px;
}

div[data-testid="stTabs"] > div:first-child {
    border-bottom: 1px solid #DDE4EA;
}

button[data-baseweb="tab"] {
    color: #7A8795 !important;
    font-size: 11px !important;
    font-weight: 750 !important;
    padding: 7px 12px !important;
    min-height: 34px !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #232F3E !important;
}

div[data-baseweb="tab-highlight"] {
    background: #FF9900 !important;
    height: 3px !important;
}


/* ============================================================
   CABEÇALHO DO TURNO
   ============================================================ */

.turno-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    margin-top: 7px;
    margin-bottom: 7px;

    padding: 8px 12px;

    background: #FFFFFF;

    border: 1px solid #DDE4EA;
    border-left: 4px solid #FF9900;

    border-radius: 8px;

    box-shadow: 0 1px 4px rgba(35,47,62,.035);
}

.turno-left {
    display: flex;
    align-items: center;
    gap: 8px;
}

.turno-icon {
    font-size: 16px;
}

.turno-titulo {
    color: #232F3E;
    font-size: 15px;
    font-weight: 850;
}

.turno-contador {
    color: #8A97A6;
    font-size: 9px;
    font-weight: 650;
    margin-left: 6px;
}

.turno-horario {
    background: #F0F6FB;
    color: #146EB4;
    border: 1px solid #D4E6F5;
    padding: 3px 8px;
    border-radius: 999px;
    font-size: 9px;
    font-weight: 850;
}


/* ============================================================
   CABEÇALHO COLUNAS
   ============================================================ */

.header-col {
    text-align: center;
    font-weight: 850;
    font-size: 8px;
    line-height: 10px;
    color: #667085;
    margin-bottom: 3px;
}

.header-esquerda {
    text-align: left;
}


/* ============================================================
   OPERADOR
   ============================================================ */

.nome-operador {
    padding-top: 4px;
    font-size: 10px;
    line-height: 13px;
    color: #232F3E;

    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.funcao-operador {
    padding-top: 3px;
    font-size: 8px;
    line-height: 10px;
    color: #7A8795;
    font-weight: 650;

    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}


/* ============================================================
   LINHA VISUAL
   ============================================================ */

.separador {
    border: 0;
    border-top: 1px solid #DDE4EA;
    margin-top: 0;
    margin-bottom: 4px;
}


/* ============================================================
   TRABALHO
   ============================================================ */

.card-trabalho {
    background: #263445;
    color: #FFFFFF;

    padding: 5px 3px;

    border-radius: 6px;
    border-left: 3px solid #FF9900;

    text-align: center;

    font-size: 8px;
    font-weight: 850;

    min-height: 31px;

    display: flex;
    flex-direction: column;
    justify-content: center;

    margin-bottom: 2px;
}

.sub-info {
    color: #FFB84D;
    font-size: 7px;
    line-height: 9px;
    margin-top: 1px;
    font-weight: 700;
}


/* ============================================================
   FOLGA
   ============================================================ */

.card-folga {
    background: #EEF5FA;
    color: #42627D;

    padding: 5px 3px;

    border-radius: 6px;
    border-left: 3px solid #3B82C4;

    text-align: center;

    font-size: 8px;
    font-weight: 850;

    min-height: 31px;

    display: flex;
    flex-direction: column;
    justify-content: center;

    margin-bottom: 2px;
}

.sub-info-folga {
    color: #8192A2;
    font-size: 7px;
    line-height: 9px;
    margin-top: 1px;
    font-weight: 650;
}


/* ============================================================
   BOTÕES
   ============================================================ */

.stButton > button {
    min-height: 24px !important;
    height: 24px !important;

    padding: 0 4px !important;

    border-radius: 6px !important;

    border: 1px solid #D7DEE7 !important;

    background: #FFFFFF !important;
    color: #526273 !important;

    font-size: 8px !important;
    font-weight: 750 !important;

    box-shadow: none !important;
}

.stButton > button:hover {
    background: #FFF8ED !important;
    color: #232F3E !important;
    border-color: #FF9900 !important;
}


/* ============================================================
   FORMULÁRIOS / INPUTS
   ============================================================ */

[data-testid="stForm"] {
    background: #FFFFFF !important;
    border: 0 !important;
    padding: 0 !important;
}

div[data-testid="stTextInput"] input {
    border-radius: 7px !important;
}

.stCaption {
    color: #7A8795 !important;
}


/* ============================================================
   DIVIDER
   ============================================================ */

hr {
    border-color: #DDE4EA !important;
}


/* ============================================================
   RODAPÉ
   ============================================================ */

.footer-app {
    color: #98A2B3;
    text-align: center;
    font-size: 8px;
    font-weight: 600;
    margin-top: 15px;
}


/* ============================================================
   TABLET
   ============================================================ */

@media (max-width: 1000px) {

    .stMainBlockContainer {
        padding-left: 12px !important;
        padding-right: 12px !important;
    }

    .top-title {
        font-size: 24px;
    }

    .metric-card {
        padding: 6px 5px;
    }

    .metric-numero {
        font-size: 18px;
    }

    .metric-label {
        font-size: 7px;
    }

    .header-col {
        font-size: 7px;
    }

    .nome-operador {
        font-size: 9px;
    }

    .funcao-operador {
        font-size: 7px;
    }

    .card-trabalho,
    .card-folga {
        font-size: 7px;
        min-height: 29px;
    }

    .sub-info,
    .sub-info-folga {
        font-size: 6px;
    }

    .stButton > button {
        font-size: 7px !important;
    }
}


/* ============================================================
   CELULAR
   ============================================================ */

@media (max-width: 700px) {

    .stMainBlockContainer {
        padding-left: 7px !important;
        padding-right: 7px !important;
        padding-top: 10px !important;
    }

    .top-title {
        font-size: 20px;
        letter-spacing: -.4px;
    }

    .top-subtitle {
        font-size: 9px;
    }

    .period-label {
        font-size: 8px;
    }

    div[data-baseweb="select"] > div {
        min-height: 34px !important;
        height: 34px !important;
    }

    div[data-baseweb="select"] span {
        font-size: 10px !important;
    }

    .metric-card {
        min-height: 44px;
        padding: 5px 2px;
    }

    .metric-numero {
        font-size: 16px;
        line-height: 17px;
    }

    .metric-label {
        font-size: 6px;
        line-height: 8px;
    }

    button[data-baseweb="tab"] {
        font-size: 9px !important;
        padding: 6px 7px !important;
    }

    .turno-header {
        padding: 7px 8px;
    }

    .turno-titulo {
        font-size: 13px;
    }

    .turno-contador {
        display: none;
    }

    .turno-horario {
        font-size: 8px;
        padding: 3px 6px;
    }

    .header-col {
        font-size: 6px;
        line-height: 8px;
    }

    .nome-operador {
        font-size: 8px;
        line-height: 10px;
        padding-top: 3px;
    }

    .funcao-operador {
        font-size: 6px;
        line-height: 8px;
        padding-top: 2px;
    }

    .card-trabalho,
    .card-folga {
        min-height: 27px;
        font-size: 6px;
        border-left-width: 2px;
        padding: 4px 1px;
    }

    .sub-info,
    .sub-info-folga {
        display: none;
    }

    .stButton > button {
        min-height: 21px !important;
        height: 21px !important;
        font-size: 6px !important;
        padding: 0 2px !important;
    }

    .footer-app {
        font-size: 7px;
    }
}


/* ============================================================
   CELULAR PEQUENO
   ============================================================ */

@media (max-width: 480px) {

    .top-title {
        font-size: 18px;
    }

    .top-subtitle {
        font-size: 8px;
    }

    .metric-card {
        min-height: 40px;
    }

    .metric-numero {
        font-size: 14px;
    }

    .metric-label {
        font-size: 5.5px;
    }

    button[data-baseweb="tab"] {
        font-size: 8px !important;
        padding-left: 4px !important;
        padding-right: 4px !important;
    }

    .turno-titulo {
        font-size: 12px;
    }

    .turno-horario {
        font-size: 7px;
    }

    .header-col {
        font-size: 5.5px;
    }

    .nome-operador {
        font-size: 7px;
    }

    .funcao-operador {
        font-size: 5.5px;
    }

    .card-trabalho,
    .card-folga {
        min-height: 25px;
        font-size: 5.5px;
    }

    .stButton > button {
        font-size: 5.5px !important;
    }
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSÃO DE AUTENTICAÇÃO
# ============================================================

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False


# ============================================================
# OPERAÇÕES DE CONSULTA AO BANCO
# ============================================================

def buscar_operadores():

    conn = conectar()

    dados = conn.execute("""
        SELECT id, nome, funcao, turno
        FROM operadores
        WHERE ativo = 1
        ORDER BY
            CASE turno
                WHEN 'T1' THEN 1
                WHEN 'T2' THEN 2
                WHEN 'T3' THEN 3
            END,
            nome
    """).fetchall()

    conn.close()

    return dados


def cadastrar_operador(nome, funcao, turno):

    conn = conectar()

    conn.execute("""
        INSERT INTO operadores
        (nome, funcao, turno)
        VALUES (?, ?, ?)
    """, (
        nome,
        funcao,
        turno
    ))

    conn.commit()
    conn.close()


def remover_operador(operador_id):

    conn = conectar()

    conn.execute("""
        UPDATE operadores
        SET ativo = 0
        WHERE id = ?
    """, (
        operador_id,
    ))

    conn.commit()
    conn.close()


def buscar_status(operador_id, semana_id):

    conn = conectar()

    resultado = conn.execute("""
        SELECT
            sexta,
            sabado,
            domingo,
            segunda
        FROM escala
        WHERE operador_id = ?
        AND semana_id = ?
    """, (
        operador_id,
        semana_id
    )).fetchone()

    conn.close()

    return resultado


def salvar_status(
    operador_id,
    semana_id,
    sexta,
    sabado,
    domingo,
    segunda
):

    conn = conectar()

    existente = conn.execute("""
        SELECT id
        FROM escala
        WHERE operador_id = ?
        AND semana_id = ?
    """, (
        operador_id,
        semana_id
    )).fetchone()

    if existente:

        conn.execute("""
            UPDATE escala
            SET
                sexta = ?,
                sabado = ?,
                domingo = ?,
                segunda = ?
            WHERE operador_id = ?
            AND semana_id = ?
        """, (
            sexta,
            sabado,
            domingo,
            segunda,
            operador_id,
            semana_id
        ))

    else:

        conn.execute("""
            INSERT INTO escala
            (
                operador_id,
                semana_id,
                sexta,
                sabado,
                domingo,
                segunda
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            operador_id,
            semana_id,
            sexta,
            sabado,
            domingo,
            segunda
        ))

    conn.commit()
    conn.close()


# ============================================================
# MONITORAMENTO DAS DATAS
# ============================================================

def obter_semana(deslocamento=0):

    hoje = datetime.now()

    dias_para_sexta = (hoje.weekday() - 4) % 7

    sexta = (
        hoje
        - timedelta(days=dias_para_sexta)
        + timedelta(weeks=deslocamento)
    )

    sabado = sexta + timedelta(days=1)
    domingo = sexta + timedelta(days=2)
    segunda = sexta + timedelta(days=3)

    return {
        "id": sexta.strftime("%Y-%m-%d"),
        "nome": (
            f"{sexta.strftime('%d/%m')} "
            f"até "
            f"{segunda.strftime('%d/%m')}"
        ),
        "Sexta": sexta.strftime("%d/%m"),
        "Sábado": sabado.strftime("%d/%m"),
        "Domingo": domingo.strftime("%d/%m"),
        "Segunda": segunda.strftime("%d/%m")
    }


semanas = [
    obter_semana(i)
    for i in range(-2, 5)
]


# ============================================================
# CABEÇALHO
# ============================================================

col_titulo, col_gestor = st.columns(
    [5.5, 1],
    vertical_alignment="center"
)


with col_titulo:

    st.markdown("""
        <div class="brand-line">
            <div class="brand-dot"></div>
            <div>
                <div class="top-title">
                    Amazon
                </div>
                <div class="top-subtitle">
                    Escala de monitoramento
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


with col_gestor:

    if not st.session_state.autenticado:

        with st.popover(
            "👤 Gestor",
            use_container_width=True
        ):

            st.markdown(
                "**Área do Gestor**"
            )

            st.caption(
                "Acesse para gerenciar operadores "
                "e alterar a escala."
            )

            with st.form(
                "login_form",
                clear_on_submit=True
            ):

                usuario = st.text_input(
                    "Usuário"
                )

                senha = st.text_input(
                    "Senha",
                    type="password"
                )

                entrar = st.form_submit_button(
                    "Entrar",
                    use_container_width=True
                )

                if entrar:

                    if (
                        usuario.lower().strip() == "admin"
                        and senha == "Amazon123"
                    ):

                        st.session_state.autenticado = True
                        st.rerun()

                    else:

                        st.error(
                            "Dados incorretos."
                        )

    else:

        with st.popover(
            "⚙️ Gestão",
            use_container_width=True
        ):

            st.success(
                "Modo Gestor ativo"
            )

            st.divider()

            menu_admin = st.selectbox(
                "Ação",
                [
                    "Adicionar Operador",
                    "Remover Operador"
                ]
            )

            # ------------------------------------------------
            # ADICIONAR
            # ------------------------------------------------

            if menu_admin == "Adicionar Operador":

                novo_nome = st.text_input(
                    "Nome"
                ).strip().upper()

                nova_funcao = st.text_input(
                    "Função"
                ).strip().upper()

                novo_turno = st.selectbox(
                    "Turno",
                    ["T1", "T2", "T3"],
                    format_func=lambda x:
                        f"{NOMES_TURNOS[x]} — "
                        f"{HORARIOS[x]}"
                )

                if st.button(
                    "Confirmar Cadastro",
                    use_container_width=True
                ):

                    if novo_nome and nova_funcao:

                        cadastrar_operador(
                            novo_nome,
                            nova_funcao,
                            novo_turno
                        )

                        st.success(
                            "Operador cadastrado!"
                        )

                        st.rerun()

                    else:

                        st.warning(
                            "Preencha todos os campos."
                        )

            # ------------------------------------------------
            # REMOVER
            # ------------------------------------------------

            else:

                operadores_lista = buscar_operadores()

                if operadores_lista:

                    opcoes_remocao = {
                        f"{x[1]} — {x[2]}": x[0]
                        for x in operadores_lista
                    }

                    selecionado = st.selectbox(
                        "Selecione o operador",
                        list(opcoes_remocao.keys())
                    )

                    if st.button(
                        "Confirmar Remoção",
                        use_container_width=True
                    ):

                        remover_operador(
                            opcoes_remocao[selecionado]
                        )

                        st.success(
                            "Operador removido!"
                        )

                        st.rerun()

                else:

                    st.info(
                        "Nenhum operador cadastrado."
                    )

            st.divider()

            if st.button(
                "🚪 Sair",
                use_container_width=True
            ):

                st.session_state.autenticado = False
                st.rerun()


# ============================================================
# PERÍODO DA ESCALA
# ============================================================

st.markdown(
    "<div class='period-label'>📅 Período da escala</div>",
    unsafe_allow_html=True
)

semana_labels = [
    x["nome"]
    for x in semanas
]

semana_escolhida = st.selectbox(
    "Período",
    semana_labels,
    index=2,
    label_visibility="collapsed"
)

semana = semanas[
    semana_labels.index(semana_escolhida)
]

semana_id = semana["id"]


# ============================================================
# OPERADORES
# ============================================================

operadores = buscar_operadores()


# ============================================================
# MÉTRICAS
# ============================================================

total = len(operadores)

t1 = len([
    x for x in operadores
    if x[3] == "T1"
])

t2 = len([
    x for x in operadores
    if x[3] == "T2"
])

t3 = len([
    x for x in operadores
    if x[3] == "T3"
])


st.write("")


m1, m2, m3, m4 = st.columns(
    [1.3, 1, 1, 1],
    gap="small"
)


with m1:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-numero">{total}</div>
            <div class="metric-label">
                OPERADORES ATIVOS
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with m2:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-numero">{t1}</div>
            <div class="metric-label">
                T1 · 07h — 15h
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with m3:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-numero">{t2}</div>
            <div class="metric-label">
                T2 · 15h — 23h
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with m4:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-numero">{t3}</div>
            <div class="metric-label">
                T3 · 23h — 07h
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.write("")


# ============================================================
# ABAS DOS TURNOS
# ============================================================

aba_t1, aba_t2, aba_t3 = st.tabs([
    f"🌅 Turno 1 · {t1}",
    f"🌆 Turno 2 · {t2}",
    f"🌌 Turno 3 · {t3}"
])


abas_mapeamento = {
    "T1": aba_t1,
    "T2": aba_t2,
    "T3": aba_t3
}


# ============================================================
# CONSTRUÇÃO DOS TURNOS
# ============================================================

for turno in ["T1", "T2", "T3"]:

    with abas_mapeamento[turno]:

        operadores_turno = [
            x for x in operadores
            if x[3] == turno
        ]

        # ----------------------------------------------------
        # SEM OPERADORES
        # ----------------------------------------------------

        if not operadores_turno:

            st.info(
                f"Nenhum operador alocado no "
                f"{NOMES_TURNOS[turno]} para este período."
            )

            continue


        # ----------------------------------------------------
        # HEADER DO TURNO
        # ----------------------------------------------------

        st.markdown(
            f"""
            <div class="turno-header">

                <div class="turno-left">

                    <span class="turno-icon">
                        {ICONS_TURNOS[turno]}
                    </span>

                    <span class="turno-titulo">
                        {NOMES_TURNOS[turno]}
                    </span>

                    <span class="turno-contador">
                        {len(operadores_turno)} operadores
                    </span>

                </div>

                <div class="turno-horario">
                    {HORARIOS_CURTOS[turno]}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # CABEÇALHO DAS COLUNAS
        # ----------------------------------------------------

        headers = st.columns(
            [2.8, 2.1, 1.65, 1.65, 1.65, 1.65],
            gap="small"
        )


        headers[0].markdown(
            "<div class='header-col header-esquerda'>"
            "OPERADOR"
            "</div>",
            unsafe_allow_html=True
        )


        headers[1].markdown(
            "<div class='header-col header-esquerda'>"
            "FUNÇÃO"
            "</div>",
            unsafe_allow_html=True
        )


        for i, (dia, _) in enumerate(DIAS, 2):

            headers[i].markdown(
                f"""
                <div class="header-col">
                    {dia.upper()}<br>
                    <span style="
                        color:#98A2B3;
                        font-weight:650;
                    ">
                        {semana[dia]}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )


        st.markdown(
            "<div class='separador'></div>",
            unsafe_allow_html=True
        )


        # ====================================================
        # OPERADORES
        # ====================================================

        for operador in operadores_turno:

            operador_id = operador[0]
            nome = operador[1]
            funcao = operador[2]

            status = buscar_status(
                operador_id,
                semana_id
            )


            # ------------------------------------------------
            # CRIA STATUS AUTOMÁTICO
            # ------------------------------------------------

            if status is None:

                horario = HORARIOS[turno]

                status = (
                    horario,
                    horario,
                    horario,
                    horario
                )

                salvar_status(
                    operador_id,
                    semana_id,
                    *status
                )


            status_lista = list(status)


            # ------------------------------------------------
            # LINHA
            # ------------------------------------------------

            linha = st.columns(
                [2.8, 2.1, 1.65, 1.65, 1.65, 1.65],
                gap="small"
            )


            # ------------------------------------------------
            # NOME
            # ------------------------------------------------

            linha[0].markdown(
                f"""
                <div class="nome-operador">
                    <b>{nome}</b>
                </div>
                """,
                unsafe_allow_html=True
            )


            # ------------------------------------------------
            # FUNÇÃO
            # ------------------------------------------------

            linha[1].markdown(
                f"""
                <div class="funcao-operador">
                    {funcao}
                </div>
                """,
                unsafe_allow_html=True
            )


            # ------------------------------------------------
            # DIAS
            # ------------------------------------------------

            for i, (dia, _) in enumerate(DIAS, 2):

                valor = status_lista[i - 2]


                # ============================================
                # TRABALHO
                # ============================================

                if valor != "FOLGA":

                    linha[i].markdown(
                        f"""
                        <div class="card-trabalho">
                            TRABALHO
                            <div class="sub-info">
                                {HORARIOS_CURTOS[turno]}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                # ============================================
                # FOLGA
                # ============================================

                else:

                    linha[i].markdown(
                        """
                        <div class="card-folga">
                            FOLGA
                            <div class="sub-info-folga">
                                Descanso
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                # ============================================
                # BOTÃO DO GESTOR
                # ============================================

                if st.session_state.autenticado:

                    novo_valor = (
                        HORARIOS[turno]
                        if valor == "FOLGA"
                        else "FOLGA"
                    )

                    texto_botao = (
                        "↻ Folga"
                        if valor != "FOLGA"
                        else "↻ Trab."
                    )


                    if linha[i].button(
                        texto_botao,
                        key=(
                            f"{operador_id}_"
                            f"{semana_id}_"
                            f"{dia}_"
                            f"{turno}"
                        ),
                        use_container_width=True
                    ):

                        status_lista[i - 2] = novo_valor

                        salvar_status(
                            operador_id,
                            semana_id,
                            *status_lista
                        )

                        st.rerun()


        # ----------------------------------------------------
        # PEQUENO ESPAÇO ENTRE TURNOS
        # ----------------------------------------------------

        st.write("")


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.markdown(
    """
    <div class="footer-app">
        Escala Amazon · Sistema independente de gestão de escala
    </div>
    """,
    unsafe_allow_html=True
)
