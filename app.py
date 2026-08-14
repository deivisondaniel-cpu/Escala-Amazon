import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Configuração da página web
st.set_page_config(page_title="Escala monitoramento", page_icon="📦", layout="wide")

# Nome do arquivo de banco de dados permanente
ARQUIVO_BANCO = "escala_amazon_db_v2.csv"

# Estilização CSS refinada com remoção completa de elementos do Streamlit e ajuste de logos
st.markdown("""
    <style>
    /* REMOVE O CABEÇALHO, MENU E RODAPÉ PADRÃO DO STREAMLIT */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDecoration {display:none !important;}
    
    /* Container para alinhar os logos no topo */
    .container-logos {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 35px;
        margin-top: 10px;
        margin-bottom: 5px;
    }
    .logo-img-amazon {
        height: 38px;
        object-fit: contain;
    }
    .logo-img-losung {
        height: 48px;
        object-fit: contain;
    }
    
    .titulo { text-align: center; color: #131921; font-family: 'Segoe UI', sans-serif; font-weight: bold; margin-bottom: 25px; font-size: 28px; padding-top: 5px; }
    
    /* Cartões de TRABALHO: Escuro elegante com borda laranja */
    .card-trabalho { background-color: #232F3E; color: white; padding: 6px 8px; border-radius: 6px; text-align: center; font-weight: 600; font-size: 12px; border-left: 4px solid #FF9900; margin-bottom: 12px; }
    
    /* Cartões de FOLGA: Amarelo suave/fosco com texto escuro */
    .card-folga { background-color: #FDF1AA; color: #403000; padding: 6px 8px; border-radius: 6px; text-align: center; font-weight: bold; font-size: 12px; border-left: 4px solid #E6A100; margin-bottom: 12px; }
    
    .sub-info { font-size: 10px; color: #FF9900; font-weight: bold; }
    .sub-info-folga { font-size: 10px; color: #8F7014; font-weight: normal; }
    
    .header-col { text-align: center; font-weight: bold; font-size: 13px; color: #131921; margin-bottom: 10px; }
    
    /* Ajuste de espaçamento para o nome e função acompanharem o bloco */
    .nome-operador { padding-top: 8px; font-size: 13px; margin-bottom: 12px; }
    .funcao-operador { padding-top: 8px; font-size: 12px; color: #64748B; margin-bottom: 12px; }
    
    .stMainBlockContainer { padding-top: 10px !important; padding-bottom: 20px !important; }
    </style>
""", unsafe_allow_html=True)

# --- EXIBIÇÃO DOS LOGOS OFICIAIS NO TOPO ---
st.markdown("""
    <div class='container-logos'>
        <img class='logo-img-amazon' src='https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg' alt='Amazon'>
        <div style='font-family: sans-serif; font-size: 24px; color: #CCC; font-weight: 300;'>|</div>
        <img class='logo-img-losung' src='data:image/png;base64,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' alt='Losong'>
    </div>
""", unsafe_allow_html=True)

st.markdown("<h1 class='titulo'>Escala Amazon</h1>", unsafe_allow_html=True)

# --- MÁGICA DA PERSISTÊNCIA DO LOGIN (TRAVA DO F5) ---
if "logged_in" in st.query_params and st.query_params["logged_in"] == "true":
    st.session_state.autenticado = True
elif 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- LÓGICA DE DATAS AUTOMÁTICAS ---
def obter_datas_semana(deslocamento_semanas=0):
    hoje = datetime.now()
    dias_para_atras = (hoje.weekday() - 4) % 7
    sexta_atual = hoje - timedelta(days=dias_para_atras)
    sexta_alvo = sexta_atual + timedelta(weeks=deslocamento_semanas)
    
    sabado_alvo = sexta_alvo + timedelta(days=1)
    domingo_alvo = sexta_alvo + timedelta(days=2)
    segunda_alvo = sexta_alvo + timedelta(days=3)
    
    return {
        "id_semana": sexta_alvo.strftime("%Y_W%W"),
        "rotulo": f"Semana de {sexta_alvo.strftime('%d/%m')} até {segunda_alvo.strftime('%d/%m')}",
        "Sexta": sexta_alvo.strftime("%d/%m"),
        "Sábado": sabado_alvo.strftime("%d/%m"),
        "Domingo": domingo_alvo.strftime("%d/%m"),
        "Segunda": segunda_alvo.strftime("%d/%m")
    }

opcoes_semanas = [obter_datas_semana(i) for i in range(-1, 4)]
formatos_semanas = {opt["rotulo"]: opt for opt in opcoes_semanas}

# --- FILTRO DE SEMANA ---
col_topo1, _ = st.columns([3, 3])
with col_topo1:
    semana_selecionada_rotulo = st.selectbox("📅 Período da Escala:", list(formatos_semanas.keys()), index=1)

dados_semana_ativa = formatos_semanas[semana_selecionada_rotulo]
id_semana_ativa = dados_semana_ativa["id_semana"]

# --- INICIALIZAÇÃO E LEITURA DO BANCO DE DADOS ---
def inicializar_banco():
    if not os.path.exists(ARQUIVO_BANCO):
        operadores_padrao = [
            # Turno 1
            {"Turno": "T1", "Nome": "ALAN ARÁUJO", "Função": "ANALISTA", "Sexta": "07:00 às 15:00", "Sábado": "FOLGA", "Domingo": "07:00 às 15:00", "Segunda": "07:00 às 15:00"},
            {"Turno": "T1", "Nome": "MARGARIDA", "Função": "PICKUP", "Sexta": "07:00 às 15:00", "Sábado": "FOLGA", "Domingo": "07:00 às 15:00", "Segunda": "07:00 às 15:00"},
            {"Turno": "T1", "Nome": "JOSÉ BRUNO PALHANO", "Função": "PICKUP", "Sexta": "FOLGA", "Sábado": "07:00 às 15:00", "Domingo": "07:00 às 15:00", "Segunda": "07:00 às 15:00"},
            {"Turno": "T1", "Nome": "CRISTOVÃO MIKELLYS", "Função": "DEPART", "Sexta": "07:00 às 15:00", "Sábado": "07:00 às 15:00", "Domingo": "FOLGA", "Segunda": "07:00 às 15:00"},
            {"Turno": "T1", "Nome": "PEDRO LUCAS", "Função": "DROPOFF", "Sexta": "07:00 às 15:00", "Sábado": "FOLGA", "Domingo": "07:00 às 15:00", "Segunda": "07:00 às 15:00"},
            {"Turno": "T1", "Nome": "FELIPE ALLAN", "Função": "DROPOFF", "Sexta": "07:00 às 15:00", "Sábado": "07:00 às 15:00", "Domingo": "FOLGA", "Segunda": "07:00 às 15:00"},
            {"Turno": "T1", "Nome": "BRUNA BLENDA", "Função": "DROPOFF", "Sexta": "FOLGA", "Sábado": "07:00 às 15:00", "Domingo": "07:00 às 15:00", "Segunda": "07:00 às 15:00"},
            {"Turno": "T1", "Nome": "CONCEIÇÃO DAIANE", "Função": "SEGURANÇA (ONISYS)", "Sexta": "07:00 às 15:00", "Sábado": "FOLGA", "Domingo": "07:00 às 15:00", "Segunda": "07:00 às 15:00"},
            {"Turno": "T1", "Nome": "MATHEUS LUSTOSA", "Função": "SEGURANÇA/ELOG", "Sexta": "FOLGA", "Sábado": "07:00 às 15:00", "Domingo": "07:00 às 15:00", "Segunda": "07:00 às 15:00"},
            # Turno 2
            {"Turno": "T2", "Nome": "MANUELA PINHEIRO", "Função": "LÍDER", "Sexta": "15:00 às 19:00", "Sábado": "15:00 às 19:00", "Domingo": "FOLGA", "Segunda": "15:00 às 19:00"},
            {"Turno": "T2", "Nome": "ISABEL", "Função": "LÍDER/SEGURANÇA", "Sexta": "15:00 às 19:00", "Sábado": "FOLGA", "Domingo": "15:00 às 19:00", "Segunda": "15:00 às 19:00"},
            {"Turno": "T2", "Nome": "ANDREZA OLIVEIRA", "Função": "PICKUP", "Sexta": "15:00 às 19:00", "Sábado": "FOLGA", "Domingo": "15:00 às 19:00", "Segunda": "15:00 às 19:00"},
            {"Turno": "T2", "Nome": "ROZIANE DA SILVA", "Função": "PICKUP", "Sexta": "FOLGA", "Sábado": "15:00 às 19:00", "Domingo": "15:00 às 19:00", "Segunda": "15:00 às 19:00"},
            {"Turno": "T2", "Nome": "DAIANE", "Função": "SEGURANÇA", "Sexta": "FOLGA", "Sábado": "15:00 às 19:00", "Domingo": "15:00 às 19:00", "Segunda": "15:00 às 19:00"},
            {"Turno": "T2", "Nome": "EMANUEL ROBERTO", "Função": "DEPART", "Sexta": "FOLGA", "Sábado": "15:00 às 19:00", "Domingo": "15:00 às 19:00", "Segunda": "15:00 às 19:00"},
            {"Turno": "T2", "Nome": "TAMMYRIS DA SILVA", "Função": "DROPOFF", "Sexta": "15:00 às 19:00", "Sábado": "FOLGA", "Domingo": "15:00 às 19:00", "Segunda": "15:00 às 19:00"},
            {"Turno": "T2", "Nome": "RAPHAEL DO NASCIMENTO", "Função": "DROPOFF", "Sexta": "15:00 às 19:00", "Sábado": "15:00 às 19:00", "Domingo": "FOLGA", "Segunda": "15:00 às 19:00"},
            {"Turno": "T2", "Nome": "LUDMILLA RODRIGUES", "Função": "DROPOFF", "Sexta": "15:00 às 19:00", "Sábado": "15:00 às 19:00", "Domingo": "15:00 às 19:00", "Segunda": "FOLGA"},
            {"Turno": "T2", "Nome": "MARIA NATHALIA", "Função": "SEGURANÇA", "Sexta": "15:00 às 19:00", "Sábado": "15:00 às 19:00", "Domingo": "FOLGA", "Segunda": "15:00 às 19:00"},
            {"Turno": "T2", "Nome": "CINAMOR", "Função": "ELOG", "Sexta": "15:00 às 19:00", "Sábado": "15:00 às 19:00", "Domingo": "15:00 às 19:00", "Segunda": "FOLGA"},
            # Turno 3
            {"Turno": "T3", "Nome": "WESLEY", "Função": "LÍDER", "Sexta": "FOLGA", "Sábado": "15:00 às 19:00", "Domingo": "15:00 às 19:00", "Segunda": "15:00 às 19:00"},
            {"Turno": "T3", "Nome": "JOÃO", "Função": "LÍDER/SEGURANÇA", "Sexta": "15:00 às 19:00", "Sábado": "15:00 às 19:00", "Domingo": "15:00 às 19:00", "Segunda": "FOLGA"},
            {"Turno": "T3", "Nome": "RILDOMAR", "Função": "PICKUP", "Sexta": "15:00 às 19:00", "Sábado": "FOLGA", "Domingo": "15:00 às 19:00", "Segunda": "15:00 às 19:00"},
            {"Turno": "T3", "Nome": "LUCIANA", "Função": "PICKUP", "Sexta": "FOLGA", "Sábado": "15:00 às 19:00", "Domingo": "FOLGA", "Segunda": "15:00 às 19:00"},
            {"Turno": "T3", "Nome": "GLAYLDSON", "Função": "SEGURANÇA", "Sexta": "15:00 às 19:00", "Sábado": "15:00 às 19:00", "Domingo": "15:00 às 19:00", "Segunda": "FOLGA"},
            {"Turno": "T3", "Nome": "TAYANARA", "Função": "DEPART", "Sexta": "15:00 às 19:00", "Sábado": "15:00 às 19:00", "Domingo": "FOLGA", "Segunda": "15:00 às 19:00"},
            {"Turno": "T3", "Nome": "RUAN", "Função": "DROPOFF", "Sexta": "15:00 às 19:00", "Sábado": "FOLGA", "Domingo": "15:00 às 19:00", "Segunda": "15:00 às 19:00"},
            {"Turno": "T3", "Nome": "BÁRBARA", "Função": "DROPOFF", "Sexta": "15:00 às 19:00", "Sábado": "15:00 às 19:00", "Domingo": "15:00 às 19:00", "Segunda": "15:00 às 19:00"}
        ]
        linhas_banco = []
        for opt in opcoes_semanas:
            for op in operadores_padrao:
                item = op.copy()
                item["SemanaID"] = opt["id_semana"]
                linhas_banco.append(item)
        pd.DataFrame(linhas_banco).to_csv(ARQUIVO_BANCO, index=False)

inicializar_banco()
df_banco = pd.read_csv(ARQUIVO_BANCO)

if df_banco[df_banco["SemanaID"] == id_semana_ativa].empty:
    ultimos_dados = df_banco[df_banco["SemanaID"] == df_banco["SemanaID"].iloc[-1]].copy()
    ultimos_dados["SemanaID"] = id_semana_ativa
    df_banco = pd.concat([df_banco, ultimos_dados], ignore_index=True)
    df_banco.to_csv(ARQUIVO_BANCO, index=False)

# --- PAINEL LATERAL (GESTÃO E AUTENTICAÇÃO) ---
with st.sidebar:
    st.markdown("<h3 style='color:#FF9900; margin-top:0;'>🔐 Área do Coordenador</h3>", unsafe_allow_html=True)
    
    if not st.session_state.autenticado:
        with st.form(key="formulario_login"):
            usuario = st.text_input("Usuário:", key="user_input")
            senha = st.text_input("Senha:", type="password", key="pass_input")
            botao_entrar = st.form_submit_button("Entrar", use_container_width=True)
            
            if botao_entrar:
                if usuario.lower() == "admin" and senha == "Amazon123":
                    st.session_state.autenticado = True
                    st.query_params["logged_in"] = "true"
                    st.rerun()
                else:
                    st.error("Dados incorretos.")
    else:
        st.write("🟢 Modo Coordenador Ativo")
        st.info("💡 DICA: Agora você pode clicar nos botões diretamente na tabela para alterar folgas rapidamente!")
        st.divider()
        
        st.markdown("**➕ Cadastrar Novo Operador**")
        novo_nome = st.text_input("Nome:").upper().strip()
        nova_funcao = st.text_input("Função:").upper().strip()
        novo_turno = st.selectbox("Turno:", ["Turno 1", "Turno 2", "Turno 3"])
        
        if st.button("Adicionar ao Sistema", use_container_width=True):
            if novo_nome and nova_funcao:
                turno_id = "T1" if "1" in novo_turno else "T2" if "2" in novo_turno else "T3"
                horario_sugerido = "07:00 às 15:00" if turno_id == "T1" else "15:00 às 19:00"
                nova_linha = {
                    "SemanaID": id_semana_ativa, "Turno": turno_id, "Nome": novo_nome, "Função": nova_funcao,
                    "Sexta": horario_sugerido, "Sábado": horario_sugerido, "Domingo": horario_sugerido, "Segunda": horario_sugerido
                }
                df_banco = pd.concat([df_banco, pd.DataFrame([nova_linha])], ignore_index=True)
                df_banco.to_csv(ARQUIVO_BANCO, index=False)
                st.success(f"{novo_nome} adicionado!")
                st.rerun()

        if st.button("🚪 Sair (Deslogar)", use_container_width=True):
            st.session_state.autenticado = False
            st.query_params.clear()
            st.rerun()

# --- EXIBIÇÃO DA ESCALA ---
df_tela = df_banco[df_banco["SemanaID"] == id_semana_ativa]
mapa_nomes_turnos = {"T1": "Turno 1", "T2": "Turno 2", "T3": "Turno 3"}
dias_lista = ["Sexta", "Sábado", "Domingo", "Segunda"]

for id_turno, nome_exibicao in mapa_nomes_turnos.items():
    df_turno = df_tela[df_tela["Turno"] == id_turno]
    
    if not df_turno.empty:
        st.markdown(f"### 🕒 {nome_exibicao}")
        
        cols_header = st.columns([2.5, 2, 1.8, 1.8, 1.8, 1.8])
        cols_header[0].markdown("<div class='header-col' style='text-align:left;'>OPERADOR</div>", unsafe_allow_html=True)
        cols_header[1].markdown("<div class='header-col' style='text-align:left; color:#64748B;'>FUNÇÃO</div>", unsafe_allow_html=True)
        
        for idx, dia in enumerate(dias_lista, 2):
            data_do_dia = dados_semana_ativa[dia]
            cols_header[idx].markdown(f"<div class='header-col'>{dia.upper()} ({data_do_dia})</div>", unsafe_allow_html=True)
            
        st.markdown("<hr style='margin-top:0; margin-bottom:15px;' />", unsafe_allow_html=True)
        
        for _, row in df_turno.iterrows():
            cols = st.columns([2.5, 2, 1.8, 1.8, 1.8, 1.8])
            
            cols[0].markdown(f"<div class='nome-operador'><b>{row['Nome']}</b></div>", unsafe_allow_html=True)
            cols[1].markdown(f"<div class='funcao-operador'>{row['Função']}</div>", unsafe_allow_html=True)
            
            for idx, dia in enumerate(dias_lista, 2):
                status_atual = str(row[dia])
                
                if "FOLGA" not in status_atual:
                    cols[idx].markdown(f"<div class='card-trabalho'>TRABALHO<div class='sub-info'>{status_atual}</div></div>", unsafe_allow_html=True)
                else:
                    cols[idx].markdown("<div class='card-folga'>FOLGA<div class='sub-info-folga'>Descanso</div></div>", unsafe_allow_html=True)
                
                if st.session_state.autenticado:
                    horario_retorno = "07:00 às 15:00" if id_turno == "T1" else "15:00 às 19:00"
                    novo_status = "FOLGA" if "FOLGA" not in status_atual else horario_retorno
                    
                    if cols[idx].button(f"🔄 Alternar", key=f"btn_{row['Nome']}_{dia}_{id_semana_ativa}"):
                        idx_banco = df_banco[(df_banco["SemanaID"] == id_semana_ativa) & (df_banco["Nome"] == row['Nome'])].index[0]
                        df_banco.at[idx_banco, dia] = novo_status
                        df_banco.to_csv(ARQUIVO_BANCO, index=False)
                        st.rerun()
                        
        st.write("")
