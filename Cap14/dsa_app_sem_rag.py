# Mini-Projeto 8 - IA Generativa, LLM e RAG Para Assistente Jurídico em Python com LangChain
# App sem o uso de RAG

# Importa o módulo 'os' para manipulação de variáveis de ambiente
import os

# Importa o Streamlit para criar a interface web do app
import streamlit as st

# Importa classes essenciais para criação de prompts de chat no LangChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Importa tipos de mensagens usadas no contexto da conversa
from langchain_core.messages import SystemMessage, HumanMessage

# Importa o conector ChatGroq para usar o modelo via API Groq
from langchain_groq import ChatGroq

# Define as configurações iniciais da página do Streamlit (título, ícone e layout)
st.set_page_config(page_title = "Data Science Academy", page_icon = ":100:", layout = "wide")

# Cria a barra lateral do app com elementos de configuração
with st.sidebar:
    st.header("Configurações")
    api_key = st.text_input("Coloque aqui sua GROQ API Key e pressione Enter", type = "password")
    st.divider()
    st.subheader("Instruções")
    st.write("1) Informe sua chave no campo acima.\n2) Digite sua pergunta ou dúvida.\n3) Clique em Enviar.")
    st.info("Aviso: a IA pode cometer erros. Verifique fatos críticos.")
    st.link_button("Clique Aqui Se Precisar de Suporte", "https://www.datascienceacademy.com.br/suportedsa")

# Exibe os títulos principais e subtítulo do app
st.title("Data Science Academy")
st.title("Mini-Projeto 8 - Versão 1")
st.title("⚖️ Assistente Jurídico (Sem o Uso de RAG)")

# Exibe o modelo utilizado
st.caption("Modelo: openai/gpt-oss-20b via Groq + LangChain")

# Verifica se a chave de API foi informada; se não, interrompe a execução
if not api_key:
    st.warning("Informe a GROQ API Key na barra lateral para começar.")
    st.stop()

# Armazena a chave informada na variável de ambiente para uso pela API Groq
os.environ["GROQ_API_KEY"] = api_key

# Inicializa o modelo de linguagem via ChatGroq com parâmetros de temperatura e limite de tokens
dsa_llm = ChatGroq(model = "openai/gpt-oss-20b", temperature = 0.2, max_tokens = 1024)

# Define o prompt base com orientações de escrita e responsabilidade jurídica
system_block = """Você é um assistente jurídico que escreve de forma objetiva e clara, sem dar aconselhamento legal definitivo.
Forneça análise, contexto e referências genéricas (leis, súmulas, doutrina) sem afirmar certeza absoluta.
Se algo for incerto, explique como um profissional verificaria a informação (consultar legislação atualizada, jurisprudência local, etc.).
Estruture a resposta com: Contexto breve, Pontos principais, Riscos/limitações, Próximos passos práticos."""

# Cria o template de prompt para conversas, incluindo o bloco de sistema e o histórico
dsa_prompt = ChatPromptTemplate.from_messages(
    [
        # Define a mensagem de sistema com as instruções do assistente
        SystemMessage(content = system_block),
        
        # Placeholder para armazenar o histórico da conversa
        MessagesPlaceholder(variable_name = "history"),
        
        # Define a mensagem humana padrão com formatação da pergunta
        ("human", "Pergunta: {pergunta}\nResponda de forma sucinta, técnica e didática.")
    ]
)

# Inicializa o histórico da conversa, caso ainda não exista na sessão
if "history" not in st.session_state:
    st.session_state.history = []

# Cria um formulário para envio da pergunta
with st.form("form"):
    
    # Campo de texto para digitar a pergunta 
    pergunta = st.text_area("Pergunta", height = 120, placeholder = "Digite sua dúvida sobre jurídica")
    
    # Botão para enviar o formulário
    enviado = st.form_submit_button("Enviar")

# Executa o processamento quando o botão "Enviar" for clicado
if enviado:
    
    # Gera as mensagens com base no histórico e na nova pergunta
    msgs = dsa_prompt.invoke({"history": st.session_state.history, "pergunta": pergunta})
    
    # Invoca o modelo de linguagem para gerar a resposta
    resp = dsa_llm.invoke(msgs.to_messages())
    
    # Atualiza o histórico da sessão com a pergunta e a resposta do modelo
    st.session_state.history.extend(
        [
            HumanMessage(content = f"Pergunta: {pergunta}"), resp
        ]
    )
    
    # Exibe o título da seção de resposta
    st.markdown("### Resposta")
    
    # Mostra o conteúdo textual retornado pelo modelo
    st.write(resp.content)


# Obrigado DSA


