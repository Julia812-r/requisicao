import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Caminho dos arquivos
REQ_FILE = "requisicoes.csv"
ALMOX_FILE = "almox.csv"

st.set_page_config(page_title="Sistema de Requisições", layout="wide")

# Função para gerar número único de solicitação
def gerar_numero():
    return f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"

# Inicializar arquivos se não existirem
if not os.path.exists(REQ_FILE):
    pd.DataFrame(columns=[ 
        'Número Solicitação', 'Nome do Solicitante', 'Métier', 'Tipo', 'Descrição', 
        'Linha de Projeto', 'Produto Novo ou Previsto', 'Valor Total', 
        'Caminho Orçamento', 'Comentários', 'Status'
    ]).to_csv(REQ_FILE, index=False)

if not os.path.exists(ALMOX_FILE):
    pd.DataFrame(columns=[ 
        'Nome do Solicitante', 'MABEC', 'Descrição do Produto', 'Quantidade'
    ]).to_csv(ALMOX_FILE, index=False)

# Carregar dados no session_state para evitar perdas ao atualizar a página
if 'df_requisicoes' not in st.session_state:
    st.session_state.df_requisicoes = pd.read_csv(REQ_FILE)

if 'df_almox' not in st.session_state:
    st.session_state.df_almox = pd.read_csv(ALMOX_FILE)

# Abas
abas = [
    "Nova Solicitação de Requisição", 
    "Conferir Status de Solicitação", 
    "Solicitação Almox", 
    "Histórico (Acesso Restrito)"
]
aba = st.sidebar.selectbox("Selecione a aba", abas)

# ABA 1 - Nova Solicitação de Requisição
if aba == "Nova Solicitação de Requisição":
    st.title("Nova Solicitação de Requisição")

    nome = st.text_input("Nome do Solicitante")
    metier = st.text_input("Métier")
    tipo = st.radio("É serviço ou produto?", ["Serviço", "Produto"])
    descricao = st.text_area("Descrição do Item")
    projeto = st.text_input("Linha de Projeto")
    novo_previsto = st.radio("É produto novo ou previsto?", ["Novo", "Previsto"])
    valor = st.number_input("Valor Total", min_value=0.0, format="%.2f")
    orcamento = st.file_uploader("Anexar Orçamento", type=["pdf", "jpg", "png"])
    comentarios = st.text_area("Comentários")

    if st.button("Enviar Solicitação"):
        numero = gerar_numero()
        caminho_arquivo = ""

        if orcamento:
            caminho_arquivo = os.path.join("uploads", f"{numero}_{orcamento.name}")
            os.makedirs("uploads", exist_ok=True)
            with open(caminho_arquivo, "wb") as f:
                f.write(orcamento.read())

        nova_linha = pd.DataFrame([{
            'Número Solicitação': numero,
            'Nome do Solicitante': nome,
            'Métier': metier,
            'Tipo': tipo,
            'Descrição': descricao,
            'Linha de Projeto': projeto,
            'Produto Novo ou Previsto': novo_previsto,
            'Valor Total': valor,
            'Caminho Orçamento': caminho_arquivo,
            'Comentários': comentarios,
            'Status': 'Aprovação de Solicitação'
        }])

        # Atualizar df_requisicoes e salvar no CSV
        st.session_state.df_requisicoes = pd.concat([st.session_state.df_requisicoes, nova_linha], ignore_index=True)
        st.session_state.df_requisicoes.to_csv(REQ_FILE, index=False)
        st.success(f"Solicitação enviada com sucesso! Número: {numero}")

# ABA 2 - Conferir Status
elif aba == "Conferir Status de Solicitação":
    st.title("Consultar Status da Solicitação")

    filtro_nome = st.text_input("Filtrar por Nome")
    filtro_numero = st.text_input("Filtrar por Número da Solicitação")

    df = st.session_state.df_requisicoes

    if filtro_nome:
        df = df[df['Nome do Solicitante'].str.lower().str.contains(filtro_nome.lower())]

    if filtro_numero:
        df = df[df['Número Solicitação'].str.upper() == filtro_numero.upper()]

    if df.empty:
        st.info("Nenhuma solicitação encontrada.")
    else:
        st.dataframe(df[['Número Solicitação', 'Nome do Solicitante', 'Status', 'Descrição']])

# ABA 3 - Solicitação Almox
elif aba == "Solicitação Almox":
    st.title("Solicitação para o Almoxarifado")

    nome = st.text_input("Nome do Solicitante")
    mabec = st.text_input("MABEC")
    descricao = st.text_input("Descrição do Produto")
    quantidade = st.number_input("Quantidade", min_value=1, step=1)

    if st.button("Enviar Solicitação de Almoxarifado"):
        nova_linha = pd.DataFrame([{
            'Nome do Solicitante': nome,
            'MABEC': mabec,
            'Descrição do Produto': descricao,
            'Quantidade': quantidade
        }])

        # Atualizar df_almox e salvar no CSV
        st.session_state.df_almox = pd.concat([st.session_state.df_almox, nova_linha], ignore_index=True)
        st.session_state.df_almox.to_csv(ALMOX_FILE, index=False)
        st.success("Solicitação de almoxarifado enviada com sucesso!")

# ABA 4 - Histórico com acesso restrito
elif aba == "Histórico (Acesso Restrito)":
    st.title("Histórico de Solicitações - Acesso Restrito")

    senha = st.text_input("Digite a senha de administrador", type="password")

    if senha == "admin123":
        df = st.session_state.df_requisicoes

        filtro_nome = st.text_input("Filtrar por nome (opcional)").strip()
        if filtro_nome:
            df = df[df['Nome do Solicitante'].str.lower().str.contains(filtro_nome.lower())]

        filtro_numero = st.text_input("Filtrar por número da solicitação (opcional)").strip()
        if filtro_numero:
            df = df[df['Número Solicitação'].str.upper() == filtro_numero.upper()]

        st.dataframe(df)

        if not df.empty:
            st.subheader("Atualizar Status")
            index = st.selectbox("Selecione a solicitação para editar (índice)", df.index)

            novo_status = st.selectbox("Novo status", [
                "Aprovação de Solicitação", "Criação da RC", "Aprovação Fabio Silva",
                "Aprovação Federico Mateos", "Pedido de Compra", "Aguardando Nota fiscal",
                "Aguardando entrega", "Entregue", "Serviço realizado", "Pago"
            ])

            if st.button("Atualizar Status"):
                st.session_state.df_requisicoes.at[index, 'Status'] = novo_status
                st.session_state.df_requisicoes.to_csv(REQ_FILE, index=False)
                st.success("Status atualizado com sucesso!")

            st.subheader("Excluir Solicitação")
            excluir_numero = st.text_input("Digite o número da solicitação para excluir", type="password")
            if excluir_numero:
                # Confirmar exclusão de solicitação
                solicitacao = df[df['Número Solicitação'] == excluir_numero]
                if not solicitacao.empty:
                    if st.button(f"Excluir Solicitação {excluir_numero}"):
                        # Excluir a solicitação
                        st.session_state.df_requisicoes = st.session_state.df_requisicoes[st.session_state.df_requisicoes['Número Solicitação'] != excluir_numero]
                        st.session_state.df_requisicoes.to_csv(REQ_FILE, index=False)
                        st.success(f"Solicitação {excluir_numero} excluída com sucesso!")
                else:
                    st.error("Número de solicitação não encontrado.")
    elif senha != "":
        st.error("Senha incorreta.")
