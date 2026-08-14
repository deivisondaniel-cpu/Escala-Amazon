import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, timedelta


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Escala do Turno",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# ARQUIVOS INTERNOS DA APLICAÇÃO
# ============================================================

ARQUIVO_BANCO = "escala_amazon_db.json"


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
# CSS PRINCIPAL
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       STREAMLIT
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
       CABEÇALHO
       ======================================================== */

    .topo-sistema {
        width: 100%;
        margin-top: 25px;
        margin-bottom: 28px;
        padding: 18px 25px;
        border-radius: 14px;
        background: linear-gradient(
            135deg,
            #131921 0%,
            #1d2939 100%
        );
        border: 1px solid #374151;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    }


    .topo-conteudo {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 20px;
    }


    .marca {
        display: flex;
        align-items: center;
        gap: 16px;
    }


    .logo-losung {
        height: 48px;
        width: auto;
        max-width: 180px;
        object-fit: contain;
    }


    .titulo-sistema {
        color: white;
        font-family: 'Segoe UI', sans-serif;
        font-size: 30px;
        font-weight: 700;
        line-height: 1.2;
        margin: 0;
        padding: 8px 0;
    }


    .subtitulo-sistema {
        color: #FF9900;
        font-family: 'Segoe UI', sans-serif;
        font-size: 13px;
        font-weight: 600;
        margin-top: 5px;
    }


    .status-sistema {
        display: flex;
        align-items: center;
        gap: 7px;
        color: #d1d5db;
        font-size: 12px;
        font-weight: 600;
        white-space: nowrap;
    }


    .bolinha-online {
        width: 9px;
        height: 9px;
        background-color: #22c55e;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px rgba(34,197,94,0.6);
    }


    /* ========================================================
       TÍTULOS DOS TURNOS
       ======================================================== */

    .titulo-turno {
        color: #131921;
        font-size: 21px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 12px;
        padding-left: 12px;
        border-left: 4px solid #FF9900;
    }


    .horario-turno {
        color: #64748B;
        font-size: 12px;
        font-weight: 600;
        margin-left: 16px;
    }


    /* ========================================================
       CABEÇALHOS
       ======================================================== */

    .header-col {
        text-align: center;
        font-weight: 700;
        font-size: 12px;
        color: #374151;
        margin-bottom: 10px;
    }


    /* ========================================================
       OPERADOR
       ======================================================== */

    .nome-operador {
        padding-top: 9px;
        font-size: 13px;
        margin-bottom: 12px;
        color: #111827;
    }


    .funcao-operador {
        padding-top: 9px;
        font-size: 11px;
        color: #64748B;
        margin-bottom: 12px;
        font-weight: 600;
    }


    /* ========================================================
       CARD TRABALHO
       ======================================================== */

    .card-trabalho {
        background: linear-gradient(
            135deg,
            #232F3E,
            #1d2939
        );
        color: white;
        padding: 8px 7px;
        border-radius: 8px;
        text-align: center;
        font-weight: 700;
        font-size: 11px;
        border-left: 4px solid #FF9900;
        margin-bottom: 7px;
        min-height: 43px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }


    .sub-info {
        font-size: 10px;
        color: #FFB84D;
        font-weight: 700;
        margin-top: 3px;
    }


    /* ========================================================
       CARD FOLGA
       ======================================================== */

    .card-folga {
        background: linear-gradient(
            135deg,
            #f3f4f6,
            #e5e7eb
        );
        color: #374151;
        padding: 8px 7px;
        border-radius: 8px;
        text-align: center;
        font-weight: 800;
        font-size: 11px;
        border-left: 4px solid #9ca3af;
        margin-bottom: 7px;
        min-height: 43px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }


    .sub-info-folga {
        font-size: 10px;
        color: #6b7280;
        font-weight: 500;
        margin-top: 3px;
    }


    /* ========================================================
       LINHA
       ======================================================== */

    .linha-separadora {
        margin-top: 2px;
        margin-bottom: 16px;
        border: none;
        border-top: 1px solid #e5e7eb;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    [data-testid="stSidebar"] {
        background-color: #131921;
    }


    [data-testid="stSidebar"] * {
        color: white;
    }


    [data-testid="stSidebar"] input {
        color: #111827 !important;
    }


    [data-testid="stSidebar"] label {
        color: #e5e7eb !important;
    }


    /* ========================================================
       BOTÕES
       ======================================================== */

    .stButton > button {
        border-radius: 7px;
        font-weight: 600;
    }


    /* ========================================================
       RESPONSIVIDADE
       ======================================================== */

    @media (max-width: 800px) {

        .topo-sistema {
            margin-top: 15px;
            padding: 15px;
        }

        .titulo-sistema {
            font-size: 23px;
        }

        .subtitulo-sistema {
            font-size: 11px;
        }

        .logo-losung {
            height: 38px;
        }

        .status-sistema {
            display: none;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FUNÇÃO - DATAS DA SEMANA
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
        "id_semana": sexta_alvo.strftime("%Y_W%W"),

        "rotulo":
            f"Semana de "
            f"{sexta_alvo.strftime('%d/%m')} "
            f"até "
            f"{segunda.strftime('%d/%m')}",

        "Sexta": sexta_alvo.strftime("%d/%m"),
        "Sábado": sabado.strftime("%d/%m"),
        "Domingo": domingo.strftime("%d/%m"),
        "Segunda": segunda.strftime("%d/%m")
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
# BANCO DE DADOS
# ============================================================

def salvar_banco(dados):

    with open(
        ARQUIVO_BANCO,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def carregar_banco():

    if not os.path.exists(
        ARQUIVO_BANCO
    ):

        return {}

    try:

        with open(
            ARQUIVO_BANCO,
            "r",
            encoding="utf-8"
        ) as arquivo:

            return json.load(arquivo)

    except Exception:

        return {}


# ============================================================
# OPERADORES PADRÃO
# ============================================================

OPERADORES_PADRAO = [

    # T1
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

    # T2
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

    # T3
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
# CRIA SEMANA
# ============================================================

def criar_semana(id_semana):

    banco = carregar_banco()

    if id_semana in banco:
        return banco

    operadores = []

    for operador in OPERADORES_PADRAO:

        registro = {
            "Turno": operador["Turno"],
            "Nome": operador["Nome"],
            "Função": operador["Função"],
            "Sexta": HORARIOS_TURNOS[
                operador["Turno"]
            ],
            "Sábado": HORARIOS_TURNOS[
                operador["Turno"]
            ],
            "Domingo": HORARIOS_TURNOS[
                operador["Turno"]
            ],
            "Segunda": HORARIOS_TURNOS[
                operador["Turno"]
            ]
        }

        operadores.append(registro)


    # Folgas padrão
    folgas = {
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


    for operador in operadores:

        nome = operador["Nome"]

        for dia in folgas.get(nome, []):

            operador[dia] = "FOLGA"


    banco[id_semana] = operadores

    salvar_banco(banco)

    return banco


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
# SEMANA
# ============================================================

col_semana, _ = st.columns([3, 5])

with col_semana:

    semana_selecionada = st.selectbox(
        "📅 Período da Escala",
        list(formatos_semanas.keys()),
        index=1
    )


dados_semana = formatos_semanas[
    semana_selecionada
]

id_semana = dados_semana[
    "id_semana"
]


# ============================================================
# GARANTE BANCO DA SEMANA
# ============================================================

banco = criar_semana(id_semana)

banco = carregar_banco()

dados = banco.get(
    id_semana,
    []
)


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    """
    <div class="topo-sistema">

        <div class="topo-conteudo">

            <div class="marca">

                <img
                    src="https://losungexpress.app.br/assets/img/logo.png"
                    class="logo-losung"
                    onerror="this.style.display='none'"
                >

                <div>

                    <div class="titulo-sistema">
                        Escala do Turno
                    </div>

                    <div class="subtitulo-sistema">
                        Monitoramento Amazon
                    </div>

                </div>

            </div>


            <div class="status-sistema">

                <span class="bolinha-online"></span>

                Sistema operacional

            </div>

        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:10px 0 20px 0;
        ">
            <div style="
                color:#FF9900;
                font-size:18px;
                font-weight:700;
            ">
                🔐 Área de Gestão
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # LOGIN
    # ========================================================

    if not st.session_state.autenticado:

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


    # ========================================================
    # GESTÃO
    # ========================================================

    else:

        st.success(
            "Modo Gestão ativo"
        )

        st.divider()


        # ====================================================
        # CADASTRO
        # ====================================================

        st.markdown(
            "**➕ Novo operador**"
        )


        novo_nome = st.text_input(
            "Nome",
            key="novo_nome"
        ).upper().strip()


        nova_funcao = st.text_input(
            "Função",
            key="nova_funcao"
        ).upper().strip()


        novo_turno = st.selectbox(
            "Turno",
            [
                "Turno 1",
                "Turno 2",
                "Turno 3"
            ],
            key="novo_turno"
        )


        if st.button(
            "Adicionar operador",
            use_container_width=True
        ):

            if novo_nome and nova_funcao:

                turno_id = (
                    "T1"
                    if novo_turno == "Turno 1"
                    else
                    "T2"
                    if novo_turno == "Turno 2"
                    else
                    "T3"
                )


                if any(
                    x["Nome"] == novo_nome
                    for x in dados
                ):

                    st.warning(
                        "Esse operador já existe."
                    )

                else:

                    novo_operador = {

                        "Turno": turno_id,

                        "Nome": novo_nome,

                        "Função": nova_funcao,

                        "Sexta":
                            HORARIOS_TURNOS[turno_id],

                        "Sábado":
                            HORARIOS_TURNOS[turno_id],

                        "Domingo":
                            HORARIOS_TURNOS[turno_id],

                        "Segunda":
                            HORARIOS_TURNOS[turno_id]
                    }


                    dados.append(
                        novo_operador
                    )

                    banco[id_semana] = dados

                    salvar_banco(
                        banco
                    )

                    st.success(
                        f"{novo_nome} adicionado."
                    )

                    st.rerun()


        st.divider()


        # ====================================================
        # REMOÇÃO
        # ====================================================

        st.markdown(
            "**❌ Remover operador**"
        )


        nomes = sorted(
            [
                x["Nome"]
                for x in dados
            ]
        )


        if nomes:

            remover = st.selectbox(
                "Operador",
                nomes
            )


            if st.button(
                "Remover da escala",
                type="primary",
                use_container_width=True
            ):

                dados = [
                    x
                    for x in dados
                    if x["Nome"] != remover
                ]


                banco[id_semana] = dados

                salvar_banco(
                    banco
                )

                st.success(
                    f"{remover} removido."
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
# EXIBIÇÃO DOS TURNOS
# ============================================================

for turno_id in [
    "T1",
    "T2",
    "T3"
]:

    operadores_turno = [
        x
        for x in dados
        if x["Turno"] == turno_id
    ]


    if not operadores_turno:
        continue


    # ========================================================
    # TÍTULO DO TURNO
    # ========================================================

    st.markdown(
        f"""
        <div class="titulo-turno">

            {NOMES_TURNOS[turno_id]}

            <span class="horario-turno">
                {HORARIOS_TURNOS[turno_id]}
            </span>

        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # CABEÇALHO
    # ========================================================

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


    for i, dia in enumerate(
        DIAS,
        2
    ):

        colunas[i].markdown(
            f"""
            <div class='header-col'>
                {dia.upper()}<br>
                <span style="
                    font-size:10px;
                    color:#64748B;
                ">
                    {dados_semana[dia]}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )


    st.markdown(
        "<hr class='linha-separadora'>",
        unsafe_allow_html=True
    )


    # ========================================================
    # OPERADORES
    # ========================================================

    for operador in operadores_turno:

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


        # ----------------------------------------------------
        # NOME
        # ----------------------------------------------------

        colunas[0].markdown(
            f"""
            <div class='nome-operador'>
                <b>{operador["Nome"]}</b>
            </div>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # FUNÇÃO
        # ----------------------------------------------------

        colunas[1].markdown(
            f"""
            <div class='funcao-operador'>
                {operador["Função"]}
            </div>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # DIAS
        # ----------------------------------------------------

        for i, dia in enumerate(
            DIAS,
            2
        ):

            status = operador.get(
                dia,
                HORARIOS_TURNOS[turno_id]
            )


            if status == "FOLGA":

                colunas[i].markdown(
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

            else:

                colunas[i].markdown(
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


            # ------------------------------------------------
            # BOTÃO DE ALTERAÇÃO
            # ------------------------------------------------

            if st.session_state.autenticado:

                novo_status = (
                    "FOLGA"
                    if status != "FOLGA"
                    else HORARIOS_TURNOS[turno_id]
                )


                if colunas[i].button(
                    "🔄 Alternar",
                    key=(
                        f"{id_semana}_"
                        f"{turno_id}_"
                        f"{operador['Nome']}_"
                        f"{dia}"
                    ),
                    use_container_width=True
                ):

                    for item in dados:

                        if (
                            item["Nome"]
                            == operador["Nome"]
                            and item["Turno"]
                            == turno_id
                        ):

                            item[dia] = novo_status

                            break


                    banco[id_semana] = dados

                    salvar_banco(
                        banco
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
        margin-top:35px;
        padding:15px;
        border-top:1px solid #e5e7eb;
        color:#9ca3af;
        font-size:10px;
    ">
        Monitoramento Amazon
        • Escala do Turno
    </div>
    """,
    unsafe_allow_html=True
)
