import pandas as pd
import openpyxl
import os
import datetime as dt
import time

cwd = os.getcwd()

path_bd = os.path.join(cwd, 'bd')

path_calendario = os.path.join(path_bd, 'calendario_uteis.csv')
path_mapa_contabil = os.path.join(path_bd, 'mapeamento_contabil.csv')
path_parametros = os.path.join(path_bd, 'parametros_fundo.csv')
path_pl_diario = os.path.join(path_bd, 'pl_diario.csv')

df_calendario = pd.read_csv(path_calendario)
df_mapa_contabil = pd.read_csv(path_mapa_contabil)
df_parametros = pd.read_csv(path_parametros)
df_pl_diario = pd.read_csv(path_pl_diario)

df_calendario_uteis = df_calendario.loc[df_calendario['e_dia_util'] == 1]

df_pl_diario_tratado = pd.merge(df_pl_diario, df_calendario_uteis, 'inner', on= 'data')

def trata_data(data):

    return time.strptime(data, '%Y-%m-%d')

df_pl_diario_tratado['data'] = df_pl_diario_tratado['data'].apply(trata_data)

df_pl_diario_tratado = df_pl_diario_tratado.set_index('data')

print(df_pl_diario_tratado)

for idx, row in df_parametros.iterrows():

    fundo_id = row['fundo_id']
    taxa_adm_aa = row['taxa_adm_aa']
    fundo_nome = row['fundo_nome']
    base_dias_uteis = row['base_dias_uteis']
    metodo_calc = row['metodo_calculo']
    regra_aprop = row['regra_apropriacao']
    regra_pagamento = row['regra_pagamento']
    dia_pagamento = row['dia_pagamento']
    arredondamento = row['arredondamento']
    moeda = row['moeda']

    df_mapa_contabil_fundo = df_mapa_contabil.loc[df_mapa_contabil['fundo_id'] == fundo_id]

    contas_aprop_txa_adm = df_mapa_contabil_fundo.loc[df_mapa_contabil_fundo['tipo_lancamento'] == 'APROPRIACAO_TAXA_ADM']

    conta_desp_txa_adm = contas_aprop_txa_adm['conta_debito'].iloc[0]

    conta_passivo_txa_adm = contas_aprop_txa_adm['conta_credito'].iloc[0]

    contas_pagamento_txa_adm = df_mapa_contabil_fundo.loc[df_mapa_contabil_fundo['tipo_lancamento'] == 'PAGAMENTO_TAXA_ADM']

    conta_passivo_txa_adm_baixa = contas_aprop_txa_adm['conta_debito'].iloc[0]

    conta_banco_txa_adm = contas_aprop_txa_adm['conta_credito'].iloc[0]


    df_pl_diario_fundo = df_pl_diario_tratado.loc[df_pl_diario_tratado['fundo_id'] == fundo_id]

    if metodo_calc == 'pro_rata_dia_util' and regra_aprop == 'diaria':

        df_rateio = []
        for data in df_pl_diario_fundo.index:

            pl_diario = df_pl_diario_fundo.loc[data]['pl']

            apropriacao = round((pl_diario * taxa_adm_aa) / base_dias_uteis , arredondamento)

            df_rateio.append([data, apropriacao])

        df_rateio_raw = pd.DataFrame.from_records(df_rateio)

        columns = {0: 'data', 1 : 'aprop_diaria'}

        df_rateio = df_rateio_raw.rename(columns, axis= 1).set_index('data')

        ultimo_dia_util = df_rateio.iloc[-1].name
    
        lancamentos = []

        # apropriações diárias

        for data, row in df_rateio.iterrows():

            data_string = time.strftime('%Y%m%d',data)
            lancamentos.append([data_string, fundo_id, 'APROPRIACAO_TAXA_ADM', conta_desp_txa_adm, conta_passivo_txa_adm, row['aprop_diaria'], 'ADM', f'Apropriacao diaria taxa de administracao - {data_string}'])
            
        print(lancamentos)
        # pagamento no final com montante provisionado
            

    