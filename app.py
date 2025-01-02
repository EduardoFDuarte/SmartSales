import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import os 
from dotenv import load_dotenv
load_dotenv()


# Configuração do MongoDB Online
client = MongoClient("mongodb+srv://edufdu:Morelena2004@cluster0.mongodb.net/Feiras_SmartSales?retryWrites=true&w=majority")
db = client["Feiras_SmartSales"]

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["Feiras_SmartSales"]




try:
    client = MongoClient("mongodb://localhost:27017/")
    client.server_info()  # Verifica a conexão
    print("Conexão bem-sucedida!")
except Exception as e:
    print(f"Erro ao conectar: {e}")

# Adiciona um administrador
admin = {
    "username": "admin",  # Substitua pelo username desejado
    "password": "admin123"  # Substitua pela senha desejada
}

#db.Usuarios.insert_one(admin)
print("Administrador adicionado com sucesso!")

def autenticar_usuario():
    username = st.text_input("username")
    password = st.text_input("password", type="password")
    if st.button("Entrar"):
        usuario = db.Usuarios.find_one({"username": username, "password": password})
        if usuario:
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = usuario
            st.success("Login realizado com sucesso!")
        else:
            st.error("Credenciais inválidas.")

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
    organizador = st.sidebar.text_input("Organizador")

    if st.sidebar.button("Pesquisar"):
        query = {}
        if localizacao:
            query["localizacao"] = {"$regex": localizacao, "$options": "i"}
        if setor:
            query["setor"] = {"$regex": setor, "$options": "i"}
        if data_inicio and data_fim:
            query["data_inicio"] = {"$gte": datetime.combine(data_inicio, datetime.min.time())}
            query["data_fim"] = {"$lte": datetime.combine(data_fim, datetime.min.time())}
        if organizador:
            query["organizador"] = {"$regex": organizador, "$options": "i"}

        resultados = db.Feiras.find(query)
        for feira in resultados:
            st.write(f"**{feira['nome']}** - {feira['localizacao']} ({feira['data_inicio'].strftime('%d/%m/%Y')} - {feira['data_fim'].strftime('%d/%m/%Y')})")

def painel_cliente():
    st.title("Painel do Cliente")
    st.subheader("Envie suas informações")
    nome = st.text_input("Nome")
    email = st.text_input("Email")
    mensagem = st.text_area("Mensagem")
    if st.button("Enviar"):
        db.Clientes.insert_one({"nome": nome, "email": email, "mensagem": mensagem, "data_envio": datetime.now()})
        st.success("Informações enviadas com sucesso!")

def painel_admin():
    if not st.session_state.get("autenticado"):
        st.error("Por favor, faça login como administrador.")
        autenticar_usuario()
        return

    st.title("Painel Administrativo")

    st.subheader("Dados Recebidos")
    tab1, tab2 = st.tabs(["Clientes", "Feiras"])

    with tab1:
        clientes = db.Clientes.find()
        for cliente in clientes:
            st.write(f"**Nome:** {cliente['nome']}, **Email:** {cliente['email']}, **Mensagem:** {cliente['mensagem']}")

    with tab2:
        feiras = db.Feiras.find()
        for feira in feiras:
            st.write(f"**Nome:** {feira['nome']}, **Localização:** {feira['localizacao']}, **Datas:** {feira['data_inicio']} - {feira['data_fim']}")

    st.subheader("Adicionar Feira")
    nome = st.text_input("Nome da Feira")
    localizacao = st.text_input("Localização")
    data_inicio = st.date_input("Data de Início")
    data_fim = st.date_input("Data de Fim")
    setor = st.text_input("Setor")
    organizador = st.text_input("Organizador")
    if st.button("Adicionar Feira"):
        db.Feiras.insert_one({
            "nome": nome,
            "localizacao": localizacao,
            "data_inicio": datetime.combine(data_inicio, datetime.min.time()),
            "data_fim": datetime.combine(data_fim, datetime.min.time()),
            "setor": setor,
            "organizador": organizador
        })
        st.success("Feira adicionada com sucesso!")

# Menu principal
menu = st.sidebar.selectbox(
    "Navegação",
    ["Página Inicial", "Painel do Cliente", "Painel Administrativo"]
)

if menu == "Página Inicial":
    pagina_inicial()
elif menu == "Painel do Cliente":
    painel_cliente()
elif menu == "Painel Administrativo":
    painel_admin()

