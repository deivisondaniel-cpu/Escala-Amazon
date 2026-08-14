import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os

# Configuração da página web
st.set_page_config(page_title="Escala monitoramento", page_icon="📦", layout="wide")

# Nome do banco de dados próprio e independente do sistema
ARQUIVO_BANCO = "banco_escala_amazon_definitivo.csv"

# 1. TRATOR CSS (Deixa o visual limpo e profissional)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden !important;}
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stDecoration {display:none !important;}
    
    .titulo { text-align: center; color: #131921; font-family: 'Segoe UI', sans-serif; font-weight: bold; margin-bottom: 25px; font-size: 28px; }
    .card-trabalho { background-color: #232F3E; color: white; padding: 6px 8px; border-radius: 6px; text-align: center; font-weight: 600; font-size: 12px; border-left: 4px solid #FF9900; margin-bottom: 12px; }
    .card-folga { background-color: #FDF1AA; color: #403000; padding: 6px 8px; border-radius: 6px; text-align: center; font-weight: bold; font-size: 12px; border-left: 4px solid #E6A100; margin-bottom: 12px; }
    .sub-info { font-size: 10px; color: #FF9900; font-weight: bold; }
    .sub-info-folga { font-size: 10px; color: #8F7014; font-weight: normal; }
    .header-col { text-align: center; font-weight: bold; font-size: 13px; color: #131921; margin-bottom: 10px; }
    .nome-operador { padding-top: 8px; font-size: 13px; margin-bottom: 12px; }
    .funcao-operador { padding-top: 8px; font-size: 12px; color: #64748B; margin-bottom: 12px; }
    .stMainBlockContainer { padding-top: 20px !important; padding-bottom: 20px !important; }
    </style>
""", unsafe_allow_html=True)

# 2. INJEÇÃO DE JAVASCRIPT MASTER (Elimina qualquer selo do Streamlit)
components.html("""
    <script>
    function exterminarSeloTeimoso() {
        const documentoPai = window.parent.document;
        const popovers = documentoPai.querySelectorAll('[data-baseweb="popover"], div[class*="StyledEmbedHoverContainer"]');
        popovers.forEach(el => el.remove());
        const links = documentoPai.querySelectorAll('a');
        links.forEach(link => {
            if (link.href.includes('streamlit.io') || link.innerHTML.includes('Hosted with Streamlit')) {
                let ancestral = link.closest('div');
                for (let i = 0; i < 4; i++) {
                    if (ancestral && (ancestral.style.position === 'fixed' || ancestral.className.includes('viewer-badge'))) {
                        ancestral.remove();
                        break;
                    }
                    if (ancestral) ancestral = ancestral.parentElement;
                }
            }
        });
        const estiloEspecial = documentoPai.createElement('style');
        estiloEspecial.innerHTML = `
            [data-testid="stFooter"], .viewer-badge, div[class*="StyledEmbedHoverContainer"], [data-baseweb="popover"] {
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
                pointer-events: none !important;
            }
        `;
        documentoPai.head.appendChild(estiloEspecial);
    }
    setInterval(exterminarSeloTeimoso, 300);
    </script>
""", height=0, width=0)

st.markdown("<h1 class='titulo'>Escala Amazon</h1>", unsafe_allow_html=True)

# --- SISTEMA DE LOGIN SEGURO ---
if "logged_in" in st.query_params and st.query_params["logged_in"] == "true":
    st.session_state.autenticado = True
elif 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- CRIAÇÃO DO BANCO DE DADOS INTERNO DO ZERO (SEM PLANILHAS) ---
def inicializar_banco_independente():
    if not os.path.exists(ARQUIVO_BANCO):
        # Aqui estão guardados todos os operadores do sistema com seus horários reais e corrigidos
        dados_iniciais = [
            # TURNO 1 (07:00 às 15:00)
            {"Turno": "T1", "Nome": "ALAN ARÁUJO", "Função": "ANALISTA", "Sexta": "07:00 às 15:00", "Sábado": "FOLGA", "Domingo": "07:00 às 15:00", "Segunda": "07:00 às 15:00"},
            {"Turno": "T1", "Nome": "MARGARIDA", "Função": "PICKUP", "Sexta": "07:00 às 15:00", "Sábado": "FOLGA", "Domingo": "07:00 às 15:00", "Segunda": "07:00 às 15:00"},
            {"Turno": "T1", "Nome": "JOSÉ BRUNO PALHANO", "Função": "PICKUP", "Sexta": "FOLGA", "Sábado": "07:00 às 15:00", "Domingo": "07:00 às 15:00", "Segunda": "07:00 às 15:00"},
            {"Turno": "T1", "Nome": "CRISTOVÃO MIKELLYS", "Função": "DEPART", "Sexta": "07:00 às 15:00", "Sábado": "07:00 às 15:00", "Domingo": "FOLGA", "Segunda": "07:00 às 15:00"},
            {"Turno": "T1", "Nome": "PEDRO LUCAS", "Função": "DROPOFF", "Sexta": "07:00 às 15:00", "Sábado": "FOLGA", "Domingo": "07:00 às 15:00", "Segunda": "07:00 às 15:00"},
            {"Turno": "T1", "Nome": "FELIPE ALLAN", "Função": "DROPOFF", "Sexta": "07:00 às 15:00", "Sábado": "07:00 às 15:00", "Domingo": "FOLGA", "Segunda": "07:00 às 15:00"},
            {"Turno": "T1", "Nome": "BRUNA BLENDA", "Função": "DROPOFF", "Sexta": "FOLGA", "Sábado": "07:00 às 15:00", "Domingo": "07:00 às 15:00", "Segunda": "07:00 às 15:00"},
            {"Turno": "T1", "Nome": "CONCEIÇÃO DAIANE", "Função": "SEGURANÇA (ONISYS)", "Sexta": "07:00 às 15:00", "Sábado": "FOLGA", "Domingo": "07:00 às 15:00", "Segunda": "07:00 às 15:00"},
            {"Turno": "T1", "Nome": "MATHEUS LUSTOSA", "Função": "SEGURANÇA/ELOG", "Sexta": "FOLGA", "Sábado": "07:00 às 15:00", "Domingo": "07:00 às 15:00", "Segunda": "07:00 às 15:00"},
            
            # TURNO 2 (15:00 às 23:00) - CORRIGIDO!
            {"Turno": "T2", "Nome": "MANUELA PINHEIRO", "Função": "LÍDER", "Sexta": "15:00 às 23:00", "Sábado": "15:00 às 23:00", "Domingo": "FOLGA", "Segunda": "15:00 às 23:00"},
            {"Turno": "T2", "Nome": "ISABEL", "Função": "LÍDER/SEGURANÇA", "Sexta": "15:00 às 23:00", "Sábado": "FOLGA", "Domingo": "15:00 às 23:00", "Segunda": "15:00 às 23:00"},
            {"Turno": "T2", "Nome": "ANDREZA OLIVEIRA", "Função": "PICKUP", "Sexta": "15:00 às 23:00", "Sábado": "FOLGA", "Domingo": "15:00 às 23:00", "Segunda": "15:00 às 23:00"},
            {"Turno": "T2", "Nome": "ROZIANE DA SILVA", "Função": "PICKUP", "Sexta": "FOLGA", "Sábado": "15:00 às 23:00", "Domingo": "15:00 às 23:00", "Segunda": "15:00 às 23:00"},
            {"Turno": "T2", "Nome": "DAIANE", "Função": "SEGURANÇA", "Sexta": "FOLGA", "Sábado": "15:00 às 23:00", "Domingo": "15:00 às 23:00", "Segunda": "15:00 às 23:00"},
            {"Turno": "T2", "Nome": "EMANUEL ROBERTO", "Função": "DEPART", "Sexta": "FOLGA", "Sábado": "15:00 às 23:00", "Domingo": "15:00 às 23:00", "Segunda": "15:00 às 23:00"},
            {"Turno": "T2", "Nome": "TAMMYRIS DA SILVA", "Função": "DROPOFF", "Sexta": "15:00 às 23:00", "Sábado": "FOLGA", "Domingo": "15:00 às 23:00", "Segunda": "15:00 às 23:00"},
            {"Turno": "T2", "Nome": "RAPHAEL DO NASCIMENTO", "Função": "DROPOFF", "Sexta": "15:00 às 23:00", "Sábado": "15:00 às 23:00", "Domingo": "FOLGA", "Segunda": "15:00 às 23:00"},
            {"Turno": "T2", "Nome": "LUDMILLA RODRIGUES", "Função": "DROPOFF", "Sexta": "15:00 às 23:00", "Sábado": "15:00 às 23:00", "Domingo": "15:00 às 23:00", "Segunda": "FOLGA"},
            {"Turno": "T2", "Nome": "MARIA NATHALIA", "Função": "SEGURANÇA", "Sexta": "15:00 às 23:00", "Sábado": "15:00 às 23:00", "Domingo": "FOLGA", "Segunda": "15:00 às 23:00"},
            {"Turno": "T2", "Nome": "CINAMOR", "Função": "ELOG", "Sexta": "15:00 às 23:00", "Sábado": "15:00 às 23:00", "Domingo": "15:00 às 23:00", "Segunda": "FOLGA"},
            
            # TURNO 3 (23:00 às 07:00) - CORRIGIDO!
            {"Turno": "T3", "Nome": "WESLEY", "Função": "LÍDER", "Sexta": "FOLGA", "Sábado": "23:00 às 07:00", "Domingo": "23:00 às 07:00", "Segunda": "23:00 às 07:00"},
            {"Turno": "T3", "Nome": "JOÃO", "Função": "LÍDER/SEGURANÇA", "Sexta": "23:00 às 07:00", "Sábado": "23:00 às 07:00", "Domingo": "23:00 às 07:00", "Segunda": "FOLGA"},
            {"Turno": "T3", "Nome": "RILDOMAR", "Função": "PICKUP", "Sexta": "23:00 às 07:00", "Sábado": "FOLGA", "Domingo": "23:00 às 07:00", "Segunda": "23:00 às 07:00"},
            {"Turno": "T3", "Nome": "LUCIANA", "Função": "PICKUP", "Sexta": "FOLGA", "Sábado": "23:00 às 07:00", "Domingo": "FOLGA", "Segunda": "23:00 às 07:00"},
            {"Turno": "T3", "Nome": "GLAYLDSON", "Função": "SEGURANÇA", "Sexta": "23:00 às 07:00", "Sábado": "23:00 às 07:00", "Domingo": "23:00 às 07:00", "Segunda": "FOLGA"},
            {"Turno": "T3", "Nome": "TAYANARA", "Função": "DEPART", "Sexta": "23:00 às 07:00", "Sábado": "23:00 às 07:00", "Domingo": "FOLGA", "Segunda": "23:00 às 07:00"},
            {"Turno": "T3", "Nome": "RUAN", "Função": "DROPOFF", "Sexta": "23:00 às 07:00", "Sábado": "FOLGA", "Domingo": "23:00 às 07:00", "Segunda": "23:00 às 07:00"},
            {"Turno": "T3", "Nome": "BÁRBARA", "Função": "DROPOFF", "Sexta": "23:00 às 07:00", "Sábado": "23:00 às 07:00", "Domingo": "23:00 às 07:00", "Segunda": "23:00 às 07:00"}
        ]
        pd.DataFrame(dados_iniciais).to_csv(ARQUIVO_BANCO, index=False)

inicializar_banco_independente()
df_banco = pd.read_csv(ARQUIVO_BANCO)

# --- PAINEL LATERAL (ÁREA DO COORDENADOR PARA TROCAR AS FOLGAS NO SITE) ---
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
        st.write("🟢 Modo Edição Ativo")
        st.info("Clique diretamente nos botões '🔄 Alternar' na tabela para trocar de TRABALHO para FOLGA instantaneamente.")
        st.divider()
        
        # CADASTRO DIRETO NO SITE
        st.markdown("**➕ Adicionar Operador**")
        novo_nome = st.text_input("Nome:").upper().strip()
        nova_funcao = st.text_input("Função:").upper().strip()
        novo_turno = st.selectbox("Turno:", ["Turno 1", "Turno 2", "Turno 3"])
        
        if st.button("Salvar no Sistema", use_container_width=True):
            if novo_nome and nova_funcao:
                turno_id = "T1" if "1" in novo_turno else "T2" if "2" in novo_turno else "T3"
                horarios_map = {"T1": "07:00 às 15:00", "T2": "15:00 às 23:00", "T3": "23:00 às 07:00"}
                horario_sugerido = horarios_map[turno_id]
                
                nova_linha = {
                    "Turno": turno_id, "Nome": novo_nome, "Função": nova_funcao,
                    "Sexta": horario_sugerido, "Sábado": horario_sugerido, "Domingo": horario_sugerido, "Segunda": horario_sugerido
                }
                df_banco = pd.concat([df_banco, pd.DataFrame([nova_linha])], ignore_index=True)
                df_banco.to_csv(ARQUIVO_BANCO, index=False)
                st.success(f"{novo_nome} adicionado!")
                st.rerun()

        st.divider()
        if st.button("🚪 Sair do Modo Edição", use_container_width=True):
            st.session_state.autenticado = False
            st.query_params.clear()
            st.rerun()

# --- EXIBIÇÃO DA ESCALA (TODOS OS TURNOS COM HORÁRIOS CORRIGIDOS) ---
mapa_nomes_turnos = {
    "T1": "Turno 1 (07:00 às 15:00)", 
    "T2": "Turno 2 (15:00 às 23:00)", 
    "T3": "Turno 3 (23:00 às 07:00)"
}
dias_lista = ["Sexta", "Sábado", "Domingo", "Segunda"]

for id_turno, nome_exibicao in mapa_nomes_turnos.items():
    df_turno = df_banco[df_banco["Turno"] == id_turno]
    
    if not df_turno.empty:
        st.markdown(f"### 🕒 {nome_exibicao}")
        
        cols_header = st.columns([2.5, 2, 1.8, 1.8, 1.8, 1.8])
        cols_header[0].markdown("<div class='header-col' style='text-align:left;'>OPERADOR</div>", unsafe_allow_html=True)
        cols_header[1].markdown("<div class='header-col' style='text-align:left; color:#64748B;'>FUNÇÃO</div>", unsafe_allow_html=True)
        
        for idx, dia in enumerate(dias_lista, 2):
            cols_header[idx].markdown(f"<div class='header-col'>{dia.upper()}</div>", unsafe_allow_html=True)
            
        st.markdown("<hr style='margin-top:0; margin-bottom:15px;' />", unsafe_allow_html=True)
        
        for _, row in df_turno.iterrows():
            cols = st.columns([2.5, 2, 1.8, 1.8, 1.8, 1.8])
            cols[0].markdown(f"<div class='nome-operador'><b>{row['Nome']}</b></div>", unsafe_allow_html=True)
            cols[1].markdown(f"<div class='funcao-operador'>{row['Função']}</div>", unsafe_allow_html=True)
            
            for idx, dia in enumerate(dias_lista, 2):
                status_atual = str(row[dia]).strip()
                
                if "FOLGA" not in status_atual.upper():
                    cols[idx].markdown(f"<div class='card-trabalho'>TRABALHO<div class='sub-info'>{status_atual}</div></div>", unsafe_allow_html=True)
                else:
                    cols[idx].markdown("<div class='card-folga'>FOLGA<div class='sub-info-folga'>Descanso</div></div>", unsafe_allow_html=True)
                
                # Se o coordenador estiver logado, ele ganha o botão para gerenciar as folgas
                if st.session_state.autenticado:
                    horarios_retorno_map = {"T1": "07:00 às 15:00", "T2": "15:00 às 23:00", "T3": "23:00 às 07:00"}
                    novo_status = "FOLGA" if "FOLGA" not in status_atual.upper() else horarios_retorno_map[id_turno]
                    
                    if cols[idx].button(f"🔄 Alternar", key=f"btn_{row['Nome']}_{dia}"):
                        idx_banco = df_banco[(df_banco["Turno"] == id_turno) & (df_banco["Nome"] == row['Nome'])].index[0]
                        df_banco.at[idx_banco, dia] = novo_status
                        df_banco.to_csv(ARQUIVO_BANCO, index=False)
                        st.rerun()
        st.write("")
