UFSC - Universidade Federal de Santa Catarina
GR - Gabinete da Reitoria
DGG - Direção Geral do Gabinete
CGA - Coordenadoria de Gestão Ambiental

Projeto de Dashboard:
-> Engenheiro Sanitarista e Ambiental Djesser Zechner Sergio
-> contato: gestaodasaguas@contato.ufsc.br

Projeto:
Dashboard Monitoramento do Consumo de Água da UFSC

Versão: 21/03/2025 - emissão inicial

Descrição geral:
--> programa gerado em python versão 3.10 (versão superiores geraram conflito no streamlit cloud em 21/03/2025).

Projeto organizado em 3 pastas e 3 arquivos de código em *ipybn

Pastas:
- Auxiliar: contém arquivos de auxílio na organização e apresentação do projeto
- Dados: contém duas subpastas, Origem e Produtos. 
--> Pasta Origem contém dados brutos de consumo de água e faturamento por unidades consumidora desde 2013 em planilha excel e csv. Além disto contém os arquivos shapefile e documentos em PDF usados no app.
--> Pasta Produtos contém o arquivo tratado dados_agua_df.csv com dados o agrupamento dos dados de consumo usados no app.

Arquivo main = Dashboard_CGA_Gestao_das_Aguas.py
Arquivo auxiliar = Run_Streamlit.py para rodar em localhost o arquivo main.
requirements.txt requerido pelo streamlit cloud para importar bibliotecas quando do deploy.


