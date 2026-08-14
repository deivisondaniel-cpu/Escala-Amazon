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
# BANCO
# ============================================================

BANCO = "escala_amazon.db"


def conectar():
    return sqlite3.connect(BANCO, check_same_thread=False)


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
# CONFIGURAÇÕES DOS TURNOS
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
# ESTADO DA SESSÃO
# ============================================================

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "turno_selecionado" not in st.session_state:
    st.session_state.turno_selecionado = "T1"


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

/* ============================================================
   IDENTIDADE AMAZON
   ============================================================

   AZUL PRINCIPAL: #232F3E
   AZUL:           #146EB4
   LARANJA:        #FF9900

   ============================================================ */


/* ============================================================
   LIMPEZA STREAMLIT
   ============================================================ */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

.stDecoration {
    display: none !important;
}


/* ============================================================
   FUNDO
   ============================================================ */

[data-testid="stAppViewContainer"] {
    background: #F3F6F9;
}

[data-testid="stHeader"] {
    background: transparent;
}


/* ============================================================
   CONTAINER
   ============================================================ */

.stMainBlockContainer {
    max-width: 1450px;
    padding-top: 22px !important;
    padding-bottom: 35px !important;
}


/* ============================================================
   TOPO
   ============================================================ */

.topo {
    background: #232F3E;
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 18px;

    display: flex;
    align-items: center;
    justify-content: space-between;

    box-shadow: 0 4px 14px rgba(35,47,62,0.12);

    border-bottom: 4px solid #FF9900;
}

.topo-esquerda {
    display: flex;
    align-items: center;
    gap: 13px;
}

.logo-amazon {
    width: 42px;
    height: 42px;

    background: #FF9900;
    color: #232F3E;

    border-radius: 9px;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 23px;
    font-weight: 900;
}

.topo-titulo {
    color: white;
    font-size: 21px;
    font-weight: 800;
    line-height: 1.1;
}

.topo-subtitulo {
    color: #B9C7D6;
    font-size: 11px;
    margin-top: 4px;
}


/* ============================================================
   BOTÃO DE GESTÃO
   ============================================================ */

div[data-testid="stPopover"] button {
    border-radius: 8px !important;
    font-weight: 800 !important;
}


/* ============================================================
   TÍTULO
   ============================================================ */

.pagina-titulo {
    color: #232F3E;
    font-size: 26px;
    font-weight: 800;
    margin-top: 6px;
    margin-bottom: 2px;
}

.pagina-subtitulo {
    color: #617184;
    font-size: 12px;
    margin-bottom: 18px;
}


/* ============================================================
   SELETOR DE SEMANA
   ============================================================ */

.seletor-label {
    color: #232F3E;
    font-size: 12px;
    font-weight: 800;
    margin-bottom: 4px;
}


/* ============================================================
   MÉTRICAS
   ============================================================ */

.metric-card {
    background: white;

    border: 1px solid #D7DEE7;
    border-top: 4px solid #146EB4;

    border-radius: 10px;

    padding: 13px 10px;

    text-align: center;

    min-height: 82px;

    box-shadow: 0 2px 8px rgba(35,47,62,0.05);
}

.metric-card.principal {
    border-top-color: #FF9900;
}

.metric-numero {
    color: #232F3E;
    font-size: 23px;
    font-weight: 900;
    line-height: 1;
}

.metric-label {
    color: #617184;
    font-size: 10px;
    font-weight: 800;
    margin-top: 6px;
}


/* ============================================================
   SELETOR DE TURNOS
   ============================================================ */

.turno-menu {
    background: white;

    border: 1px solid #D7DEE7;
    border-radius: 11px;

    padding: 10px 14px 5px 14px;

    margin-top: 18px;
    margin-bottom: 14px;

    box-shadow: 0 2px 8px rgba(35,47,62,0.05);
}

.turno-menu-titulo {
    color: #617184;
    font-size: 10px;
    font-weight: 800;
    margin-bottom: 2px;
}


/* Radio horizontal */

div[role="radiogroup"] {
    gap: 8px !important;
}

div[role="radiogroup"] label {
    background: #F3F6F9;
    border: 1px solid #D7DEE7;
    border-radius: 8px;
    padding: 7px 15px !important;
    min-width: 130px;
    justify-content: center;
}

div[role="radiogroup"] label:hover {
    border-color: #146EB4;
}

div[role="radiogroup"] label[data-checked="true"] {
    background: #232F3E;
    border-color: #FF9900;
}


/* ============================================================
   CABEÇALHO DO TURNO
   ============================================================ */

.turno-header {
    background: #FFFFFF;

    border-radius: 11px;

    padding: 12px 16px;

    margin-top: 8px;
    margin-bottom: 10px;

    border-left: 5px solid #FF9900;

    box-shadow: 0 2px 8px rgba(35,47,62,0.06);

    display: flex;
    align-items: center;
    gap: 12px;
}

.turno-titulo {
    color: #232F3E;
    font-size: 19px;
    font-weight: 900;
}

.turno-horario {
    background: #EAF3FB;

    color: #146EB4;

    border: 1px solid #B9D7EE;

    padding: 4px 11px;

    border-radius: 20px;

    font-size: 11px;
    font-weight: 800;
}


/* ============================================================
   CABEÇALHO DA TABELA
   ============================================================ */

.header-col {
    color: #617184;

    font-size: 10px;
    font-weight: 900;

    text-align: center;

    padding-bottom: 5px;
}

.header-esquerda {
    text-align: left;
}


/* ============================================================
   LINHA DO OPERADOR
   ============================================================ */

.linha-operador {
    background: #FFFFFF;

    border: 1px solid #E1E7EE;

    border-radius: 9px;

    padding: 4px 0;

    margin-bottom: 7px;

    box-shadow: 0 1px 5px rgba(35,47,62,0.035);
}


/* ============================================================
   NOME
   ============================================================ */

.nome-operador {
    color: #232F3E;

    font-size: 12px;

    font-weight: 800;

    padding-top: 10px;
    padding-left: 5px;
}

.funcao-operador {
    color: #617184;

    font-size: 10px;

    font-weight: 600;

    padding-top: 10px;
}


/* ============================================================
   CARD TRABALHO
   ============================================================ */

.card-trabalho {
    background: #232F3E;

    color: #FFFFFF;

    border-left: 4px solid #FF9900;

    border-radius: 7px;

    padding: 7px 4px;

    min-height: 42px;

    text-align: center;

    font-size: 10px;

    font-weight: 900;

    display: flex;
    flex-direction: column;
    justify-content: center;

    box-shadow: 0 2px 5px rgba(35,47,62,0.10);
}

.sub-info {
    color: #FFB84D;

    font-size: 9px;

    margin-top: 3px;

    font-weight: 700;
}


/* ============================================================
   CARD FOLGA
   ============================================================ */

.card-folga {
    background: #EAF3FB;

    color: #232F3E;

    border-left: 4px solid #146EB4;

    border-radius: 7px;

    padding: 7px 4px;

    min-height: 42px;

    text-align: center;

    font-size: 10px;

    font-weight: 900;

    display: flex;
    flex-direction: column;
    justify-content: center;

    box-shadow: 0 2px 5px rgba(20,110,180,0.06);
}

.sub-info-folga {
    color: #6B8196;

    font-size: 9px;

    margin-top: 3px;
}


/* ============================================================
   BOTÕES DA ESCALA
   ============================================================ */

.stButton > button {
    border-radius: 7px !important;

    font-weight: 700 !important;

    border: 1px solid #D7DEE7 !important;

    min-height: 28px !important;

    font-size: 10px !important;
}

.stButton > button:hover {
    border-color: #FF9900 !important;

    color: #232F3E !important;
}


/* ============================================================
   ÁREA ADMINISTRATIVA
   ============================================================ */

.admin-box {
    background: #F3F6F9;

    border: 1px solid #D7DEE7;

    border-radius: 9px;

    padding: 10px;

    margin-bottom: 10px;
}

.admin-status {
    background: #EAF3FB;

    border-left: 4px solid #FF9900;

    color: #146EB4;

    border-radius: 6px;

    padding: 8px;

    font-size: 11px;

    font-weight: 800;
}


/* ============================================================
   POPOVER
   ============================================================ */

div[data-baseweb="popover"] {
    border-radius: 12px !important;
}

div[data-baseweb="popover"] > div {
    border-radius: 12px !important;
}


/* ============================================================
   INPUTS
   ============================================================ */

input {
    border-radius: 7px !important;
}


/* ============================================================
   DIVISORES
   ============================================================ */

hr {
    border-color: #D7DEE7 !important;
}


/* ============================================================
   RODAPÉ
   ============================================================ */

.rodape {
    text-align: center;

    color: #8A98A8;

    font-size: 10px;

    padding-top: 10px;
}


/* ============================================================
   RESPONSIVO
   ============================================================ */

@media (max-width: 900px) {

    .topo-titulo {
        font-size: 17px;
    }

    .pagina-titulo {
        font-size: 22px;
    }

    div[role="radiogroup"] label {
        min-width: 90px;
        padding: 7px 8px !important;
    }

    .turno-titulo {
        font-size: 16px;
    }

}

</style>
""", unsafe_allow_html=True)


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
# DATAS
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
            f"até {segunda.strftime('%d/%m')}"
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
# OPERADORES
# ============================================================

operadores = buscar_operadores()


# ============================================================
# TOPO DO SISTEMA
# ============================================================

topo_col1, topo_col2 = st.columns([7, 1.5])


with topo_col1:

    st.markdown(
        """
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
        """,
        unsafe_allow_html=True
    )


with topo_col2:

    # ========================================================
    # LOGIN COMPACTO
    # ========================================================

    with st.popover(
        "🟢 Gestão" if st.session_state.autenticado
        else "🔐 Gestão",
        use_container_width=True
    ):

        if not st.session_state.autenticado:

            st.markdown("### 🔐 Acesso administrativo")

            st.caption(
                "Entre para alterar operadores e escala."
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
                    usuario.lower().strip() == "admin"
                    and senha == "Amazon123"
                ):

                    st.session_state.autenticado = True

                    st.rerun()

                else:

                    st.error(
                        "Usuário ou senha incorretos."
                    )

        else:

            st.markdown("### 🟢 Gestão ativa")

            st.success(
                "Você possui acesso para alterar a escala."
            )

            st.divider()

            # =================================================
            # NOVO OPERADOR
            # =================================================

            st.markdown("#### ➕ Novo operador")

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
                    f"{NOMES_TURNOS[x]} — {HORARIOS[x]}",
                key="novo_turno"
            )

            if st.button(
                "Cadastrar operador",
                use_container_width=True,
                key="cadastrar"
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
                        "Operador cadastrado!"
                    )

                    st.rerun()

                else:

                    st.warning(
                        "Preencha nome e função."
                    )

            st.divider()

            # =================================================
            # REMOVER OPERADOR
            # =================================================

            st.markdown("#### ❌ Remover operador")

            if operadores:

                opcoes_remocao = {
                    f"{x[1]} — {x[2]}": x[0]
                    for x in operadores
                }

                selecionado = st.selectbox(
                    "Operador",
                    list(opcoes_remocao.keys()),
                    key="remover_operador"
                )

                if st.button(
                    "Remover operador",
                    use_container_width=True,
                    key="remover"
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

            # =================================================
            # SAIR
            # =================================================

            if st.button(
                "🚪 Encerrar gestão",
                use_container_width=True,
                key="logout"
            ):

                st.session_state.autenticado = False

                st.rerun()


# ============================================================
# TÍTULO DA PÁGINA
# ============================================================

st.markdown(
    """
    <div class="pagina-titulo">
        Monitoramento Amazon
    </div>

    <div class="pagina-subtitulo">
        Gestão de operadores e escala operacional
    </div>
    """,
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
    semana_labels.index(semana_escolhida)
]

semana_id = semana["id"]


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


m1, m2, m3, m4 = st.columns(4)


with m1:

    st.markdown(
        f"""
        <div class="metric-card principal">

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
    """
    <div class="turno-menu">
        <div class="turno-menu-titulo">
            VISUALIZAÇÃO DA OPERAÇÃO
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


turno_selecionado = st.radio(
    "Selecione o turno",
    options=["T1", "T2", "T3"],
    index=["T1", "T2", "T3"].index(
        st.session_state.turno_selecionado
    ),
    format_func=lambda x:
        f"{NOMES_TURNOS[x]}  •  {HORARIOS[x]}",
    horizontal=True,
    label_visibility="collapsed"
)


st.session_state.turno_selecionado = turno_selecionado


# ============================================================
# OPERADORES DO TURNO SELECIONADO
# ============================================================

operadores_turno = [
    x for x in operadores
    if x[3] == turno_selecionado
]


# ============================================================
# CABEÇALHO DO TURNO
# ============================================================

st.markdown(
    f"""
    <div class="turno-header">

        <div class="turno-titulo">
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
# CABEÇALHO DA TABELA
# ============================================================

if operadores_turno:

    headers = st.columns(
        [
            2.5,
            1.7,
            1.8,
            1.8,
            1.8,
            1.8
        ]
    )

    headers[0].markdown(
        """
        <div class="header-col header-esquerda">
            OPERADOR
        </div>
        """,
        unsafe_allow_html=True
    )

    headers[1].markdown(
        """
        <div class="header-col header-esquerda">
            FUNÇÃO
        </div>
        """,
        unsafe_allow_html=True
    )

    for i, (dia, _) in enumerate(DIAS, 2):

        headers[i].markdown(
            f"""
            <div class="header-col">
                {dia.upper()}<br>
                ({semana[dia]})
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


    # ========================================================
    # PRIMEIRO ACESSO DA SEMANA
    # ========================================================

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


    # ========================================================
    # LINHA
    # ========================================================

    linha = st.columns(
        [
            2.5,
            1.7,
            1.8,
            1.8,
            1.8,
            1.8
        ]
    )


    # ========================================================
    # OPERADOR
    # ========================================================

    linha[0].markdown(
        f"""
        <div class="nome-operador">
            {nome}
        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # FUNÇÃO
    # ========================================================

    linha[1].markdown(
        f"""
        <div class="funcao-operador">
            {funcao}
        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # DIAS
    # ========================================================

    for i, (dia, _) in enumerate(DIAS, 2):

        valor = status_lista[i - 2]


        # ====================================================
        # TRABALHO
        # ====================================================

        if valor != "FOLGA":

            linha[i].markdown(
                f"""
                <div class="card-trabalho">

                    TRABALHO

                    <div class="sub-info">
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


        # ====================================================
        # ALTERAÇÃO
        # ====================================================

        if st.session_state.autenticado:

            if valor == "FOLGA":

                novo_valor = HORARIOS[
                    turno_selecionado
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

                status_lista[i - 2] = novo_valor

                salvar_status(
                    operador_id,
                    semana_id,
                    *status_lista
                )

                st.rerun()


# ============================================================
# CASO NÃO TENHA OPERADORES
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

st.markdown(
    """
    <div class="rodape">
        Escala Amazon • Sistema independente de gestão de escala
    </div>
    """,
    unsafe_allow_html=True
)
