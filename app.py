import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Escala monitoramento",
    page_icon="📦",
    layout="wide"
)

ARQUIVO_BANCO = "escala_amazon_db_v2.csv"


# ============================================================
# CSS
# ============================================================

st.markdown("""
    <style>

    /* ========================================================
       ELEMENTOS PADRÃO DESNECESSÁRIOS DO STREAMLIT
       NÃO ESCONDER O HEADER.
       O HEADER CONTÉM O CONTROLE DA SIDEBAR.
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
       TÍTULO
       ======================================================== */

    .titulo {
        text-align: center;
        color: #131921;
        font-family: 'Segoe UI', sans-serif;
        font-weight: bold;
        margin-bottom: 25px;
        font-size: 28px;
    }


    /* ========================================================
       CARD - TRABALHO
       ======================================================== */

    .card-trabalho {
        background-color: #232F3E;
        color: white;
        padding: 6px 8px;
        border-radius: 6px;
        text-align: center;
        font-weight: 600;
        font-size: 12px;
        border-left: 4px solid #FF9900;
        margin-bottom: 12px;
    }


    /* ========================================================
       CARD - FOLGA
       ======================================================== */

    .card-folga {
        background-color: #FDF1AA;
        color: #403000;
        padding: 6px 8px;
        border-radius: 6px;
        text-align: center;
        font-weight: bold;
        font-size: 12px;
        border-left: 4px solid #E6A100;
        margin-bottom: 12px;
    }


    /* ========================================================
       INFORMAÇÕES DOS CARDS
       ======================================================== */

    .sub-info {
        font-size: 10px;
        color: #FF9900;
        font-weight: bold;
    }

    .sub-info-folga {
        font-size: 10px;
        color: #8F7014;
        font-weight: normal;
    }


    /* ========================================================
       CABEÇALHOS
       ======================================================== */

    .header-col {
        text-align: center;
        font-weight: bold;
        font-size: 13px;
        color: #131921;
        margin-bottom: 10px;
    }


    /* ========================================================
       NOME E FUNÇÃO
       ======================================================== */

    .nome-operador {
        padding-top: 8px;
        font-size: 13px;
        margin-bottom: 12px;
    }

    .funcao-operador {
        padding-top: 8px;
        font-size: 12px;
        color: #64748B;
        margin-bottom: 12px;
    }


    /* ========================================================
       ESPAÇAMENTO
       ======================================================== */

    .stMainBlockContainer {
        padding-top: 20px !important;
        padding-bottom: 20px !important;
    }

    </style>
""", unsafe_allow_html=True)


# ============================================================
# TÍTULO
# ============================================================

st.markdown(
    "<h1 class='titulo'>Escala Amazon</h1>",
    unsafe_allow_html=True
)


# ============================================================
# PERSISTÊNCIA DO LOGIN
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
#
# IMPORTANTE:
# ESTES HORÁRIOS SÃO A FONTE OFICIAL DO SISTEMA.
#
# NÃO VÊM DE:
# - GOOGLE SHEETS
# - CSV
# - EXCEL
#
# ============================================================

horarios_turnos = {
    "T1": "07:00 às 15:00",
    "T2": "15:00 às 23:00",
    "T3": "23:00 às 07:00"
}


# ============================================================
# FUNÇÃO CENTRAL DO HORÁRIO
#
# QUALQUER LUGAR DO SISTEMA QUE PRECISAR DO HORÁRIO
# DEVE USAR ESTA FUNÇÃO.
# ============================================================

def obter_horario_turno(turno):

    return horarios_turnos.get(
        turno,
        "HORÁRIO NÃO CONFIGURADO"
    )


# ============================================================
# DATAS AUTOMÁTICAS
# ============================================================

def obter_datas_semana(deslocamento_semanas=0):

    hoje = datetime.now()

    dias_para_atras = (hoje.weekday() - 4) % 7

    sexta_atual = hoje - timedelta(
        days=dias_para_atras
    )

    sexta_alvo = sexta_atual + timedelta(
        weeks=deslocamento_semanas
    )

    sabado_alvo = sexta_alvo + timedelta(days=1)

    domingo_alvo = sexta_alvo + timedelta(days=2)

    segunda_alvo = sexta_alvo + timedelta(days=3)

    return {
        "id_semana":
            sexta_alvo.strftime("%Y_W%W"),

        "rotulo":
            f"Semana de {sexta_alvo.strftime('%d/%m')} "
            f"até {segunda_alvo.strftime('%d/%m')}",

        "Sexta":
            sexta_alvo.strftime("%d/%m"),

        "Sábado":
            sabado_alvo.strftime("%d/%m"),

        "Domingo":
            domingo_alvo.strftime("%d/%m"),

        "Segunda":
            segunda_alvo.strftime("%d/%m")
    }


# ============================================================
# OPÇÕES DE SEMANA
# ============================================================

opcoes_semanas = [
    obter_datas_semana(i)
    for i in range(-1, 4)
]

formatos_semanas = {
    opt["rotulo"]: opt
    for opt in opcoes_semanas
}


# ============================================================
# SELEÇÃO DA SEMANA
# ============================================================

col_topo1, _ = st.columns([3, 3])

with col_topo1:

    semana_selecionada_rotulo = st.selectbox(
        "📅 Período da Escala:",
        list(formatos_semanas.keys()),
        index=1
    )


dados_semana_ativa = formatos_semanas[
    semana_selecionada_rotulo
]

id_semana_ativa = dados_semana_ativa[
    "id_semana"
]


# ============================================================
# OPERADORES PADRÃO
#
# ESTES SÃO OS DADOS INICIAIS DO SISTEMA.
# ============================================================

operadores_padrao = [

    # ========================================================
    # T1
    # ========================================================

    {
        "Turno": "T1",
        "Nome": "ALAN ARÁUJO",
        "Função": "ANALISTA",
        "Sexta": "07:00 às 15:00",
        "Sábado": "FOLGA",
        "Domingo": "07:00 às 15:00",
        "Segunda": "07:00 às 15:00"
    },

    {
        "Turno": "T1",
        "Nome": "MARGARIDA",
        "Função": "PICKUP",
        "Sexta": "07:00 às 15:00",
        "Sábado": "FOLGA",
        "Domingo": "07:00 às 15:00",
        "Segunda": "07:00 às 15:00"
    },

    {
        "Turno": "T1",
        "Nome": "JOSÉ BRUNO PALHANO",
        "Função": "PICKUP",
        "Sexta": "FOLGA",
        "Sábado": "07:00 às 15:00",
        "Domingo": "07:00 às 15:00",
        "Segunda": "07:00 às 15:00"
    },

    {
        "Turno": "T1",
        "Nome": "CRISTOVÃO MIKELLYS",
        "Função": "DEPART",
        "Sexta": "07:00 às 15:00",
        "Sábado": "07:00 às 15:00",
        "Domingo": "FOLGA",
        "Segunda": "07:00 às 15:00"
    },

    {
        "Turno": "T1",
        "Nome": "PEDRO LUCAS",
        "Função": "DROPOFF",
        "Sexta": "07:00 às 15:00",
        "Sábado": "FOLGA",
        "Domingo": "07:00 às 15:00",
        "Segunda": "07:00 às 15:00"
    },

    {
        "Turno": "T1",
        "Nome": "FELIPE ALLAN",
        "Função": "DROPOFF",
        "Sexta": "07:00 às 15:00",
        "Sábado": "07:00 às 15:00",
        "Domingo": "FOLGA",
        "Segunda": "07:00 às 15:00"
    },

    {
        "Turno": "T1",
        "Nome": "BRUNA BLENDA",
        "Função": "DROPOFF",
        "Sexta": "FOLGA",
        "Sábado": "07:00 às 15:00",
        "Domingo": "07:00 às 15:00",
        "Segunda": "07:00 às 15:00"
    },

    {
        "Turno": "T1",
        "Nome": "CONCEIÇÃO DAIANE",
        "Função": "SEGURANÇA (ONISYS)",
        "Sexta": "07:00 às 15:00",
        "Sábado": "FOLGA",
        "Domingo": "07:00 às 15:00",
        "Segunda": "07:00 às 15:00"
    },

    {
        "Turno": "T1",
        "Nome": "MATHEUS LUSTOSA",
        "Função": "SEGURANÇA/ELOG",
        "Sexta": "FOLGA",
        "Sábado": "07:00 às 15:00",
        "Domingo": "07:00 às 15:00",
        "Segunda": "07:00 às 15:00"
    },


    # ========================================================
    # T2
    # ========================================================

    {
        "Turno": "T2",
        "Nome": "MANUELA PINHEIRO",
        "Função": "LÍDER",
        "Sexta": "15:00 às 23:00",
        "Sábado": "15:00 às 23:00",
        "Domingo": "FOLGA",
        "Segunda": "15:00 às 23:00"
    },

    {
        "Turno": "T2",
        "Nome": "ISABEL",
        "Função": "LÍDER/SEGURANÇA",
        "Sexta": "15:00 às 23:00",
        "Sábado": "FOLGA",
        "Domingo": "15:00 às 23:00",
        "Segunda": "15:00 às 23:00"
    },

    {
        "Turno": "T2",
        "Nome": "ANDREZA OLIVEIRA",
        "Função": "PICKUP",
        "Sexta": "15:00 às 23:00",
        "Sábado": "FOLGA",
        "Domingo": "15:00 às 23:00",
        "Segunda": "15:00 às 23:00"
    },

    {
        "Turno": "T2",
        "Nome": "ROZIANE DA SILVA",
        "Função": "PICKUP",
        "Sexta": "FOLGA",
        "Sábado": "15:00 às 23:00",
        "Domingo": "15:00 às 23:00",
        "Segunda": "15:00 às 23:00"
    },

    {
        "Turno": "T2",
        "Nome": "DAIANE",
        "Função": "SEGURANÇA",
        "Sexta": "FOLGA",
        "Sábado": "15:00 às 23:00",
        "Domingo": "15:00 às 23:00",
        "Segunda": "15:00 às 23:00"
    },

    {
        "Turno": "T2",
        "Nome": "EMANUEL ROBERTO",
        "Função": "DEPART",
        "Sexta": "FOLGA",
        "Sábado": "15:00 às 23:00",
        "Domingo": "15:00 às 23:00",
        "Segunda": "15:00 às 23:00"
    },

    {
        "Turno": "T2",
        "Nome": "TAMMYRIS DA SILVA",
        "Função": "DROPOFF",
        "Sexta": "15:00 às 23:00",
        "Sábado": "FOLGA",
        "Domingo": "15:00 às 23:00",
        "Segunda": "15:00 às 23:00"
    },

    {
        "Turno": "T2",
        "Nome": "RAPHAEL DO NASCIMENTO",
        "Função": "DROPOFF",
        "Sexta": "15:00 às 23:00",
        "Sábado": "15:00 às 23:00",
        "Domingo": "FOLGA",
        "Segunda": "15:00 às 23:00"
    },

    {
        "Turno": "T2",
        "Nome": "LUDMILLA RODRIGUES",
        "Função": "DROPOFF",
        "Sexta": "15:00 às 23:00",
        "Sábado": "15:00 às 23:00",
        "Domingo": "15:00 às 23:00",
        "Segunda": "FOLGA"
    },

    {
        "Turno": "T2",
        "Nome": "MARIA NATHALIA",
        "Função": "SEGURANÇA",
        "Sexta": "15:00 às 23:00",
        "Sábado": "15:00 às 23:00",
        "Domingo": "FOLGA",
        "Segunda": "15:00 às 23:00"
    },

    {
        "Turno": "T2",
        "Nome": "CINAMOR",
        "Função": "ELOG",
        "Sexta": "15:00 às 23:00",
        "Sábado": "15:00 às 23:00",
        "Domingo": "15:00 às 23:00",
        "Segunda": "FOLGA"
    },


    # ========================================================
    # T3
    # ========================================================

    {
        "Turno": "T3",
        "Nome": "WESLEY",
        "Função": "LÍDER",
        "Sexta": "FOLGA",
        "Sábado": "23:00 às 07:00",
        "Domingo": "23:00 às 07:00",
        "Segunda": "23:00 às 07:00"
    },

    {
        "Turno": "T3",
        "Nome": "JOÃO",
        "Função": "LÍDER/SEGURANÇA",
        "Sexta": "23:00 às 07:00",
        "Sábado": "23:00 às 07:00",
        "Domingo": "23:00 às 07:00",
        "Segunda": "FOLGA"
    },

    {
        "Turno": "T3",
        "Nome": "RILDOMAR",
        "Função": "PICKUP",
        "Sexta": "23:00 às 07:00",
        "Sábado": "FOLGA",
        "Domingo": "23:00 às 07:00",
        "Segunda": "23:00 às 07:00"
    },

    {
        "Turno": "T3",
        "Nome": "LUCIANA",
        "Função": "PICKUP",
        "Sexta": "FOLGA",
        "Sábado": "23:00 às 07:00",
        "Domingo": "FOLGA",
        "Segunda": "23:00 às 07:00"
    },

    {
        "Turno": "T3",
        "Nome": "GLAYLDSON",
        "Função": "SEGURANÇA",
        "Sexta": "23:00 às 07:00",
        "Sábado": "23:00 às 07:00",
        "Domingo": "23:00 às 07:00",
        "Segunda": "FOLGA"
    },

    {
        "Turno": "T3",
        "Nome": "TAYANARA",
        "Função": "DEPART",
        "Sexta": "23:00 às 07:00",
        "Sábado": "23:00 às 07:00",
        "Domingo": "FOLGA",
        "Segunda": "23:00 às 07:00"
    },

    {
        "Turno": "T3",
        "Nome": "RUAN",
        "Função": "DROPOFF",
        "Sexta": "23:00 às 07:00",
        "Sábado": "FOLGA",
        "Domingo": "23:00 às 07:00",
        "Segunda": "23:00 às 07:00"
    },

    {
        "Turno": "T3",
        "Nome": "BÁRBARA",
        "Função": "DROPOFF",
        "Sexta": "23:00 às 07:00",
        "Sábado": "23:00 às 07:00",
        "Domingo": "23:00 às 07:00",
        "Segunda": "23:00 às 07:00"
    }
]


# ============================================================
# CRIAÇÃO DO BANCO LOCAL
#
# O CSV É APENAS UM BANCO DE DADOS LOCAL.
# NÃO É FONTE DE HORÁRIO.
# ============================================================

def inicializar_banco():

    if not os.path.exists(ARQUIVO_BANCO):

        linhas_banco = []

        for opt in opcoes_semanas:

            for operador in operadores_padrao:

                item = operador.copy()

                item["SemanaID"] = opt["id_semana"]

                linhas_banco.append(item)

        pd.DataFrame(
            linhas_banco
        ).to_csv(
            ARQUIVO_BANCO,
            index=False
        )


# ============================================================
# INICIALIZA BANCO
# ============================================================

inicializar_banco()


# ============================================================
# CARREGA BANCO
# ============================================================

df_banco = pd.read_csv(
    ARQUIVO_BANCO
)


# ============================================================
# GARANTE COLUNAS NECESSÁRIAS
# ============================================================

colunas_necessarias = [
    "SemanaID",
    "Turno",
    "Nome",
    "Função",
    "Sexta",
    "Sábado",
    "Domingo",
    "Segunda"
]

for coluna in colunas_necessarias:

    if coluna not in df_banco.columns:

        df_banco[coluna] = ""


# ============================================================
# CORREÇÃO AUTOMÁTICA DOS HORÁRIOS
#
# ESTA É A PARTE MAIS IMPORTANTE.
#
# O SISTEMA IGNORA QUALQUER HORÁRIO ANTIGO DO CSV.
#
# SE FOR TRABALHO:
#   T1 = 07:00 às 15:00
#   T2 = 15:00 às 23:00
#   T3 = 23:00 às 07:00
#
# SE FOR FOLGA:
#   CONTINUA FOLGA.
# ============================================================

dias_lista = [
    "Sexta",
    "Sábado",
    "Domingo",
    "Segunda"
]


for indice in df_banco.index:

    turno = str(
        df_banco.at[indice, "Turno"]
    ).strip()

    horario_correto = obter_horario_turno(
        turno
    )

    for dia in dias_lista:

        valor = str(
            df_banco.at[indice, dia]
        ).strip()

        if "FOLGA" in valor.upper():

            df_banco.at[
                indice,
                dia
            ] = "FOLGA"

        else:

            df_banco.at[
                indice,
                dia
            ] = horario_correto


# ============================================================
# SALVA A CORREÇÃO
# ============================================================

df_banco.to_csv(
    ARQUIVO_BANCO,
    index=False
)


# ============================================================
# CRIA SEMANA NOVA AUTOMATICAMENTE
# ============================================================

if df_banco[
    df_banco["SemanaID"] == id_semana_ativa
].empty:

    semanas_existentes = df_banco[
        "SemanaID"
    ].dropna().unique()

    if len(semanas_existentes) > 0:

        ultima_semana = semanas_existentes[-1]

        ultimos_dados = df_banco[
            df_banco["SemanaID"] ==
            ultima_semana
        ].copy()

        ultimos_dados[
            "SemanaID"
        ] = id_semana_ativa

        df_banco = pd.concat(
            [
                df_banco,
                ultimos_dados
            ],
            ignore_index=True
        )

        # Corrige horários da nova semana
        for indice in df_banco.index:

            turno = str(
                df_banco.at[
                    indice,
                    "Turno"
                ]
            ).strip()

            horario_correto = obter_horario_turno(
                turno
            )

            if (
                df_banco.at[
                    indice,
                    "SemanaID"
                ] == id_semana_ativa
            ):

                for dia in dias_lista:

                    valor = str(
                        df_banco.at[
                            indice,
                            dia
                        ]
                    ).strip()

                    if "FOLGA" in valor.upper():

                        df_banco.at[
                            indice,
                            dia
                        ] = "FOLGA"

                    else:

                        df_banco.at[
                            indice,
                            dia
                        ] = horario_correto


        df_banco.to_csv(
            ARQUIVO_BANCO,
            index=False
        )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "<h3 style='color:#FF9900; margin-top:0;'>"
        "🔐 Área do Gestor"
        "</h3>",
        unsafe_allow_html=True
    )


    # ========================================================
    # LOGIN
    # ========================================================

    if not st.session_state.autenticado:

        with st.form(
            key="formulario_login"
        ):

            usuario = st.text_input(
                "Usuário:",
                key="user_input"
            )

            senha = st.text_input(
                "Senha:",
                type="password",
                key="pass_input"
            )

            botao_entrar = st.form_submit_button(
                "Entrar",
                use_container_width=True
            )


            if botao_entrar:

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
                        "Dados incorretos."
                    )


    # ========================================================
    # ÁREA LOGADA
    # ========================================================

    else:

        st.write(
            "🟢 Modo Gestão ativo"
        )

        st.info(
            "💡 DICA: Agora você pode clicar nos "
            "botões diretamente na tabela para "
            "alterar folgas rapidamente!"
        )

        st.divider()


        # ====================================================
        # CADASTRAR OPERADOR
        # ====================================================

        st.markdown(
            "**➕ Cadastrar Novo Operador**"
        )

        novo_nome = st.text_input(
            "Nome:"
        ).upper().strip()

        nova_funcao = st.text_input(
            "Função:"
        ).upper().strip()

        novo_turno = st.selectbox(
            "Turno:",
            [
                "Turno 1",
                "Turno 2",
                "Turno 3"
            ]
        )


        if st.button(
            "Adicionar ao Sistema",
            use_container_width=True
        ):

            if novo_nome and nova_funcao:

                if "1" in novo_turno:

                    turno_id = "T1"

                elif "2" in novo_turno:

                    turno_id = "T2"

                else:

                    turno_id = "T3"


                horario_sugerido = obter_horario_turno(
                    turno_id
                )


                nova_linha = {

                    "SemanaID":
                        id_semana_ativa,

                    "Turno":
                        turno_id,

                    "Nome":
                        novo_nome,

                    "Função":
                        nova_funcao,

                    "Sexta":
                        horario_sugerido,

                    "Sábado":
                        horario_sugerido,

                    "Domingo":
                        horario_sugerido,

                    "Segunda":
                        horario_sugerido
                }


                df_banco = pd.concat(
                    [
                        df_banco,
                        pd.DataFrame(
                            [nova_linha]
                        )
                    ],
                    ignore_index=True
                )


                df_banco.to_csv(
                    ARQUIVO_BANCO,
                    index=False
                )


                st.success(
                    f"{novo_nome} adicionado!"
                )

                st.rerun()


        st.divider()


        # ====================================================
        # REMOVER OPERADOR
        # ====================================================

        st.markdown(
            "**❌ Remover / Desligar Operador**"
        )


        lista_operadores_atuais = sorted(
            df_banco[
                df_banco["SemanaID"] ==
                id_semana_ativa
            ]["Nome"].unique()
        )


        if lista_operadores_atuais:

            operador_para_remover = st.selectbox(
                "Selecione quem remover:",
                lista_operadores_atuais
            )


            tipo_remocao = st.radio(
                "Escopo da remoção:",
                [
                    "Apenas da semana atual",
                    "De todo o sistema (Definitivo)"
                ]
            )


            if st.button(
                "Confirmar Exclusão",
                type="primary",
                use_container_width=True
            ):

                if (
                    tipo_remocao ==
                    "Apenas da semana atual"
                ):

                    df_banco = df_banco[
                        ~(
                            (
                                df_banco["SemanaID"] ==
                                id_semana_ativa
                            )
                            &
                            (
                                df_banco["Nome"] ==
                                operador_para_remover
                            )
                        )
                    ]

                    st.success(
                        f"Removido da escala da semana "
                        f"{id_semana_ativa}!"
                    )


                else:

                    df_banco = df_banco[
                        df_banco["Nome"] !=
                        operador_para_remover
                    ]

                    st.success(
                        f"{operador_para_remover} "
                        f"deletado do sistema permanentemente!"
                    )


                df_banco.to_csv(
                    ARQUIVO_BANCO,
                    index=False
                )

                st.rerun()


        else:

            st.caption(
                "Nenhum operador listado nesta semana."
            )


        st.divider()


        # ====================================================
        # SAIR
        # ====================================================

        if st.button(
            "🚪 Sair (Deslogar)",
            use_container_width=True
        ):

            st.session_state.autenticado = False

            st.query_params.clear()

            st.rerun()


# ============================================================
# EXIBIÇÃO DA ESCALA
# ============================================================

df_tela = df_banco[
    df_banco["SemanaID"] ==
    id_semana_ativa
]


mapa_nomes_turnos = {
    "T1": "Turno 1",
    "T2": "Turno 2",
    "T3": "Turno 3"
}


# ============================================================
# LOOP DOS TURNOS
# ============================================================

for id_turno, nome_exibicao in mapa_nomes_turnos.items():

    df_turno = df_tela[
        df_tela["Turno"] == id_turno
    ]


    if not df_turno.empty:

        st.markdown(
            f"### 🕒 {nome_exibicao}"
        )


        # ====================================================
        # CABEÇALHO
        # ====================================================

        cols_header = st.columns(
            [
                2.5,
                2,
                1.8,
                1.8,
                1.8,
                1.8
            ]
        )


        cols_header[0].markdown(
            "<div class='header-col' "
            "style='text-align:left;'>"
            "OPERADOR"
            "</div>",
            unsafe_allow_html=True
        )


        cols_header[1].markdown(
            "<div class='header-col' "
            "style='text-align:left; color:#64748B;'>"
            "FUNÇÃO"
            "</div>",
            unsafe_allow_html=True
        )


        for idx, dia in enumerate(
            dias_lista,
            2
        ):

            data_do_dia = dados_semana_ativa[
                dia
            ]


            cols_header[idx].markdown(
                f"<div class='header-col'>"
                f"{dia.upper()} ({data_do_dia})"
                f"</div>",
                unsafe_allow_html=True
            )


        st.markdown(
            "<hr style='margin-top:0; "
            "margin-bottom:15px;' />",
            unsafe_allow_html=True
        )


        # ====================================================
        # OPERADORES
        # ====================================================

        for _, row in df_turno.iterrows():

            cols = st.columns(
                [
                    2.5,
                    2,
                    1.8,
                    1.8,
                    1.8,
                    1.8
                ]
            )


            cols[0].markdown(
                f"<div class='nome-operador'>"
                f"<b>{row['Nome']}</b>"
                f"</div>",
                unsafe_allow_html=True
            )


            cols[1].markdown(
                f"<div class='funcao-operador'>"
                f"{row['Função']}"
                f"</div>",
                unsafe_allow_html=True
            )


            # =================================================
            # HORÁRIO OFICIAL DO TURNO
            #
            # NUNCA PEGA DO CSV.
            # =================================================

            horario_oficial = obter_horario_turno(
                id_turno
            )


            # =================================================
            # DIAS
            # =================================================

            for idx, dia in enumerate(
                dias_lista,
                2
            ):

                valor_original = str(
                    row[dia]
                ).strip()


                # =============================================
                # VERIFICA FOLGA
                # =============================================

                esta_de_folga = (
                    "FOLGA"
                    in valor_original.upper()
                )


                # =============================================
                # TRABALHO
                # =============================================

                if not esta_de_folga:

                    cols[idx].markdown(

                        f"<div class='card-trabalho'>"
                        f"TRABALHO"
                        f"<div class='sub-info'>"
                        f"{horario_oficial}"
                        f"</div>"
                        f"</div>",

                        unsafe_allow_html=True
                    )


                # =============================================
                # FOLGA
                # =============================================

                else:

                    cols[idx].markdown(

                        "<div class='card-folga'>"
                        "FOLGA"
                        "<div class='sub-info-folga'>"
                        "Descanso"
                        "</div>"
                        "</div>",

                        unsafe_allow_html=True
                    )


                # =================================================
                # BOTÃO DO GESTOR
                # =================================================

                if st.session_state.autenticado:

                    # ---------------------------------------------
                    # Se está trabalhando → vira folga
                    # ---------------------------------------------

                    if not esta_de_folga:

                        novo_status = "FOLGA"


                    # ---------------------------------------------
                    # Se está de folga → volta para horário oficial
                    # ---------------------------------------------

                    else:

                        novo_status = horario_oficial


                    if cols[idx].button(

                        "🔄 Alternar",

                        key=(
                            f"btn_"
                            f"{row['Nome']}_"
                            f"{dia}_"
                            f"{id_semana_ativa}"
                        )
                    ):

                        indices_encontrados = df_banco[
                            (
                                df_banco["SemanaID"] ==
                                id_semana_ativa
                            )
                            &
                            (
                                df_banco["Nome"] ==
                                row["Nome"]
                            )
                        ].index


                        if len(indices_encontrados) > 0:

                            idx_banco = (
                                indices_encontrados[0]
                            )


                            # ---------------------------------
                            # SALVA SOMENTE FOLGA OU HORÁRIO
                            # ---------------------------------

                            df_banco.at[
                                idx_banco,
                                dia
                            ] = novo_status


                            df_banco.to_csv(
                                ARQUIVO_BANCO,
                                index=False
                            )


                            st.rerun()


        st.write("")
