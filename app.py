import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import os


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Escala Amazon",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# BANCO DE DADOS INTERNO
# NÃO USA EXCEL / GOOGLE SHEETS / CSV
# ============================================================

ARQUIVO_BANCO = "escala_amazon.db"


# ============================================================
# HORÁRIOS OFICIAIS DOS TURNOS
# ============================================================

HORARIOS_TURNOS = {
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
    "Sexta",
    "Sábado",
    "Domingo",
    "Segunda"
]


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

/* ============================================================
   STREAMLIT
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
   TÍTULO
   ============================================================ */

.titulo {
    text-align: center;
    color: #131921;
    font-family: 'Segoe UI', sans-serif;
    font-weight: 700;
    margin-top: 5px;
    margin-bottom: 8px;
    font-size: 30px;
}

.subtitulo {
    text-align: center;
    color: #64748B;
    font-size: 13px;
    margin-bottom: 25px;
}


/* ============================================================
   CABEÇALHO DO TURNO
   ============================================================ */

.turno-header {
    background: linear-gradient(
        90deg,
        #232F3E 0%,
        #2D3B4D 100%
    );

    color: white;

    border-radius: 10px;

    padding: 13px 18px;

    margin-top: 28px;
    margin-bottom: 12px;

    border-left: 5px solid #FF9900;

    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.turno-titulo {
    font-size: 19px;
    font-weight: 700;
}

.turno-horario {
    color: #FF9900;
    font-size: 12px;
    font-weight: 600;
    margin-top: 2px;
}


/* ============================================================
   RESUMO DO TURNO
   ============================================================ */

.resumo-turno {
    display: flex;
    gap: 8px;
    margin-bottom: 15px;
    flex-wrap: wrap;
}

.resumo-item {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 7px;
    padding: 6px 11px;
    font-size: 11px;
    color: #475569;
}

.resumo-numero {
    font-weight: 700;
    color: #131921;
}


/* ============================================================
   CABEÇALHO DA TABELA
   ============================================================ */

.header-col {
    text-align: center;
    font-weight: 700;
    font-size: 11px;
    color: #475569;
    margin-bottom: 8px;
    line-height: 1.25;
}

.header-col-esquerda {
    text-align: left;
}


/* ============================================================
   NOME / FUNÇÃO
   ============================================================ */

.nome-operador {
    padding-top: 9px;
    font-size: 13px;
    margin-bottom: 12px;
    color: #131921;
}

.funcao-operador {
    padding-top: 9px;
    font-size: 11px;
    color: #64748B;
    margin-bottom: 12px;
}


/* ============================================================
   CARD TRABALHO
   ============================================================ */

.card-trabalho {
    background: #232F3E;
    color: white;

    padding: 7px 5px;

    border-radius: 7px;

    text-align: center;

    font-weight: 700;
    font-size: 10px;

    border-left: 4px solid #FF9900;

    margin-bottom: 6px;

    min-height: 42px;

    display: flex;
    flex-direction: column;
    justify-content: center;
}

.sub-info {
    font-size: 9px;
    color: #FF9900;
    font-weight: 700;
    margin-top: 3px;
}


/* ============================================================
   CARD FOLGA
   ============================================================ */

.card-folga {
    background: #F1F5F9;
    color: #475569;

    padding: 7px 5px;

    border-radius: 7px;

    text-align: center;

    font-weight: 700;
    font-size: 10px;

    border-left: 4px solid #94A3B8;

    margin-bottom: 6px;

    min-height: 42px;

    display: flex;
    flex-direction: column;
    justify-content: center;
}

.sub-info-folga {
    font-size: 9px;
    color: #94A3B8;
    font-weight: 500;
    margin-top: 3px;
}


/* ============================================================
   DIVISÓRIA
   ============================================================ */

.divisor {
    border-top: 1px solid #E2E8F0;
    margin: 4px 0 12px 0;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

.sidebar-titulo {
    color: #FF9900;
    font-weight: 700;
    font-size: 18px;
}

.sidebar-info {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 10px;
    font-size: 11px;
    color: #475569;
    margin-bottom: 10px;
}


/* ============================================================
   LEGENDA
   ============================================================ */

.legenda {
    display: flex;
    gap: 15px;
    justify-content: center;
    margin-top: 10px;
    margin-bottom: 20px;
}

.legenda-item {
    font-size: 11px;
    color: #64748B;
}


/* ============================================================
   RODAPÉ INTERNO
   ============================================================ */

.rodape {
    text-align: center;
    color: #94A3B8;
    font-size: 10px;
    margin-top: 30px;
    padding: 15px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# BANCO SQLITE
# ============================================================

def conectar_banco():
    return sqlite3.connect(ARQUIVO_BANCO)


def criar_banco():

    conn = conectar_banco()
    cursor = conn.cursor()

    # --------------------------------------------------------
    # OPERADORES
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            funcao TEXT NOT NULL,
            turno TEXT NOT NULL,
            ativo INTEGER DEFAULT 1
        )
    """)

    # --------------------------------------------------------
    # ESCALAS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS escalas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operador_id INTEGER NOT NULL,
            semana_id TEXT NOT NULL,
            sexta TEXT NOT NULL,
            sabado TEXT NOT NULL,
            domingo TEXT NOT NULL,
            segunda TEXT NOT NULL,

            UNIQUE(operador_id, semana_id),

            FOREIGN KEY(operador_id)
            REFERENCES operadores(id)
        )
    """)

    conn.commit()
    conn.close()


criar_banco()


# ============================================================
# OPERADORES PADRÃO
# SÓ SÃO CRIADOS SE O BANCO ESTIVER VAZIO
# ============================================================

def criar_operadores_iniciais():

    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM operadores"
    )

    quantidade = cursor.fetchone()[0]

    if quantidade > 0:
        conn.close()
        return

    operadores = [

        # T1
        ("ALAN ARÁUJO", "ANALISTA", "T1"),
        ("MARGARIDA", "PICKUP", "T1"),
        ("JOSÉ BRUNO PALHANO", "PICKUP", "T1"),
        ("CRISTOVÃO MIKELLYS", "DEPART", "T1"),
        ("PEDRO LUCAS", "DROPOFF", "T1"),
        ("FELIPE ALLAN", "DROPOFF", "T1"),
        ("BRUNA BLENDA", "DROPOFF", "T1"),
        ("CONCEIÇÃO DAIANE", "SEGURANÇA (ONISYS)", "T1"),
        ("MATHEUS LUSTOSA", "SEGURANÇA/ELOG", "T1"),

        # T2
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

        # T3
        ("WESLEY", "LÍDER", "T3"),
        ("JOÃO", "LÍDER/SEGURANÇA", "T3"),
        ("RILDOMAR", "PICKUP", "T3"),
        ("LUCIANA", "PICKUP", "T3"),
        ("GLAYLDSON", "SEGURANÇA", "T3"),
        ("TAYANARA", "DEPART", "T3"),
        ("RUAN", "DROPOFF", "T3"),
        ("BÁRBARA", "DROPOFF", "T3")
    ]

    for nome, funcao, turno in operadores:

        cursor.execute("""
            INSERT INTO operadores
            (nome, funcao, turno)
            VALUES (?, ?, ?)
        """, (nome, funcao, turno))

    conn.commit()
    conn.close()


criar_operadores_iniciais()


# ============================================================
# DATAS
# ============================================================

def obter_datas_semana(deslocamento_semanas=0):

    hoje = datetime.now()

    dias_para_sexta = (hoje.weekday() - 4) % 7

    sexta = hoje - timedelta(
        days=dias_para_sexta
    )

    sexta = sexta + timedelta(
        weeks=deslocamento_semanas
    )

    sabado = sexta + timedelta(days=1)
    domingo = sexta + timedelta(days=2)
    segunda = sexta + timedelta(days=3)

    return {

        "id_semana":
            sexta.strftime("%Y_W%W"),

        "rotulo":
            f"Semana de {sexta.strftime('%d/%m')} "
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


# ============================================================
# SEMANAS DISPONÍVEIS
# ============================================================

opcoes_semanas = [
    obter_datas_semana(i)
    for i in range(-1, 5)
]

formatos_semanas = {
    item["rotulo"]: item
    for item in opcoes_semanas
}


# ============================================================
# LOGIN
# ============================================================

if (
    "logged_in" in st.query_params
    and st.query_params["logged_in"] == "true"
):

    st.session_state.autenticado = True

elif "autenticado" not in st.session_state:

    st.session_state.autenticado = False


# ============================================================
# GARANTE QUE A SEMANA TENHA ESCALA
# ============================================================

def garantir_escala_semana(semana_id):

    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, turno
        FROM operadores
        WHERE ativo = 1
    """)

    operadores = cursor.fetchall()

    for operador_id, turno in operadores:

        cursor.execute("""
            SELECT id
            FROM escalas
            WHERE operador_id = ?
            AND semana_id = ?
        """, (
            operador_id,
            semana_id
        ))

        existe = cursor.fetchone()

        if not existe:

            horario = HORARIOS_TURNOS[turno]

            cursor.execute("""
                INSERT INTO escalas
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
                horario,
                horario,
                horario,
                horario
            ))

    conn.commit()
    conn.close()


# ============================================================
# LEITURA DA ESCALA
# ============================================================

def carregar_escala(semana_id):

    conn = conectar_banco()

    query = """
        SELECT
            o.id,
            o.nome,
            o.funcao,
            o.turno,
            e.sexta,
            e.sabado,
            e.domingo,
            e.segunda

        FROM operadores o

        INNER JOIN escalas e
            ON o.id = e.operador_id

        WHERE o.ativo = 1
        AND e.semana_id = ?

        ORDER BY
            o.turno,
            o.nome
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=(semana_id,)
    )

    conn.close()

    return df


# ============================================================
# TOGGLE DE ESCALA
# ============================================================

def alternar_status(
    operador_id,
    semana_id,
    dia,
    turno
):

    coluna = {
        "Sexta": "sexta",
        "Sábado": "sabado",
        "Domingo": "domingo",
        "Segunda": "segunda"
    }[dia]

    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute(
        f"""
        SELECT {coluna}
        FROM escalas
        WHERE operador_id = ?
        AND semana_id = ?
        """,
        (
            operador_id,
            semana_id
        )
    )

    resultado = cursor.fetchone()

    if not resultado:
        conn.close()
        return

    status_atual = resultado[0]

    if status_atual == "FOLGA":

        novo_status = HORARIOS_TURNOS[turno]

    else:

        novo_status = "FOLGA"

    cursor.execute(
        f"""
        UPDATE escalas
        SET {coluna} = ?
        WHERE operador_id = ?
        AND semana_id = ?
        """,
        (
            novo_status,
            operador_id,
            semana_id
        )
    )

    conn.commit()
    conn.close()


# ============================================================
# TÍTULO
# ============================================================

st.markdown(
    "<div class='titulo'>📦 Escala Amazon</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitulo'>"
    "Monitoramento Operacional • Gestão de Escala"
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# FILTROS PRINCIPAIS
# ============================================================

col1, col2, col3 = st.columns(
    [2.5, 2, 2]
)

with col1:

    semana_selecionada = st.selectbox(
        "📅 Período da Escala",
        list(formatos_semanas.keys()),
        index=1
    )


dados_semana = formatos_semanas[
    semana_selecionada
]

semana_id = dados_semana["id_semana"]


garantir_escala_semana(
    semana_id
)


with col2:

    filtro_turno = st.selectbox(
        "🕒 Turno",
        [
            "Todos",
            "Turno 1",
            "Turno 2",
            "Turno 3"
        ]
    )


with col3:

    busca_nome = st.text_input(
        "🔎 Buscar operador",
        placeholder="Digite um nome..."
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "<div class='sidebar-titulo'>"
        "🔐 Área do Gestor"
        "</div>",
        unsafe_allow_html=True
    )

    st.divider()

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    if not st.session_state.autenticado:

        st.caption(
            "Acesso restrito à gestão da escala."
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
                    usuario.lower() == "admin"
                    and senha == "Amazon123"
                ):

                    st.session_state.autenticado = True

                    st.query_params[
                        "logged_in"
                    ] = "true"

                    st.rerun()

                else:

                    st.error(
                        "Usuário ou senha incorretos."
                    )


    # --------------------------------------------------------
    # GESTÃO
    # --------------------------------------------------------

    else:

        st.success(
            "🟢 Modo Gestão ativo"
        )

        st.markdown(
            "<div class='sidebar-info'>"
            "<b>Como funciona:</b><br><br>"
            "Os horários são definidos automaticamente "
            "pelo turno do operador.<br><br>"
            "Você só precisa cadastrar o nome, função "
            "e turno."
            "</div>",
            unsafe_allow_html=True
        )

        st.divider()

        # ====================================================
        # CADASTRAR OPERADOR
        # ====================================================

        st.markdown(
            "### ➕ Novo Operador"
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
                "Turno 1",
                "Turno 2",
                "Turno 3"
            ],
            key="novo_turno"
        )

        turno_id_novo = (
            "T1"
            if novo_turno == "Turno 1"
            else
            "T2"
            if novo_turno == "Turno 2"
            else
            "T3"
        )

        st.caption(
            f"⏰ Horário automático: "
            f"**{HORARIOS_TURNOS[turno_id_novo]}**"
        )

        if st.button(
            "Adicionar Operador",
            use_container_width=True
        ):

            nome = novo_nome.upper().strip()
            funcao = nova_funcao.upper().strip()

            if not nome or not funcao:

                st.warning(
                    "Preencha nome e função."
                )

            else:

                conn = conectar_banco()
                cursor = conn.cursor()

                try:

                    cursor.execute("""
                        INSERT INTO operadores
                        (nome, funcao, turno)
                        VALUES (?, ?, ?)
                    """, (
                        nome,
                        funcao,
                        turno_id_novo
                    ))

                    conn.commit()

                    operador_id = cursor.lastrowid

                    horario = HORARIOS_TURNOS[
                        turno_id_novo
                    ]

                    cursor.execute("""
                        INSERT INTO escalas
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
                        horario,
                        horario,
                        horario,
                        horario
                    ))

                    conn.commit()

                    st.success(
                        f"{nome} cadastrado!"
                    )

                except sqlite3.IntegrityError:

                    st.error(
                        "Esse operador já está cadastrado."
                    )

                conn.close()

                st.rerun()

        st.divider()

        # ====================================================
        # REMOVER OPERADOR
        # ====================================================

        st.markdown(
            "### ❌ Remover Operador"
        )

        conn = conectar_banco()

        df_operadores = pd.read_sql_query(
            """
            SELECT id, nome
            FROM operadores
            WHERE ativo = 1
            ORDER BY nome
            """,
            conn
        )

        conn.close()

        if not df_operadores.empty:

            nomes = df_operadores[
                "nome"
            ].tolist()

            operador_remover = st.selectbox(
                "Selecione o operador",
                nomes
            )

            tipo_remocao = st.radio(
                "Tipo de remoção",
                [
                    "Somente da escala atual",
                    "Definitivamente"
                ]
            )

            if st.button(
                "Confirmar remoção",
                type="primary",
                use_container_width=True
            ):

                conn = conectar_banco()
                cursor = conn.cursor()

                operador_id = int(
                    df_operadores[
                        df_operadores["nome"]
                        == operador_remover
                    ]["id"].iloc[0]
                )

                if tipo_remocao == "Somente da escala atual":

                    cursor.execute("""
                        DELETE FROM escalas
                        WHERE operador_id = ?
                        AND semana_id = ?
                    """, (
                        operador_id,
                        semana_id
                    ))

                    st.success(
                        f"{operador_remover} removido "
                        "da semana atual."
                    )

                else:

                    cursor.execute("""
                        DELETE FROM escalas
                        WHERE operador_id = ?
                    """, (
                        operador_id,
                    ))

                    cursor.execute("""
                        DELETE FROM operadores
                        WHERE id = ?
                    """, (
                        operador_id,
                    ))

                    st.success(
                        f"{operador_remover} removido "
                        "definitivamente."
                    )

                conn.commit()
                conn.close()

                st.rerun()

        st.divider()

        # ====================================================
        # LOGOUT
        # ====================================================

        if st.button(
            "🚪 Sair",
            use_container_width=True
        ):

            st.session_state.autenticado = False

            st.query_params.clear()

            st.rerun()


# ============================================================
# CARREGA ESCALA
# ============================================================

df = carregar_escala(
    semana_id
)


# ============================================================
# FILTRO DE TURNO
# ============================================================

if filtro_turno != "Todos":

    turno_filtro_id = {
        "Turno 1": "T1",
        "Turno 2": "T2",
        "Turno 3": "T3"
    }[filtro_turno]

    df = df[
        df["turno"] == turno_filtro_id
    ]


# ============================================================
# FILTRO DE NOME
# ============================================================

if busca_nome:

    df = df[
        df["nome"].str.contains(
            busca_nome,
            case=False,
            na=False
        )
    ]


# ============================================================
# LEGENDA
# ============================================================

st.markdown("""
<div class='legenda'>

<div class='legenda-item'>
🔵 <b>Trabalho</b>
</div>

<div class='legenda-item'>
⚪ <b>Folga</b>
</div>

<div class='legenda-item'>
🔄 <b>Alternar</b>
</div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# EXIBIÇÃO DOS TURNOS
# ============================================================

for turno_id in [
    "T1",
    "T2",
    "T3"
]:

    df_turno = df[
        df["turno"] == turno_id
    ].copy()

    if df_turno.empty:
        continue


    # ========================================================
    # CONTADORES
    # ========================================================

    total_operadores = len(
        df_turno
    )

    trabalhando = 0
    folgas = 0

    for _, linha in df_turno.iterrows():

        for dia in [
            "sexta",
            "sabado",
            "domingo",
            "segunda"
        ]:

            if linha[dia] == "FOLGA":
                folgas += 1
            else:
                trabalhando += 1


    # ========================================================
    # CABEÇALHO DO TURNO
    # ========================================================

    st.markdown(
        f"""
        <div class='turno-header'>

            <div class='turno-titulo'>
                🕒 {NOMES_TURNOS[turno_id]}
            </div>

            <div class='turno-horario'>
                ⏰ {HORARIOS_TURNOS[turno_id]}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # RESUMO
    # ========================================================

    st.markdown(
        f"""
        <div class='resumo-turno'>

            <div class='resumo-item'>
                👥 Operadores:
                <span class='resumo-numero'>
                    {total_operadores}
                </span>
            </div>

            <div class='resumo-item'>
                🟢 Dias trabalhados:
                <span class='resumo-numero'>
                    {trabalhando}
                </span>
            </div>

            <div class='resumo-item'>
                ⚪ Folgas:
                <span class='resumo-numero'>
                    {folgas}
                </span>
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # CABEÇALHO DAS COLUNAS
    # ========================================================

    cols_header = st.columns(
        [
            2.4,
            1.8,
            1.8,
            1.8,
            1.8,
            1.8
        ]
    )


    cols_header[0].markdown(
        "<div class='header-col header-col-esquerda'>"
        "OPERADOR"
        "</div>",
        unsafe_allow_html=True
    )


    cols_header[1].markdown(
        "<div class='header-col header-col-esquerda'>"
        "FUNÇÃO"
        "</div>",
        unsafe_allow_html=True
    )


    for i, dia in enumerate(
        DIAS,
        2
    ):

        data_dia = dados_semana[dia]

        cols_header[i].markdown(
            f"""
            <div class='header-col'>
                {dia.upper()}<br>
                <span style='font-size:9px;color:#94A3B8;'>
                    {data_dia}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )


    st.markdown(
        "<div class='divisor'></div>",
        unsafe_allow_html=True
    )


    # ========================================================
    # OPERADORES
    # ========================================================

    for _, row in df_turno.iterrows():

        cols = st.columns(
            [
                2.4,
                1.8,
                1.8,
                1.8,
                1.8,
                1.8
            ]
        )


        # ----------------------------------------------------
        # NOME
        # ----------------------------------------------------

        cols[0].markdown(
            f"""
            <div class='nome-operador'>
                <b>{row['nome']}</b>
            </div>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # FUNÇÃO
        # ----------------------------------------------------

        cols[1].markdown(
            f"""
            <div class='funcao-operador'>
                {row['funcao']}
            </div>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # DIAS
        # ----------------------------------------------------

        colunas_dias = {
            "Sexta": "sexta",
            "Sábado": "sabado",
            "Domingo": "domingo",
            "Segunda": "segunda"
        }


        for idx, dia in enumerate(
            DIAS,
            2
        ):

            coluna_banco = colunas_dias[dia]

            status = str(
                row[coluna_banco]
            )


            # -----------------------------------------------
            # TRABALHO
            # -----------------------------------------------

            if status != "FOLGA":

                cols[idx].markdown(
                    f"""
                    <div class='card-trabalho'>
                        TRABALHO
                        <div class='sub-info'>
                            {status}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # -----------------------------------------------
            # FOLGA
            # -----------------------------------------------

            else:

                cols[idx].markdown(
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
            # BOTÃO GESTOR
            # -----------------------------------------------

            if st.session_state.autenticado:

                if cols[idx].button(
                    "🔄 Alternar",
                    key=(
                        f"alternar_"
                        f"{row['id']}_"
                        f"{dia}_"
                        f"{semana_id}"
                    ),
                    use_container_width=True
                ):

                    alternar_status(
                        int(row["id"]),
                        semana_id,
                        dia,
                        turno_id
                    )

                    st.rerun()


    st.write("")


# ============================================================
# MENSAGEM QUANDO NÃO HÁ RESULTADOS
# ============================================================

if df.empty:

    st.info(
        "Nenhum operador encontrado com os filtros selecionados."
    )


# ============================================================
# RODAPÉ
# ============================================================

st.markdown(
    """
    <div class='rodape'>
        Escala Amazon • Sistema de Monitoramento Operacional
    </div>
    """,
    unsafe_allow_html=True
)
