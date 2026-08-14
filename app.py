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
    return sqlite3.connect(
        BANCO,
        check_same_thread=False
    )


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
# CORES AMAZON
# ============================================================

AMAZON_DARK = "#232F3E"
AMAZON_BLUE = "#146EB4"
AMAZON_ORANGE = "#FF9900"

BG_DARK = "#111820"
BG_CARD = "#1B2633"
BG_CARD_2 = "#202D3A"

TEXT_WHITE = "#FFFFFF"
TEXT_LIGHT = "#CBD5E1"
TEXT_MUTED = "#8FA1B3"

BORDER = "#344454"


# ============================================================
# CSS
# ============================================================

st.markdown(
    f"""
<style>

/* ============================================================
   RESET
   ============================================================ */

#MainMenu {{
    visibility: hidden;
}}

footer {{
    visibility: hidden;
}}

.stDecoration {{
    display: none !important;
}}


/* ============================================================
   FUNDO PRINCIPAL
   ============================================================ */

[data-testid="stAppViewContainer"] {{
    background: {BG_DARK};
}}

[data-testid="stHeader"] {{
    background: {BG_DARK};
}}

.stApp {{
    background: {BG_DARK};
}}


/* ============================================================
   CONTAINER
   ============================================================ */

.stMainBlockContainer {{
    padding-top: 20px !important;
    padding-bottom: 35px !important;
    max-width: 1500px;
}}


/* ============================================================
   TÍTULO
   ============================================================ */

.titulo {{
    text-align: center;
    color: {TEXT_WHITE};

    font-family: 'Segoe UI', sans-serif;

    font-size: 31px;
    font-weight: 800;

    margin-top: 15px;
    margin-bottom: 3px;
}}

.subtitulo {{
    text-align: center;

    color: {AMAZON_ORANGE};

    font-size: 13px;
    font-weight: 700;

    letter-spacing: 0.4px;

    margin-bottom: 22px;
}}


/* ============================================================
   SELEÇÃO DA SEMANA
   ============================================================ */

[data-testid="stSelectbox"] label {{
    color: {TEXT_LIGHT} !important;
    font-weight: 700 !important;
}}

div[data-baseweb="select"] > div {{
    background: {BG_CARD} !important;

    border: 1px solid {BORDER} !important;

    border-radius: 8px !important;

    color: {TEXT_WHITE} !important;
}}

div[data-baseweb="select"] span {{
    color: {TEXT_WHITE} !important;
}}

div[data-baseweb="select"] > div:focus-within {{
    border-color: {AMAZON_BLUE} !important;

    box-shadow: 0 0 0 1px {AMAZON_BLUE} !important;
}}


/* ============================================================
   SELETOR DE TURNO
   ============================================================ */

.seletor-titulo {{
    color: {TEXT_LIGHT};

    font-size: 12px;

    font-weight: 800;

    letter-spacing: 0.5px;

    margin-top: 18px;

    margin-bottom: 7px;
}}


/* ============================================================
   RADIO DOS TURNOS
   ============================================================ */

div[role="radiogroup"] {{
    display: flex;

    gap: 8px;

    background: transparent;

    padding: 0;

    margin-bottom: 15px;
}}

div[role="radiogroup"] label {{
    background: {BG_CARD};

    border: 1px solid {BORDER};

    border-radius: 8px;

    padding: 8px 18px;

    min-width: 120px;

    justify-content: center;

    transition: all 0.15s ease;
}}

div[role="radiogroup"] label:hover {{
    border-color: {AMAZON_BLUE};

    background: {BG_CARD_2};
}}

div[role="radiogroup"] label[data-checked="true"] {{
    background: {AMAZON_DARK};

    border: 1px solid {AMAZON_ORANGE};

    box-shadow: 0 0 0 1px {AMAZON_ORANGE};
}}

div[role="radiogroup"] label p {{
    color: {TEXT_WHITE} !important;

    font-weight: 800;

    font-size: 12px;
}}


/* ============================================================
   MÉTRICAS
   ============================================================ */

.metric-card {{
    background: {BG_CARD};

    border: 1px solid {BORDER};

    border-top: 3px solid {AMAZON_BLUE};

    border-radius: 10px;

    padding: 13px 10px;

    text-align: center;

    box-shadow: 0 3px 10px rgba(0,0,0,0.18);
}}

.metric-card-principal {{
    border-top-color: {AMAZON_ORANGE};
}}

.metric-numero {{
    font-size: 23px;

    font-weight: 800;

    color: {TEXT_WHITE};
}}

.metric-label {{
    font-size: 10px;

    color: {TEXT_MUTED};

    font-weight: 800;

    letter-spacing: 0.3px;
}}


/* ============================================================
   CABEÇALHO DO TURNO
   ============================================================ */

.turno-header {{
    display: flex;

    align-items: center;

    gap: 11px;

    margin-top: 18px;
    margin-bottom: 9px;

    padding: 11px 14px;

    background: {AMAZON_DARK};

    border-left: 5px solid {AMAZON_ORANGE};

    border-radius: 8px;

    box-shadow: 0 3px 10px rgba(0,0,0,0.20);
}}

.turno-titulo {{
    font-size: 20px;

    font-weight: 800;

    color: {TEXT_WHITE};
}}

.turno-horario {{
    background: rgba(20,110,180,0.18);

    color: #5FA8DC;

    border: 1px solid rgba(20,110,180,0.50);

    padding: 4px 11px;

    border-radius: 20px;

    font-size: 11px;

    font-weight: 800;
}}


/* ============================================================
   CABEÇALHOS DA TABELA
   ============================================================ */

.header-col {{
    text-align: center;

    font-weight: 800;

    font-size: 11px;

    color: {TEXT_MUTED};

    margin-bottom: 6px;

    letter-spacing: 0.2px;
}}

.header-esquerda {{
    text-align: left;
}}


/* ============================================================
   OPERADOR
   ============================================================ */

.nome-operador {{
    padding-top: 10px;

    font-size: 13px;

    color: {TEXT_WHITE};
}}

.funcao-operador {{
    padding-top: 10px;

    font-size: 10px;

    color: {TEXT_MUTED};

    font-weight: 700;
}}


/* ============================================================
   CARD TRABALHO
   ============================================================ */

.card-trabalho {{
    background: {AMAZON_DARK};

    color: {TEXT_WHITE};

    padding: 8px 5px;

    border-radius: 7px;

    text-align: center;

    font-weight: 800;

    font-size: 10px;

    border-left: 4px solid {AMAZON_ORANGE};

    margin-bottom: 4px;

    min-height: 42px;

    display: flex;

    flex-direction: column;

    justify-content: center;

    box-shadow: 0 2px 6px rgba(0,0,0,0.18);
}}

.sub-info {{
    color: {AMAZON_ORANGE};

    font-size: 9px;

    margin-top: 3px;

    font-weight: 700;
}}


/* ============================================================
   CARD FOLGA
   ============================================================ */

.card-folga {{
    background: #263544;

    color: {TEXT_LIGHT};

    padding: 8px 5px;

    border-radius: 7px;

    text-align: center;

    font-weight: 800;

    font-size: 10px;

    border-left: 4px solid {AMAZON_BLUE};

    margin-bottom: 4px;

    min-height: 42px;

    display: flex;

    flex-direction: column;

    justify-content: center;

    box-shadow: 0 2px 6px rgba(0,0,0,0.14);
}}

.sub-info-folga {{
    color: {TEXT_MUTED};

    font-size: 9px;

    margin-top: 3px;

    font-weight: 600;
}}


/* ============================================================
   SEPARADOR
   ============================================================ */

.separador {{
    border: 0;

    border-top: 1px solid {BORDER};

    margin-top: 2px;

    margin-bottom: 12px;
}}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {{
    background: {AMAZON_DARK};

    border-right: 1px solid {BORDER};
}}

section[data-testid="stSidebar"] > div {{
    background: {AMAZON_DARK};
}}

section[data-testid="stSidebar"] * {{
    color: {TEXT_WHITE};
}}


/* ============================================================
   SIDEBAR - TÍTULO
   ============================================================ */

.sidebar-titulo {{
    color: {AMAZON_ORANGE};

    font-size: 18px;

    font-weight: 800;

    margin-bottom: 5px;
}}

.sidebar-status {{
    background: rgba(20,110,180,0.18);

    color: #70B7E8 !important;

    padding: 8px 10px;

    border-radius: 7px;

    font-size: 11px;

    font-weight: 800;

    border-left: 4px solid {AMAZON_ORANGE};
}}


/* ============================================================
   SIDEBAR - INPUTS
   ============================================================ */

section[data-testid="stSidebar"] input {{
    background: #FFFFFF !important;

    color: #232F3E !important;

    border-radius: 7px !important;
}}

section[data-testid="stSidebar"] input::placeholder {{
    color: #64748B !important;
}}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
    background: #FFFFFF !important;

    color: #232F3E !important;
}}

section[data-testid="stSidebar"] div[data-baseweb="select"] span {{
    color: #232F3E !important;
}}


/* ============================================================
   SIDEBAR - BOTÕES
   ============================================================ */

section[data-testid="stSidebar"] .stButton > button {{
    background: {AMAZON_ORANGE};

    color: #232F3E;

    border: 1px solid {AMAZON_ORANGE};

    border-radius: 7px;

    font-weight: 800;
}}

section[data-testid="stSidebar"] .stButton > button:hover {{
    background: #FFB84D;

    border-color: #FFB84D;

    color: #232F3E;
}}


/* ============================================================
   FORM LOGIN
   ============================================================ */

section[data-testid="stSidebar"] [data-testid="stForm"] {{
    background: #1B2633;

    border: 1px solid {BORDER};

    border-radius: 9px;

    padding: 13px;
}}


/* ============================================================
   BOTÕES DA ESCALA
   ============================================================ */

.stButton > button {{
    border-radius: 6px;

    font-weight: 700;

    border: 1px solid {BORDER};

    background: {BG_CARD};

    color: {TEXT_LIGHT};
}}

.stButton > button:hover {{
    border-color: {AMAZON_BLUE};

    color: {TEXT_WHITE};

    background: {BG_CARD_2};
}}


/* ============================================================
   DIVISORES
   ============================================================ */

hr {{
    border-color: {BORDER} !important;
}}


/* ============================================================
   ALERTAS
   ============================================================ */

[data-testid="stAlert"] {{
    border-radius: 8px;
}}


/* ============================================================
   CAPTION
   ============================================================ */

.stCaption {{
    color: {TEXT_MUTED} !important;
}}


/* ============================================================
   RESPONSIVIDADE
   ============================================================ */

@media (max-width: 900px) {{

    .titulo {{
        font-size: 25px;
    }}

    div[role="radiogroup"] {{
        flex-wrap: wrap;
    }}

    div[role="radiogroup"] label {{
        min-width: 95px;
        padding: 7px 10px;
    }}

    .turno-titulo {{
        font-size: 17px;
    }}

}}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# LOGIN
# ============================================================

if "autenticado" not in st.session_state:

    st.session_state.autenticado = False


# ============================================================
# FUNÇÕES DO BANCO
# ============================================================

def buscar_operadores():

    conn = conectar()

    dados = conn.execute("""
        SELECT id, nome, funcao, turno
        FROM operadores
        WHERE ativo = 1
        ORDER BY turno, nome
    """).fetchall()

    conn.close()

    return dados


def cadastrar_operador(
    nome,
    funcao,
    turno
):

    conn = conectar()

    conn.execute("""
        INSERT INTO operadores
        (
            nome,
            funcao,
            turno
        )
        VALUES (?, ?, ?)
    """, (
        nome,
        funcao,
        turno
    ))

    conn.commit()
    conn.close()


def remover_operador(
    operador_id
):

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


def buscar_status(
    operador_id,
    semana_id
):

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
# DATAS
# ============================================================

def obter_semana(
    deslocamento=0
):

    hoje = datetime.now()

    dias_para_sexta = (
        hoje.weekday() - 4
    ) % 7

    sexta = (
        hoje
        - timedelta(days=dias_para_sexta)
        + timedelta(weeks=deslocamento)
    )

    sabado = sexta + timedelta(days=1)

    domingo = sexta + timedelta(days=2)

    segunda = sexta + timedelta(days=3)

    return {

        "id":
            sexta.strftime("%Y-%m-%d"),

        "nome":
            f"{sexta.strftime('%d/%m')} "
            f"até {segunda.strftime('%d/%m')}",

        "Sexta":
            sexta.strftime("%d/%m"),

        "Sábado":
            sabado.strftime("%d/%m"),

        "Domingo":
            domingo.strftime("%d/%m"),

        "Segunda":
            segunda.strftime("%d/%m")
    }


semanas = [
    obter_semana(i)
    for i in range(-2, 5)
]


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # CABEÇALHO
    # --------------------------------------------------------

    st.markdown(
        "<div class='sidebar-titulo'>🔐 Gestão da Escala</div>",
        unsafe_allow_html=True
    )

    st.caption(
        "Acesso restrito à gestão"
    )

    st.divider()


    # ========================================================
    # LOGIN
    # ========================================================

    if not st.session_state.autenticado:

        st.markdown(
            "### 🔐 Login"
        )

        with st.form(
            "login_form"
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
                usuario.lower().strip()
                == "admin"
                and senha
                == "Amazon123"
            ):

                st.session_state.autenticado = True

                st.rerun()

            else:

                st.error(
                    "Usuário ou senha incorretos."
                )


    # ========================================================
    # GESTÃO
    # ========================================================

    else:

        st.markdown(
            "<div class='sidebar-status'>"
            "● Modo Gestão ativo"
            "</div>",
            unsafe_allow_html=True
        )

        st.divider()


        # ====================================================
        # NOVO OPERADOR
        # ====================================================

        st.markdown(
            "### ➕ Novo operador"
        )

        novo_nome = st.text_input(
            "Nome",
            key="novo_nome"
        )

        nova_funcao = st.text_input(
            "Função",
            key="nova_funcao"
        )

        novo_turno = st.selectbox(
            "Turno",
            ["T1", "T2", "T3"],
            format_func=lambda x:
                f"{NOMES_TURNOS[x]} — {HORARIOS[x]}"
        )

        if st.button(
            "Cadastrar operador",
            use_container_width=True
        ):

            if (
                novo_nome.strip()
                and nova_funcao.strip()
            ):

                cadastrar_operador(
                    novo_nome.strip().upper(),
                    nova_funcao.strip().upper(),
                    novo_turno
                )

                st.success(
                    f"{novo_nome.strip().upper()} cadastrado!"
                )

                st.rerun()

            else:

                st.warning(
                    "Preencha nome e função."
                )


        st.divider()


        # ====================================================
        # REMOVER OPERADOR
        # ====================================================

        st.markdown(
            "### ❌ Remover operador"
        )

        operadores_sidebar = buscar_operadores()

        if operadores_sidebar:

            opcoes_remocao = {
                f"{x[1]} — {x[2]}": x[0]
                for x in operadores_sidebar
            }

            selecionado = st.selectbox(
                "Operador",
                list(opcoes_remocao.keys())
            )

            if st.button(
                "Remover",
                use_container_width=True
            ):

                remover_operador(
                    opcoes_remocao[selecionado]
                )

                st.success(
                    "Operador removido."
                )

                st.rerun()

        else:

            st.info(
                "Nenhum operador cadastrado."
            )


        st.divider()


        # ====================================================
        # LOGOUT
        # ====================================================

        if st.button(
            "🚪 Sair da gestão",
            use_container_width=True
        ):

            st.session_state.autenticado = False

            st.rerun()


# ============================================================
# TÍTULO
# ============================================================

st.markdown(
    "<div class='titulo'>Escala Amazon</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitulo'>"
    "MONITORAMENTO AMAZON"
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# SELEÇÃO DA SEMANA
# ============================================================

semana_labels = [
    x["nome"]
    for x in semanas
]

semana_escolhida = st.selectbox(
    "📅 Período da escala",
    semana_labels,
    index=2
)

semana = semanas[
    semana_labels.index(
        semana_escolhida
    )
]

semana_id = semana["id"]


# ============================================================
# OPERADORES
# ============================================================

operadores = buscar_operadores()


# ============================================================
# MÉTRICAS
# ============================================================

total = len(
    operadores
)

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


m1, m2, m3, m4 = st.columns(4)


with m1:

    st.markdown(
        f"""
        <div class="metric-card metric-card-principal">
            <div class="metric-numero">
                {total}
            </div>

            <div class="metric-label">
                OPERADORES
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with m2:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-numero">
                {t1}
            </div>

            <div class="metric-label">
                T1 • 07h às 15h
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with m3:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-numero">
                {t2}
            </div>

            <div class="metric-label">
                T2 • 15h às 23h
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with m4:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-numero">
                {t3}
            </div>

            <div class="metric-label">
                T3 • 23h às 07h
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# SELETOR DE TURNO
# ============================================================

st.markdown(
    "<div class='seletor-titulo'>"
    "VISUALIZAÇÃO DO TURNO"
    "</div>",
    unsafe_allow_html=True
)


turno_selecionado = st.radio(
    "Escolha o turno",
    ["T1", "T2", "T3"],
    format_func=lambda x:
        f"{NOMES_TURNOS[x]}  •  {HORARIOS[x]}",
    horizontal=True,
    label_visibility="collapsed"
)


# ============================================================
# DIAS
# ============================================================

DIAS = [
    ("Sexta", "sexta"),
    ("Sábado", "sabado"),
    ("Domingo", "domingo"),
    ("Segunda", "segunda")
]


# ============================================================
# ESCALA
# ============================================================

turno = turno_selecionado

operadores_turno = [
    x for x in operadores
    if x[3] == turno
]


if not operadores_turno:

    st.info(
        f"Nenhum operador cadastrado no {NOMES_TURNOS[turno]}."
    )

else:

    # ========================================================
    # CABEÇALHO
    # ========================================================

    st.markdown(
        f"""
        <div class='turno-header'>

            <div class='turno-titulo'>
                🕒 {NOMES_TURNOS[turno]}
            </div>

            <div class='turno-horario'>
                {HORARIOS[turno]}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # CABEÇALHO DA TABELA
    # ========================================================

    headers = st.columns(
        [
            2.5,
            2,
            1.8,
            1.8,
            1.8,
            1.8
        ]
    )


    headers[0].markdown(
        """
        <div class='header-col header-esquerda'>
            OPERADOR
        </div>
        """,
        unsafe_allow_html=True
    )


    headers[1].markdown(
        """
        <div class='header-col header-esquerda'>
            FUNÇÃO
        </div>
        """,
        unsafe_allow_html=True
    )


    for i, (dia, _) in enumerate(
        DIAS,
        2
    ):

        headers[i].markdown(
            f"""
            <div class='header-col'>
                {dia.upper()} ({semana[dia]})
            </div>
            """,
            unsafe_allow_html=True
        )


    st.markdown(
        "<div class='separador'></div>",
        unsafe_allow_html=True
    )


    # ========================================================
    # OPERADORES
    # ========================================================

    for operador in operadores_turno:

        operador_id = operador[0]

        nome = operador[1]

        funcao = operador[2]


        status = buscar_status(
            operador_id,
            semana_id
        )


        # ====================================================
        # PRIMEIRO ACESSO
        # ====================================================

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


        linha = st.columns(
            [
                2.5,
                2,
                1.8,
                1.8,
                1.8,
                1.8
            ]
        )


        # ====================================================
        # NOME
        # ====================================================

        linha[0].markdown(
            f"""
            <div class='nome-operador'>
                <b>{nome}</b>
            </div>
            """,
            unsafe_allow_html=True
        )


        # ====================================================
        # FUNÇÃO
        # ====================================================

        linha[1].markdown(
            f"""
            <div class='funcao-operador'>
                {funcao}
            </div>
            """,
            unsafe_allow_html=True
        )


        # ====================================================
        # DIAS
        # ====================================================

        status_lista = list(status)


        for i, (dia, _) in enumerate(
            DIAS,
            2
        ):

            valor = status_lista[
                i - 2
            ]


            # ------------------------------------------------
            # TRABALHO
            # ------------------------------------------------

            if valor != "FOLGA":

                linha[i].markdown(
                    f"""
                    <div class='card-trabalho'>

                        TRABALHO

                        <div class='sub-info'>
                            {HORARIOS[turno]}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # ------------------------------------------------
            # FOLGA
            # ------------------------------------------------

            else:

                linha[i].markdown(
                    """
                    <div class='card-folga'>

                        FOLGA

                        <div class='sub-info-folga'>
                            Descanso
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # ------------------------------------------------
            # BOTÃO DE GESTÃO
            # ------------------------------------------------

            if st.session_state.autenticado:

                if valor == "FOLGA":

                    novo_valor = HORARIOS[turno]

                else:

                    novo_valor = "FOLGA"


                if linha[i].button(
                    "↔ Alternar",
                    key=(
                        f"{operador_id}_"
                        f"{semana_id}_"
                        f"{dia}"
                    ),
                    use_container_width=True
                ):

                    status_lista[
                        i - 2
                    ] = novo_valor

                    salvar_status(
                        operador_id,
                        semana_id,
                        *status_lista
                    )

                    st.rerun()


    # ========================================================
    # INFORMAÇÃO DO TURNO
    # ========================================================

    st.write("")

    st.markdown(
        f"""
        <div style="
            text-align:center;
            color:{TEXT_MUTED};
            font-size:11px;
            padding:8px;
        ">
            Exibindo {len(operadores_turno)}
            operador(es) •
            {NOMES_TURNOS[turno]} •
            {HORARIOS[turno]}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.caption(
    "Escala Amazon • Sistema independente de gestão de escala"
)
