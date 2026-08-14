import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
from datetime import datetime, timedelta

# Configuração da página web
st.set_page_config(page_title="Escala monitoramento", page_icon="📦", layout="wide")

# Nome do arquivo de banco de dados permanente
ARQUIVO_BANCO = "escala_amazon_db_v2.csv"

# 1. TRATOR CSS PARA REFORÇAR NO AMBIENTE LOCAL
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

# 2. INJEÇÃO DE JAVASCRIPT MASTER (Quebra a segurança e limpa o elemento do pai)
components.html("""
    <script>
    function exterminarSeloTeimoso() {
        // Acessa a página principal de fora do iframe atual
        const documentoPai = window.parent.document;
        
        // 1. Procura e destrói o maldito popover flutuante
        const popovers = documentoPai.querySelectorAll('[data-baseweb="popover"], div[class*="StyledEmbedHoverContainer"]');
        popovers.forEach(el => el.remove());
        
        // 2. Procura o botão flutuante redondo (ícone) e a barra vermelha e apaga de vez
        const links = documentoPai.querySelectorAll('a');
        links.forEach(link => {
            if (link.href.includes('streamlit.io') || link.innerHTML.includes('Hosted with Streamlit')) {
                let ancestral = link.closest('div');
                // Sobe até achar o container flutuante maior na barra inferior e deleta
                for (let i = 0; i < 4; i++) {
                    if (ancestral && (ancestral.style.position === 'fixed' || ancestral.className.includes('viewer-badge'))) {
                        ancestral.remove();
                        break;
                    }
                    if (ancestral) ancestral = ancestral.parentElement;
                }
            }
        });
        
        // 3. Aplica CSS direto na raiz do documento pai para garantir que nada herde o bloco vermelho
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
    
    // Executa imediatamente e repete a cada 300 milissegundos para não dar chance dele voltar
    setInterval(exterminarSeloTeimoso, 300);
    </script>
""", height=0, width=0)

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
            {"Turno": "T2",
