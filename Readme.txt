UFSC - Universidade Federal de Santa Catarina
GR - Gabinete da Reitoria
DGG - Direção Geral do Gabinete
CGA - Coordenadoria de Gestão Ambiental

Painel Interativo de Dados do Monitoramento do Consumo de água da UFSC:
-> projeto: Djesser Zechner Sergio
-> contato: gestaodasaguas@contato.ufsc.br

Versão inicial divulgada: 24/04/2025

Descrição geral:
--> App gerado em python versão 3.10 (versões superiores geraram conflito no streamlit cloud em 21/03/2025).

Pastas:
- Auxiliar: contém arquivos de auxílio na organização e apresentação do projeto
- Dados: contém duas subpastas, Origem e Produtos. 
--> Pasta Origem contém dados brutos de consumo de água e faturamento por unidades consumidoras. Contém arquivos shapefile e faturas em PDF usadas no app.
--> Pasta Produtos contém o arquivo tratado dados_agua_df(&"complementos").csv com dados o agrupamento dos dados de consumo usados no app. Maior numeração representa a última versão.

Arquivos principais:
Arquivo main = P3_Dashboard_CGA_Gestao_das_Aguas.py
requirements.txt requerido pelo streamlit cloud para importar bibliotecas quando do deploy.
Obs: No requirements.txt é necessário retirar os módulos de windows pywin32.
