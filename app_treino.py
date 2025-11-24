import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- Configuração da Página ---
st.set_page_config(page_title="Hybrid Trainer Elite V3", layout="wide", page_icon="💎")

# --- Estilo Visual ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #00E676; /* Verde Neon Sport */
        color: #000;
        font-weight: 800;
        height: 3.5em;
        border-radius: 8px;
        border: none;
        font-size: 16px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        background-color: #00C853;
    }
    h3 { color: #00C853 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💎 Hybrid Trainer: Inteligência Anti-Conflito")
st.markdown("Periodização completa com gestão de fadiga (Corrida x Musculação).")

# --- BARRA LATERAL (CORRIGIDA E COMPLETA) ---
with st.sidebar:
    st.header("⚙️ Configurações")
    
    # 1. Lógica da Chave Secreta (Auto-Login)
    if "GEMINI_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_KEY"]
        st.success("✅ Licença Ativa: Sistema Conectado")
    else:
        api_key = st.text_input("Sua Gemini API Key", type="password")
    
    st.markdown("---")
    
    # 2. Configurações do Ciclo (Que tinham sumido)
    st.markdown("**Ciclo & Nível**")
    semanas = st.slider("Duração do Ciclo (Semanas)", 8, 16, 12)
    nivel_experiencia = st.selectbox(
        "Nível do Atleta", 
        ["Iniciante (Foco em Adaptação)", "Intermediário", "Avançado/Elite"]
    )
    
    st.info("🧠 **Smart Logic Ativada:** O sistema evitará chocar treinos de perna pesados com treinos de corrida intensos.")

# --- SEÇÃO 1: PERFIL DE PERFORMANCE ---
st.subheader("1. Perfil do Atleta")
col1, col2, col3 = st.columns(3)
with col1:
    nome = st.text_input("Nome", value="Atleta")
    peso = st.number_input("Peso (kg)", value=78.0)
with col2:
    objetivo_prova = st.text_input("Meta Principal", value="Meia Maratona Sub 1h50")
    # Checkbox de volume mantido
    volume_alto = st.checkbox("Já suporta longos de 14km+?", value=True)
with col3:
    tempos_atuais = st.text_area("Seus Tempos (5k/10k/21k)", 
                                 value="5km: 24:20 | 10km: 53:50 | 21km: 1h59", height=100)

st.markdown("**Cargas de Referência (Para calibrar a musculação):**")
cargas_atuais = st.text_area("Cargas Atuais (Agachamento, Supino, etc)", 
                             value="Agachamento: 35kg/lado | Supino: 90kg total", height=70)

# --- SEÇÃO 2: ESTRUTURA DA ROTINA ---
st.subheader("2. Definição da Rotina Semanal")
st.caption("Selecione os dias disponíveis. A IA organizará a intensidade para evitar lesões.")

col_rot1, col_rot2 = st.columns(2)

with col_rot1:
    st.markdown("🏋️ **Musculação**")
    dias_musculacao = st.multiselect(
        "Dias de Treino de Força", 
        ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"],
        ["Seg", "Ter", "Qui", "Sex"]
    )
    divisao_treino = st.selectbox(
        "Estilo de Divisão Preferido", 
        ["Upper / Lower (Superior/Inferior)", "Upper / Lower / fullbody (Superior/Inferior/Corpo Todo)" , "Push / Pull / Legs (Empurrar/Puxar/Pernas)", "Full Body (Corpo Todo)"]
    )

with col_rot2:
    st.markdown("🏃 **Corrida**")
    dias_corrida = st.multiselect(
        "Dias de Treino de Corrida", 
        ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"],
        ["Seg", "Qua", "Sex", "Sáb"]
    )
    dia_longao = st.selectbox("Dia do Longão (Volume)", ["Sáb", "Dom", "Sex"], index=0)

# --- ENGINE DO PROMPT "GOLD EDITION" ---
st.markdown("---")
if st.button("GERAR PLANEJAMENTO BLINDADO 🛡️"):
    if not api_key:
        st.error("⚠️ Erro de Licença: Chave API não encontrada (Secrets ou Input).")
    elif not dias_musculacao or not dias_corrida:
        st.warning("⚠️ Selecione os dias de treino de força e corrida.")
    else:
        # Configuração do Modelo
        genai.configure(api_key=api_key)
        # Usando o modelo Flash 2.5
        model = genai.GenerativeModel('models/gemini-2.5-flash-preview-09-2025')

        # --- PROMPT COM LÓGICA DE TREINADOR HUMANO ---
        prompt_gold = f"""
        Aja como um Treinador de Elite (Especialista em Treinamento Concorrente/Híbrido).
        Crie um plano periodizado de {semanas} semanas.

        PERFIL DO ALUNO:
        - Nome: {nome} | Peso: {peso}kg
        - Nível: {nivel_experiencia} (IMPORTANTE: Ajuste a complexidade e volume baseado nisso).
        - Meta: {objetivo_prova}
        - Benchmarks Força: {cargas_atuais}
        - Benchmarks Corrida: {tempos_atuais}

        DISPONIBILIDADE:
        - Musculação ({divisao_treino}): {', '.join(dias_musculacao)}
        - Corrida: {', '.join(dias_corrida)} (Longo Obrigatório: {dia_longao})

        ---
        REGRAS DE OURO DA RECUPERAÇÃO (SISTEMA ANTI-LESÃO):
        1. GESTÃO DE CONFLITO: Ao distribuir os treinos, NUNCA coloque um treino de PERNAS (Lower Body) pesado no dia imediatamente anterior a um treino de TIROS (Z5) ou LONGO.
           - Se os dias forem seguidos, ajuste a musculação para um treino regenerativo ou foco em Upper Body nesse dia pré-corrida forte.
        2. DISTRIBUIÇÃO DE INTENSIDADE: Afaste os treinos chaves (Tiros e Longos) um do outro o máximo possível na semana.
        3. PARA INICIANTES: Se o nível for Iniciante, priorize técnica e volume moderado. Se for Avançado, use cargas altas e métodos de choque.

        ---
        ESTRUTURA DE GERAÇÃO (TOKEN SAVING):
        
        MÓDULO 1: A FICHA DE MUSCULAÇÃO (FIXA)
        - Crie fichas A, B (ou A/B/C) baseadas na divisão "{divisao_treino}".
        - Mínimo de 6 exercícios por treino.
        - Tabela: Exercício | Séries | Reps | Intervalo | RPE Sugerido.
        - Regra de Progressão: Explique como subir a carga ao longo das semanas.

        MÓDULO 2: O CRONOGRAMA DE CORRIDA (DINÂMICO - {semanas} SEMANAS)
        - Detalhe SEMANA A SEMANA.
        - Treinos Leves (Rodagem): Seja breve (ex: "50' Z2 Leve").
        - Treinos Chaves (Tiros/Longos): Detalhe o aquecimento, o tiro e o desaquecimento.
        - Progressão: O volume DEVE subir progressivamente nas fases de Base e Construção e cair no Polimento (Taper).
        
        SAÍDA (HTML PURO):
        - Estilo moderno, limpo e responsivo.
        - Use cores para diferenciar Força (Azul) e Corrida (Laranja).
        - Inclua uma tabela inicial de Zonas de Pace (Z1-Z5).
        - Não use Markdown, apenas HTML.
        """

        with st.spinner('O Treinador IA está calculando a logística de recuperação e gerando o plano...'):
            try:
                response = model.generate_content(prompt_gold)
                plano_html = response.text
                
                # Limpeza de segurança
                plano_html = plano_html.replace("```html", "").replace("```", "")

                st.success("✅ Planejamento Gerado com Inteligência Anti-Conflito!")
                
                # Renderização
                st.components.v1.html(plano_html, height=800, scrolling=True)

                # Download
                st.download_button(
                    label="📥 BAIXAR PLANO FINAL (.HTML)",
                    data=plano_html,
                    file_name=f"Treino_Hibrido_{nome}.html",
                    mime="text/html"
                )

            except Exception as e:
                st.error(f"Erro ao processar: {e}")

