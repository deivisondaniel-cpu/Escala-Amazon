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
# IDENTIDADE VISUAL
# ============================================================

AZUL_AMAZON = "#232F3E"
AZUL = "#146EB4"
AZUL_CLARO = "#2E7DB5"

LARANJA = "#FF9900"
LARANJA_CLARO = "#FFB84D"

FUNDO = "#0F1720"
FUNDO_CARD = "#17212D"
FUNDO_CARD_2 = "#1D2A38"

BORDA = "#2B3A4A"

BRANCO = "#FFFFFF"
TEXTO = "#E8EDF2"
TEXTO_SECUNDARIO = "#8FA1B3"

VERDE = "#21C77A"


# ============================================================
# BANCO
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
# HORÁRIOS
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
# CSS
# ============================================================

st.markdown(
    f"""
    <style>

    /* ========================================================
       BASE
       ======================================================== */

    #MainMenu {{
        visibility: hidden;
    }}

    footer {{
        visibility: hidden;
    }}

    header {{
        background: transparent !important;
    }}

    .stApp {{
        background: {FUNDO};
        color: {TEXTO};
    }}

    [data-testid="stAppViewContainer"] {{
        background: {FUNDO};
    }}

    .stMainBlockContainer {{
        max-width: 1500px;
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
    }}


    /* ========================================================
       TEXTO GERAL
       ======================================================== */

    h1, h2, h3, h4, h5, h6 {{
        color: {BRANCO} !important;
    }}

    p, label {{
        color: {TEXTO} !important;
    }}


    /* ========================================================
       TOPO
       ======================================================== */

    .topo {{
        display: flex;
        align-items: center;
        justify-content: space-between;

        background:
            linear-gradient(
                135deg,
                #17212D 0%,
                #111A24 100%
            );

        border: 1px solid {BORDA};

        border-radius: 16px;

        padding: 22px 26px;

        margin-bottom: 22px;

        box-shadow:
            0 8px 30px rgba(0,0,0,0.20);

        position: relative;

        overflow: hidden;
    }}

    .topo::before {{
        content: "";

        position: absolute;

        left: 0;
        top: 0;
        bottom: 0;

        width: 5px;

        background: {LARANJA};
    }}

    .topo-esquerda {{
        display: flex;
        align-items: center;
        gap: 16px;
    }}

    .logo {{
        width: 48px;
        height: 48px;

        border-radius: 12px;

        background: {LARANJA};

        color: {AZUL_AMAZON};

        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 27px;
        font-weight: 900;

        box-shadow:
            0 4px 14px rgba(255,153,0,0.20);
    }}

    .topo-titulo {{
        font-size: 25px;
        font-weight: 850;

        color: {BRANCO};

        line-height: 1.1;
    }}

    .topo-subtitulo {{
        font-size: 12px;

        color: {TEXTO_SECUNDARIO};

        margin-top: 5px;

        letter-spacing: 0.3px;
    }}

    .badge-status {{
        display: inline-flex;
        align-items: center;
        gap: 7px;

        background: rgba(33,199,122,0.10);

        border: 1px solid rgba(33,199,122,0.25);

        color: {VERDE};

        padding: 7px 12px;

        border-radius: 30px;

        font-size: 11px;
        font-weight: 800;
    }}


    /* ========================================================
       PERÍODO
       ======================================================== */

    .periodo-card {{
        background: {FUNDO_CARD};

        border: 1px solid {BORDA};

        border-radius: 12px;

        padding: 14px 18px;

        margin-bottom: 18px;
    }}

    .periodo-label {{
        color: {TEXTO_SECUNDARIO};

        font-size: 10px;

        font-weight: 800;

        text-transform: uppercase;

        letter-spacing: 1px;

        margin-bottom: 5px;
    }}

    .periodo-valor {{
        color: {BRANCO};

        font-size: 17px;

        font-weight: 800;
    }}


    /* ========================================================
       MÉTRICAS
       ======================================================== */

    .metric-card {{
        background:
            linear-gradient(
                145deg,
                {FUNDO_CARD_2},
                {FUNDO_CARD}
            );

        border: 1px solid {BORDA};

        border-radius: 13px;

        padding: 17px 18px;

        min-height: 92px;

        box-shadow:
            0 5px 20px rgba(0,0,0,0.14);

        position: relative;

        overflow: hidden;
    }}

    .metric-card::after {{
        content: "";

        position: absolute;

        right: -20px;
        top: -25px;

        width: 75px;
        height: 75px;

        border-radius: 50%;

        background: rgba(255,153,0,0.04);
    }}

    .metric-numero {{
        color: {BRANCO};

        font-size: 27px;

        font-weight: 850;

        line-height: 1;
    }}

    .metric-label {{
        color: {TEXTO_SECUNDARIO};

        font-size: 10px;

        font-weight: 800;

        margin-top: 8px;

        letter-spacing: 0.6px;
    }}

    .metric-destaque {{
        border-top: 3px solid {LARANJA};
    }}

    .metric-azul {{
        border-top: 3px solid {AZUL};
    }}


    /* ========================================================
       ÁREA DE VISUALIZAÇÃO
       ======================================================== */

    .secao-titulo {{
        display: flex;
        align-items: center;

        gap: 10px;

        margin-top: 30px;

        margin-bottom: 10px;
    }}

    .secao-titulo-texto {{
        font-size: 15px;

        font-weight: 850;

        color: {BRANCO};

        letter-spacing: 0.2px;
    }}

    .secao-linha {{
        flex: 1;

        height: 1px;

        background: {BORDA};
    }}


    /* ========================================================
       TABS
       ======================================================== */

    button[data-baseweb="tab"] {{
        background: transparent !important;

        color: {TEXTO_SECUNDARIO} !important;

        border-radius: 9px 9px 0 0 !important;

        font-weight: 800 !important;
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {LARANJA} !important;
    }}

    div[data-baseweb="tab-highlight"] {{
        background-color: {LARANJA} !important;
    }}


    /* ========================================================
       CABEÇALHO DO TURNO
       ======================================================== */

    .turno-header {{
        display: flex;

        align-items: center;

        gap: 12px;

        background: {FUNDO_CARD};

        border: 1px solid {BORDA};

        border-left: 4px solid {LARANJA};

        border-radius: 10px;

        padding: 13px 16px;

        margin-top: 12px;

        margin-bottom: 12px;
    }}

    .turno-titulo {{
        font-size: 17px;

        font-weight: 850;

        color: {BRANCO};
    }}

    .turno-horario {{
        background: rgba(20,110,180,0.14);

        border: 1px solid rgba(20,110,180,0.35);

        color: #6EB5E8;

        border-radius: 20px;

        padding: 5px 11px;

        font-size: 11px;

        font-weight: 800;
    }}


    /* ========================================================
       CABEÇALHO DA TABELA
       ======================================================== */

    .table-header {{
        color: {TEXTO_SECUNDARIO};

        font-size: 10px;

        font-weight: 850;

        letter-spacing: 0.5px;

        padding: 7px 4px;

        text-transform: uppercase;
    }}


    /* ========================================================
       OPERADOR
       ======================================================== */

    .operador-card {{
        padding: 7px 4px;
    }}

    .operador-nome {{
        color: {BRANCO};

        font-size: 12px;

        font-weight: 800;
    }}

    .operador-funcao {{
        color: {TEXTO_SECUNDARIO};

        font-size: 10px;

        margin-top: 3px;
    }}


    /* ========================================================
       STATUS
       ======================================================== */

    .status-trabalho {{
        background:
            linear-gradient(
                135deg,
                #1F3040,
                #182631
            );

        border: 1px solid #30495E;

        border-left: 3px solid {LARANJA};

        border-radius: 8px;

        padding: 8px 4px;

        text-align: center;

        min-height: 43px;
    }}

    .status-trabalho-titulo {{
        color: {BRANCO};

        font-size: 10px;

        font-weight: 850;
    }}

    .status-trabalho-hora {{
        color: {LARANJA_CLARO};

        font-size: 9px;

        margin-top: 3px;

        font-weight: 700;
    }}

    .status-folga {{
        background:
            linear-gradient(
                135deg,
                #172C3B,
                #152430
            );

        border: 1px solid #27516D;

        border-left: 3px solid {AZUL};

        border-radius: 8px;

        padding: 8px 4px;

        text-align: center;

        min-height: 43px;
    }}

    .status-folga-titulo {{
        color: #8BC4EB;

        font-size: 10px;

        font-weight: 850;
    }}

    .status-folga-sub {{
        color: #607F96;

        font-size: 9px;

        margin-top: 3px;
    }}


    /* ========================================================
       BOTÕES
       ======================================================== */

    .stButton > button {{
        border-radius: 7px !important;

        border: 1px solid {BORDA} !important;

        background: {FUNDO_CARD} !important;

        color: {TEXTO} !important;

        font-weight: 750 !important;
    }}

    .stButton > button:hover {{
        border-color: {LARANJA} !important;

        color: {LARANJA} !important;
    }}


    /* ========================================================
       SELECTS
       ======================================================== */

    div[data-baseweb="select"] > div {{
        background: {FUNDO_CARD} !important;

        border: 1px solid {BORDA} !important;

        border-radius: 8px !important;

        color: {BRANCO} !important;
    }}


    /* ========================================================
       MODAL / DIALOG
       ======================================================== */

    div[data-testid="stDialog"] > div {{
        background: {FUNDO_CARD} !important;

        border: 1px solid {BORDA};

        border-radius: 15px;
    }}


    /* ========================================================
       FORMULÁRIOS
       ======================================================== */

    div[data-testid="stForm"] {{
        background: {FUNDO_CARD};

        border: 1px solid {BORDA};

        border-radius: 12px;

        padding: 18px;
    }}

    input {{
        background: #111A24 !important;

        color: {BRANCO} !important;

        border-color: {BORDA} !important;
    }}


    /* ========================================================
       EXPANDER
       ======================================================== */

    details {{
        background: {FUNDO_CARD} !important;

        border: 1px solid {BORDA} !important;

        border-radius: 10px !important;
    }}


    /* ========================================================
       ALERTAS
       ======================================================== */

    div[data-testid="stAlert"] {{
        border-radius: 9px;
    }}


    /* ========================================================
       RODAPÉ
       ======================================================== */

    .rodape {{
        text-align: center;

        color: #5F7182;

        font-size: 10px;

        margin-top: 30px;

        padding-top: 15px;

        border-top: 1px solid {BORDA};
    }}


    /* ========================================================
       RESPONSIVO
       ======================================================== */

    @media (max-width: 900px) {{

        .topo {{
            padding: 17px;
        }}

        .topo-titulo {{
            font-size: 21px;
        }}

        .logo {{
            width: 42px;
            height: 42px;
            font-size: 23px;
        }}

        .metric-numero {{
            font-size: 22px;
        }}

    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False


if "turno_selecionado" not in st.session_state:
    st.session_state.turno_selecionado = "T1"


# ============================================================
# FUNÇÕES DE BANCO
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
            INSERT INTO escala (
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

def obter_semana(deslocamento=0):

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
# CABEÇALHO
# ============================================================

topo_esq, topo_dir = st.columns(
    [8, 2]
)


with topo_esq:

    st.markdown(
        """
        <div class="topo">

            <div class="topo-esquerda">

                <div class="logo">
                    A
                </div>

                <div>

                    <div class="topo-titulo">
                        Escala Amazon
                    </div>

                    <div class="topo-subtitulo">
                        Painel de Monitoramento Operacional
                    </div>

                </div>

            </div>

            <div class="badge-status">
                ● OPERAÇÃO ATIVA
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with topo_dir:

    st.write("")

    if st.button(
        "⚙ Gestão",
        use_container_width=True
    ):

        st.session_state["abrir_gestao"] = True


# ============================================================
# GESTÃO
# ============================================================

if "abrir_gestao" not in st.session_state:

    st.session_state.abrir_gestao = False


if st.session_state.abrir_gestao:

    with st.expander(
        "🔐 Área de Gestão",
        expanded=True
    ):

        if not st.session_state.autenticado:

            st.markdown(
                "### Acesso administrativo"
            )

            st.caption(
                "A gestão fica protegida e não ocupa espaço "
                "permanente no painel."
            )

            with st.form("login_form"):

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
                    usuario.strip().lower() == "admin"
                    and senha == "Amazon123"
                ):

                    st.session_state.autenticado = True

                    st.success(
                        "Acesso autorizado."
                    )

                    st.rerun()

                else:

                    st.error(
                        "Usuário ou senha incorretos."
                    )

        else:

            st.success(
                "🟢 Modo gestão ativo"
            )

            g1, g2 = st.columns(2)

            with g1:

                st.markdown(
                    "### ➕ Novo operador"
                )

                with st.form(
                    "cadastro_operador"
                ):

                    nome = st.text_input(
                        "Nome"
                    )

                    funcao = st.text_input(
                        "Função"
                    )

                    turno = st.selectbox(
                        "Turno",
                        ["T1", "T2", "T3"],
                        format_func=lambda x:
                            f"{NOMES_TURNOS[x]} • {HORARIOS[x]}"
                    )

                    cadastrar = st.form_submit_button(
                        "Cadastrar operador",
                        use_container_width=True
                    )

                if cadastrar:

                    if (
                        nome.strip()
                        and funcao.strip()
                    ):

                        cadastrar_operador(
                            nome.strip().upper(),
                            funcao.strip().upper(),
                            turno
                        )

                        st.success(
                            f"{nome.strip().upper()} cadastrado."
                        )

                        st.rerun()

                    else:

                        st.warning(
                            "Preencha nome e função."
                        )

            with g2:

                st.markdown(
                    "### ❌ Remover operador"
                )

                operadores_gestao = buscar_operadores()

                if operadores_gestao:

                    opcoes = {
                        f"{x[1]} • {x[2]} • {x[3]}":
                        x[0]

                        for x in operadores_gestao
                    }

                    selecionado = st.selectbox(
                        "Operador",
                        list(opcoes.keys())
                    )

                    if st.button(
                        "Remover operador",
                        use_container_width=True
                    ):

                        remover_operador(
                            opcoes[selecionado]
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

            if st.button(
                "🚪 Sair da gestão"
            ):

                st.session_state.autenticado = False

                st.session_state.abrir_gestao = False

                st.rerun()


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

total = len(operadores)

t1 = sum(
    1
    for x in operadores
    if x[3] == "T1"
)

t2 = sum(
    1
    for x in operadores
    if x[3] == "T2"
)

t3 = sum(
    1
    for x in operadores
    if x[3] == "T3"
)


m1, m2, m3, m4 = st.columns(4)


with m1:

    st.markdown(
        f"""
        <div class="metric-card metric-destaque">

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
        <div class="metric-card metric-azul">

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
        <div class="metric-card metric-azul">

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
        <div class="metric-card metric-azul">

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
# TÍTULO DA ÁREA
# ============================================================

st.markdown(
    """
    <div class="secao-titulo">

        <div class="secao-titulo-texto">
            VISUALIZAÇÃO DA OPERAÇÃO
        </div>

        <div class="secao-linha"></div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TABS DOS TURNOS
# ============================================================

tab1, tab2, tab3 = st.tabs(
    [
        "🕒 T1 • 07h às 15h",
        "🕒 T2 • 15h às 23h",
        "🕒 T3 • 23h às 07h"
    ]
)


# ============================================================
# FUNÇÃO PARA DESENHAR TURNO
# ============================================================

def desenhar_turno(turno):

    operadores_turno = [
        x
        for x in operadores
        if x[3] == turno
    ]

    st.markdown(
        f"""
        <div class="turno-header">

            <div class="turno-titulo">
                {NOMES_TURNOS[turno]}
            </div>

            <div class="turno-horario">
                {HORARIOS[turno]}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    if not operadores_turno:

        st.info(
            "Nenhum operador cadastrado neste turno."
        )

        return


    # ========================================================
    # CABEÇALHO
    # ========================================================

    headers = st.columns(
        [
            2.7,
            1.9,
            1.65,
            1.65,
            1.65,
            1.65
        ]
    )


    headers[0].markdown(
        '<div class="table-header">OPERADOR</div>',
        unsafe_allow_html=True
    )

    headers[1].markdown(
        '<div class="table-header">FUNÇÃO</div>',
        unsafe_allow_html=True
    )


    for i, dia in enumerate(
        ["Sexta", "Sábado", "Domingo", "Segunda"],
        2
    ):

        headers[i].markdown(
            f"""
            <div class="table-header">
                {dia.upper()}<br>
                <span style="color:{AZUL_CLARO}">
                    {semana[dia]}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )


    st.markdown(
        f"""
        <div style="
            height:1px;
            background:{BORDA};
            margin:0 0 8px 0;
        "></div>
        """,
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


        # ----------------------------------------------------
        # PRIMEIRA UTILIZAÇÃO DA SEMANA
        # ----------------------------------------------------

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


        linha = st.columns(
            [
                2.7,
                1.9,
                1.65,
                1.65,
                1.65,
                1.65
            ]
        )


        # ----------------------------------------------------
        # OPERADOR
        # ----------------------------------------------------

        linha[0].markdown(
            f"""
            <div class="operador-card">

                <div class="operador-nome">
                    {nome}
                </div>

                <div class="operador-funcao">
                    ● Operador ativo
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # FUNÇÃO
        # ----------------------------------------------------

        linha[1].markdown(
            f"""
            <div class="operador-card">

                <div class="operador-nome"
                     style="font-size:10px;">
                    {funcao}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # DIAS
        # ----------------------------------------------------

        for i, (dia, _) in enumerate(
            [
                ("Sexta", "sexta"),
                ("Sábado", "sabado"),
                ("Domingo", "domingo"),
                ("Segunda", "segunda")
            ],
            2
        ):

            valor = status_lista[i - 2]


            # =================================================
            # TRABALHO
            # =================================================

            if valor != "FOLGA":

                linha[i].markdown(
                    f"""
                    <div class="status-trabalho">

                        <div class="status-trabalho-titulo">
                            TRABALHO
                        </div>

                        <div class="status-trabalho-hora">
                            {HORARIOS[turno]}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # =================================================
            # FOLGA
            # =================================================

            else:

                linha[i].markdown(
                    """
                    <div class="status-folga">

                        <div class="status-folga-titulo">
                            FOLGA
                        </div>

                        <div class="status-folga-sub">
                            Descanso
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # =================================================
            # CONTROLE DE GESTÃO
            # =================================================

            if st.session_state.autenticado:

                if valor == "FOLGA":

                    novo_valor = HORARIOS[turno]

                    texto_botao = "↗ Trabalho"

                else:

                    novo_valor = "FOLGA"

                    texto_botao = "↘ Folga"


                if linha[i].button(
                    texto_botao,
                    key=(
                        f"alterar_"
                        f"{operador_id}_"
                        f"{semana_id}_"
                        f"{dia}"
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


# ============================================================
# RENDERIZAÇÃO DOS TURNOS
# ============================================================

with tab1:

    desenhar_turno("T1")


with tab2:

    desenhar_turno("T2")


with tab3:

    desenhar_turno("T3")


# ============================================================
# RODAPÉ
# ============================================================

st.markdown(
    """
    <div class="rodape">
        ESCALA AMAZON
        &nbsp;•&nbsp;
        Monitoramento Operacional
        &nbsp;•&nbsp;
        Sistema interno de gestão
    </div>
    """,
    unsafe_allow_html=True
)
