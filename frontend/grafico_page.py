import streamlit as st
from datetime import date
from backend.views import gerar_grafico, pegar_df_preco_corrigido
import pandas as pd

def mostrar_pagina():
    st.header("Gráficos de Preço de Fechamento")
    st.write("Esta página exibirá gráficos baseados no preço de fechamento das ações da sua carteira.")

    # Verifica se a carteira está no session_state
    if 'carteira' not in st.session_state:
        st.error("Primeiro, gere a carteira na página de 'Estratégia'.")
        return

    # Recupera a carteira salva no session_state
    carteira = st.session_state['carteira']
    ticker_carteira = carteira['ticker'].tolist()

    # Inputs para data de início e fim
    data_ini = st.date_input('Data Inicial', value=date(2023, 1, 1))
    data_fim = st.date_input('Data Final', value=date(2023, 12, 31))

    # Simulação: Carrega o DataFrame de preços (isso será substituído pelo seu próprio carregamento de dados)
    df_preco = pegar_df_preco_corrigido(data_ini,data_fim,ticker_carteira)  # Aqui você precisa carregar o seu DataFrame real com os preços corrigidos

    # Botão para gerar gráfico
    if st.button('Gerar Gráficos'):
        if data_ini and data_fim:
            try:
                # Chama a função para gerar o gráfico
                fig = gerar_grafico(data_ini, data_fim, carteira['ticker'].tolist(), df_preco)
                
                # Exibe o gráfico gerado na página do Streamlit
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Ocorreu um erro ao gerar o gráfico: {str(e)}")
