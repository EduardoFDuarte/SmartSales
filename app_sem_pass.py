import sqlite3
import pandas as pd
import streamlit as st

# Configurando o banco de dados SQLite
DB_PATH = "feiras_smart_sales.db"

def criar_tabelas():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.executescript('''
        CREATE TABLE IF NOT EXISTS Feiras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            localizacao TEXT NOT NULL,
            data_inicio DATE NOT NULL,
            data_fim DATE NOT NULL,
            setor TEXT NOT NULL,
            organizador TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            telefone TEXT,
            endereco TEXT,
            historico_servicos TEXT
        );

        CREATE TABLE IF NOT EXISTS Servicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            preco_base REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS SolicitacoesServicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            feira_id INTEGER NOT NULL,
            servico_id INTEGER NOT NULL,
            data_solicitacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Pendente',
            preco_final REAL,
            FOREIGN KEY (cliente_id) REFERENCES Clientes (id),
            FOREIGN KEY (feira_id) REFERENCES Feiras (id),
            FOREIGN KEY (servico_id) REFERENCES Servicos (id)
        );

        CREATE TABLE IF NOT EXISTS Localizacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feira_id INTEGER NOT NULL,
            latitude REAL,
            longitude REAL,
            endereco_completo TEXT,
            FOREIGN KEY (feira_id) REFERENCES Feiras (id)
        );

        CREATE TABLE IF NOT EXISTS PublicidadePatrocinios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feira_id INTEGER NOT NULL,
            cliente_id INTEGER NOT NULL,
            espaco_publicitario TEXT NOT NULL,
            preco REAL NOT NULL,
            visualizacoes INTEGER DEFAULT 0,
            FOREIGN KEY (feira_id) REFERENCES Feiras (id),
            FOREIGN KEY (cliente_id) REFERENCES Clientes (id)
        );

        CREATE TABLE IF NOT EXISTS Comunicacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            feira_id INTEGER NOT NULL,
            mensagem TEXT NOT NULL,
            data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            documento_path TEXT,
            FOREIGN KEY (cliente_id) REFERENCES Clientes (id),
            FOREIGN KEY (feira_id) REFERENCES Feiras (id)
        );
        ''')


# Chamando a função para criar as tabelas ao iniciar o sistema
criar_tabelas()


# Função para executar comandos SQL
def executar_comando(sql, params=()):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor


# Funções para cada funcionalidade
def pagina_inicial():
    st.title("Bem-vindo à Smart Sales – Logística de Feiras")
    st.subheader("Destaques")
    st.write("- Pesquisa de feiras por localização, setor, ou data.")
    st.write("- Banner rotativo com destaque para serviços e parcerias.")
    st.write("- Call-to-action para solicitar serviços logísticos ou consultoria.")


def pesquisa_feiras():
    st.title("Pesquisa de Feiras")
    st.sidebar.header("Filtros")
    localizacao = st.sidebar.text_input("Localização")
    setor = st.sidebar.text_input("Setor")
    data_inicio = st.sidebar.date_input("Data de Início")
    data_fim = st.sidebar.date_input("Data de Fim")

    if st.sidebar.button("Pesquisar"):
        query = "SELECT * FROM Feiras WHERE 1=1"
        params = []

        if localizacao:
            query += " AND localizacao LIKE ?"
            params.append(f"%{localizacao}%")

        if setor:
            query += " AND setor LIKE ?"
            params.append(f"%{setor}%")

        if data_inicio:
            query += " AND data_inicio >= ?"
            params.append(data_inicio.strftime('%Y-%m-%d'))

        if data_fim:
            query += " AND data_fim <= ?"
            params.append(data_fim.strftime('%Y-%m-%d'))

        resultados = executar_comando(query, params).fetchall()
        for feira in resultados:
            st.write(f"**{feira[1]}** - {feira[2]} ({feira[3]} - {feira[4]})")

def pesquisa_clientes():
    st.title("Pesquisa de Clientes")
    
    # Configuração de filtros
    st.sidebar.header("Filtros de Pesquisa")
    nome = st.sidebar.text_input("Nome")
    email = st.sidebar.text_input("Email")
    telefone = st.sidebar.text_input("Telefone")

    # Botão de pesquisa
    if st.sidebar.button("Pesquisar"):
        query = "SELECT * FROM Clientes WHERE 1=1"
        params = []

        # Adiciona filtros dinamicamente
        if nome:
            query += " AND nome LIKE ?"
            params.append(f"%{nome}%")

        if email:
            query += " AND email LIKE ?"
            params.append(f"%{email}%")

        if telefone:
            query += " AND telefone LIKE ?"
            params.append(f"%{telefone}%")

        # Executa a consulta
        resultados = executar_comando(query, params).fetchall()

        # Exibe resultados
        if resultados:
            st.subheader("Resultados da Pesquisa")
            for cliente in resultados:
                st.write(f"**Nome:** {cliente[1]}")
                st.write(f"**Email:** {cliente[2]}")
                st.write(f"**Telefone:** {cliente[3]}")
                st.write(f"**Endereço:** {cliente[4]}")
                st.write(f"**Histórico de Serviços:** {cliente[5]}")
                st.write("---")
        else:
            st.warning("Nenhum cliente encontrado com os critérios fornecidos.")



def painel_cliente():
    st.title("Painel do Cliente")
    st.subheader("Envie suas informações")
    nome = st.text_input("Nome")
    email = st.text_input("Email")
    telefone = st.text_input("Telefone")
    mensagem = st.text_area("Mensagem")

    if st.button("Enviar"):
        query = "INSERT INTO Clientes (nome, email, telefone, historico_servicos) VALUES (?, ?, ?, ?)"
        executar_comando(query, (nome, email, telefone, mensagem))
        st.success("Informações enviadas com sucesso!")


import pandas as pd  # Biblioteca necessária para manipulação de dados

def painel_admin():
    st.title("Painel Administrativo")
    st.subheader("Gerenciamento de Dados")

    # Exibe abas para gerenciar dados
    tab1, tab2 = st.tabs(["Clientes", "Feiras"])

    # Aba para Clientes
    with tab1:
        st.subheader("Adicionar Cliente")
        nome = st.text_input("Nome do Cliente", key="adicionar_nome_cliente")
        email = st.text_input("Email do Cliente", key="adicionar_email_cliente")
        telefone = st.text_input("Telefone do Cliente", key="adicionar_telefone_cliente")
        endereco = st.text_area("Endereço do Cliente", key="adicionar_endereco_cliente")
        historico_servicos = st.text_area("Histórico de Serviços", key="adicionar_historico_cliente")

        if st.button("Adicionar Cliente", key="botao_adicionar_cliente"):
            if not nome or not email:
                st.error("Os campos Nome e Email são obrigatórios.")
            else:
                query = """
                INSERT INTO Clientes (nome, email, telefone, endereco, historico_servicos)
                VALUES (?, ?, ?, ?, ?)
                """
                executar_comando(query, (nome, email, telefone, endereco, historico_servicos))
                st.success("Cliente adicionado com sucesso!")
                

        st.subheader("Lista de Clientes")
        clientes = executar_comando("SELECT * FROM Clientes").fetchall()
        clientes_df = pd.DataFrame(clientes, columns=["ID", "Nome", "Email", "Telefone", "Endereço", "Histórico de Serviços"])
        
        if not clientes_df.empty:
            st.dataframe(clientes_df)

            # Botão para download do CSV
            csv_clientes = clientes_df.to_csv(index=False)
            st.download_button(
                label="Download da Lista de Clientes (CSV)",
                data=csv_clientes,
                file_name="clientes.csv",
                mime="text/csv",
            )

    # Aba para Feiras
    with tab2:
        st.subheader("Adicionar Feira")
        nome = st.text_input("Nome da Feira", key="adicionar_nome_feira")
        localizacao = st.text_input("Localização", key="adicionar_localizacao_feira")
        data_inicio = st.date_input("Data de Início", key="adicionar_data_inicio_feira")
        data_fim = st.date_input("Data de Fim", key="adicionar_data_fim_feira")
        setor = st.text_input("Setor", key="adicionar_setor_feira")
        organizador = st.text_input("Organizador", key="adicionar_organizador_feira")

        if st.button("Adicionar Feira", key="botao_adicionar_feira"):
            query = """
            INSERT INTO Feiras (nome, localizacao, data_inicio, data_fim, setor, organizador)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            executar_comando(query, (nome, localizacao, data_inicio, data_fim, setor, organizador))
            st.success("Feira adicionada com sucesso!")

        st.subheader("Lista de Feiras")
        feiras = executar_comando("SELECT * FROM Feiras").fetchall()
        feiras_df = pd.DataFrame(feiras, columns=["ID", "Nome", "Localização", "Data de Início", "Data de Fim", "Setor", "Organizador"])
        
        if not feiras_df.empty:
            st.dataframe(feiras_df)

            # Botão para download do CSV
            csv_feiras = feiras_df.to_csv(index=False)
            st.download_button(
                label="Download da Lista de Feiras (CSV)",
                data=csv_feiras,
                file_name="feiras.csv",
                mime="text/csv",
            )




# Menu principal
menu = st.sidebar.selectbox(
    "Navegação",
    ["Página Inicial", "Painel do Cliente", "Painel Administrativo", "Pesquisa de Feiras", "Pesquisa de Clientes"]
)

if menu == "Página Inicial":
    pagina_inicial()
elif menu == "Painel do Cliente":
    painel_cliente()
elif menu == "Painel Administrativo":
    painel_admin()
elif menu == "Pesquisa de Feiras":
    pesquisa_feiras()
elif menu == "Pesquisa de Clientes":
    pesquisa_clientes()
