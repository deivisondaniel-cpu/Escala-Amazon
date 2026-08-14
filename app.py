import streamlit as st
import sqlite3
from datetime import datetime, timedelta


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
# BANCO INTERNO
# ============================================================
# Não utiliza CSV, Excel ou Google Sheets.
# O próprio aplicativo possui seu banco SQLite.

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
# CSS
# ============================================================

st.markdown("""
<style>



\#MainMenu {

&#x20;   visibility: hidden;

}



footer {

&#x20;   visibility: hidden;

}



.stDecoration {

&#x20;   display: none !important;

}





/\* ============================================================

&#x20;  TÍTULO

&#x20;  ============================================================ \*/



.titulo {

&#x20;   text-align: center;

&#x20;   color: #131921;

&#x20;   font-family: 'Segoe UI', sans-serif;

&#x20;   font-size: 30px;

&#x20;   font-weight: 800;

&#x20;   margin-top: 5px;

&#x20;   margin-bottom: 5px;

}



.subtitulo {

&#x20;   text-align: center;

&#x20;   color: #64748B;

&#x20;   font-size: 13px;

&#x20;   margin-bottom: 25px;

}





/\* ============================================================

&#x20;  CABEÇALHO DOS TURNOS

&#x20;  ============================================================ \*/



.turno-header {

&#x20;   display: flex;

&#x20;   align-items: center;

&#x20;   gap: 10px;

&#x20;   margin-top: 28px;

&#x20;   margin-bottom: 5px;

}



.turno-titulo {

&#x20;   font-size: 21px;

&#x20;   font-weight: 800;

&#x20;   color: #131921;

}



.turno-horario {

&#x20;   background: #FFF3E0;

&#x20;   color: #D97706;

&#x20;   border: 1px solid #FDBA74;

&#x20;   padding: 4px 10px;

&#x20;   border-radius: 20px;

&#x20;   font-size: 12px;

&#x20;   font-weight: 700;

}





/\* ============================================================

&#x20;  CABEÇALHOS

&#x20;  ============================================================ \*/



.header-col {

&#x20;   text-align: center;

&#x20;   font-weight: 800;

&#x20;   font-size: 12px;

&#x20;   color: #475569;

&#x20;   margin-bottom: 8px;

}



.header-esquerda {

&#x20;   text-align: left;

}





/\* ============================================================

&#x20;  OPERADOR

&#x20;  ============================================================ \*/



.nome-operador {

&#x20;   padding-top: 9px;

&#x20;   font-size: 13px;

&#x20;   color: #111827;

}



.funcao-operador {

&#x20;   padding-top: 9px;

&#x20;   font-size: 11px;

&#x20;   color: #64748B;

}





/\* ============================================================

&#x20;  CARD TRABALHO

&#x20;  ============================================================ \*/



.card-trabalho {

&#x20;   background: linear-gradient(

&#x20;       135deg,

&#x20;       #263646,

&#x20;       #1F2937

&#x20;   );



&#x20;   color: white;



&#x20;   padding: 8px 5px;



&#x20;   border-radius: 7px;



&#x20;   text-align: center;



&#x20;   font-weight: 700;



&#x20;   font-size: 11px;



&#x20;   border-left: 4px solid #FF9900;



&#x20;   margin-bottom: 4px;



&#x20;   box-shadow: 0 2px 5px rgba(0,0,0,0.08);

}



.sub-info {

&#x20;   color: #FFB84D;

&#x20;   font-size: 10px;

&#x20;   margin-top: 3px;

}





/\* ============================================================

&#x20;  CARD FOLGA

&#x20;  ============================================================ \*/



.card-folga {

&#x20;   background: #F1F5F9;



&#x20;   color: #475569;



&#x20;   padding: 8px 5px;



&#x20;   border-radius: 7px;



&#x20;   text-align: center;



&#x20;   font-weight: 800;



&#x20;   font-size: 11px;



&#x20;   border-left: 4px solid #94A3B8;



&#x20;   margin-bottom: 4px;

}



.sub-info-folga {

&#x20;   color: #94A3B8;

&#x20;   font-size: 10px;

&#x20;   margin-top: 3px;

}





/\* ============================================================

&#x20;  SEPARADOR

&#x20;  ============================================================ \*/



.separador {

&#x20;   border: 0;

&#x20;   border-top: 1px solid #E2E8F0;

&#x20;   margin-top: 2px;

&#x20;   margin-bottom: 15px;

}





/\* ============================================================

&#x20;  SIDEBAR

&#x20;  ============================================================ \*/



section\[data-testid="stSidebar"] {

&#x20;   border-right: 1px solid #E2E8F0;

}



.sidebar-titulo {

&#x20;   color: #FF9900;

&#x20;   font-size: 20px;

&#x20;   font-weight: 800;

}



.sidebar-status {

&#x20;   background: #ECFDF5;

&#x20;   color: #047857;

&#x20;   padding: 8px;

&#x20;   border-radius: 7px;

&#x20;   font-size: 12px;

&#x20;   font-weight: 700;

}





/\* ============================================================

&#x20;  MÉTRICAS

&#x20;  ============================================================ \*/



.metric-card {

&#x20;   background: white;

&#x20;   border: 1px solid #E2E8F0;

&#x20;   border-radius: 10px;

&#x20;   padding: 12px;

&#x20;   text-align: center;

}



.metric-numero {

&#x20;   font-size: 22px;

&#x20;   font-weight: 800;

&#x20;   color: #131921;

}



.metric-label {

&#x20;   font-size: 11px;

&#x20;   color: #64748B;

}





/\* ============================================================

&#x20;  BOTÕES

&#x20;  ============================================================ \*/



.stButton > button {

&#x20;   border-radius: 7px;

&#x20;   font-weight: 600;

}





/\* ============================================================

&#x20;  CONTAINER PRINCIPAL

&#x20;  ============================================================ \*/



.stMainBlockContainer {

&#x20;   padding-top: 18px !important;

&#x20;   padding-bottom: 30px !important;

}



""", unsafe_allow_html=True)


# ============================================================
# LOGIN
# ============================================================

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False


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
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "<div class='sidebar-titulo'>🔐 Gestão da Escala</div>",
        unsafe_allow_html=True
    )

    st.divider()

    if not st.session_state.autenticado:

        st.markdown("### Acesso")

        usuario = st.text_input(
            "Usuário"
        )

        senha = st.text_input(
            "Senha",
            type="password"
        )

        if st.button(
            "Entrar",
            use_container_width=True
        ):

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

        st.markdown("### ➕ Novo operador")

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

            if novo_nome.strip() and nova_funcao.strip():

                cadastrar_operador(
                    novo_nome.strip().upper(),
                    nova_funcao.strip().upper(),
                    novo_turno
                )

                st.success(
                    f"{novo_nome.upper()} cadastrado!"
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

        st.markdown("### ❌ Remover operador")

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
                    opcoes_remocao[selecionado]
                )

                st.success(
                    "Operador removido."
                )

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

            st.rerun()


# ============================================================
# TÍTULO
# ============================================================

st.markdown(
    "<div class='titulo'>📦 Escala Amazon</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitulo'>"
    "Monitoramento Operacional • Escala de Equipe"
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


m1, m2, m3, m4 = st.columns(4)


with m1:

    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-numero'>{total}</div>
            <div class='metric-label'>OPERADORES</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with m2:

    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-numero'>{t1}</div>
            <div class='metric-label'>T1 • 07h às 15h</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with m3:

    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-numero'>{t2}</div>
            <div class='metric-label'>T2 • 15h às 23h</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with m4:

    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-numero'>{t3}</div>
            <div class='metric-label'>T3 • 23h às 07h</div>
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

for turno in ["T1", "T2", "T3"]:

    operadores_turno = [
        x for x in operadores
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
        # PRIMEIRO ACESSO DA SEMANA
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
                {nome}
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

        for i, (dia, _) in enumerate(DIAS, 2):

            valor = status_lista[i - 2]


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

                    status_lista[i - 2] = novo_valor

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
