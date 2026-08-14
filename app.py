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
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDecoration { display: none !important; }

/* Espaço superior para não cortar o título */
.stMainBlockContainer {
    padding-top: 35px !important;
    padding-bottom: 30px !important;
}

/* TÍTULO */
.titulo {
    text-align: center;
    color: #131921;
    font-family: 'Segoe UI', sans-serif;
    font-size: 30px;
    font-weight: 800;
    line-height: 1.3;
    margin: 0;
    padding: 0;
}

.subtitulo {
    text-align: center;
    color: #64748B;
    font-size: 13px;
    margin-top: 5px;
    margin-bottom: 25px;
}

/* CABEÇALHO DOS TURNOS */
.turno-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 28px;
    margin-bottom: 5px;
}

.turno-titulo {
    font-size: 21px;
    font-weight: 800;
    color: #131921;
}

.turno-horario {
    background: #FFF3E0;
    color: #D97706;
    border: 1px solid #FDBA74;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
}

.turno-contador {
    background: #F1F5F9;
    color: #64748B;
    padding: 4px 9px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
}

/* CABEÇALHOS */
.header-col {
    text-align: center;
    font-weight: 800;
    font-size: 11px;
    color: #475569;
    margin-bottom: 8px;
}

.header-esquerda {
    text-align: left;
}

/* OPERADOR */
.nome-operador {
    padding-top: 9px;
    font-size: 13px;
    color: #111827;
}

.funcao-operador {
    padding-top: 9px;
    font-size: 11px;
    color: #64748B;
}

/* TRABALHO */
.card-trabalho {
    background: linear-gradient(135deg, #263646, #1F2937);
    color: white;
    padding: 8px 5px;
    border-radius: 7px;
    text-align: center;
    font-weight: 800;
    font-size: 10px;
    border-left: 4px solid #FF9900;
    margin-bottom: 4px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.08);
}

/* FOLGA */
.card-folga {
    background: #F1F5F9;
    color: #475569;
    padding: 8px 5px;
    border-radius: 7px;
    text-align: center;
    font-weight: 800;
    font-size: 10px;
    border-left: 4px solid #94A3B8;
    margin-bottom: 4px;
}

/* SEPARADOR */
.separador {
    border: 0;
    border-top: 1px solid #E2E8F0;
    margin-top: 2px;
    margin-bottom: 15px;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    border-right: 1px solid #E2E8F0;
}

.sidebar-titulo {
    color: #FF9900;
    font-size: 20px;
    font-weight: 800;
}

.sidebar-status {
    background: #ECFDF5;
    color: #047857;
    padding: 8px;
    border-radius: 7px;
    font-size: 12px;
    font-weight: 700;
    text-align: center;
}

/* MÉTRICAS */
.metric-card {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 12px;
    text-align: center;
    min-height: 70px;
}

.metric-numero {
    font-size: 22px;
    font-weight: 800;
    color: #131921;
}

.metric-label {
    font-size: 10px;
    color: #64748B;
}

/* VISÃO GERENCIAL */
.visao-gerencial {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 9px;
    padding: 10px 14px;
    text-align: center;
    color: #475569;
    font-size: 12px;
    margin-top: 12px;
    margin-bottom: 18px;
}

.visao-gerencial .numero {
    color: #131921;
    font-weight: 800;
}

.visao-gerencial .trabalho {
    color: #047857;
    font-weight: 800;
}

.visao-gerencial .folga {
    color: #64748B;
    font-weight: 800;
}

/* BOTÕES */
.stButton > button {
    border-radius: 7px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

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

    existente = conn.execute("""
        SELECT id
        FROM operadores
        WHERE UPPER(nome) = UPPER(?)
        AND ativo = 1
    """, (nome,)).fetchone()

    if existente:
        conn.close()
        return False

    conn.execute("""
        INSERT INTO operadores (nome, funcao, turno)
        VALUES (?, ?, ?)
    """, (nome, funcao, turno))

    conn.commit()
    conn.close()
    return True


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
    """, (operador_id, semana_id)).fetchone()

    conn.close()
    return resultado


def salvar_status(operador_id, semana_id, sexta, sabado, domingo, segunda):
    conn = conectar()

    existente = conn.execute("""
        SELECT id
        FROM escala
        WHERE operador_id = ?
        AND semana_id = ?
    """, (operador_id, semana_id)).fetchone()

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
            sexta, sabado, domingo, segunda,
            operador_id, semana_id
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


semanas = [obter_semana(i) for i in range(-2, 5)]

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

        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar", use_container_width=True):

            if (
                usuario.lower().strip() == "admin"
                and senha == "Amazon123"
            ):
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

    else:

        st.markdown(
            "<div class='sidebar-status'>🟢 Modo Gestão ativo</div>",
            unsafe_allow_html=True
        )

        st.divider()

        # CADASTRAR
        st.markdown("### ➕ Novo operador")

        novo_nome = st.text_input("Nome", key="novo_nome")
        nova_funcao = st.text_input("Função", key="nova_funcao")

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

                sucesso = cadastrar_operador(
                    novo_nome.strip().upper(),
                    nova_funcao.strip().upper(),
                    novo_turno
                )

                if sucesso:
                    st.success(
                        f"{novo_nome.strip().upper()} cadastrado!"
                    )
                    st.rerun()
                else:
                    st.warning(
                        "Já existe um operador ativo com esse nome."
                    )

            else:
                st.warning("Preencha nome e função.")

        st.divider()

        # REMOVER
        st.markdown("### ❌ Remover operador")

        operadores_sidebar = buscar_operadores()

        if operadores_sidebar:

            opcoes_remocao = {
                f"{x[1]} — {x[2]} — {x[3]}": x[0]
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

                st.success("Operador removido.")
                st.rerun()

        st.divider()

        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.autenticado = False
            st.rerun()

# ============================================================
# TÍTULO
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        margin-top:0px;
        margin-bottom:26px;
        padding-top:4px;
    ">
        <div class="titulo">📦 Escala Amazon</div>
        <div class="subtitulo">
            Monitoramento Operacional • Escala de Equipe
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# SELEÇÃO DA SEMANA E DIA
# ============================================================

col1, col2 = st.columns([2.4, 1])

semana_labels = [x["nome"] for x in semanas]

with col1:

    st.markdown(
        "<b style='font-size:12px;color:#475569;'>📅 Período da escala</b>",
        unsafe_allow_html=True
    )

    semana_escolhida = st.selectbox(
        "Período",
        semana_labels,
        index=2,
        label_visibility="collapsed"
    )

semana = semanas[semana_labels.index(semana_escolhida)]
semana_id = semana["id"]

with col2:

    st.markdown(
        "<b style='font-size:12px;color:#475569;'>👁 Visão do dia</b>",
        unsafe_allow_html=True
    )

    dia_escolhido = st.selectbox(
        "Dia",
        [x[0] for x in DIAS],
        label_visibility="collapsed"
    )

# ============================================================
# OPERADORES
# ============================================================

operadores = buscar_operadores()

# ============================================================
# GARANTIR ESCALA PADRÃO
# ============================================================

def garantir_status(operador):
    status = buscar_status(operador[0], semana_id)

    if status is None:

        horario = HORARIOS[operador[3]]

        status = (
            horario,
            horario,
            horario,
            horario
        )

        salvar_status(
            operador[0],
            semana_id,
            *status
        )

    return status

# ============================================================
# MÉTRICAS
# ============================================================

total = len(operadores)

t1 = len([x for x in operadores if x[3] == "T1"])
t2 = len([x for x in operadores if x[3] == "T2"])
t3 = len([x for x in operadores if x[3] == "T3"])

indice_dia = [x[0] for x in DIAS].index(dia_escolhido)

trabalhando_dia = 0
folga_dia = 0

for operador in operadores:

    status = garantir_status(operador)

    if status[indice_dia] == "FOLGA":
        folga_dia += 1
    else:
        trabalhando_dia += 1

# ============================================================
# CARDS
# ============================================================

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-numero">{total}</div>
            <div class="metric-label">OPERADORES</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with m2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-numero">{t1}</div>
            <div class="metric-label">T1 • 07h às 15h</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with m3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-numero">{t2}</div>
            <div class="metric-label">T2 • 15h às 23h</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with m4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-numero">{t3}</div>
            <div class="metric-label">T3 • 23h às 07h</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# RESUMO GERENCIAL
# ============================================================

st.markdown(
    f"""
    <div class="visao-gerencial">
        <span class="numero">
            Visão de {dia_escolhido} ({semana[dia_escolhido]})
        </span>
        &nbsp;&nbsp;•&nbsp;&nbsp;
        <span class="trabalho">
            🟢 {trabalhando_dia} trabalhando
        </span>
        &nbsp;&nbsp;•&nbsp;&nbsp;
        <span class="folga">
            ⚪ {folga_dia} de folga
        </span>
        &nbsp;&nbsp;•&nbsp;&nbsp;
        <span class="numero">
            {total} operadores
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

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

    st.markdown(
        f"""
        <div class="turno-header">
            <div class="turno-titulo">
                🕒 {NOMES_TURNOS[turno]}
            </div>

            <div class="turno-horario">
                {HORARIOS[turno]}
            </div>

            <div class="turno-contador">
                {len(operadores_turno)} operadores
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    headers = st.columns(
        [2.5, 2, 1.8, 1.8, 1.8, 1.8]
    )

    headers[0].markdown(
        "<div class='header-col header-esquerda'>OPERADOR</div>",
        unsafe_allow_html=True
    )

    headers[1].markdown(
        "<div class='header-col header-esquerda'>FUNÇÃO</div>",
        unsafe_allow_html=True
    )

    for i, (dia, _) in enumerate(DIAS, 2):

        headers[i].markdown(
            f"""
            <div class="header-col">
                {dia.upper()} ({semana[dia]})
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        "<div class='separador'></div>",
        unsafe_allow_html=True
    )

    for operador in operadores_turno:

        operador_id = operador[0]
        nome = operador[1]
        funcao = operador[2]
        status = garantir_status(operador)

        linha = st.columns(
            [2.5, 2, 1.8, 1.8, 1.8, 1.8]
        )

        linha[0].markdown(
            f"""
            <div class="nome-operador">
                <b>{nome}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

        linha[1].markdown(
            f"""
            <div class="funcao-operador">
                {funcao}
            </div>
            """,
            unsafe_allow_html=True
        )

        status_lista = list(status)

        for i, (dia, _) in enumerate(DIAS, 2):

            valor = status_lista[i - 2]

            if valor == "FOLGA":

                linha[i].markdown(
                    """
                    <div class="card-folga">
                        FOLGA
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                linha[i].markdown(
                    """
                    <div class="card-trabalho">
                        TRABALHO
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            if st.session_state.autenticado:

                if valor == "FOLGA":
                    novo_valor = HORARIOS[turno]
                else:
                    novo_valor = "FOLGA"

                if linha[i].button(
                    "↔ Alternar",
                    key=f"{operador_id}_{semana_id}_{dia}",
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
