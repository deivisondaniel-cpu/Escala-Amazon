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

BANCO = "escala_amazon_v2.db"


# ============================================================
# BANCO DE DADOS
# ============================================================

def conectar():
    return sqlite3.connect(BANCO, check_same_thread=False)


def criar_banco_do_zero():
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

    dados_existentes = cursor.execute(
        "SELECT COUNT(*) FROM operadores WHERE ativo = 1"
    ).fetchone()[0]

    if dados_existentes == 0:
        funcionarios_oficiais = [
            # T1
            ("ALAN ARAÚJO", "ANALISTA", "T1"),
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

        cursor.executemany("""
            INSERT INTO operadores (nome, funcao, turno)
            VALUES (?, ?, ?)
        """, funcionarios_oficiais)

        conn.commit()

    conn.close()


criar_banco_do_zero()


# ============================================================
# CONSTANTES
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

EMOJIS_TURNOS = {
    "T1": "🌅",
    "T2": "🌆",
    "T3": "🌌"
}

DIAS = [
    ("Sexta", "sexta"),
    ("Sábado", "sabado"),
    ("Domingo", "domingo"),
    ("Segunda", "segunda")
]


# ============================================================
# CSS — NOVA INTERFACE
# ============================================================

st.markdown("""
<style>

/* ============================================================
   BASE
   ============================================================ */

header[data-testid="stHeader"],
.stAppDeployButton,
div[data-testid="stViewerBadge"],
footer,
#MainMenu,
.stDecoration {
    display: none !important;
}

[data-testid="stSidebar"] {
    display: none !important;
}

.stApp {
    background: #F4F6F8;
}

[data-testid="stAppViewContainer"] {
    background: #F4F6F8;
}

.stMainBlockContainer {
    max-width: 1500px !important;
    padding-top: 20px !important;
    padding-bottom: 24px !important;
}


/* ============================================================
   CABEÇALHO
   ============================================================ */

.app-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    margin-bottom: 14px;
}

.app-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}

.amazon-mark {
    width: 38px;
    height: 38px;
    border-radius: 9px;
    background: #FF9900;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #232F3E;
    font-size: 21px;
    font-weight: 900;
    box-shadow: 0 2px 5px rgba(0,0,0,.08);
}

.app-title {
    color: #232F3E;
    font-size: 25px;
    font-weight: 850;
    line-height: 1.05;
    letter-spacing: -.5px;
}

.app-subtitle {
    color: #667085;
    font-size: 12px;
    font-weight: 600;
    margin-top: 3px;
}


/* ============================================================
   SELETOR DE PERÍODO
   ============================================================ */

.period-area {
    background: #FFFFFF;
    border: 1px solid #E1E6EB;
    border-radius: 10px;
    padding: 9px 13px 4px 13px;
    margin-bottom: 10px;
}

.period-label {
    color: #667085;
    font-size: 10px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .6px;
    margin-bottom: -3px;
}

div[data-baseweb="select"] > div {
    min-height: 38px !important;
    border: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
    padding-left: 0 !important;
}


/* ============================================================
   MÉTRICAS
   ============================================================ */

.metrics-row {
    display: grid;
    grid-template-columns: 1.3fr 1fr 1fr 1fr;
    gap: 8px;
    margin: 10px 0 15px 0;
}

.metric-card {
    background: #FFFFFF;
    border: 1px solid #E1E6EB;
    border-radius: 9px;
    padding: 9px 12px;
    display: flex;
    align-items: center;
    gap: 10px;
    min-height: 51px;
}

.metric-number {
    font-size: 20px;
    font-weight: 850;
    color: #232F3E;
    line-height: 1;
}

.metric-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.metric-label {
    color: #667085;
    font-size: 9px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .3px;
}

.metric-time {
    color: #98A2B3;
    font-size: 9px;
    font-weight: 600;
}

.metric-main {
    border-left: 3px solid #FF9900;
}

.metric-t1 {
    border-left: 3px solid #FF9900;
}

.metric-t2 {
    border-left: 3px solid #8B5CF6;
}

.metric-t3 {
    border-left: 3px solid #475569;
}


/* ============================================================
   TABS / TURNOS
   ============================================================ */

div[data-testid="stTabs"] {
    margin-top: 0 !important;
}

button[data-baseweb="tab"] {
    color: #667085 !important;
    font-size: 12px !important;
    font-weight: 750 !important;
    padding: 8px 14px !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #232F3E !important;
}

div[data-baseweb="tab-highlight"] {
    background-color: #FF9900 !important;
    height: 3px !important;
}


/* ============================================================
   CABEÇALHO DO TURNO
   ============================================================ */

.turno-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #FFFFFF;
    border: 1px solid #E1E6EB;
    border-left: 4px solid #FF9900;
    border-radius: 9px;
    padding: 9px 13px;
    margin: 8px 0 8px 0;
}

.turno-left {
    display: flex;
    align-items: center;
    gap: 9px;
}

.turno-icon {
    font-size: 18px;
}

.turno-title {
    color: #232F3E;
    font-size: 15px;
    font-weight: 850;
}

.turno-subtitle {
    color: #98A2B3;
    font-size: 10px;
    font-weight: 650;
    margin-left: 4px;
}

.turno-horario {
    background: #F2F7FC;
    color: #146EB4;
    border: 1px solid #D6E7F5;
    padding: 4px 9px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 800;
}


/* ============================================================
   CABEÇALHO DA TABELA
   ============================================================ */

.grid-header {
    display: grid;
    grid-template-columns: minmax(180px, 2.4fr) minmax(130px, 1.8fr) repeat(4, minmax(90px, 1fr));
    gap: 6px;
    padding: 5px 8px;
    margin-top: 4px;
}

.grid-header-cell {
    color: #667085;
    font-size: 9px;
    font-weight: 850;
    text-transform: uppercase;
    letter-spacing: .45px;
}

.grid-header-cell.day {
    text-align: center;
}


/* ============================================================
   LINHAS DA ESCALA
   ============================================================ */

.operator-row {
    display: grid;
    grid-template-columns: minmax(180px, 2.4fr) minmax(130px, 1.8fr) repeat(4, minmax(90px, 1fr));
    gap: 6px;
    align-items: stretch;
    background: #FFFFFF;
    border: 1px solid #E7EBEF;
    border-radius: 8px;
    padding: 5px 7px;
    margin-bottom: 4px;
    transition: border-color .15s ease, box-shadow .15s ease;
}

.operator-row:hover {
    border-color: #D1D9E0;
    box-shadow: 0 2px 7px rgba(35,47,62,.04);
}

.operator-info {
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-width: 0;
    padding-left: 3px;
}

.operator-name {
    color: #232F3E;
    font-size: 11px;
    font-weight: 850;
    line-height: 1.25;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.operator-function {
    color: #8A97A6;
    font-size: 9px;
    font-weight: 650;
    margin-top: 2px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.status-cell {
    min-width: 0;
}


/* ============================================================
   STATUS TRABALHO
   ============================================================ */

.status-work {
    height: 40px;
    background: #263445;
    color: #FFFFFF;
    border-radius: 6px;
    border-left: 3px solid #FF9900;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    font-size: 9px;
    font-weight: 850;
}

.status-work small {
    display: block;
    color: #FFB84D;
    font-size: 8px;
    font-weight: 700;
    margin-top: 1px;
}


/* ============================================================
   STATUS FOLGA
   ============================================================ */

.status-off {
    height: 40px;
    background: #F0F6FB;
    color: #42627D;
    border-radius: 6px;
    border-left: 3px solid #3B82C4;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    font-size: 9px;
    font-weight: 850;
}

.status-off small {
    display: block;
    color: #8A9BAB;
    font-size: 8px;
    font-weight: 650;
    margin-top: 1px;
}


/* ============================================================
   BOTÕES DO GESTOR
   ============================================================ */

.admin-action {
    margin-top: 2px;
}

.admin-action button {
    min-height: 24px !important;
    height: 24px !important;
    padding: 0 4px !important;
    font-size: 9px !important;
    border-radius: 5px !important;
}


/* ============================================================
   PAINEL DO GESTOR
   ============================================================ */

div[data-testid="stPopover"] > button {
    background: #FFFFFF !important;
    color: #232F3E !important;
    border: 1px solid #D7DEE7 !important;
    border-radius: 8px !important;
    font-size: 11px !important;
    font-weight: 800 !important;
    min-height: 36px !important;
}

div[data-testid="stPopover"] > button:hover {
    border-color: #FF9900 !important;
    color: #232F3E !important;
    background: #FFF9F0 !important;
}


/* ============================================================
   FORMULÁRIOS
   ============================================================ */

[data-testid="stForm"] {
    border: 0 !important;
    padding: 0 !important;
}

.stButton > button {
    border-radius: 7px;
    font-weight: 750;
}

div[data-testid="stTextInput"] input {
    border-radius: 7px !important;
}

div[data-baseweb="select"] {
    border-radius: 7px !important;
}


/* ============================================================
   INFORMAÇÃO DE AUSÊNCIA
   ============================================================ */

.empty-turn {
    background: #FFFFFF;
    border: 1px dashed #D7DEE7;
    color: #667085;
    border-radius: 8px;
    padding: 18px;
    text-align: center;
    font-size: 11px;
}


/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 850px) {

    .stMainBlockContainer {
        padding-left: 10px !important;
        padding-right: 10px !important;
        padding-top: 12px !important;
    }

    .app-header {
        margin-bottom: 9px;
    }

    .amazon-mark {
        width: 32px;
        height: 32px;
        font-size: 17px;
    }

    .app-title {
        font-size: 20px;
    }

    .app-subtitle {
        font-size: 10px;
    }

    .metrics-row {
        grid-template-columns: 1fr 1fr;
        gap: 6px;
        margin-bottom: 9px;
    }

    .metric-card {
        min-height: 45px;
        padding: 7px 9px;
    }

    .metric-number {
        font-size: 17px;
    }

    .metric-label {
        font-size: 8px;
    }

    .metric-time {
        display: none;
    }

    button[data-baseweb="tab"] {
        font-size: 10px !important;
        padding: 7px 7px !important;
    }

    .turno-header {
        padding: 8px 9px;
    }

    .turno-title {
        font-size: 13px;
    }

    .turno-subtitle {
        display: none;
    }

    .turno-horario {
        font-size: 9px;
        padding: 3px 7px;
    }

    /* Reduz a tabela para caber no celular */
    .grid-header,
    .operator-row {
        grid-template-columns:
            minmax(105px, 1.9fr)
            minmax(70px, 1.2fr)
            repeat(4, minmax(43px, .75fr));
        gap: 3px;
    }

    .grid-header {
        padding: 4px 4px;
    }

    .operator-row {
        padding: 4px;
        border-radius: 7px;
    }

    .grid-header-cell {
        font-size: 7px;
        letter-spacing: 0;
    }

    .operator-name {
        font-size: 9px;
    }

    .operator-function {
        font-size: 7px;
    }

    .status-work,
    .status-off {
        height: 34px;
        border-left-width: 2px;
        font-size: 7px;
    }

    .status-work small,
    .status-off small {
        display: none;
    }

    .admin-action button {
        font-size: 7px !important;
        min-height: 20px !important;
        height: 20px !important;
    }
}


/* ============================================================
   MOBILE MUITO PEQUENO
   ============================================================ */

@media (max-width: 520px) {

    .app-header {
        align-items: flex-start;
    }

    .app-title {
        font-size: 18px;
    }

    .app-subtitle {
        font-size: 9px;
    }

    .amazon-mark {
        width: 29px;
        height: 29px;
        font-size: 15px;
    }

    .period-area {
        padding: 7px 9px 2px 9px;
    }

    .metrics-row {
        grid-template-columns: repeat(4, 1fr);
        gap: 4px;
    }

    .metric-card {
        min-height: 42px;
        padding: 6px 4px;
        justify-content: center;
        text-align: center;
        display: flex;
        flex-direction: column;
        gap: 2px;
    }

    .metric-number {
        font-size: 16px;
    }

    .metric-label {
        font-size: 7px;
    }

    .grid-header,
    .operator-row {
        grid-template-columns:
            minmax(92px, 1.7fr)
            minmax(58px, 1fr)
            repeat(4, minmax(39px, .7fr));
    }

    .operator-name {
        font-size: 8px;
    }

    .operator-function {
        font-size: 6.5px;
    }

    .status-work,
    .status-off {
        height: 31px;
        font-size: 6.5px;
    }

    .grid-header-cell {
        font-size: 6.5px;
    }

    button[data-baseweb="tab"] {
        font-size: 9px !important;
        padding-left: 4px !important;
        padding-right: 4px !important;
    }
}


/* ============================================================
   RODAPÉ
   ============================================================ */

.footer-app {
    color: #98A2B3;
    text-align: center;
    font-size: 9px;
    font-weight: 600;
    margin-top: 20px;
    padding-top: 10px;
    border-top: 1px solid #E5E7EB;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# AUTENTICAÇÃO
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
        INSERT INTO operadores (nome, funcao, turno)
        VALUES (?, ?, ?)
    """, (nome, funcao, turno))

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
    """, (operador_id, semana_id)).fetchone()

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
        "nome": f"{sexta.strftime('%d/%m')} até {segunda.strftime('%d/%m')}",
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
# CABEÇALHO
# ============================================================

col_titulo, col_gestor = st.columns(
    [5, 1],
    vertical_alignment="center"
)

with col_titulo:

    st.markdown("""
        <div class="app-header">
            <div class="app-brand">
                <div class="amazon-mark">A</div>

                <div>
                    <div class="app-title">Amazon</div>
                    <div class="app-subtitle">
                        Escala de monitoramento
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


# ============================================================
# PAINEL DO GESTOR
# ============================================================

with col_gestor:

    if not st.session_state.autenticado:

        with st.popover(
            "👤 Área do Gestor",
            use_container_width=True
        ):

            st.markdown(
                "**Acesso administrativo**"
            )

            st.caption(
                "Entre para alterar a escala ou gerenciar operadores."
            )

            with st.form(
                "login_form",
                clear_on_submit=True
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

        with st.popover(
            "⚙️ Gestão",
            use_container_width=True
        ):

            st.success(
                "Modo Gestor ativo"
            )

            st.divider()

            menu_admin = st.radio(
                "Ação",
                [
                    "Adicionar operador",
                    "Remover operador"
                ],
                label_visibility="collapsed"
            )

            # ------------------------------------------------
            # ADICIONAR
            # ------------------------------------------------

            if menu_admin == "Adicionar operador":

                novo_nome = st.text_input(
                    "Nome"
                ).strip().upper()

                nova_funcao = st.text_input(
                    "Função"
                ).strip().upper()

                novo_turno = st.selectbox(
                    "Turno",
                    ["T1", "T2", "T3"],
                    format_func=lambda x:
                        f"{NOMES_TURNOS[x]} — {HORARIOS[x]}"
                )

                if st.button(
                    "Adicionar operador",
                    use_container_width=True
                ):

                    if novo_nome and nova_funcao:

                        cadastrar_operador(
                            novo_nome,
                            nova_funcao,
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

            # ------------------------------------------------
            # REMOVER
            # ------------------------------------------------

            else:

                operadores_lista = buscar_operadores()

                if operadores_lista:

                    opcoes_remocao = {
                        f"{x[1]} — {x[2]}": x[0]
                        for x in operadores_lista
                    }

                    selecionado = st.selectbox(
                        "Operador",
                        list(opcoes_remocao.keys())
                    )

                    if st.button(
                        "Remover operador",
                        use_container_width=True
                    ):

                        remover_operador(
                            opcoes_remocao[selecionado]
                        )

                        st.success(
                            "Operador removido!"
                        )

                        st.rerun()

                else:

                    st.info(
                        "Nenhum operador cadastrado."
                    )

            st.divider()

            if st.button(
                "🚪 Sair",
                use_container_width=True
            ):

                st.session_state.autenticado = False
                st.rerun()


# ============================================================
# PERÍODO
# ============================================================

semana_labels = [
    x["nome"]
    for x in semanas
]

st.markdown(
    '<div class="period-area">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="period-label">📅 Período da escala</div>',
    unsafe_allow_html=True
)

semana_escolhida = st.selectbox(
    "Período",
    semana_labels,
    index=2,
    label_visibility="collapsed"
)

st.markdown(
    '</div>',
    unsafe_allow_html=True
)

semana = semanas[
    semana_labels.index(semana_escolhida)
]

semana_id = semana["id"]

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


st.markdown(f"""
<div class="metrics-row">

    <div class="metric-card metric-main">
        <div class="metric-number">{total}</div>
        <div class="metric-info">
            <div class="metric-label">Operadores</div>
            <div class="metric-time">Total ativo</div>
        </div>
    </div>

    <div class="metric-card metric-t1">
        <div class="metric-number">{t1}</div>
        <div class="metric-info">
            <div class="metric-label">Turno 1</div>
            <div class="metric-time">07h — 15h</div>
        </div>
    </div>

    <div class="metric-card metric-t2">
        <div class="metric-number">{t2}</div>
        <div class="metric-info">
            <div class="metric-label">Turno 2</div>
            <div class="metric-time">15h — 23h</div>
        </div>
    </div>

    <div class="metric-card metric-t3">
        <div class="metric-number">{t3}</div>
        <div class="metric-info">
            <div class="metric-label">Turno 3</div>
            <div class="metric-time">23h — 07h</div>
        </div>
    </div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# TABS
# ============================================================

aba_t1, aba_t2, aba_t3 = st.tabs([
    f"🌅 T1 · {t1}",
    f"🌆 T2 · {t2}",
    f"🌌 T3 · {t3}"
])

abas_mapeamento = {
    "T1": aba_t1,
    "T2": aba_t2,
    "T3": aba_t3
}


# ============================================================
# RENDERIZAÇÃO DOS TURNOS
# ============================================================

for turno in ["T1", "T2", "T3"]:

    with abas_mapeamento[turno]:

        operadores_turno = [
            x for x in operadores
            if x[3] == turno
        ]

        if not operadores_turno:

            st.markdown(f"""
                <div class="empty-turn">
                    Nenhum operador alocado no {NOMES_TURNOS[turno]}.
                </div>
            """, unsafe_allow_html=True)

            continue


        # ----------------------------------------------------
        # HEADER TURNO
        # ----------------------------------------------------

        st.markdown(f"""
            <div class="turno-header">

                <div class="turno-left">

                    <div class="turno-icon">
                        {EMOJIS_TURNOS[turno]}
                    </div>

                    <div>
                        <span class="turno-title">
                            {NOMES_TURNOS[turno]}
                        </span>

                        <span class="turno-subtitle">
                            {len(operadores_turno)} operadores
                        </span>
                    </div>

                </div>

                <div class="turno-horario">
                    {HORARIOS[turno]}
                </div>

            </div>
        """, unsafe_allow_html=True)


        # ----------------------------------------------------
        # CABEÇALHO DA TABELA
        # ----------------------------------------------------

        header_html = """
        <div class="grid-header">

            <div class="grid-header-cell">
                Operador
            </div>

            <div class="grid-header-cell">
                Função
            </div>
        """

        for dia, _ in DIAS:

            header_html += f"""
                <div class="grid-header-cell day">
                    {dia[:3].upper()}<br>
                    <span style="font-weight:600;color:#98A2B3;">
                        {semana[dia]}
                    </span>
                </div>
            """

        header_html += "</div>"

        st.markdown(
            header_html,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # OPERADORES
        # ----------------------------------------------------

        for operador in operadores_turno:

            operador_id = operador[0]
            nome = operador[1]
            funcao = operador[2]

            status = buscar_status(
                operador_id,
                semana_id
            )

            # -----------------------------------------------
            # STATUS PADRÃO
            # -----------------------------------------------

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


            # -----------------------------------------------
            # LINHA VISUAL
            # -----------------------------------------------

            st.markdown(
                '<div class="operator-row">',
                unsafe_allow_html=True
            )


            # -----------------------------------------------
            # OPERADOR
            # -----------------------------------------------

            st.markdown(f"""
                <div class="operator-info">

                    <div class="operator-name">
                        {nome}
                    </div>

                    <div class="operator-function">
                        {funcao}
                    </div>

                </div>
            """, unsafe_allow_html=True)


            # -----------------------------------------------
            # FUNÇÃO
            # -----------------------------------------------

            st.markdown(f"""
                <div class="operator-info">
                    <div class="operator-function"
                         style="font-size:9px;color:#667085;">
                        {funcao}
                    </div>
                </div>
            """, unsafe_allow_html=True)


            # -----------------------------------------------
            # DIAS
            # -----------------------------------------------

            for i, (dia, _) in enumerate(DIAS):

                valor = status_lista[i]

                if valor == "FOLGA":

                    status_html = """
                        <div class="status-off">
                            FOLGA
                        </div>
                    """

                else:

                    status_html = """
                        <div class="status-work">
                            TRABALHO
                        </div>
                    """

                st.markdown(
                    f"""
                    <div class="status-cell">

                        {status_html}

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )


            # ------------------------------------------------
            # CONTROLES DO GESTOR
            # ------------------------------------------------

            if st.session_state.autenticado:

                controles = st.columns(
                    [2.4, 1.8, 1, 1, 1, 1],
                    gap="small"
                )

                # espaço visual para operador
                controles[0].markdown("")

                controles[1].markdown("")

                for i, (dia, _) in enumerate(DIAS):

                    valor = status_lista[i]

                    novo_valor = (
                        HORARIOS[turno]
                        if valor == "FOLGA"
                        else "FOLGA"
                    )

                    texto_botao = (
                        "Trabalhar"
                        if valor == "FOLGA"
                        else "Folga"
                    )

                    if controles[i + 2].button(
                        texto_botao,
                        key=(
                            f"{operador_id}_"
                            f"{semana_id}_"
                            f"{dia}_"
                            f"{turno}"
                        ),
                        use_container_width=True
                    ):

                        status_lista[i] = novo_valor

                        salvar_status(
                            operador_id,
                            semana_id,
                            *status_lista
                        )

                        st.rerun()


# ============================================================
# RODAPÉ
# ============================================================

st.markdown("""
<div class="footer-app">
    Escala Amazon · Sistema independente de gestão de escala
</div>
""", unsafe_allow_html=True)
