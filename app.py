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
# CORES AMAZON
# ============================================================

AZUL = "#232F3E"
AZUL_2 = "#146EB4"
LARANJA = "#FF9900"
LARANJA_CLARO = "#FEBD69"

FUNDO = "#F3F6F9"
BRANCO = "#FFFFFF"
CINZA = "#64748B"
BORDA = "#D7DEE7"


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
            FOREIGN KEY (operador_id)
            REFERENCES operadores(id)
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
       GERAL
       ======================================================== */

    #MainMenu {{
        visibility: hidden;
    }}

    footer {{
        visibility: hidden;
    }}

    .stApp {{
        background: {FUNDO};
    }}

    [data-testid="stAppViewContainer"] {{
        background: {FUNDO};
    }}

    .stMainBlockContainer {{
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1500px;
    }}


    /* ========================================================
       HEADER
       ======================================================== */

    .topo {{
        background: {AZUL};
        border-radius: 14px;
        padding: 18px 24px;
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(35,47,62,0.15);
    }}

    .logo {{
        width: 46px;
        height: 46px;
        min-width: 46px;
        background: {LARANJA};
        color: {AZUL};
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 25px;
        font-weight: 900;
    }}

    .topo-titulo {{
        color: white;
        font-size: 25px;
        font-weight: 800;
        line-height: 1.1;
    }}

    .topo-subtitulo {{
        color: #B9C4D0;
        font-size: 12px;
        margin-top: 4px;
    }}


    /* ========================================================
       TÍTULOS
       ======================================================== */

    .secao-titulo {{
        color: {AZUL};
        font-size: 18px;
        font-weight: 800;
        margin-top: 12px;
        margin-bottom: 4px;
    }}

    .secao-subtitulo {{
        color: {CINZA};
        font-size: 12px;
        margin-bottom: 15px;
    }}


    /* ========================================================
       MÉTRICAS
       ======================================================== */

    .metric-card {{
        background: {BRANCO};
        border: 1px solid {BORDA};
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(35,47,62,0.05);
        min-height: 88px;
    }}

    .metric-card-laranja {{
        border-top: 4px solid {LARANJA};
    }}

    .metric-card-azul {{
        border-top: 4px solid {AZUL_2};
    }}

    .metric-numero {{
        color: {AZUL};
        font-size: 25px;
        font-weight: 900;
        line-height: 1;
    }}

    .metric-label {{
        color: {CINZA};
        font-size: 10px;
        font-weight: 800;
        margin-top: 7px;
        letter-spacing: .3px;
    }}


    /* ========================================================
       PAINEL DE VISUALIZAÇÃO
       ======================================================== */

    .painel {{
        background: {BRANCO};
        border: 1px solid {BORDA};
        border-radius: 14px;
        padding: 18px;
        margin-top: 20px;
        box-shadow: 0 3px 12px rgba(35,47,62,0.05);
    }}

    .painel-titulo {{
        color: {AZUL};
        font-size: 16px;
        font-weight: 800;
    }}

    .painel-subtitulo {{
        color: {CINZA};
        font-size: 11px;
        margin-top: 3px;
    }}


    /* ========================================================
       TURNO
       ======================================================== */

    .turno-header {{
        background: {AZUL};
        border-radius: 10px;
        padding: 13px 16px;
        margin-top: 18px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    .turno-nome {{
        color: white;
        font-size: 17px;
        font-weight: 800;
    }}

    .turno-horario {{
        background: {LARANJA};
        color: {AZUL};
        padding: 5px 11px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 900;
    }}


    /* ========================================================
       CABEÇALHO DA ESCALA
       ======================================================== */

    .cabecalho {{
        color: {CINZA};
        font-size: 10px;
        font-weight: 900;
        text-align: center;
        padding-bottom: 7px;
        border-bottom: 2px solid {BORDA};
    }}

    .cabecalho-esquerda {{
        text-align: left;
    }}


    /* ========================================================
       OPERADORES
       ======================================================== */

    .nome {{
        color: {AZUL};
        font-size: 12px;
        font-weight: 800;
        padding-top: 10px;
    }}

    .funcao {{
        color: {CINZA};
        font-size: 10px;
        padding-top: 10px;
        font-weight: 600;
    }}


    /* ========================================================
       TRABALHO
       ======================================================== */

    .trabalho {{
        background: {AZUL};
        color: white;
        border-left: 4px solid {LARANJA};
        border-radius: 7px;
        padding: 8px 4px;
        text-align: center;
        font-size: 10px;
        font-weight: 900;
        margin-top: 5px;
    }}

    .trabalho-horario {{
        color: {LARANJA_CLARO};
        font-size: 9px;
        margin-top: 3px;
        font-weight: 700;
    }}


    /* ========================================================
       FOLGA
       ======================================================== */

    .folga {{
        background: #EAF3FB;
        color: {AZUL};
        border-left: 4px solid {AZUL_2};
        border-radius: 7px;
        padding: 8px 4px;
        text-align: center;
        font-size: 10px;
        font-weight: 900;
        margin-top: 5px;
    }}

    .folga-info {{
        color: #6B8196;
        font-size: 9px;
        margin-top: 3px;
    }}


    /* ========================================================
       BOTÕES
       ======================================================== */

    .stButton > button {{
        border-radius: 7px !important;
        font-weight: 700 !important;
        border: 1px solid {BORDA} !important;
    }}

    .stButton > button:hover {{
        border-color: {LARANJA} !important;
        color: {AZUL} !important;
    }}


    /* ========================================================
       SELECTBOX
       ======================================================== */

    div[data-baseweb="select"] > div {{
        border-radius: 8px !important;
        border-color: {BORDA} !important;
        background: white !important;
    }}

    div[data-baseweb="select"] > div:focus-within {{
        border-color: {AZUL_2} !important;
        box-shadow: 0 0 0 1px {AZUL_2} !important;
    }}


    /* ========================================================
       EXPANDER LOGIN
       ======================================================== */

    [data-testid="stExpander"] {{
        border: 1px solid {BORDA};
        border-radius: 10px;
        background: white;
    }}

    [data-testid="stExpander"] summary {{
        color: {AZUL};
        font-weight: 800;
    }}


    /* ========================================================
       DIVISOR
       ======================================================== */

    hr {{
        border-color: {BORDA} !important;
    }}


    /* ========================================================
       MOBILE
       ======================================================== */

    @media (max-width: 900px) {{

        .topo {{
            padding: 15px;
        }}

        .topo-titulo {{
            font-size: 20px;
        }}

        .metric-numero {{
            font-size: 20px;
        }}

        .painel {{
            padding: 10px;
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
# FUNÇÕES BANCO
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
    """, (operador_id,))

    conn.commit()
    conn.close()


def buscar_status(operador_id, semana_id):

    conn = conectar()

    resultado = conn.execute("""
        SELECT sexta, sabado, domingo, segunda
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
            SET sexta = ?,
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
# SEMANAS
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
        "id": sexta.strftime("%Y-%m-%d"),

        "nome":
            f"{sexta.strftime('%d/%m')} "
            f"até {segunda.strftime('%d/%m')}",

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
# HEADER
# ============================================================

st.markdown(
    """
    <div class="topo">

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
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOGIN COMPACTO
# ============================================================

with st.expander(
    "🔐 Login / Gestão",
    expanded=False
):

    if not st.session_state.autenticado:

        col1, col2, col3 = st.columns(
            [1, 1, 0.7]
        )

        with col1:

            usuario = st.text_input(
                "Usuário",
                key="login_usuario"
            )

        with col2:

            senha = st.text_input(
                "Senha",
                type="password",
                key="login_senha"
            )

        with col3:

            st.write("")

            entrar = st.button(
                "Entrar",
                use_container_width=True
            )

        if entrar:

            if (
                usuario.lower().strip() == "admin"
                and senha == "Amazon123"
            ):

                st.session_state.autenticado = True

                st.success("Modo gestão ativado.")

                st.rerun()

            else:

                st.error(
                    "Usuário ou senha incorretos."
                )

    else:

        st.success(
            "🟢 Modo Gestão ativo"
        )

        col1, col2, col3 = st.columns(
            [1, 1, 1]
        )

        with col1:

            st.markdown(
                "**Cadastrar operador**"
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
                "Cadastrar",
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
                        "Operador cadastrado."
                    )

                    st.rerun()

                else:

                    st.warning(
                        "Preencha nome e função."
                    )

        with col2:

            st.markdown(
                "**Remover operador**"
            )

            operadores_temp = buscar_operadores()

            if operadores_temp:

                opcoes = {
                    f"{x[1]} — {x[2]}": x[0]
                    for x in operadores_temp
                }

                escolhido = st.selectbox(
                    "Operador",
                    list(opcoes.keys())
                )

                if st.button(
                    "Remover",
                    use_container_width=True
                ):

                    remover_operador(
                        opcoes[escolhido]
                    )

                    st.success(
                        "Operador removido."
                    )

                    st.rerun()

        with col3:

            st.markdown(
                "**Sessão**"
            )

            st.write("")

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
    """
    <div class="secao-titulo">
        Monitoramento Amazon
    </div>

    <div class="secao-subtitulo">
        Gestão de operadores e escala operacional
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SEMANA
# ============================================================

col_periodo, col_vazia = st.columns(
    [2, 4]
)

with col_periodo:

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
        <div class="metric-card metric-card-laranja">

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
        <div class="metric-card metric-card-azul">

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
        <div class="metric-card metric-card-azul">

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
        <div class="metric-card metric-card-azul">

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

st.write("")

st.markdown(
    """
    <div class="secao-titulo">
        Visualização da operação
    </div>

    <div class="secao-subtitulo">
        Selecione o turno que deseja visualizar
    </div>
    """,
    unsafe_allow_html=True
)


turno_selecionado = st.radio(
    "Turno",
    ["T1", "T2", "T3"],
    format_func=lambda x:
        f"{NOMES_TURNOS[x]}  •  {HORARIOS[x]}",
    horizontal=True,
    label_visibility="collapsed"
)


# ============================================================
# OPERADORES DO TURNO
# ============================================================

operadores_turno = [
    x for x in operadores
    if x[3] == turno_selecionado
]


# ============================================================
# PAINEL
# ============================================================

st.markdown(
    f"""
    <div class="painel">

        <div class="painel-titulo">
            {NOMES_TURNOS[turno_selecionado]}
        </div>

        <div class="painel-subtitulo">
            {HORARIOS[turno_selecionado]}
            &nbsp; • &nbsp;
            {len(operadores_turno)} operadores
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CABEÇALHO TURNO
# ============================================================

st.markdown(
    f"""
    <div class="turno-header">

        <div class="turno-nome">
            🕒 {NOMES_TURNOS[turno_selecionado]}
        </div>

        <div class="turno-horario">
            {HORARIOS[turno_selecionado]}
        </div>

    </div>
    """,
    unsafe_allow_html=True
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
# CABEÇALHO
# ============================================================

headers = st.columns(
    [
        2.4,
        1.7,
        1.7,
        1.7,
        1.7,
        1.7
    ]
)


headers[0].markdown(
    """
    <div class="cabecalho cabecalho-esquerda">
        OPERADOR
    </div>
    """,
    unsafe_allow_html=True
)


headers[1].markdown(
    """
    <div class="cabecalho cabecalho-esquerda">
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
        <div class="cabecalho">

            {dia.upper()}<br>

            <span style="font-weight:600;">
                ({semana[dia]})
            </span>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# LINHAS
# ============================================================

for operador in operadores_turno:

    operador_id = operador[0]
    nome = operador[1]
    funcao = operador[2]


    status = buscar_status(
        operador_id,
        semana_id
    )


    # --------------------------------------------------------
    # PRIMEIRO ACESSO
    # --------------------------------------------------------

    if status is None:

        horario = HORARIOS[
            turno_selecionado
        ]

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
            2.4,
            1.7,
            1.7,
            1.7,
            1.7,
            1.7
        ]
    )


    # --------------------------------------------------------
    # NOME
    # --------------------------------------------------------

    linha[0].markdown(
        f"""
        <div class="nome">
            {nome}
        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # FUNÇÃO
    # --------------------------------------------------------

    linha[1].markdown(
        f"""
        <div class="funcao">
            {funcao}
        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # DIAS
    # --------------------------------------------------------

    for i, (dia, _) in enumerate(
        DIAS,
        2
    ):

        valor = status_lista[i - 2]


        if valor == "FOLGA":

            linha[i].markdown(
                """
                <div class="folga">

                    FOLGA

                    <div class="folga-info">
                        Descanso
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            linha[i].markdown(
                f"""
                <div class="trabalho">

                    TRABALHO

                    <div class="trabalho-horario">
                        {HORARIOS[turno_selecionado]}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


        # ----------------------------------------------------
        # GESTÃO
        # ----------------------------------------------------

        if st.session_state.autenticado:

            if valor == "FOLGA":

                novo_valor = HORARIOS[
                    turno_selecionado
                ]

            else:

                novo_valor = "FOLGA"


            if linha[i].button(
                "Alternar",
                key=(
                    f"btn_"
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
# SEM OPERADORES
# ============================================================

if not operadores_turno:

    st.info(
        f"Nenhum operador cadastrado no {NOMES_TURNOS[turno_selecionado]}."
    )


# ============================================================
# RODAPÉ
# ============================================================

st.write("")

st.divider()

st.caption(
    "Escala Amazon • Painel de Monitoramento Operacional"
)
