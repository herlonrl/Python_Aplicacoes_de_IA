# Mini-Projeto 10 - Data App Para Dashboard Interativo de Sales Analytics em Python com Streamlit


# --- Bloco 1: Importação de Bibliotecas e Configuração da Página ---

# Para interagir com o banco de dados SQLite
import sqlite3 

# Importa bibliotecas de manipulação e análise de dados
import numpy as np   # Para operações numéricas e geração de dados aleatórios
import pandas as pd  # Para manipulação e análise de dados (DataFrames)

# Importa bibliotecas de visualização e web app
import plotly.express as px  # Para criação de gráficos interativos
import streamlit as st       # A biblioteca principal para criar a Data App

# Importa a biblioteca de geração de PDF e seus componentes
from fpdf import FPDF
from fpdf.enums import XPos, YPos  # Enumerações para posicionamento no PDF

# Importa módulos de data e hora
from datetime import datetime, date, timedelta  # Para manipular datas e calcular períodos

# Configuração Inicial da Aplicação Streamlit
st.set_page_config(
    page_title="Data Science Academy",  # Título que aparece na aba do navegador
    page_icon=":100:",                  # Ícone (emoji) que aparece na aba do navegador
    layout="wide",                      # Define o layout da página para usar a largura total da tela
    initial_sidebar_state="expanded",   # Garante que a sidebar (menu lateral) comece aberta
)


# --- Bloco 2: Inicialização e População do Banco de Dados ---

# Função de inicialização do banco de dados
def dsa_init_db(conn):

    """
    Inicializa o banco de dados.
    1. Cria a tabela 'tb_vendas' se ela não existir.
    2. Verifica se a tabela está vazia.
    3. Se estiver vazia, popula com 180 dias de dados fictícios.
    """

    # Cria um objeto 'cursor' para executar comandos SQL na conexão fornecida
    cursor = conn.cursor()
    
    # Define o comando SQL para criar a tabela
    # 'IF NOT EXISTS' é uma cláusula de segurança que impede erro se a tabela já existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tb_vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            date TEXT,
            regiao TEXT,
            categoria TEXT,
            produto TEXT,
            faturamento REAL,
            quantidade INTEGER
        )
    """)

    # Confirma (commita) a transação de criação da tabela
    conn.commit()

    # Verifica quantos registros (linhas) existem na tabela
    cursor.execute("SELECT COUNT(*) FROM tb_vendas")

    # .fetchone()[0] captura o primeiro valor da primeira linha do resultado (a contagem)
    # Este 'if' garante que o código de popular dados SÓ rode se a tabela estiver vazia
    if cursor.fetchone()[0] == 0:

        # --- Geração de Dados Fictícios ---
        
        # Define a "semente" (seed) para o gerador de números aleatórios
        # Isso garante que os mesmos dados "aleatórios" sejam gerados toda vez
        # que o script for executado, tornando os resultados reprodutíveis.
        np.random.seed(42)
        
        # Define uma data de início fixa (1º de Jan de 2026) para os dados
        start_date = date(2026, 1, 1)
        
        # Cria uma lista de 180 objetos 'date' consecutivos
        datas = [start_date + timedelta(days = i) for i in range(180)]
        
        # Define as listas de dimensões para os dados
        regioes = ["Norte", "Nordeste", "Sul", "Sudeste", "Centro-Oeste"]
        categorias = ["Eletrônicos", "Roupas", "Alimentos", "Serviços"]
        
        # Dicionário aninhado para mapear produtos e seus preços base por categoria
        # Isso é crucial para criar a correlação positiva entre quantidade e faturamento
        dict_produtos = {
            "Eletrônicos": {"Smartphone": 1200, "Laptop": 3500, "Tablet": 800},
            "Roupas": {"Camiseta": 50, "Terno": 150, "Casaco": 300},
            "Alimentos": {"Congelados": 40, "Bebidas": 15, "Limpeza": 25},
            "Serviços": {"Consultoria": 1000, "Instalação": 400, "Suporte": 200}
        }

        # Lista vazia para armazenar todas as linhas (tuplas) de dados
        rows = []

        # Loop para cada dia na lista de datas
        for d in datas:

            # Simula um número aleatório de vendas (entre 5 e 14) para aquele dia
            vendas_diarias = np.random.randint(5, 15)

            # Loop para cada venda individual dentro do dia
            # Usamos '_' como variável pois não precisamos do número do índice
            for _ in range(vendas_diarias):

                # Escolhe aleatoriamente os atributos da venda
                r = np.random.choice(regioes)
                c = np.random.choice(categorias)
                
                # Escolhe um produto aleatório *baseado* na categoria escolhida
                p = np.random.choice(list(dict_produtos[c].keys()))
                
                # Obtém o preço base do produto escolhido
                preco_base = dict_produtos[c][p]
                
                # Gera uma quantidade aleatória (entre 1 e 24)
                quantidade = np.random.randint(1, 25) 
                
                # Calcula o faturamento base (preço * quantidade)
                base_faturamento = preco_base * quantidade
                
                # Adiciona "ruído" (noise) de +/- 20% para tornar os dados mais realistas
                # Isso simula descontos, impostos ou pequenas variações de preço
                noise = np.random.uniform(-0.20, 0.20)
                faturamento = base_faturamento * (1 + noise)
                
                # Garante que o faturamento nunca seja negativo
                faturamento = max(0, faturamento)

                # Adiciona a linha de venda (como uma tupla) à lista 'rows'
                # O formato da tupla deve corresponder exatamente à ordem das colunas no INSERT
                rows.append((d.isoformat(), r, c, p, round(faturamento, 2), quantidade))

        # --- Inserção em Massa (Bulk Insert) ---
        # 'executemany' é MUITO mais eficiente do que fazer um 'execute' para cada linha
        # Insere todas as tuplas da lista 'rows' no banco de dados de uma só vez
        cursor.executemany(
            "INSERT INTO tb_vendas (date, regiao, categoria, produto, faturamento, quantidade) VALUES (?, ?, ?, ?, ?, ?)",
            rows,
        )

        # Confirma (commita) a transação de inserção de dados
        conn.commit()


# --- Bloco 3: Função de Conexão com o Banco de Dados ---

# Função de conexão ao banco de dados
def dsa_cria_conexao(db_path = "dsa_database.db"):

    """
    Cria e retorna um objeto de conexão com o banco de dados SQLite.
    
    Parâmetros:
    db_path (str): O caminho e nome do arquivo .db a ser usado. 
                   O padrão é "dsa_database.db".
                   Se o arquivo não existir, o SQLite o criará.
    """

    # Cria a conexão com o banco de dados SQLite
    # check_same_thread=False: Esta é uma configuração importante para o Streamlit.
    # O Streamlit executa o código em diferentes threads (processos). 
    # Por padrão, o SQLite só permite que a thread que o criou interaja com ele.
    # Definir como 'False' permite que múltiplas threads (como as do Streamlit) 
    # acessem a mesma conexão.
    conn = sqlite3.connect(db_path, check_same_thread = False)
    
    # Retorna o objeto de conexão para ser usado por outras funções
    return conn


# --- Bloco 4: Função de Carregamento de Dados com Cache ---

# --- Decorador de Cache do Streamlit ---
# @st.cache_data: Este é um comando "mágico" do Streamlit.
# Ele "memoriza" o resultado (o DataFrame) desta função.
# Se a função for chamada novamente (ex: quando o usuário mexe um filtro),
# o Streamlit usa o resultado salvo na memória em vez de rodar a função de novo.
# ttl=600: (Time To Live) Define que o cache expira após 600 segundos (10 minutos).
# Após 10 minutos, o Streamlit executará a função novamente para buscar dados frescos.
@st.cache_data(ttl=600) 
def dsa_carrega_dados():

    """
    Função principal para carregar os dados.
    1. Conecta ao banco.
    2. Garante que o banco esteja inicializado (chama Bloco 2).
    3. Carrega a tabela 'tb_vendas' em um DataFrame do Pandas.
    4. Fecha a conexão.
    5. Retorna o DataFrame.
    """
    
    # Chama a função do Bloco 3 para obter uma conexão com o DB
    conn = dsa_cria_conexao()
    
    # Chama a função do Bloco 2 para garantir que o DB e a tabela existam
    # Se a tabela estiver vazia, esta função também irá populá-la.
    dsa_init_db(conn) 
    
    # Executa uma consulta SQL para selecionar TUDO (*) da 'tb_vendas'
    # pd.read_sql_query: Função do Pandas que lê o resultado de um SQL direto para um DataFrame.
    # parse_dates=["date"]: Instrui o Pandas a converter a coluna 'date' (que é TEXTO no SQLite)
    # em um tipo de dado datetime, que é essencial para gráficos e filtros de tempo.
    df = pd.read_sql_query("SELECT * FROM tb_vendas", conn, parse_dates = ["date"])
    
    # Boa prática: Fecha a conexão com o banco de dados após a consulta
    conn.close()
    
    # Retorna o DataFrame carregado para ser usado pelo restante do app
    return df


# --- Bloco 5: Função da Sidebar e Filtros ---

# Função com os filtros na barra lateral
def dsa_filtros_sidebar(df):

    """
    Cria todos os widgets da sidebar (menu lateral).
    1. Exibe o banner da DSA.
    2. Cria os filtros de data, região, categoria e produto.
    3. Aplica os filtros ao DataFrame.
    4. Retorna o DataFrame filtrado.
    
    Parâmetros:
    df (pd.DataFrame): O DataFrame original completo (antes dos filtros).
    """
    
    # --- Banner da Sidebar ---
    # 'st.sidebar' ancora qualquer elemento streamlit na barra lateral
    # 'markdown' renderiza texto formatado.
    # 'unsafe_allow_html=True' é necessário para renderizar o bloco HTML/CSS customizado
    st.sidebar.markdown(
        """
        <div style="background-color:#00CC96; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 15px;">
            <h3 style="color:white; margin:0; font-weight:bold;">Data Science Academy</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Adiciona um cabeçalho para a seção de filtros
    st.sidebar.header("🔍 Filtros")
    
    # --- Filtro de Data ---

    # Encontra a data mínima e máxima no DataFrame para definir os limites do filtro
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    
    # Cria o widget de seleção de intervalo de datas (calendário)
    # O valor padrão 'value' é uma tupla com o intervalo completo (min_date, max_date)
    date_range = st.sidebar.date_input("Período de Análise", (min_date, max_date), min_value = min_date, max_value = max_date)

    # --- Filtros de Seleção Múltipla (Multiselect) ---

    # Filtro de Região
    # 1. Pega todos os valores únicos da coluna 'regiao'
    # 2. 'sorted()' os coloca em ordem alfabética para o menu
    all_regioes = sorted(df["regiao"].unique())
    
    # 3. Cria o widget. 'default=all_regioes' faz com que todas as opções comecem selecionadas por padrão.
    selected_regioes = st.sidebar.multiselect("Regiões", all_regioes, default = all_regioes)

    # Filtro de Categoria (mesma lógica)
    all_categorias = sorted(df["categoria"].unique())
    selected_categorias = st.sidebar.multiselect("Categorias", all_categorias, default = all_categorias)
    
    # Filtro de Produto (mesma lógica)
    all_produtos = sorted(df["produto"].unique())
    selected_produtos = st.sidebar.multiselect("Produtos", all_produtos, default = all_produtos)

    # --- Lógica de Aplicação dos Filtros ---

    # Validação para garantir que o 'date_range' retornou um início e fim
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        # Fallback caso algo dê errado (ex: usuário limpa o campo)
        start_date, end_date = min_date, max_date

    # Aplica a filtragem no DataFrame principal ('df') usando boolean indexing do Pandas
    df_dsa_filtrado = df[

        # 1. Filtro de Data: Compara a data da linha com o 'start_date' e 'end_date'
        (df["date"].dt.date >= start_date) &
        (df["date"].dt.date <= end_date) &
        
        # 2. Filtros de Categoria: '.isin()' verifica se o valor da linha está presente na lista de itens selecionados no multiselect
        (df["regiao"].isin(selected_regioes)) &
        (df["categoria"].isin(selected_categorias)) &
        (df["produto"].isin(selected_produtos))
    ].copy() # .copy() cria um novo DataFrame independente, em vez de uma "fatia"

    # --- Rodapé da Sidebar ---
    
    # Adiciona uma linha horizontal para separar os filtros do rodapé
    st.sidebar.markdown("---")

    # Cria um "expander" para informações de suporte
    # 'expanded=False' garante que ele comece fechado
    with st.sidebar.expander("🆘 Suporte / Fale conosco", expanded = False):
        st.write("Se tiver dúvidas envie mensagem para suporte@datascienceacademy.com.br")
    
    # Adiciona uma legenda de rodapé com 'st.sidebar.caption'
    st.sidebar.caption("Dashboard Desenvolvido no Mini-Projeto 10 do Curso Gratuito de Python da Data Science Academy.")

    # Retorna o DataFrame recém-filtrado para ser usado no corpo principal da página
    return df_dsa_filtrado


# --- Bloco 6: Função para Renderizar os Cards de KPIs ---

# Função para os KPIs
def dsa_renderiza_cards_kpis(df):

    """
    Calcula e exibe os 4 principais KPIs (Indicadores-Chave de Performance)
    em cards estilizados no topo da página.
    
    Utiliza o DataFrame JÁ FILTRADO para fazer os cálculos.
    
    Parâmetros:
    df (pd.DataFrame): O DataFrame filtrado pela sidebar.
    
    Retorna:
    (tuple): Uma tupla com os valores calculados (total_faturamento, total_qty, avg_ticket)
             para que possam ser reutilizados (ex: no PDF).
    """

    # --- 1. Cálculos dos KPIs ---
    
    # Soma a coluna 'faturamento' para obter o total
    total_faturamento = df["faturamento"].sum()
    
    # Soma a coluna 'quantidade'
    total_qty = df["quantidade"].sum()
    
    # Calcula o Ticket Médio (Faturamento / Quantidade)
    # Inclui uma verificação 'if total_qty > 0' para evitar um erro de Divisão por Zero
    # se o DataFrame filtrado estiver vazio.
    avg_ticket = total_faturamento / total_qty if total_qty > 0 else 0
    
    # Gera um número aleatório para SIMULAR uma variação (delta) vs. meta.
    # Este é um valor fictício apenas para fins de design do dashboard.
    delta_rev = np.random.uniform(-5, 15)
    
    # --- 2. Criação do Layout ---

    # 'st.columns(4)' cria 4 colunas virtuais de mesmo tamanho
    # 'c1', 'c2', 'c3', 'c4' se tornam "containers" para esses espaços
    c1, c2, c3, c4 = st.columns(4)
    
    # --- 3. Renderização dos Cards ---
    
    # Bloco 'with' garante que o conteúdo a seguir seja renderizado dentro da Coluna 1
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Receita Total</h3>
            <h2>R$ {total_faturamento:,.0f}</h2>
            <div class="delta" style="color: {'#4CAF50' if delta_rev > 0 else '#FF5252'}">
                {delta_rev:+.1f}% vs meta
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Renderiza o Card 2 na Coluna 2
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Vendas (Qtd)</h3>
            <h2>{total_qty:,.0f}</h2>
            <div class="delta">Unidades vendidas</div>
        </div>
        """, unsafe_allow_html=True)

    # Renderiza o Card 3 na Coluna 3
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Ticket Médio</h3>
            <h2>R$ {avg_ticket:,.2f}</h2>
            <div class="delta">Por transação</div>
        </div>
        """, unsafe_allow_html=True)

    # Renderiza o Card 4 na Coluna 4
    with c4:
        transactions = df.shape[0]
        st.markdown(f"""
        <div class="metric-card">
            <h3>Transações</h3>
            <h2>{transactions}</h2>
            <div class="delta">Volume total</div>
        </div>
        """, unsafe_allow_html=True)
        
    # Retorna os valores calculados para que a função 'main' possa passá-los para a função de gerar o PDF
    return total_faturamento, total_qty, avg_ticket


# --- Bloco 7: Função de Geração de Relatório PDF ---

# Função para gerar o relatório em pdf
def dsa_gera_pdf_report(df_dsa_filtrado, total_faturamento, total_quantidade, avg_ticket):

    """
    Gera um relatório PDF customizado usando a biblioteca FPDF.
    
    Parâmetros:
    df_dsa_filtrado (pd.DataFrame): O DataFrame filtrado.
    total_faturamento (float): O valor do KPI de faturamento.
    total_quantidade (int): O valor do KPI de quantidade.
    avg_ticket (float): O valor do KPI de ticket médio.
    
    Retorna:
    (bytes): Os bytes brutos do arquivo PDF gerado.
    """
    
    # --- 1. Configuração Inicial do PDF ---

    # Inicializa o objeto FPDF
    pdf = FPDF()
    
    # Habilita a quebra de página automática com 15mm de margem inferior
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Adiciona uma nova página ao documento
    pdf.add_page()

    # --- 2. Título e Metadados ---

    # Define a fonte ("Helvetica", Negrito, Tamanho 16)
    # A fonte "Helvetica" é a substituta moderna da "Arial" para evitar warnings.
    pdf.set_font("Helvetica", "B", 16)
    
    # Cria a célula do título.
    # Parâmetros: (largura, altura, texto, alinhamento)
    # new_x/new_y são a sintaxe moderna para substituir o 'ln=True' (quebra de linha)
    pdf.cell(0, 10, "Relatorio Executivo de Vendas", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Adiciona um espaço vertical (quebra de linha) de 5 pontos
    pdf.ln(5)

    # Adiciona o carimbo de data/hora da geração
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # --- 3. Bloco de Resumo de KPIs (com fundo cinza) ---
    
    # Define a cor de preenchimento (cinza claro) e desenha um retângulo
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(10, 35, 190, 25, 'F')
    
    # Define a posição Y (vertical) do cursor para 40,
    # para que o texto seja escrito EM CIMA do retângulo
    pdf.set_y(40)
    
    # Escreve os cabeçalhos dos KPIs
    pdf.set_font("Helvetica", "B", 12)
    
    # new_x=XPos.RIGHT, new_y=YPos.TOP: move o cursor para a direita, mas mantém na mesma linha
    pdf.cell(60, 8, f"Receita Total", align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(60, 8, f"Quantidade", align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    
    # new_x=XPos.LMARGIN, new_y=YPos.NEXT: quebra a linha após esta célula
    pdf.cell(60, 8, f"Ticket Medio", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Escreve os valores dos KPIs (logo abaixo dos cabeçalhos)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(60, 8, f"R$ {total_faturamento:,.2f}", align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(60, 8, f"{total_quantidade:,}", align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(60, 8, f"R$ {avg_ticket:,.2f}", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Adiciona um espaço vertical grande após o bloco de KPIs
    pdf.ln(15)

    # --- 4. Tabela "Top 15 Vendas" ---
    
    # Adiciona o subtítulo da tabela
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Top 15 Vendas (por receita):", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Define as larguras de cada coluna da tabela e os nomes dos cabeçalhos
    col_widths = [30, 30, 30, 40, 25, 30] 
    headers = ["Data", "Regiao", "Categoria", "Produto", "Qtd", "Receita"]
    
    # Loop para desenhar o CABEÇALHO da tabela
    pdf.set_font("Helvetica", "B", 9)
    for i, h in enumerate(headers):
        
        # O '1' no quarto parâmetro desenha a borda da célula
        pdf.cell(col_widths[i], 8, h, 1, align='C', new_x=XPos.RIGHT, new_y=YPos.TOP)
    
    pdf.ln() # Quebra a linha após o cabeçalho estar completo
    
    # --- 5. População da Tabela com Dados ---

    # Prepara os dados: ordena o DataFrame pelo faturamento e pega os 15 primeiros
    pdf.set_font("Helvetica", "", 9)
    df_top = df_dsa_filtrado.sort_values("faturamento", ascending=False).head(15)
    
    # Loop principal (externo): itera sobre cada linha do DataFrame df_top
    for _, row in df_top.iterrows():
        
        # Extrai os dados da linha do Pandas para uma lista simples
        # Trunca o nome do produto para 20 caracteres para caber na célula
        data = [
            str(row['date'].date()),
            row['regiao'],
            row['categoria'],
            row['produto'][:20], 
            str(row['quantidade']),
            f"R$ {row['faturamento']:,.2f}"
        ]
        
        # Loop interno: itera sobre cada item (célula) da linha atual
        for i, d in enumerate(data):
            
            # TRATAMENTO DE ENCODING:
            # O FPDF (baseado em Latin-1) quebra com caracteres especiais (ex: ç, ã).
            # Esta linha força o texto para o encoding 'latin-1', substituindo
            # caracteres inválidos por um '?' para evitar que o PDF quebre.
            safe_txt = str(d).encode("latin-1", "replace").decode("latin-1")
            
            # Desenha a célula de dados com o texto seguro e borda
            pdf.cell(col_widths[i], 7, safe_txt, 1, align=('C' if i==4 else 'L'), new_x=XPos.RIGHT, new_y=YPos.TOP)
        
        pdf.ln() # Quebra a linha após desenhar todas as células da linha

    # --- 6. Geração e Retorno do PDF ---

    # .output() sem parâmetros retorna o conteúdo do PDF como bytes (substitui o antigo 'dest="S"')
    result = pdf.output() 

    # Retorna os bytes brutos do PDF, prontos para o botão de download
    return result.encode("latin-1") if isinstance(result, str) else bytes(result)


# --- Bloco 8: Função de Estilização (Tema Customizado) ---

# Função para customização da interface com CSS
def dsa_set_custom_theme():

    """
    Define e injeta CSS customizado no app Streamlit.
    Isso é usado para alterar a aparência de elementos que
    o Streamlit não permite customizar nativamente (ex: cores de filtros, cards).
    """

    # --- 1. Definição das Cores do Tema ---

    # Cores usadas nos estilos CSS abaixo
    card_bg_color = "#262730"  # Fundo cinza escuro para os cards de KPI
    text_color = "#FAFAFA"     # Cor do texto principal (branco)
    gold_color = "#E1C16E"     # Cor bege-ouro para os filtros selecionados
    dark_text = "#1E1E1E"      # Cor de texto escura para usar sobre o fundo bege-ouro
    
    # --- 2. Criação do Bloco de Estilo CSS ---

    # 'css' é uma "f-string" gigante que contém todo o código CSS.
    # As variáveis Python (ex: {gold_color}) são injetadas no texto.
    css = f"""
    <style>

        /* --- Aumentar Altura Mínima dos Filtros Multiselect --- */
        /* [data-testid="stMultiSelect"]... : É um seletor CSS complexo que "mira" 
           exatamente na caixa interna do widget multiselect da sidebar. */
        [data-testid="stMultiSelect"] div[data-baseweb="select"] > div:first-child {{
            min-height: 100px !important;  /* Define uma altura mínima de 100px */
            overflow-y: auto !important;   /* Adiciona scroll vertical se os itens estourarem */
        }}
    
        /* --- Estilização dos Cards de KPI --- */
        /* Define a aparência da classe 'metric-card' (usada no Bloco 6) */
        .metric-card {{
            background-color: {card_bg_color};
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #444;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.3); /* Sombra sutil */
            text-align: center;
            margin-bottom: 10px; /* Espaçamento inferior */
        }}

        /* Estilo do subtítulo do card (ex: "Receita Total") */
        .metric-card h3 {{
            margin: 0;
            font-size: 1.2rem;
            color: #AAA; /* Cinza claro */
            font-weight: normal;
        }}

        /* Estilo do valor principal do card (ex: "R$ 1.500.000") */
        .metric-card h2 {{
            margin: 10px 0 0 0;
            font-size: 2rem;
            color: {text_color};
            font-weight: bold;
        }}

        /* Estilo do texto 'delta' (ex: "+5.0% vs meta") */
        .metric-card .delta {{
            font-size: 0.9rem;
            color: #4CAF50; /* Verde (padrão) */
            margin-top: 5px;
        }}
                
        /* --- Estilização dos Itens de Filtro Selecionados (Bege-Ouro) --- */
        /* [data-baseweb="tag"]: Mira nas "pílulas" dos itens selecionados
           dentro da caixa do multiselect. */
        [data-baseweb="tag"] {{
            background-color: {gold_color} !important;
            color: {dark_text} !important;
            border-radius: 4px !important;
        }}
        
        /* Mira no ícone 'X' dentro da pílula bege-ouro */
        [data-baseweb="tag"] svg {{
            color: {dark_text} !important;
        }}
        
        /* Muda a cor do 'X' para vermelho ao passar o mouse, indicando "excluir" */
        [data-baseweb="tag"] svg:hover {{
            color: #FF0000 !important; 
        }}
        
    </style>
    """
    
    # --- 3. Injeção do CSS na Página ---

    # st.markdown é usado para renderizar o bloco CSS.
    # 'unsafe_allow_html=True' é OBRIGATÓRIO para que o <style> seja aplicado.
    st.markdown(css, unsafe_allow_html = True)


# --- Bloco 9: Função Principal ---

# Esta é a função que "orquestra" todo o aplicativo.
# Ela define a ordem em que as coisas acontecem:
# 1. Configura o tema
# 2. Carrega os dados
# 3. Renderiza a sidebar e obtém os filtros
# 4. Renderiza o conteúdo da página principal (títulos, KPIs, abas)

# Função principal
def datascienceacademy_mp10():

    # Chama a função (Bloco 8) para injetar o CSS customizado
    dsa_set_custom_theme()
    
    # Carrega o DataFrame principal. 
    # Graças ao cache (@st.cache_data), isso só executa a consulta SQL
    # uma vez a cada 10 minutos, tornando o app muito rápido.
    df = dsa_carrega_dados()
    
    # Chama a função (Bloco 5) que desenha a sidebar e retorna
    # o DataFrame já filtrado (df_dsa_filtrado) com base nas seleções do usuário.
    df_dsa_filtrado = dsa_filtros_sidebar(df)

    # --- Início: Layout da Página Principal ---
    
    # Define os títulos e a descrição que aparecem no corpo principal do app
    st.title("Data Science Academy")
    st.title("Curso Gratuito de Linguagem Python - Mini-Projeto 10")
    st.title("📊 Data App Para Dashboard Interativo de Sales Analytics")
    st.subheader("Com Banco de Dados SQLite e Streamlit")
    st.write("Navegue pelo dashboard e use os filtros na barra lateral para diferentes visualizações. Os dados podem ser exportados para formato CSV e PDF.")
    st.markdown("---")
    st.markdown(f"Visão Consolidada de Vendas com KPIs.")

    # --- Verificação de Segurança ---

    # Se os filtros do usuário resultarem em um DataFrame vazio,
    # exibe um aviso e para a execução da 'main' aqui.
    # Isso evita que os cálculos de KPIs e gráficos quebrem.
    if df_dsa_filtrado.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
        return # Para a execução da função

    # Chama a função (Bloco 6) para renderizar os 4 cards de KPI.
    # Ela usa o DataFrame *filtrado* para os cálculos.
    # Também armazena os valores retornados (total_faturamento, etc.)
    # para usá-los mais tarde na geração do PDF.
    total_faturamento, total_qty, avg_ticket = dsa_renderiza_cards_kpis(df_dsa_filtrado)

    # Adiciona uma linha horizontal para separar os KPIs das abas
    st.markdown("---")

    # --- Layout de Abas (Tabs) ---

    # Cria a navegação principal da página com duas abas
    tab1, tab2 = st.tabs(["📈 Visão Gráfica", "📄 Dados Detalhados & Exportação (CSV e PDF)"])

    # --- Conteúdo da Aba 1: Gráficos ---
    with tab1:

        # Cria a primeira linha de layout da aba: 
        # uma coluna à esquerda com 2/3 da largura e uma à direita com 1/3
        col_left, col_right = st.columns([2, 1])
        
        # Bloco do Gráfico 1: Evolução da Receita (Coluna da Esquerda)
        with col_left:
            
            st.subheader("Evolução da Receita Diária")
            
            # Agrupa os dados por data e soma o faturamento
            daily_rev = df_dsa_filtrado.groupby("date")[["faturamento"]].sum().reset_index()
            
            # Cria o gráfico de linha com Plotly Express
            fig_line = px.line(daily_rev, x = "date", y = "faturamento", template = "plotly_dark", height = 400)
            
            # Adiciona uma estilização: preenchimento verde sob a linha
            fig_line.update_traces(fill = 'tozeroy', line = dict(color = '#00CC96', width = 3))
            
            # Renderiza o gráfico no Streamlit, usando a largura total da coluna
            st.plotly_chart(fig_line, width = 'stretch') 

        # Bloco do Gráfico 2: Mix de Categorias (Coluna da Direita)
        with col_right:
            
            st.subheader("Mix de Categorias")

            # Agrupa por categoria e soma o faturamento
            cat_rev = df_dsa_filtrado.groupby("categoria")[["faturamento"]].sum().reset_index()
            
            # Cria um gráfico de pizza (donut)
            fig_pie = px.pie(cat_rev, values="faturamento", names="categoria", hole=0.4, template="plotly_dark", height=400)
            st.plotly_chart(fig_pie, width='stretch') 

        # Cria a segunda linha de layout da aba: duas colunas de tamanho igual
        c_a, c_b = st.columns(2)
        
        # Bloco do Gráfico 3: Performance Regional
        with c_a:

            st.subheader("Performance Regional")
            fig_bar = px.bar(
                df_dsa_filtrado.groupby("regiao")[["faturamento"]].sum().reset_index(),
                x="regiao", y="faturamento", color="regiao", template="plotly_dark", text_auto='.2s'
            )

            st.plotly_chart(fig_bar, width='stretch') 
            
        # Bloco do Gráfico 4: Análise de Dia da Semana (com tradução)
        with c_b:

            st.subheader("Análise Dia da Semana")

            # Mapeamento para traduzir os dias da semana para Português
            dias_pt_map = {
                0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira",
                3: "Quinta-feira", 4: "Sexta-feira", 5: "Sábado", 6: "Domingo"
            }

            # Lista para garantir a ordem correta no gráfico
            dias_pt_ordem = [
                "Segunda-feira", "Terça-feira", "Quarta-feira", 
                "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"
            ]

            # Criação das colunas de dia da semana (número e nome em PT)
            # .dt.dayofweek retorna o dia (Segunda=0, Domingo=6)
            df_dsa_filtrado["weekday_num"] = df_dsa_filtrado["date"].dt.dayofweek
            
            # .map() usa o dicionário para "traduzir" os números
            df_dsa_filtrado["dia_semana"] = df_dsa_filtrado["weekday_num"].map(dias_pt_map)

            # Agrupa pelo nome em PT, calcula a média, e reordena
            wd_rev = df_dsa_filtrado.groupby("dia_semana")[["faturamento"]].mean().reindex(dias_pt_ordem).reset_index()

            # Cria o gráfico de barras
            fig_heat = px.bar(wd_rev, x="dia_semana", y="faturamento", title="Receita Média x Dia", template="plotly_dark")
            st.plotly_chart(fig_heat, width='stretch')
            
        # Bloco do Gráfico 5: Dispersão (Scatter Plot)
        st.subheader("Dispersão: Quantidade x Faturamento x Produto")
        
        # Este gráfico mostra a correlação positiva que criamos nos dados fictícios
        fig_scat = px.scatter(
            df_dsa_filtrado, x="quantidade", y="faturamento", color="categoria", size="faturamento",
            hover_data=["produto"], template="plotly_dark", height=500
        )
        
        st.plotly_chart(fig_scat, width='stretch') 

    # --- Conteúdo da Aba 2: Dados e Exportação ---
    with tab2:

        # Exibe a tabela de dados filtrados
        st.subheader("Visualização Tabular")
        st.dataframe(df_dsa_filtrado, width='stretch', height=400) 
        
        st.markdown("### 📥 Área de Exportação")
        
        # Cria duas colunas para os botões de download
        c_exp1, c_exp2 = st.columns(2)
        
        # Coluna do Botão 1: Download CSV
        with c_exp1:
            
            # Converte o DataFrame filtrado para um string CSV em memória
            csv = df_dsa_filtrado.to_csv(index=False).encode('utf-8')
            
            # Cria o botão de download
            st.download_button(
                label = "💾 Baixar CSV (Excel)",
                data = csv,
                file_name = "dados_filtrados.csv",
                mime = "text/csv",
                width = 'stretch' 
            )
            
        # Coluna do Botão 2: Download PDF
        with c_exp2:
            
            # Lógica de 2 cliques:
            # 1. O usuário clica neste 'st.button'
            if st.button("📄 Gerar Relatório PDF", width='stretch'): 
                
                # 2. O app mostra um "spinner" (loading)
                with st.spinner("Renderizando PDF..."):
                    
                    # 3. A função de geração de PDF (Bloco 7) é executada
                    pdf_bytes = dsa_gera_pdf_report(df_dsa_filtrado, total_faturamento, total_qty, avg_ticket)
                    
                    # 4. O botão de download real aparece para o usuário clicar
                    st.download_button(
                        label = "⬇️ Clique aqui para Salvar PDF",
                        data = pdf_bytes,
                        file_name = f"Relatorio_Vendas_{date.today()}.pdf",
                        mime = "application/pdf",
                        key = "pdf-download-final" # Chave única para o widget
                    )

    # --- Rodapé da Página Principal ---
    st.markdown("---")
    
    # Caixa "expander" (sanfona) com informações sobre o app
    with st.expander("ℹ️ Sobre Esta Data App", expanded=False):
        st.info("Este dashboard combina as melhores práticas de visualização e manipulação de dados.")
        st.markdown("""
        **Recursos Integrados:**
        - **Engine:** Python + Streamlit + SQLite.
        - **Visualização:** Plotly Express e tema Dark no Streamlit.
        - **Relatórios:** Geração de PDF com FPDF (compatível com Latin-1).
        - **Performance:** Cache de dados (`@st.cache_data`).
        - **DSA:** Para conhecer mais sobre os cursos visite: www.datascienceacademy.com.br.
        """)


# --- Bloco 10: Ponto de Entrada da Execução ---

# Esta é uma construção padrão em Python.
# Python define internamente a variável '__name__' para todos os scripts.
# Se você executar este script DIRETAMENTE (ex: 'python dsa_app.py'),
# Python definirá __name__ = "__main__".
# Se este script for IMPORTADO por outro script,
# Python definirá __name__ = "dsa_app" (o nome do arquivo).

# Portanto, este 'if' garante que o código dentro dele (a chamada para 'datascienceacademy_mp10()')
# só será executado se este arquivo for o ponto de partida,
# e não se ele for apenas importado como um módulo.
if __name__ == "__main__":
    
    # Chama a função principal (Bloco 9) para iniciar o aplicativo.
    datascienceacademy_mp10()


# Obrigado DSA

