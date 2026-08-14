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
# CONFIGURAÇÕES DO SISTEMA
# ============================================================

BANCO = "escala_amazon.db"

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

DIAS = [
    ("Sexta", "sexta"),
    ("Sábado", "sabado"),
    ("Domingo", "domingo"),
    ("Segunda", "segunda")
]


# ============================================================
# BANCO DE DADOS
# ============================================================

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
# CSS
# ============================================================

st.markdown("""
<style>

/* ============================================================
   BASE
   ============================================================ */

html, body, [class*="css"] {
    font-family: "Segoe UI", Arial, sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: #0F1720;
}

[data-testid="stHeader"] {
    background: transparent;
}

.stMainBlockContainer {
    max-width: 1500px;
    padding-top: 25px !important;
    padding-bottom: 40px !important;
}


/* ============================================================
   ESCONDER ELEMENTOS DESNECESSÁRIOS
   ============================================================ */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {
    background: #172231;
    border-right: 1px solid #2B3A4D;
}

section[data-testid="stSidebar"] * {
    color: #FFFFFF;
}


/* ============================================================
   TOPO
   ============================================================ */

.topo {
    background: linear-gradient(
        135deg,
        #172231 0%,
        #1E2D3F 100%
    );

    border: 1px solid #2B3A4D;
    border-radius: 16px;

    padding: 20px 24px;

    margin-bottom: 20px;

    display: flex;
    align-items: center;
    justify-content: space-between;

    box-shadow: 0 8px 25px rgba(0,0,0,0.20);
}

.topo-esquerda {
    display: flex;
    align-items: center;
    gap: 15px;
}

.logo-amazon {
    width: 48px;
    height: 48px;

    border-radius: 12px;

    background: #FF9900;

    color: #172231;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 28px;
    font-weight: 900;

    box-shadow: 0 5px 15px rgba(255,153,0,0.25);
}

.topo-titulo {
    color: #FFFFFF;

    font-size: 26px;
    font-weight: 800;

    line-height: 1.1;
}

.topo-subtitulo {
    color: #9FB0C2;

    font-size: 12px;

    margin-top: 4px;
}


/* ============================================================
   STATUS
   ============================================================ */

.status-online {
    background: #132A25;

    border: 1px solid #225E4F;

    color: #54D6B1;

    padding: 8px 13px;

    border-radius: 20px;

    font-size: 11px;

    font-weight: 800;
}


/* ============================================================
   SEÇÃO
   ============================================================ */

.section-title {
    color: #FFFFFF;

    font-size: 18px;

    font-weight: 800;

    margin-top: 15px;
    margin-bottom: 4px;
}

.section-subtitle {
    color: #8799AD;

    font-size: 12px;

    margin-bottom: 15px;
}


/* ============================================================
   MÉTRICAS
   ============================================================ */

.metric-card {
    background: #172231;

    border: 1px solid #2B3A4D;

    border-radius: 13px;

    padding: 16px;

    min-height: 88px;

    box-shadow: 0 5px 15px rgba(0,0,0,0.15);
}

.metric-card-orange {
    border-top: 3px solid #FF9900;
}

.metric-card-blue {
    border-top: 3px solid #146EB4;
}

.metric-number {
    color: #FFFFFF;

    font-size: 25px;

    font-weight: 850;

    line-height: 1;
}

.metric-label {
    color: #899AAC;

    font-size: 10px;

    font-weight: 700;

    margin-top: 7px;

    letter-spacing: .4px;
}


/* ============================================================
   CONTROLE DE VISUALIZAÇÃO
   ============================================================ */

.controle {
    background: #172231;

    border: 1px solid #2B3A4D;

    border-radius: 14px;

    padding: 16px 18px;

    margin-top: 20px;
    margin-bottom: 18px;
}

.controle-label {
    color: #FF9900;

    font-size: 10px;

    font-weight: 800;

    letter-spacing: .8px;

    margin-bottom: 5px;
}


/* ============================================================
   TURNO
   ============================================================ */

.turno-box {
    background: linear-gradient(
        135deg,
        #172231,
        #1D2B3C
    );

    border: 1px solid #2B3A4D;

    border-left: 5px solid #FF9900;

    border-radius: 13px;

    padding: 16px 20px;

    margin-top: 12px;
    margin-bottom: 12px;

    display: flex;

    align-items: center;

    justify-content: space-between;

    box-shadow: 0 7px 20px rgba(0,0,0,0.18);
}

.turno-nome {
    color: #FFFFFF;

    font-size: 20px;

    font-weight: 850;
}

.turno-info {
    color: #8EA1B5;

    font-size: 11px;

    margin-top: 3px;
}

.turno-horario {
    background: #14324D;

    border: 1px solid #225B88;

    color: #62B8F5;

    padding: 7px 12px;

    border-radius: 20px;

    font-size: 11px;

    font-weight: 800;
}


/* ============================================================
   CABEÇALHO DA ESCALA
   ============================================================ */

.grid-header {
    display: grid;

    grid-template-columns:
        2.2fr
        1.5fr
        1fr
        1fr
        1fr
        1fr;

    gap: 8px;

    padding: 10px 8px;

    color: #75889C;

    font-size: 10px;

    font-weight: 800;

    letter-spacing: .5px;

    text-align: center;
}

.grid-header .left {
    text-align: left;
}


/* ============================================================
   LINHA DA ESCALA
   ============================================================ */

.operador-row {
    display: grid;

    grid-template-columns:
        2.2fr
        1.5fr
        1fr
        1fr
        1fr
        1fr;

    gap: 8px;

    align-items: center;

    background: #172231;

    border: 1px solid #263648;

    border-radius: 10px;

    padding: 8px;

    margin-bottom: 7px;

    transition: .15s;
}

.operador-row:hover {
    border-color: #3B5065;
}


/* ============================================================
   OPERADOR
   ============================================================ */

.operador-nome {
    color: #FFFFFF;

    font-size: 12px;

    font-weight: 750;
}

.operador-funcao {
    color: #8497AA;

    font-size: 10px;

    margin-top: 2px;
}


/* ============================================================
   STATUS TRABALHO
   ============================================================ */

.status-trabalho {
    background: #202E3C;

    border: 1px solid #34485C;

    border-left: 3px solid #FF9900;

    border-radius: 7px;

    padding: 7px 3px;

    text-align: center;

    color: #FFFFFF;

    font-size: 9px;

    font-weight: 800;
}

.status-trabalho-hora {
    color: #FFB84D;

    font-size: 8px;

    margin-top: 3px;
}


/* ============================================================
   STATUS FOLGA
   ============================================================ */

.status-folga {
    background: #162A3B;

    border: 1px solid #245274;

    border-left: 3px solid #146EB4;

    border-radius: 7px;

    padding: 7px 3px;

    text-align: center;

    color: #8CC9F5;

    font-size: 9px;

    font-weight: 800;
}

.status-folga-info {
    color: #66859E;

    font-size: 8px;

    margin-top: 3px;
}


/* ============================================================
   BOTÕES
   ============================================================ */

.stButton > button {
    background: #202E3C;

    color: #D8E1EA;

    border: 1px solid #35495D;

    border-radius: 7px;

    font-weight: 700;

    font-size: 10px;
}

.stButton > button:hover {
    border-color: #FF9900;

    color: #FF9900;

    background: #243342;
}


/* ============================================================
   SELECTBOX
   ============================================================ */

div[data-baseweb="select"] > div {
    background: #172231 !important;

    border: 1px solid #35495D !important;

    border-radius: 8px !important;

    color: #FFFFFF !important;
}

div[data-baseweb="select"] span {
    color: #FFFFFF !important;
}


/* ============================================================
   INPUTS
   ============================================================ */

div[data-baseweb="input"] > div {
    background: #172231 !important;

    border-color: #35495D !important;
}

div[data-baseweb="input"] input {
    color: #FFFFFF !important;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

.sidebar-title {
    color: #FF9900;

    font-size: 18px;

    font-weight: 850;

    margin-bottom: 15px;
}

.sidebar-box {
    background: #1D2B3C;

    border: 1px solid #34485C;

    border-radius: 9px;

    padding: 10px;

    color: #9FB0C2;

    font-size: 11px;
}


/* ============================================================
   LOGIN
   ============================================================ */

.login-box {
    background: #1D2B3C;

    border: 1px solid #34485C;

    border-radius: 12px;

    padding: 14px;

    margin-bottom: 15px;
}

.login-title {
    color: #FFFFFF;

    font-size: 14px;

    font-weight: 800;

    margin-bottom: 10px;
}


/* ============================================================
   ALERTAS
   ============================================================ */

div[data-testid="stAlert"] {
    border-radius: 8px;
}


/* ============================================================
   DIVISOR
   ============================================================ */

hr {
    border-color: #263648 !important;
}


/* ============================================================
   RODAPÉ
   ============================================================ */

.rodape {
    text-align: center;

    color: #617386;

    font-size: 10px;

    margin-top: 25px;
}


/* ============================================================
   RESPONSIVO
   ============================================================ */

@media (max-width: 900px) {

    .topo {
        padding: 16px;
    }

    .topo-titulo {
        font-size: 21px;
    }

    .grid-header,
    .operador-row {
        grid-template-columns:
            1.8fr
            1.2fr
            1fr
            1fr
            1fr
            1fr;
    }

}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSÃO
# ============================================================

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False


# ============================================================
# FUNÇÕES DE OPERADORES
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
                ELSE 4
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


# ============================================================
# FUNÇÕES DE ESCALA
# ============================================================

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
            f"{sexta.strftime('%d/%m')}"
            f" até "
            f"{segunda.strftime('%d/%m')} ",

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
# SIDEBAR COMPACTA
# ============================================================

with st.sidebar:

    if not st.session_state.autenticado:

        st.markdown(
            """
            <div class="sidebar-title">
                🔐 Login
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="sidebar-box">
                Acesso restrito à gestão da escala.
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        usuario = st.text_input(
            "Usuário",
            key="login_usuario"
        )

        senha = st.text_input(
            "Senha",
            type="password",
            key="login_senha"
        )

        if st.button(
            "Entrar",
            use_container_width=True
        ):

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

        st.markdown(
            """
            <div class="sidebar-title">
                ⚙️ Gestão
            </div>
            """,
            unsafe_allow_html=True
        )

        st.success(
            "Modo gestão ativo."
        )

        st.divider()

        # ----------------------------------------------------
        # NOVO OPERADOR
        # ----------------------------------------------------

        st.markdown("### Novo operador")

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
                    "Operador cadastrado."
                )

                st.rerun()

            else:

                st.warning(
                    "Preencha nome e função."
                )

        st.divider()

        # ----------------------------------------------------
        # REMOVER
        # ----------------------------------------------------

        st.markdown("### Remover operador")

        operadores_sidebar = buscar_operadores()

        if operadores_sidebar:

            opcoes = {
                f"{x[1]} — {x[2]}": x[0]
                for x in operadores_sidebar
            }

            escolhido = st.selectbox(
                "Operador",
                list(opcoes.keys())
            )

            if st.button(
                "Remover operador",
                use_container_width=True
            ):

                remover_operador(
                    opcoes[escolhido]
                )

                st.success(
                    "Operador removido."
                )

                st.rerun()

        st.divider()

        if st.button(
            "🚪 Sair",
            use_container_width=True
        ):

            st.session_state.autenticado = False

            st.rerun()


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    """
    <div class="topo">

        <div class="topo-esquerda">

            <div class="logo-amazon">
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

        <div class="status-online">
            ● SISTEMA ONLINE
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# OPERADORES
# ============================================================

operadores = buscar_operadores()


# ============================================================
# PERÍODO
# ============================================================

st.markdown(
    """
    <div class="section-title">
        Monitoramento Amazon
    </div>

    <div class="section-subtitle">
        Gestão de operadores e escala operacional
    </div>
    """,
    unsafe_allow_html=True
)


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
    semana_labels.index(semana_escolhida)
]

semana_id = semana["id"]


# ============================================================
# MÉTRICAS
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


m1, m2, m3, m4 = st.columns(4)


with m1:

    st.markdown(
        f"""
        <div class="metric-card metric-card-orange">

            <div class="metric-number">
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
        <div class="metric-card metric-card-blue">

            <div class="metric-number">
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
        <div class="metric-card metric-card-blue">

            <div class="metric-number">
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
        <div class="metric-card metric-card-blue">

            <div class="metric-number">
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
# SELEÇÃO DO TURNO
# ============================================================

st.markdown(
    """
    <div class="controle">

        <div class="controle-label">
            VISUALIZAÇÃO DA OPERAÇÃO
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


turno_selecionado = st.radio(
    "Selecione o turno",
    ["T1", "T2", "T3"],
    format_func=lambda x:
        f"{NOMES_TURNOS[x]}  •  {HORARIOS[x]}",
    horizontal=True,
    label_visibility="collapsed"
)


# ============================================================
# FILTRO DO TURNO
# ============================================================

operadores_turno = [
    operador
    for operador in operadores
    if operador[3] == turno_selecionado
]


# ============================================================
# CABEÇALHO DO TURNO
# ============================================================

st.markdown(
    f"""
    <div class="turno-box">

        <div>

            <div class="turno-nome">
                🕒 {NOMES_TURNOS[turno_selecionado]}
            </div>

            <div class="turno-info">
                {len(operadores_turno)} operadores escalados
            </div>

        </div>

        <div class="turno-horario">
            {HORARIOS[turno_selecionado]}
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CABEÇALHO DA TABELA
# ============================================================

st.markdown(
    f"""
    <div class="grid-header">

        <div class="left">
            OPERADOR
        </div>

        <div class="left">
            FUNÇÃO
        </div>

        <div>
            SEXTA<br>
            ({semana["Sexta"]})
        </div>

        <div>
            SÁBADO<br>
            ({semana["Sábado"]})
        </div>

        <div>
            DOMINGO<br>
            ({semana["Domingo"]})
        </div>

        <div>
            SEGUNDA<br>
            ({semana["Segunda"]})
        </div>

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

    status = buscar_status(
        operador_id,
        semana_id
    )


    # --------------------------------------------------------
    # PRIMEIRO ACESSO
    # --------------------------------------------------------

    if status is None:

        horario = HORARIOS[turno_selecionado]

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

    colunas = st.columns(
        [
            2.2,
            1.5,
            1,
            1,
            1,
            1
        ]
    )


    # --------------------------------------------------------
    # OPERADOR
    # --------------------------------------------------------

    with colunas[0]:

        st.markdown(
            f"""
            <div class="operador-nome">
                {nome}
            </div>

            <div class="operador-funcao">
                {funcao}
            </div>
            """,
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # FUNÇÃO
    # --------------------------------------------------------

    with colunas[1]:

        st.markdown(
            f"""
            <div class="operador-funcao">
                {funcao}
            </div>
            """,
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # DIAS
    # --------------------------------------------------------

    for indice in range(4):

        valor = status_lista[indice]

        with colunas[indice + 2]:

            if valor == "FOLGA":

                st.markdown(
                    """
                    <div class="status-folga">

                        FOLGA

                        <div class="status-folga-info">
                            Descanso
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    f"""
                    <div class="status-trabalho">

                        TRABALHO

                        <div class="status-trabalho-hora">
                            {HORARIOS[turno_selecionado]}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


    # --------------------------------------------------------
    # BOTÕES DE GESTÃO
    # --------------------------------------------------------

    if st.session_state.autenticado:

        botoes = st.columns(6)

        botoes[0].write("")

        botoes[1].write("")

        for indice in range(4):

            with botoes[indice + 2]:

                dia_nome = DIAS[indice][0]

                if status_lista[indice] == "FOLGA":

                    texto_botao = "Trabalhar"

                    novo_valor = HORARIOS[
                        turno_selecionado
                    ]

                else:

                    texto_botao = "Folga"

                    novo_valor = "FOLGA"


                if st.button(
                    texto_botao,
                    key=(
                        f"btn_"
                        f"{operador_id}_"
                        f"{semana_id}_"
                        f"{dia_nome}"
                    ),
                    use_container_width=True
                ):

                    status_lista[indice] = novo_valor

                    salvar_status(
                        operador_id,
                        semana_id,
                        *status_lista
                    )

                    st.rerun()


# ============================================================
# CASO NÃO EXISTAM OPERADORES
# ============================================================

if not operadores_turno:

    st.info(
        "Nenhum operador cadastrado neste turno."
    )


# ============================================================
# RODAPÉ
# ============================================================

st.markdown(
    """
    <div class="rodape">
        Escala Amazon • Painel de Monitoramento Operacional
    </div>
    """,
    unsafe_allow_html=True
)
