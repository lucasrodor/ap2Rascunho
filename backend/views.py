import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
import logging
logger = logging.getLogger(__name__)
from apis import (obter_dados_planilhao,obter_preco_corrigido,obter_preco_ibovespa)


def filtrar_duplicado(df:pd.DataFrame, meio:str = None) -> pd.DataFrame:
    """
    Filtra o df das ações duplicados baseado no meio escolhido (defau

    params:
    df (pd.DataFrame): dataframe com os ticker duplicados 
    meio (str): campo escolhido para escolher qual ticker escolher (default: volume)

    return:
    (pd.DataFrame): dataframe com os ticker filtrados.
    """
    meio = meio or 'volume'
    df_dup = df[df.empresa.duplicated(keep=False)]
    lst_dup = df_dup.empresa.unique()
    lst_final = []
    for tic in lst_dup:
        tic_dup = df_dup[df_dup.empresa==tic].sort_values(by=[meio], ascending=False)['ticker'].values[0]
        lst_final = lst_final + [tic_dup]
    lst_dup = df_dup[~df_dup.ticker.isin(lst_final)]['ticker'].values
    logger.info(f"Ticker Duplicados Filtrados: {lst_dup}")
    print(f"Ticker Duplicados Filtrados: {lst_dup}")
    return df[~df.ticker.isin(lst_dup)]

def pegar_df_planilhao(data_base:date) -> pd.DataFrame:
    """
    Consulta todas as ações com os principais indicadores fundamentalistas

    params:
    data_base (date): Data Base para o cálculo dos indicadores.

    return:
    df (pd.DataFrame): DataFrame com todas as Ações.
    """
    dados = obter_dados_planilhao(data_base)
    if dados:
        dados = dados['dados']
        planilhao = pd.DataFrame(dados)
        planilhao['empresa'] = [ticker[:4] for ticker in planilhao.ticker.values]
        df = filtrar_duplicado(planilhao)
        logger.info(f"Dados do Planilhao consultados com sucesso: {data_base}")
        print(f"Dados do Planilhao consultados com sucesso: {data_base}")
        return df
    else:
        logger.info(f"Sem Dados no Planilhão: {data_base}")
        print(f"Sem Dados no Planilhão: {data_base}")
    

def pegar_df_preco_corrigido(data_ini:date, data_fim:date, carteira:list):
    """
    Consulta os preços Corrigidos de uma lista de ações

    params:
    data_ini (date): data inicial da consulta
    data_fim (date): data final da consulta
    carteira (list): lista de ativos a serem consultados

    return:
    df_preco (pd.DataFrame): dataframe com os preços do período dos ativos da lista
    """
    df_preco = pd.DataFrame()
    print(f"Consultando as seguintes ações: {carteira}")
    for ticker in carteira:
        print(f"Consultando dados para a ação: {ticker}")

        dados = obter_preco_corrigido(ticker, data_ini, data_fim)
        if dados:
            df_temp = pd.DataFrame.from_dict(dados)
            df_preco = pd.concat([df_preco, df_temp], axis=0, ignore_index=True)
            logger.info(f'{ticker} finalizado!')
            print(f'{ticker} finalizado!')   
        else:
            logger.error(f"Sem Preco Corrigido: {ticker}")
            print(f"Sem Preco Corrigido: {ticker}")
    return df_preco


def pegar_df_preco_diversos(data_ini:date, data_fim:date, carteira:list) -> pd.DataFrame:
    """
    Consulta os preços históricos de uma carteira de ativos

    params:

    data_ini (date): data inicial da consulta
    data_fim (date): data final da consulta
    carteira (list): lista de ativos a serem consultados

    return:
    df_preco (pd.DataFrame): dataframe com os preços do período dos ativos da lista
    """
    df_preco = pd.DataFrame()
    for ticker in carteira:
        dados = obter_preco_ibovespa(data_ini, data_fim, ticker)
        if dados:
            df_temp = pd.DataFrame.from_dict(dados)
            df_preco = pd.concat([df_preco, df_temp], axis=0, ignore_index=True)
            logger.info(f'{ticker} finalizado!')
            print(f'{ticker} finalizado!')   
        else:
            logger.error(f"Sem Preco Corrigido: {ticker}")
            print(f"Sem Preco Corrigido: {ticker}")
    return df_preco
 

def gerar_carteira(indicador_rentabilidade, indicador_desconto, data_inicio, quantidade_acoes):
    """
    Gera uma carteira com as melhores ações com base na Magic Formula:
    usa o indicador de rentabilidade e o indicador de desconto.

    Params:
    - indicador_rentabilidade (str): Indicador de rentabilidade escolhido (ex: 'roe', 'roc', 'roic').
    - indicador_desconto (str): Indicador de desconto escolhido (ex: 'earning_yield', 'dividend_yield', 'p_vp').
    - data_inicio (str): Data de início da análise no formato 'YYYY-MM-DD' (para consulta na API, não utilizado no DataFrame).
    - quantidade_acoes (int): Quantidade de ações a serem selecionadas para a carteira.

    Returns:
    - pd.DataFrame: DataFrame contendo as ações selecionadas para a carteira.
    """
    
    # Obter os dados do planilhão
    dados = obter_dados_planilhao(data_inicio)

    # Converter os dados em DataFrame
    df = pd.DataFrame(dados['dados'])
    # Verificando se os indicadores escolhidos estão na lista de colunas do DataFrame
    if indicador_rentabilidade not in df.columns or indicador_desconto not in df.columns:
        raise ValueError(f"Um ou ambos os indicadores não estão disponíveis no DataFrame: '{indicador_rentabilidade}', '{indicador_desconto}'.")

    # Calculando o ranking para cada indicador
    df['ranking_rentabilidade'] = df[indicador_rentabilidade].rank(ascending=False)
    df['ranking_desconto'] = df[indicador_desconto].rank(ascending=True)  # Menor valor é melhor para desconto

    # Calculando a soma dos rankings
    df['ranking'] = df['ranking_rentabilidade'] + df['ranking_desconto']
    
    # Ordenando as ações com base no ranking total
    df_ordenado = df.sort_values(by='ranking')
    df_final = df_ordenado[['ticker','setor','roc','roe','roic','earning_yield','dividend_yield','p_vp','ranking']]
    # Selecionar as melhores ações com base na quantidade especificada
    df_final = df_final.head(quantidade_acoes).reset_index(drop=True)  # Resetando índice
    df_final.index = df_final.index + 1
    carteira = df_final

    return carteira


def gerar_grafico(data_ini: date, data_fim: date, carteira: list, df_preco: pd.DataFrame):
    """
    Gera gráficos com o preço de fechamento das ações da carteira durante o período especificado.

    params:
    - data_ini (date): Data inicial do período
    - data_fim (date): Data final do período
    - carteira (list): Lista de tickers das ações na carteira
    - df_preco (pd.DataFrame): DataFrame contendo os preços das ações, incluindo a coluna 'fechamento'

    return:
    - fig: Figura gerada do Matplotlib
    """

    try:
        # Verifique se o DataFrame contém dados
        if df_preco.empty:
            raise ValueError("O DataFrame de preços está vazio. Verifique os dados fornecidos.")

        # Filtra o DataFrame para o período especificado
        df_preco['data'] = pd.to_datetime(df_preco['data'])
        df_filtrado = df_preco[(df_preco['data'] >= pd.to_datetime(data_ini)) & (df_preco['data'] <= pd.to_datetime(data_fim))]

        if df_filtrado.empty:
            raise ValueError("Não foram encontrados dados de preços para os tickers selecionados no período especificado.")

        # Inicia a criação da figura
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plota o preço de fechamento para cada ticker da carteira
        for ticker in carteira:
            # Filtra os dados para cada ação
            dados_ticker = df_filtrado[df_filtrado['ticker'] == ticker]
            if not dados_ticker.empty:
                ax.plot(dados_ticker['data'], dados_ticker['fechamento'], label=ticker)
            else:
                logger.warning(f"Nenhum dado de fechamento encontrado para o ticker: {ticker}")

        # Adiciona título, rótulos e legenda
        ax.set_title("Preço de Fechamento das Ações", fontsize=14)
        ax.set_xlabel("Data", fontsize=12)
        ax.set_ylabel("Preço de Fechamento", fontsize=12)
        ax.legend()  # Exibe a legenda com os tickers

        # Retorna a figura gerada
        return fig

    except Exception as e:
        logger.error(f"Ocorreu um erro ao gerar o gráfico: {str(e)}")
        raise






carteira = gerar_carteira('roc','earning_yield','2024-11-04',10)
carteira_pc =[]
for ticker in carteira['ticker']:
    carteira_pc.append(ticker)

print(carteira_pc)
pegar_df_preco_corrigido('2024-11-04','2024-11-06',carteira['ticker'])








