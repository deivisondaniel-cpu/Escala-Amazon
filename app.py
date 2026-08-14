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
    initial_sidebar_state="expanded"
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
# ESTADOS DO SISTEMA
# ============================================================

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False


if "tema" not in st.session_state:
    st.session_state.tema = "Claro"


# ============================================================
# PALETA DOS TEMAS
# ============================================================

if st.session_state.tema == "Claro":

    CORES = {

        "fundo": "#FFFFFF",
        "fundo_secundario": "#F8FAFC",

        "texto": "#131921",
        "texto_secundario": "#64748B",

        "borda": "#E2E8F0",

        "card_metrica": "#FFFFFF",

        "card_folga": "#F1F5F9",
        "texto_folga": "#475569",
        "borda_folga": "#94A3B8",

        "header_input": "#FFFFFF",

        "sidebar": "#FFFFFF",
        "sidebar_texto": "#131921",

        "select_bg": "#FFFFFF",

        "sombra": "rgba(0,0,0,0.08)"
    }

else:

    CORES = {

        "fundo": "#0F172A",
        "fundo_secundario": "#111827",

        "texto": "#F8FAFC",
        "texto_secundario": "#CBD5E1",

        "borda": "#334155",

        "card_metrica": "#1E293B",

        "card_folga": "#1E293B",
        "texto_folga": "#CBD5E1",
        "borda_folga": "#64748B",

        "header_input": "#1E293B",

        "sidebar": "#111827",
        "sidebar_texto": "#F8FAFC",

        "select_bg": "#1E293B",

        "sombra": "rgba(0,0,0,0.30)"
    }


# ============================================================
# CSS
# ============================================================

st.markdown(
    f"""
<style>

/* ============================================================
   ELEMENTOS PADRÃO
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
   APLICAÇÃO
   ============================================================ */

.stApp {{
    background-color: {CORES["fundo"]};
    color: {CORES["texto"]};
}}

[data-testid="stAppViewContainer"] {{
    background-color: {CORES["fundo"]};
}}

[data-testid="stHeader"] {{
    background-color: transparent;
}}


/* ============================================================
   TÍTULO
   ============================================================ */

.titulo {{
    text-align: center;
    color: {CORES["texto"]};
    font-family: 'Segoe UI', sans-serif;
    font-size: 30px;
    font-weight: 800;

    margin-top: 35px;
    margin-bottom: 5px;
}}

.subtitulo {{
    text-align: center;
    color: #FF9900;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 25px;
}}


/* ============================================================
   CABEÇALHO DOS TURNOS
   ============================================================ */

.turno-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 28px;
    margin-bottom: 5px;
}}

.turno-titulo {{
    font-size: 21px;
    font-weight: 800;
    color: {CORES["texto"]};
}}

.turno-horario {{
    background: rgba(255,153,0,0.10);
    color: #D97706;
    border: 1px solid rgba(255,153,0,0.35);
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
}}


/* ============================================================
   CABEÇALHOS
   ============================================================ */

.header-col {{
    text-align: center;
    font-weight: 800;
    font-size: 12px;
    color: {CORES["texto_secundario"]};
    margin-bottom: 8px;
}}

.header-esquerda {{
    text-align: left;
}}


/* ============================================================
   OPERADOR
   ============================================================ */

.nome-operador {{
    padding-top: 9px;
    font-size: 13px;
    color: {CORES["texto"]};
}}

.funcao-operador {{
    padding-top: 9px;
    font-size: 11px;
    color: {CORES["texto_secundario"]};
}}


/* ============================================================
   CARD TRABALHO
   ============================================================ */

.card-trabalho {{
    background: linear-gradient(
        135deg,
        #263646,
        #1F2937
    );

    color: white;

    padding: 8px 5px;

    border-radius: 7px;

    text-align: center;

    font-weight: 700;

    font-size: 11px;

    border-left: 4px solid #FF9900;

    margin-bottom: 4px;

    box-shadow: 0 2px 5px {CORES["sombra"]};
}}

.sub-info {{
    color: #FFB84D;
    font-size: 10px;
    margin-top: 3px;
}}


/* ============================================================
   CARD FOLGA
   ============================================================ */

.card-folga {{
    background: {CORES["card_folga"]};

    color: {CORES["texto_folga"]};

    padding: 8px 5px;

    border-radius: 7px;

    text-align: center;

    font-weight: 800;

    font-size: 11px;

    border-left: 4px solid {CORES["borda_folga"]};

    margin-bottom: 4px;
}}

.sub-info-folga {{
    color: {CORES["borda_folga"]};
    font-size: 10px;
    margin-top: 3px;
}}


/* ============================================================
   SEPARADOR
   ============================================================ */

.separador {{
    border: 0;
    border-top: 1px solid {CORES["borda"]};
    margin-top: 2px;
    margin-bottom: 15px;
}}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {{
    background-color: {CORES["sidebar"]};
    border-right: 1px solid {CORES["borda"]};
}}

section[data-testid="stSidebar"] * {{
    color: {CORES["sidebar_texto"]};
}}

.sidebar-titulo {{
    color: #FF9900;
    font-size: 20px;
    font-weight: 800;
}}

.sidebar-status {{
    background: #ECFDF5;
    color: #047857 !important;
    padding: 8px;
    border-radius: 7px;
    font-size: 12px;
    font-weight: 700;
}}


/* ============================================================
   MÉTRICAS
   ============================================================ */

.metric-card {{
    background: {CORES["card_metrica"]};
    border: 1px solid {CORES["borda"]};
    border-radius: 10px;
    padding: 12px;
    text-align: center;
    box-shadow: 0 2px 6px {CORES["sombra"]};
}}

.metric-numero {{
    font-size: 22px;
    font-weight: 800;
    color: {CORES["texto"]};
}}

.metric-label {{
    font-size: 11px;
    color: {CORES["texto_secundario"]};
}}


/* ============================================================
   INPUTS / SELECTS
   ============================================================ */

div[data-baseweb="input"] {{
    background-color: {CORES["header_input"]};
}}

div[data-baseweb="select"] > div {{
    background-color: {CORES["select_bg"]};
}}

input {{
    color: {CORES["texto"]} !important;
}}


/* ============================================================
   BOTÕES
   ============================================================ */

.stButton > button {{
    border-radius: 7px;
    font-weight: 600;
}}


/* ============================================================
   FORMULÁRIO DE LOGIN
   ============================================================ */

[data-testid="stForm"] {{
    border: 1px solid {CORES["borda"]};
    border-radius: 10px;
    padding: 15px;
    background: {CORES["fundo_secundario"]};
}}


/* ============================================================
   CONTAINER PRINCIPAL
   ============================================================ */

.stMainBlockContainer {{
    padding-top: 18px !important;
    padding-bottom: 30px !important;
}}


/* ============================================================
   RESPONSIVIDADE
   ============================================================ */

@media (max-width: 800px) {{

    .titulo {{
        font-size: 24px;
        margin-top: 25px;
    }}

    .turno-titulo {{
        font-size: 18px;
    }}

    .turno-horario {{
        font-size: 10px;
    }}

    .metric-numero {{
        font-size: 18px;
    }}

}}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# FUNÇÕES DE BANCO
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
# DATAS
# ============================================================

def obter_semana(deslocamento=0):

    hoje = datetime.now()

    dias_para_sexta = (
        hoje.weekday() - 4
    ) % 7

    sexta = (
        hoje
        - timedelta(
            days=dias_para_sexta
        )
        + timedelta(
            weeks=deslocamento
        )
    )

    sabado = sexta + timedelta(
        days=1
    )

    domingo = sexta + timedelta(
        days=2
    )

    segunda = sexta + timedelta(
        days=3
    )

    return {

        "id":
            sexta.strftime(
                "%Y-%m-%d"
            ),

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

    st.markdown(
        "<div class='sidebar-titulo'>"
        "🔐 Gestão da Escala"
        "</div>",
        unsafe_allow_html=True
    )

    st.divider()


    # ========================================================
    # TEMA
    # ========================================================

    st.markdown(
        "### 🎨 Aparência"
    )

    tema_escolhido = st.radio(
        "Tema",
        [
            "Claro",
            "Escuro"
        ],
        horizontal=True,
        key="tema"
    )

    # Se o usuário mudou o tema,
    # recarrega a interface imediatamente.
    if tema_escolhido != st.session_state.tema:

        st.session_state.tema = tema_escolhido

        st.rerun()


    st.divider()


    # ========================================================
    # LOGIN
    # ========================================================

    if not st.session_state.autenticado:

        st.markdown(
            "### Acesso"
        )


        # ----------------------------------------------------
        # FORMULÁRIO
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # VALIDAÇÃO
        # ----------------------------------------------------

        if entrar:

            if (
                usuario.lower().strip()
                == "admin"

                and

                senha
                == "Amazon123"
            ):

                st.session_state.autenticado = True

                st.rerun()

            else:

                st.error(
                    "Usuário ou senha incorretos."
                )


    # ========================================================
    # MODO GESTÃO
    # ========================================================

    else:

        st.markdown(
            "<div class='sidebar-status'>"
            "🟢 Modo Gestão ativo"
            "</div>",
            unsafe_allow_html=True
        )

        st.divider()


        # ====================================================
        # CADASTRAR
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
            [
                "T1",
                "T2",
                "T3"
            ],
            format_func=lambda x:
                (
                    f"{NOMES_TURNOS[x]} "
                    f"— {HORARIOS[x]}"
                )
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
                    f"{novo_nome.strip().upper()} "
                    "cadastrado!"
                )

                st.rerun()

            else:

                st.warning(
                    "Preencha nome e função."
                )


        st.divider()


        # ====================================================
        # REMOVER
        # ====================================================

        st.markdown(
            "### ❌ Remover operador"
        )

        operadores = buscar_operadores()


        if operadores:

            opcoes_remocao = {
                f"{x[1]} — {x[2]}": x[0]
                for x in operadores
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
                    opcoes_remocao[
                        selecionado
                    ]
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
            "🚪 Sair",
            use_container_width=True
        ):

            st.session_state.autenticado = False

            st.rerun()


# ============================================================
# TÍTULO PRINCIPAL
# ============================================================

st.markdown(
    "<div class='titulo'>"
    "Escala Amazon"
    "</div>",
    unsafe_allow_html=True
)


st.markdown(
    "<div class='subtitulo'>"
    "Monitoramento Amazon"
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
    x
    for x in operadores
    if x[3] == "T1"
])


t2 = len([
    x
    for x in operadores
    if x[3] == "T2"
])


t3 = len([
    x
    for x in operadores
    if x[3] == "T3"
])


m1, m2, m3, m4 = st.columns(
    4
)


with m1:

    st.markdown(
        f"""
        <div class='metric-card'>

            <div class='metric-numero'>
                {total}
            </div>

            <div class='metric-label'>
                OPERADORES
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with m2:

    st.markdown(
        f"""
        <div class='metric-card'>

            <div class='metric-numero'>
                {t1}
            </div>

            <div class='metric-label'>
                T1 • 07h às 15h
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with m3:

    st.markdown(
        f"""
        <div class='metric-card'>

            <div class='metric-numero'>
                {t2}
            </div>

            <div class='metric-label'>
                T2 • 15h às 23h
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with m4:

    st.markdown(
        f"""
        <div class='metric-card'>

            <div class='metric-numero'>
                {t3}
            </div>

            <div class='metric-label'>
                T3 • 23h às 07h
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# ESPAÇO
# ============================================================

st.write("")


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

for turno in [
    "T1",
    "T2",
    "T3"
]:

    operadores_turno = [
        x
        for x in operadores
        if x[3] == turno
    ]


    if not operadores_turno:
        continue


    # ========================================================
    # CABEÇALHO DO TURNO
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
        "<div class='header-col "
        "header-esquerda'>"
        "OPERADOR"
        "</div>",
        unsafe_allow_html=True
    )


    headers[1].markdown(
        "<div class='header-col "
        "header-esquerda'>"
        "FUNÇÃO"
        "</div>",
        unsafe_allow_html=True
    )


    for i, (
        dia,
        _
    ) in enumerate(
        DIAS,
        2
    ):

        headers[i].markdown(
            f"""
            <div class='header-col'>
                {dia.upper()}
                ({semana[dia]})
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
        # PRIMEIRO ACESSO DA SEMANA
        # ====================================================

        if status is None:

            horario = HORARIOS[
                turno
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

        status_lista = list(
            status
        )


        for i, (
            dia,
            _
        ) in enumerate(
            DIAS,
            2
        ):

            valor = status_lista[
                i - 2
            ]


            # -----------------------------------------------
            # TRABALHO
            # -----------------------------------------------

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


            # -----------------------------------------------
            # FOLGA
            # -----------------------------------------------

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


            # -----------------------------------------------
            # BOTÃO GESTÃO
            # -----------------------------------------------

            if st.session_state.autenticado:

                if valor == "FOLGA":

                    novo_valor = HORARIOS[
                        turno
                    ]

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


    st.write("")


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.caption(
    "Escala Amazon • Sistema independente de gestão de escala"
)
