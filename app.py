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
# IDENTIDADE VISUAL AMAZON
# ============================================================

AZUL = "#232F3E"
AZUL_MEDIO = "#146EB4"
LARANJA = "#FF9900"
LARANJA_CLARO = "#FEBD69"

FUNDO = "#F3F6F9"
BRANCO = "#FFFFFF"
CINZA = "#64748B"
CINZA_CLARO = "#E2E8F0"
VERDE = "#16A34A"


# ============================================================
# BANCO DE DADOS
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

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS operadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            funcao TEXT NOT NULL,
            turno TEXT NOT NULL,
            ativo INTEGER DEFAULT 1
        )
        """
    )

    cursor.execute(
        """
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
        """
    )

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

    .stApp {{
        background-color: {FUNDO};
    }}

    [data-testid="stAppViewContainer"] {{
        background-color: {FUNDO};
    }}

    [data-testid="stHeader"] {{
        background-color: transparent;
    }}

    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1500px;
    }}


    /* ========================================================
       TOPO
       ======================================================== */

    .topo-amazon {{
        background-color: {AZUL};
        border-radius: 14px;
        padding: 18px 22px;
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 20px;
        border-bottom: 4px solid {LARANJA};
        box-shadow: 0 4px 14px rgba(35, 47, 62, 0.14);
    }}

    .logo-amazon {{
        width: 48px;
        height: 48px;
        min-width: 48px;
        border-radius: 10px;
        background-color: {LARANJA};
        color: {AZUL};
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 27px;
        font-weight: 900;
    }}

    .titulo-amazon {{
        color: #FFFFFF;
        font-size: 25px;
        font-weight: 800;
        line-height: 1.1;
    }}

    .subtitulo-amazon {{
        color: #B8C3CF;
        font-size: 12px;
        margin-top: 5px;
    }}


    /* ========================================================
       TÍTULOS
       ======================================================== */

    .titulo-secao {{
        color: {AZUL};
        font-size: 19px;
        font-weight: 800;
        margin-top: 8px;
    }}

    .subtitulo-secao {{
        color: {CINZA};
        font-size: 12px;
        margin-bottom: 15px;
    }}


    /* ========================================================
       CARDS DE MÉTRICA
       ======================================================== */

    .metric-amazon {{
        background-color: {BRANCO};
        border: 1px solid {CINZA_CLARO};
        border-radius: 11px;
        padding: 14px;
        text-align: center;
        min-height: 88px;
        box-shadow: 0 2px 8px rgba(35, 47, 62, 0.05);
    }}

    .metric-principal {{
        border-top: 4px solid {LARANJA};
    }}

    .metric-turno {{
        border-top: 4px solid {AZUL_MEDIO};
    }}

    .metric-numero {{
        color: {AZUL};
        font-size: 26px;
        font-weight: 900;
        line-height: 1;
    }}

    .metric-label {{
        color: {CINZA};
        font-size: 10px;
        font-weight: 800;
        margin-top: 7px;
        letter-spacing: 0.3px;
    }}


    /* ========================================================
       PAINEL
       ======================================================== */

    .painel {{
        background-color: {BRANCO};
        border: 1px solid {CINZA_CLARO};
        border-radius: 13px;
        padding: 18px;
        margin-top: 20px;
        box-shadow: 0 2px 10px rgba(35, 47, 62, 0.05);
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

    .turno-barra {{
        background-color: {AZUL};
        border-radius: 10px;
        padding: 12px 15px;
        margin-top: 16px;
        margin-bottom: 12px;
        border-left: 5px solid {LARANJA};
    }}

    .turno-nome {{
        color: #FFFFFF;
        font-size: 17px;
        font-weight: 800;
    }}

    .turno-horario {{
        color: {LARANJA_CLARO};
        font-size: 11px;
        font-weight: 700;
        margin-top: 2px;
    }}


    /* ========================================================
       CABEÇALHO DA TABELA
       ======================================================== */

    .cabecalho-tabela {{
        color: {CINZA};
        font-size: 10px;
        font-weight: 900;
        text-align: center;
        padding-bottom: 7px;
        border-bottom: 2px solid {CINZA_CLARO};
    }}

    .cabecalho-esquerda {{
        text-align: left;
    }}


    /* ========================================================
       OPERADOR
       ======================================================== */

    .nome-operador {{
        color: {AZUL};
        font-size: 12px;
        font-weight: 800;
        padding-top: 10px;
    }}

    .funcao-operador {{
        color: {CINZA};
        font-size: 10px;
        font-weight: 600;
        padding-top: 10px;
    }}


    /* ========================================================
       TRABALHO
       ======================================================== */

    .status-trabalho {{
        background-color: {AZUL};
        color: #FFFFFF;
        border-left: 4px solid {LARANJA};
        border-radius: 7px;
        padding: 7px 4px;
        margin-top: 5px;
        text-align: center;
        font-size: 10px;
        font-weight: 900;
    }}

    .horario-trabalho {{
        color: {LARANJA_CLARO};
        font-size: 9px;
        margin-top: 3px;
    }}


    /* ========================================================
       FOLGA
       ======================================================== */

    .status-folga {{
        background-color: #EAF3FB;
        color: {AZUL};
        border-left: 4px solid {AZUL_MEDIO};
        border-radius: 7px;
        padding: 7px 4px;
        margin-top: 5px;
        text-align: center;
        font-size: 10px;
        font-weight: 900;
    }}

    .descanso {{
        color: #718096;
        font-size: 9px;
        margin-top: 3px;
    }}


    /* ========================================================
       BOTÕES
       ======================================================== */

    .stButton > button {{
        border-radius: 7px !important;
        font-weight: 700 !important;
        border: 1px solid {CINZA_CLARO} !important;
        background-color: {BRANCO} !important;
        color: {AZUL} !important;
    }}

    .stButton > button:hover {{
        border-color: {LARANJA} !important;
        color: {AZUL} !important;
    }}


    /* ========================================================
       SELECTBOX
       ======================================================== */

    div[data-baseweb="select"] > div {{
        background-color: {BRANCO} !important;
        border-radius: 8px !important;
        border-color: {CINZA_CLARO} !important;
    }}

    div[data-baseweb="select"] > div:focus-within {{
        border-color: {AZUL_MEDIO} !important;
        box-shadow: 0 0 0 1px {AZUL_MEDIO} !important;
    }}


    /* ========================================================
       RADIO DE TURNO
       ======================================================== */

    div[role="radiogroup"] {{
        gap: 8px;
    }}

    div[role="radiogroup"] label {{
        background-color: {BRANCO};
        border: 1px solid {CINZA_CLARO};
        border-radius: 8px;
        padding: 8px 13px;
    }}


    /* ========================================================
       LOGIN
       ======================================================== */

    [data-testid="stExpander"] {{
        background-color: {BRANCO};
        border: 1px solid {CINZA_CLARO};
        border-radius: 10px;
    }}

    [data-testid="stExpander"] summary {{
        color: {AZUL};
        font-weight: 800;
    }}


    /* ========================================================
       RESPONSIVO
       ======================================================== */

    @media (max-width: 900px) {{

        .titulo-amazon {{
            font-size: 20px;
        }}

        .logo-amazon {{
            width: 42px;
            height: 42px;
            min-width: 42px;
            font-size: 23px;
        }}

        .metric-numero {{
            font-size: 21px;
        }}

    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# ESTADO DO LOGIN
# ============================================================

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False


# ============================================================
# FUNÇÕES DO BANCO
# ============================================================

def buscar_operadores():

    conn = conectar()

    dados = conn.execute(
        """
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
        """
    ).fetchall()

    conn.close()

    return dados


def cadastrar_operador(nome, funcao, turno):

    conn = conectar()

    conn.execute(
        """
        INSERT INTO operadores
        (nome, funcao, turno)
        VALUES (?, ?, ?)
        """,
        (
            nome,
            funcao,
            turno
        )
    )

    conn.commit()
    conn.close()


def remover_operador(operador_id):

    conn = conectar()

    conn.execute(
        """
        UPDATE operadores
        SET ativo = 0
        WHERE id = ?
        """,
        (operador_id,)
    )

    conn.commit()
    conn.close()


def buscar_status(operador_id, semana_id):

    conn = conectar()

    resultado = conn.execute(
        """
        SELECT
            sexta,
            sabado,
            domingo,
            segunda
        FROM escala
        WHERE operador_id = ?
        AND semana_id = ?
        """,
        (
            operador_id,
            semana_id
        )
    ).fetchone()

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

    existente = conn.execute(
        """
        SELECT id
        FROM escala
        WHERE operador_id = ?
        AND semana_id = ?
        """,
        (
            operador_id,
            semana_id
        )
    ).fetchone()

    if existente:

        conn.execute(
            """
            UPDATE escala
            SET
                sexta = ?,
                sabado = ?,
                domingo = ?,
                segunda = ?
            WHERE operador_id = ?
            AND semana_id = ?
            """,
            (
                sexta,
                sabado,
                domingo,
                segunda,
                operador_id,
                semana_id
            )
        )

    else:

        conn.execute(
            """
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
            """,
            (
                operador_id,
                semana_id,
                sexta,
                sabado,
                domingo,
                segunda
            )
        )

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
# TOPO
# ============================================================

st.markdown(
    """
    <div class="topo-amazon">

        <div class="logo-amazon">
            A
        </div>

        <div>
            <div class="titulo-amazon">
                Escala Amazon
            </div>

            <div class="subtitulo-amazon">
                Painel de Monitoramento Operacional
            </div>
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOGIN / GESTÃO
# ============================================================

with st.expander(
    "🔐 Gestão",
    expanded=False
):

    if not st.session_state.autenticado:

        st.markdown(
            "### Acesso administrativo"
        )

        col1, col2, col3 = st.columns(
            [1, 1, 0.6]
        )

        with col1:

            usuario = st.text_input(
                "Usuário",
                key="usuario_login"
            )

        with col2:

            senha = st.text_input(
                "Senha",
                type="password",
                key="senha_login"
            )

        with col3:

            st.write("")

            entrar = st.button(
                "Entrar",
                use_container_width=True
            )

        if entrar:

            if (
                usuario.strip().lower() == "admin"
                and senha == "Amazon123"
            ):

                st.session_state.autenticado = True

                st.rerun()

            else:

                st.error(
                    "Usuário ou senha incorretos."
                )

    else:

        st.success(
            "🟢 Modo gestão ativo"
        )

        tab_cadastro, tab_remocao, tab_sessao = st.tabs(
            [
                "➕ Cadastrar",
                "🗑️ Remover",
                "🚪 Sessão"
            ]
        )

        # ----------------------------------------------------
        # CADASTRO
        # ----------------------------------------------------

        with tab_cadastro:

            col1, col2, col3 = st.columns(3)

            with col1:

                novo_nome = st.text_input(
                    "Nome do operador",
                    key="novo_nome"
                )

            with col2:

                nova_funcao = st.text_input(
                    "Função",
                    key="nova_funcao"
                )

            with col3:

                novo_turno = st.selectbox(
                    "Turno",
                    ["T1", "T2", "T3"],
                    format_func=lambda x:
                        f"{NOMES_TURNOS[x]} — {HORARIOS[x]}",
                    key="novo_turno"
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
                        "Operador cadastrado com sucesso."
                    )

                    st.rerun()

                else:

                    st.warning(
                        "Preencha nome e função."
                    )

        # ----------------------------------------------------
        # REMOÇÃO
        # ----------------------------------------------------

        with tab_remocao:

            operadores_remocao = buscar_operadores()

            if operadores_remocao:

                opcoes_remocao = {
                    f"{x[1]} — {x[2]} — {x[3]}": x[0]
                    for x in operadores_remocao
                }

                selecionado = st.selectbox(
                    "Operador",
                    list(opcoes_remocao.keys()),
                    key="operador_remocao"
                )

                if st.button(
                    "Remover operador",
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

        # ----------------------------------------------------
        # SESSÃO
        # ----------------------------------------------------

        with tab_sessao:

            st.write(
                "Você está conectado como administrador."
            )

            if st.button(
                "Sair da gestão",
                use_container_width=True
            ):

                st.session_state.autenticado = False

                st.rerun()


# ============================================================
# TÍTULO DA PÁGINA
# ============================================================

st.markdown(
    """
    <div class="titulo-secao">
        Monitoramento Amazon
    </div>

    <div class="subtitulo-secao">
        Gestão de operadores e escala operacional
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PERÍODO
# ============================================================

col_periodo, col_espaco = st.columns(
    [2, 5]
)

with col_periodo:

    semana_labels = [
        semana["nome"]
        for semana in semanas
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
# CONTAGEM
# ============================================================

total = len(operadores)

t1 = sum(
    1 for operador in operadores
    if operador[3] == "T1"
)

t2 = sum(
    1 for operador in operadores
    if operador[3] == "T2"
)

t3 = sum(
    1 for operador in operadores
    if operador[3] == "T3"
)


# ============================================================
# MÉTRICAS
# ============================================================

m1, m2, m3, m4 = st.columns(4)


with m1:

    st.markdown(
        f"""
        <div class="metric-amazon metric-principal">

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
        <div class="metric-amazon metric-turno">

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
        <div class="metric-amazon metric-turno">

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
        <div class="metric-amazon metric-turno">

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
# SELEÇÃO DE TURNO
# ============================================================

st.write("")

st.markdown(
    """
    <div class="titulo-secao">
        Visualização da operação
    </div>

    <div class="subtitulo-secao">
        Selecione o turno que deseja acompanhar
    </div>
    """,
    unsafe_allow_html=True
)


turno_selecionado = st.radio(
    "Escolha o turno",
    ["T1", "T2", "T3"],
    format_func=lambda turno:
        f"{NOMES_TURNOS[turno]}  •  {HORARIOS[turno]}",
    horizontal=True,
    label_visibility="collapsed"
)


# ============================================================
# OPERADORES DO TURNO
# ============================================================

operadores_turno = [
    operador
    for operador in operadores
    if operador[3] == turno_selecionado
]


# ============================================================
# PAINEL DO TURNO
# ============================================================

st.markdown(
    f"""
    <div class="painel">

        <div class="painel-titulo">
            {NOMES_TURNOS[turno_selecionado]}
        </div>

        <div class="painel-subtitulo">
            {HORARIOS[turno_selecionado]}
            •
            {len(operadores_turno)} operadores escalados
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# BARRA DO TURNO
# ============================================================

st.markdown(
    f"""
    <div class="turno-barra">

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

cabecalho = st.columns(
    [
        2.5,
        1.8,
        1.7,
        1.7,
        1.7,
        1.7
    ]
)


cabecalho[0].markdown(
    """
    <div class="cabecalho-tabela cabecalho-esquerda">
        OPERADOR
    </div>
    """,
    unsafe_allow_html=True
)


cabecalho[1].markdown(
    """
    <div class="cabecalho-tabela cabecalho-esquerda">
        FUNÇÃO
    </div>
    """,
    unsafe_allow_html=True
)


for indice, (dia, _) in enumerate(
    DIAS,
    2
):

    cabecalho[indice].markdown(
        f"""
        <div class="cabecalho-tabela">

            {dia.upper()}

            <br>

            <span>
                ({semana[dia]})
            </span>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# ESCALA
# ============================================================

for operador in operadores_turno:

    operador_id = operador[0]
    nome = operador[1]
    funcao = operador[2]


    # --------------------------------------------------------
    # BUSCA STATUS
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # LINHA
    # --------------------------------------------------------

    linha = st.columns(
        [
            2.5,
            1.8,
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
        <div class="nome-operador">
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
        <div class="funcao-operador">
            {funcao}
        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # DIAS
    # --------------------------------------------------------

    for indice, (dia, _) in enumerate(
        DIAS,
        2
    ):

        valor = status_lista[
            indice - 2
        ]


        # ====================================================
        # TRABALHO
        # ====================================================

        if valor != "FOLGA":

            linha[indice].markdown(
                f"""
                <div class="status-trabalho">

                    TRABALHO

                    <div class="horario-trabalho">
                        {HORARIOS[turno_selecionado]}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


        # ====================================================
        # FOLGA
        # ====================================================

        else:

            linha[indice].markdown(
                """
                <div class="status-folga">

                    FOLGA

                    <div class="descanso">
                        Descanso
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


        # ====================================================
        # BOTÃO DE GESTÃO
        # ====================================================

        if st.session_state.autenticado:

            if valor == "FOLGA":

                novo_valor = HORARIOS[
                    turno_selecionado
                ]

            else:

                novo_valor = "FOLGA"


            if linha[indice].button(
                "Alternar",
                key=(
                    "alternar_"
                    + str(operador_id)
                    + "_"
                    + semana_id
                    + "_"
                    + dia
                ),
                use_container_width=True
            ):

                status_lista[
                    indice - 2
                ] = novo_valor


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
        f"Nenhum operador cadastrado no "
        f"{NOMES_TURNOS[turno_selecionado]}."
    )


# ============================================================
# RODAPÉ
# ============================================================

st.write("")

st.divider()

st.caption(
    "Escala Amazon • Painel de Monitoramento Operacional"
)
