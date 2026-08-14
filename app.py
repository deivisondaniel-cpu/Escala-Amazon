import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Escala do Turno",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# ARQUIVO LOCAL DO SISTEMA
# ============================================================

ARQUIVO_BANCO = "escala_amazon_db.csv"


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

    /* ========================================================
       OCULTAR ELEMENTOS DESNECESSÁRIOS
       ======================================================== */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    .stDecoration {
        display: none !important;
    }


    /* ========================================================
       ESPAÇAMENTO SUPERIOR
       ======================================================== */

    .stMainBlockContainer {
        padding-top: 55px !important;
        padding-bottom: 30px !important;
    }


    /* ========================================================
       TÍTULO PRINCIPAL
       ======================================================== */

    .titulo-principal {
        text-align: center;
        color: #131921;
        font-family: "Segoe UI", sans-serif;
        font-weight: 700;
        font-size: 32px;
        margin-top: 15px;
        margin-bottom: 4px;
        line-height: 1.3;
    }


    /* ========================================================
       SUBTÍTULO
       ======================================================== */

    .subtitulo-principal {
        text-align: center;
        color: #64748B;
        font-family: "Segoe UI", sans-serif;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 32px;
    }


    /* ========================================================
       TÍTULO DO TURNO
       ======================================================== */

    .titulo-turno {
        color: #131921;
        font-family: "Segoe UI", sans-serif;
        font-weight: 700;
        font-size: 22px;
        margin-top: 25px;
        margin-bottom: 15px;
    }


    /* ========================================================
       CARDS DE TRABALHO
       ======================================================== */

    .card-trabalho {
        background: #232F3E;
        color: white;
        padding: 9px 7px;
        border-radius: 7px;
        text-align: center;
        font-weight: 600;
        font-size: 12px;
        border-left: 4px solid #FF9900;
        margin-bottom: 8px;
        min-height: 38px;
    }


    .sub-info {
        font-size: 10px;
        color: #FFB84D;
        font-weight: 600;
        margin-top: 2px;
    }


    /* ========================================================
       CARDS DE FOLGA
       ======================================================== */

    .card-folga {
        background: #F3F4F6;
        color: #374151;
        padding: 9px 7px;
        border-radius: 7px;
        text-align: center;
        font-weight: 700;
        font-size: 12px;
        border-left: 4px solid #94A3B8;
        margin-bottom: 8px;
        min-height: 38px;
    }


    .sub-info-folga {
        font-size: 10px;
        color: #64748B;
        font-weight: 500;
        margin-top: 2px;
    }


    /* ========================================================
       CABEÇALHOS
       ======================================================== */

    .header-col {
        text-align: center;
        font-weight: 700;
        font-size: 12px;
        color: #131921;
        margin-bottom: 8px;
        line-height: 1.25;
    }


    /* ========================================================
       NOME
       ======================================================== */

    .nome-operador {
        padding-top: 9px;
        font-size: 13px;
        margin-bottom: 10px;
        color: #131921;
    }


    /* ========================================================
       FUNÇÃO
       ======================================================== */

    .funcao-operador {
        padding-top: 9px;
        font-size: 12px;
        color: #64748B;
        margin-bottom: 10px;
    }


    /* ========================================================
       LINHA DIVISÓRIA
       ======================================================== */

    .linha-divisoria {
        border: none;
        border-top: 1px solid #E5E7EB;
        margin-top: 0px;
        margin-bottom: 18px;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        background-color: #131921;
    }


    section[data-testid="stSidebar"] * {
        color: white;
    }


    section[data-testid="stSidebar"] input {
        color: #131921 !important;
    }


    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stTextInput label,
    section[data-testid="stSidebar"] .stRadio label {
        color: white !important;
    }


    /* ========================================================
       BOTÕES
       ======================================================== */

    .stButton > button {
        border-radius: 6px;
        font-weight: 600;
    }


    /* ========================================================
       RESPONSIVIDADE
       ======================================================== */

    @media (max-width: 900px) {

        .titulo-principal {
            font-size: 25px;
        }

        .subtitulo-principal {
            font-size: 13px;
        }

    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    """
    <div class="titulo-principal">
        Escala do Turno
    </div>

    <div class="subtitulo-principal">
        Monitoramento Amazon
    </div>
    """,
    unsafe_allow_html=True
)


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
# HORÁRIOS OFICIAIS DOS TURNOS
# ============================================================

HORARIOS_TURNOS = {
    "T1": "07:00 às 15:00",
    "T2": "15:00 às 23:00",
    "T3": "23:00 às 07:00"
}


# ============================================================
# FUNÇÃO DE DATAS
# ============================================================

def obter_datas_semana(deslocamento_semanas=0):

    hoje = datetime.now()

    dias_para_sexta = (hoje.weekday() - 4) % 7

    sexta_atual = hoje - timedelta(
        days=dias_para_sexta
    )

    sexta_alvo = sexta_atual + timedelta(
        weeks=deslocamento_semanas
    )

    sabado = sexta_alvo + timedelta(days=1)
    domingo = sexta_alvo + timedelta(days=2)
    segunda = sexta_alvo + timedelta(days=3)

    return {

        "id_semana":
            sexta_alvo.strftime("%Y_W%W"),

        "rotulo":
            f"Semana de "
            f"{sexta_alvo.strftime('%d/%m')} "
            f"até "
            f"{segunda.strftime('%d/%m')}",

        "Sexta":
            sexta_alvo.strftime("%d/%m"),

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
# SELEÇÃO DE SEMANA
# ============================================================

col_semana, _ = st.columns([3, 3])

with col_semana:

    semana_selecionada = st.selectbox(
        "📅 Período da Escala",
        list(formatos_semanas.keys()),
        index=1
    )


dados_semana = formatos_semanas[
    semana_selecionada
]

id_semana = dados_semana["id_semana"]


# ============================================================
# OPERADORES PADRÃO
# ============================================================

OPERADORES_PADRAO = [

    # ========================================================
    # T1
    # ========================================================

    {
        "Turno": "T1",
        "Nome": "ALAN ARÁUJO",
        "Função": "ANALISTA"
    },

    {
        "Turno": "T1",
        "Nome": "MARGARIDA",
        "Função": "PICKUP"
    },

    {
        "Turno": "T1",
        "Nome": "JOSÉ BRUNO PALHANO",
        "Função": "PICKUP"
    },

    {
        "Turno": "T1",
        "Nome": "CRISTOVÃO MIKELLYS",
        "Função": "DEPART"
    },

    {
        "Turno": "T1",
        "Nome": "PEDRO LUCAS",
        "Função": "DROPOFF"
    },

    {
        "Turno": "T1",
        "Nome": "FELIPE ALLAN",
        "Função": "DROPOFF"
    },

    {
        "Turno": "T1",
        "Nome": "BRUNA BLENDA",
        "Função": "DROPOFF"
    },

    {
        "Turno": "T1",
        "Nome": "CONCEIÇÃO DAIANE",
        "Função": "SEGURANÇA (ONISYS)"
    },

    {
        "Turno": "T1",
        "Nome": "MATHEUS LUSTOSA",
        "Função": "SEGURANÇA/ELOG"
    },


    # ========================================================
    # T2
    # ========================================================

    {
        "Turno": "T2",
        "Nome": "MANUELA PINHEIRO",
        "Função": "LÍDER"
    },

    {
        "Turno": "T2",
        "Nome": "ISABEL",
        "Função": "LÍDER/SEGURANÇA"
    },

    {
        "Turno": "T2",
        "Nome": "ANDREZA OLIVEIRA",
        "Função": "PICKUP"
    },

    {
        "Turno": "T2",
        "Nome": "ROZIANE DA SILVA",
        "Função": "PICKUP"
    },

    {
        "Turno": "T2",
        "Nome": "DAIANE",
        "Função": "SEGURANÇA"
    },

    {
        "Turno": "T2",
        "Nome": "EMANUEL ROBERTO",
        "Função": "DEPART"
    },

    {
        "Turno": "T2",
        "Nome": "TAMMYRIS DA SILVA",
        "Função": "DROPOFF"
    },

    {
        "Turno": "T2",
        "Nome": "RAPHAEL DO NASCIMENTO",
        "Função": "DROPOFF"
    },

    {
        "Turno": "T2",
        "Nome": "LUDMILLA RODRIGUES",
        "Função": "DROPOFF"
    },

    {
        "Turno": "T2",
        "Nome": "MARIA NATHALIA",
        "Função": "SEGURANÇA"
    },

    {
        "Turno": "T2",
        "Nome": "CINAMOR",
        "Função": "ELOG"
    },


    # ========================================================
    # T3
    # ========================================================

    {
        "Turno": "T3",
        "Nome": "WESLEY",
        "Função": "LÍDER"
    },

    {
        "Turno": "T3",
        "Nome": "JOÃO",
        "Função": "LÍDER/SEGURANÇA"
    },

    {
        "Turno": "T3",
        "Nome": "RILDOMAR",
        "Função": "PICKUP"
    },

    {
        "Turno": "T3",
        "Nome": "LUCIANA",
        "Função": "PICKUP"
    },

    {
        "Turno": "T3",
        "Nome": "GLAYLDSON",
        "Função": "SEGURANÇA"
    },

    {
        "Turno": "T3",
        "Nome": "TAYANARA",
        "Função": "DEPART"
    },

    {
        "Turno": "T3",
        "Nome": "RUAN",
        "Função": "DROPOFF"
    },

    {
        "Turno": "T3",
        "Nome": "BÁRBARA",
        "Função": "DROPOFF"
    }
]


# ============================================================
# ESCALA DE FOLGAS PADRÃO
# ============================================================

FOLGAS_PADRAO = {

    "ALAN ARÁUJO": ["Sábado"],
    "MARGARIDA": ["Sábado"],
    "JOSÉ BRUNO PALHANO": ["Sexta"],
    "CRISTOVÃO MIKELLYS": ["Domingo"],
    "PEDRO LUCAS": ["Sábado"],
    "FELIPE ALLAN": ["Domingo"],
    "BRUNA BLENDA": ["Sexta"],
    "CONCEIÇÃO DAIANE": ["Sábado"],
    "MATHEUS LUSTOSA": ["Sexta"],

    "MANUELA PINHEIRO": ["Domingo"],
    "ISABEL": ["Sábado"],
    "ANDREZA OLIVEIRA": ["Sábado"],
    "ROZIANE DA SILVA": ["Sexta"],
    "DAIANE": ["Sexta"],
    "EMANUEL ROBERTO": ["Sexta"],
    "TAMMYRIS DA SILVA": ["Sábado"],
    "RAPHAEL DO NASCIMENTO": ["Domingo"],
    "LUDMILLA RODRIGUES": ["Segunda"],
    "MARIA NATHALIA": ["Domingo"],
    "CINAMOR": ["Segunda"],

    "WESLEY": ["Sexta"],
    "JOÃO": ["Segunda"],
    "RILDOMAR": ["Sábado"],
    "LUCIANA": ["Sexta", "Domingo"],
    "GLAYLDSON": ["Segunda"],
    "TAYANARA": ["Domingo"],
    "RUAN": ["Sábado"],
    "BÁRBARA": []
}


# ============================================================
# CRIAÇÃO DO BANCO
# ============================================================

def criar_semana_padrao(id_da_semana):

    linhas = []

    for operador in OPERADORES_PADRAO:

        turno = operador["Turno"]
        nome = operador["Nome"]

        horario = HORARIOS_TURNOS[turno]

        linha = {

            "SemanaID":
                id_da_semana,

            "Turno":
                turno,

            "Nome":
                nome,

            "Função":
                operador["Função"],

            "Sexta":
                "FOLGA"
                if "Sexta" in FOLGAS_PADRAO.get(nome, [])
                else horario,

            "Sábado":
                "FOLGA"
                if "Sábado" in FOLGAS_PADRAO.get(nome, [])
                else horario,

            "Domingo":
                "FOLGA"
                if "Domingo" in FOLGAS_PADRAO.get(nome, [])
                else horario,

            "Segunda":
                "FOLGA"
                if "Segunda" in FOLGAS_PADRAO.get(nome, [])
                else horario
        }

        linhas.append(linha)

    return pd.DataFrame(linhas)


# ============================================================
# INICIALIZAÇÃO DO BANCO LOCAL
# ============================================================

def inicializar_banco():

    if not os.path.exists(ARQUIVO_BANCO):

        df_inicial = pd.DataFrame()

        for semana in opcoes_semanas:

            df_semana = criar_semana_padrao(
                semana["id_semana"]
            )

            df_inicial = pd.concat(
                [
                    df_inicial,
                    df_semana
                ],
                ignore_index=True
            )

        df_inicial.to_csv(
            ARQUIVO_BANCO,
            index=False,
            encoding="utf-8-sig"
        )


# ============================================================
# CARREGAR BANCO
# ============================================================

inicializar_banco()

df_banco = pd.read_csv(
    ARQUIVO_BANCO,
    encoding="utf-8-sig"
)


# ============================================================
# CRIAR SEMANA AUTOMATICAMENTE
# ============================================================

if df_banco[
    df_banco["SemanaID"] == id_semana
].empty:

    semanas_existentes = df_banco["SemanaID"].unique()

    if len(semanas_existentes) > 0:

        ultima_semana = semanas_existentes[-1]

        df_nova = df_banco[
            df_banco["SemanaID"] == ultima_semana
        ].copy()

        df_nova["SemanaID"] = id_semana

        df_banco = pd.concat(
            [
                df_banco,
                df_nova
            ],
            ignore_index=True
        )

    else:

        df_nova = criar_semana_padrao(
            id_semana
        )

        df_banco = pd.concat(
            [
                df_banco,
                df_nova
            ],
            ignore_index=True
        )

    df_banco.to_csv(
        ARQUIVO_BANCO,
        index=False,
        encoding="utf-8-sig"
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <h2 style="
            color:#FF9900;
            margin-top:0;
            margin-bottom:4px;
        ">
            Área do Gestor
        </h2>

        <div style="
            color:#94A3B8;
            font-size:12px;
            margin-bottom:20px;
        ">
            Administração da escala
        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # LOGIN
    # ========================================================

    if not st.session_state.autenticado:

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

                    st.query_params["logged_in"] = "true"

                    st.rerun()

                else:

                    st.error(
                        "Usuário ou senha incorretos."
                    )


    # ========================================================
    # ÁREA ADMINISTRATIVA
    # ========================================================

    else:

        st.success(
            "Modo Gestão ativo"
        )

        st.divider()


        # ====================================================
        # CADASTRAR
        # ====================================================

        st.markdown(
            "### ➕ Novo operador"
        )

        novo_nome = st.text_input(
            "Nome"
        ).upper().strip()

        nova_funcao = st.text_input(
            "Função"
        ).upper().strip()

        novo_turno = st.selectbox(
            "Turno",
            [
                "T1 — 07:00 às 15:00",
                "T2 — 15:00 às 23:00",
                "T3 — 23:00 às 07:00"
            ]
        )


        if st.button(
            "Adicionar operador",
            use_container_width=True
        ):

            if novo_nome and nova_funcao:

                turno_id = novo_turno[:2]

                horario = HORARIOS_TURNOS[
                    turno_id
                ]

                nova_linha = {

                    "SemanaID":
                        id_semana,

                    "Turno":
                        turno_id,

                    "Nome":
                        novo_nome,

                    "Função":
                        nova_funcao,

                    "Sexta":
                        horario,

                    "Sábado":
                        horario,

                    "Domingo":
                        horario,

                    "Segunda":
                        horario
                }

                df_banco = pd.concat(
                    [
                        df_banco,
                        pd.DataFrame([nova_linha])
                    ],
                    ignore_index=True
                )

                df_banco.to_csv(
                    ARQUIVO_BANCO,
                    index=False,
                    encoding="utf-8-sig"
                )

                st.success(
                    f"{novo_nome} adicionado."
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

        operadores_semana = sorted(
            df_banco[
                df_banco["SemanaID"] == id_semana
            ]["Nome"].unique()
        )


        if operadores_semana:

            operador_remover = st.selectbox(
                "Operador",
                operadores_semana
            )

            tipo_remocao = st.radio(
                "Remover de:",
                [
                    "Semana atual",
                    "Todo o sistema"
                ]
            )


            if st.button(
                "Confirmar remoção",
                type="primary",
                use_container_width=True
            ):

                if tipo_remocao == "Semana atual":

                    df_banco = df_banco[
                        ~(
                            (
                                df_banco["SemanaID"]
                                == id_semana
                            )
                            &
                            (
                                df_banco["Nome"]
                                == operador_remover
                            )
                        )
                    ]

                else:

                    df_banco = df_banco[
                        df_banco["Nome"]
                        != operador_remover
                    ]

                df_banco.to_csv(
                    ARQUIVO_BANCO,
                    index=False,
                    encoding="utf-8-sig"
                )

                st.success(
                    f"{operador_remover} removido."
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

            st.query_params.clear()

            st.rerun()


# ============================================================
# ESCALA ATUAL
# ============================================================

df_tela = df_banco[
    df_banco["SemanaID"] == id_semana
]


MAPA_TURNOS = {
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
# EXIBIÇÃO DOS TURNOS
# ============================================================

for turno_id, nome_turno in MAPA_TURNOS.items():

    df_turno = df_tela[
        df_tela["Turno"] == turno_id
    ]


    if df_turno.empty:
        continue


    horario_turno = HORARIOS_TURNOS[
        turno_id
    ]


    # ========================================================
    # CABEÇALHO DO TURNO
    # ========================================================

    st.markdown(
        f"""
        <div class="titulo-turno">
            🕒 {nome_turno}
            <span style="
                color:#64748B;
                font-size:13px;
                font-weight:500;
                margin-left:8px;
            ">
                {horario_turno}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )


    colunas = st.columns(
        [
            2.5,
            2,
            1.8,
            1.8,
            1.8,
            1.8
        ]
    )


    # ========================================================
    # CABEÇALHO
    # ========================================================

    colunas[0].markdown(
        "<div class='header-col' "
        "style='text-align:left;'>"
        "OPERADOR"
        "</div>",
        unsafe_allow_html=True
    )


    colunas[1].markdown(
        "<div class='header-col' "
        "style='text-align:left;'>"
        "FUNÇÃO"
        "</div>",
        unsafe_allow_html=True
    )


    for indice, dia in enumerate(
        DIAS,
        2
    ):

        colunas[indice].markdown(
            f"""
            <div class="header-col">
                {dia.upper()}
                <br>
                <span style="
                    font-size:10px;
                    color:#64748B;
                    font-weight:500;
                ">
                    {dados_semana[dia]}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )


    st.markdown(
        "<hr class='linha-divisoria'>",
        unsafe_allow_html=True
    )


    # ========================================================
    # OPERADORES
    # ========================================================

    for _, row in df_turno.iterrows():

        colunas = st.columns(
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

        colunas[0].markdown(
            f"""
            <div class="nome-operador">
                <b>{row["Nome"]}</b>
            </div>
            """,
            unsafe_allow_html=True
        )


        # ====================================================
        # FUNÇÃO
        # ====================================================

        colunas[1].markdown(
            f"""
            <div class="funcao-operador">
                {row["Função"]}
            </div>
            """,
            unsafe_allow_html=True
        )


        # ====================================================
        # DIAS
        # ====================================================

        for indice, dia in enumerate(
            DIAS,
            2
        ):

            status = str(
                row[dia]
            )


            # ================================================
            # TRABALHO
            # ================================================

            if status != "FOLGA":

                colunas[indice].markdown(
                    f"""
                    <div class="card-trabalho">
                        TRABALHO
                        <div class="sub-info">
                            {status}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # ================================================
            # FOLGA
            # ================================================

            else:

                colunas[indice].markdown(
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


            # ================================================
            # BOTÃO DE ALTERAÇÃO
            # ================================================

            if st.session_state.autenticado:

                novo_status = (
                    "FOLGA"
                    if status != "FOLGA"
                    else HORARIOS_TURNOS[turno_id]
                )


                if colunas[indice].button(
                    "🔄 Alternar",
                    key=(
                        f"{id_semana}_"
                        f"{turno_id}_"
                        f"{row['Nome']}_"
                        f"{dia}"
                    ),
                    use_container_width=True
                ):

                    filtro = (
                        (df_banco["SemanaID"] == id_semana)
                        &
                        (df_banco["Nome"] == row["Nome"])
                    )


                    indices = df_banco[
                        filtro
                    ].index


                    if len(indices) > 0:

                        indice_banco = indices[0]

                        df_banco.at[
                            indice_banco,
                            dia
                        ] = novo_status


                        df_banco.to_csv(
                            ARQUIVO_BANCO,
                            index=False,
                            encoding="utf-8-sig"
                        )

                        st.rerun()


    st.write("")


# ============================================================
# RODAPÉ
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#94A3B8;
        font-size:11px;
        margin-top:35px;
        padding-top:15px;
        border-top:1px solid #E5E7EB;
    ">
        Monitoramento Amazon • Escala do Turno
    </div>
    """,
    unsafe_allow_html=True
)
