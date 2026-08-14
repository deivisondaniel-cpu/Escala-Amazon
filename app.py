import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# Configuração da página web
st.set_page_config(page_title="Escala monitoramento", page_icon="📦", layout="wide")

# 1. TRATOR CSS (Formatação visual idêntica para todos os turnos)
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

# 2. INJEÇÃO DE JAVASCRIPT MASTER (Elimina o selo com a foto do GitHub)
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

# --- CONFIGURAÇÃO DOS TURNOS E SEUS HORÁRIOS ATUALIZADOS ---
TURNOS_CONFIG = {
    "T1": {"nome": "Turno 1 (07:00 às 15:00)", "horario": "07:00 às 15:00", "gid": "0"},
    "T2": {"nome": "Turno 2 (15:00 às 23:00)", "horario": "15:00 às 23:00", "gid": "1740365530"},
    "T3": {"nome": "Turno 3 (23:00 às 07:00)", "horario": "23:00 às 07:00", "gid": "111816576"}
}

# --- FUNÇÃO PARA CARREGAR UMA ABA ESPECÍFICA DO GOOGLE SHEETS ---
@st.cache_data(ttl=15)
def carregar_dados_turno(gid_aba):
    sheet_id = "16u4SXhN3NNDmJ6o3UstFHNgRk3Go5V2KkvhGJewNl8E"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid_aba}"
    try:
        df = pd.read_csv(url, skiprows=2)
        df = df.dropna(subset=["NOME"])
        return df
    except Exception as e:
        return pd.DataFrame()

dias_lista = ["SEXTA", "SÁBADO", "DOMINGO", "SEGUNDA"]

# --- RENDERIZAÇÃO DE CADA TURNO NA TELA ---
for chave_turno, conf in TURNOS_CONFIG.items():
    df_turno = carregar_dados_turno(conf["gid"])
    
    if not df_turno.empty:
        st.markdown(f"### 🕒 {conf['nome']}")
        
        # Cria as colunas de cabeçalho do turno atual
        cols_header = st.columns([2.5, 2, 1.8, 1.8, 1.8, 1.8])
        cols_header[0].markdown("<div class='header-col' style='text-align:left;'>OPERADOR</div>", unsafe_allow_html=True)
        cols_header[1].markdown("<div class='header-col' style='text-align:left; color:#64748B;'>FUNÇÃO</div>", unsafe_allow_html=True)
        
        for idx, dia in enumerate(dias_lista, 2):
            cols_header[idx].markdown(f"<div class='header-col'>{dia}</div>", unsafe_allow_html=True)
            
        st.markdown("<hr style='margin-top:0; margin-bottom:15px;' />", unsafe_allow_html=True)
        
        # Renderiza os operadores do turno atual
        for _, row in df_turno.iterrows():
            nome_clean = str(row["NOME"]).strip()
            if "TOTAL" in nome_clean.upper() or nome_clean == "" or nome_clean == "nan":
                continue
                
            cols = st.columns([2.5, 2, 1.8, 1.8, 1.8, 1.8])
            cols[0].markdown(f"<div class='nome-operador'><b>{nome_clean}</b></div>", unsafe_allow_html=True)
            cols[1].markdown(f"<div class='funcao-operador'>{str(row['FUNÇÃO'])}</div>", unsafe_allow_html=True)
            
            for idx, dia in enumerate(dias_lista, 2):
                celula = str(row[dia]).strip().upper()
                
                # Exibe o bloco preto se for dia de trabalho, ou amarelo se for folga
                if "FOLGA" not in celula and celula != "NAN" and celula != "":
                    cols[idx].markdown(f"<div class='card-trabalho'>TRABALHO<div class='sub-info'>{conf['horario']}</div></div>", unsafe_allow_html=True)
                else:
                    cols[idx].markdown("<div class='card-folga'>FOLGA<div class='sub-info-folga'>Descanso</div></div>", unsafe_allow_html=True)
        st.write("") # Espaço entre os turnos
    else:
        st.caption(f"Não foi possível carregar os dados do {conf['nome']}. Verifique as abas da planilha.")
