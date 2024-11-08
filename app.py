# app.py
import streamlit as st
from streamlit_option_menu import option_menu
import setup_paths  # Configuração de caminhos do sistema
import frontend.inicio_page as inicio
import frontend.planilhao_page as planilhao
import frontend.estrategia_page as estrategia
import frontend.grafico_page as grafico


# Título principal da aplicação
st.title("Projeto AP2 - Lucas Rodor")

# Menu lateral com navegação
with st.sidebar:
    # Menu principal para navegar entre as páginas
    pagina_selecionada = option_menu(
        menu_title="",  
        options=["Página Inicial", "Planilhão", "Estratégia", "Gráficos"],  
        icons=["house", "file-bar-graph", "sliders", "bar-chart-line"],  
        menu_icon="cast",  
        default_index=0,  
    )

# Exibe o conteúdo da página com base na seleção
if pagina_selecionada == "Página Inicial":
    inicio.mostrar_pagina()
elif pagina_selecionada == "Planilhão":
    planilhao.mostrar_pagina()
elif pagina_selecionada == "Estratégia":
    estrategia.mostrar_pagina()
elif pagina_selecionada == "Gráficos":
    grafico.mostrar_pagina()
