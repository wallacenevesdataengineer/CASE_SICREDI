Case desenvolvido para modelagem de dados e arquitetura de dados bancários. 
Com objetivo de estruturar os dados em camadas úteis para tomada de decisão.

Arquitetura

Fonte de dados - Sistemas transacionais(arquivos CRM, API,JSON,CSV e XML)

Raw/Bronze - dados brutos.

Trusted/Silver - Transformação de dados e padronizados.

Gold/Dimensional - Modelo desenvolvido star schema com tabelas fatos e dimensões.

Semântica - camada de BI e com às regras de négocios definidas.

Consultas de Negocio 
- Quais foram os 20 clientes com maior volume financeiro de transações nos últimos 90 dias?
- Clientes que possuíam saldo médio superior a R$ 100.000 e realizaram mais de 10 transações PIX acima de R$ 5.000 no mesmo mês
- Historico de clientes no momento da Transação.

