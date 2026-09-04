# Import SparkSession
from pyspark.sql import SparkSession

def main():
      # Create SparkSession 
      spark = SparkSession.builder \
            .master("local[1]") \
            .appName("SparkByExamples.com") \
            .getOrCreate() 

      print("Inicio da sessão pypsark")

      df_fat_transacao = createOrReplaceTempView('F_TRANSACAO')
      df_saldo = createOrReplaceTempView('F_SALDO')
      df_cliente = createOrReplaceTempView('DIM_CLIENTE')
      df_tempo = createOrReplaceTempView('DIM_TEMPO')
      df_brdige = createOrReplaceTempView('BRIGDE_CLIENTE_GERENTE')
      df_agencia = createOrReplaceTempView('DIM_AGENCIA')
      df_gerente = createOrReplaceTempView('DIM_GERENTE')

      query_top_clientes = '''
                                          SELECT TOP 20,
                        C.NOME AS CLIENTE,
                        C.SEGMENTO,
                        COUNT(T.VALOR_TRANSACAO) AS QTD_TRANSACOES,
                        SUM(T.VALOR_TRANSACAO) AS VALOR_TOTAL,
                        AVG(T.VALOR_TRANSACAO) AS TICKET_MEDIO
                  FROM FATO_TRANSACAO T 
                  JOIN DIM_CLIENTE C 
                  ON T.ID_CLIENTE = C.ID_CLIENTE
                  JOIN DIM_TEMPO TT 
                  ON T.ID_TEMPO_TRANSACAO = TT.ID_TEMPO
                  WHERE T.DATA >= DATEADD(DAY,-90,GETDATE())
                  GROUP BY C.NOME,C.SEGMENTO
                  ORDER BY VALOR_TOTAL DESC;
                        '''
      df_return_query = spark.sql(query_top_clientes)
      df_return_query.show()

      query_transacao_pix = '''
                                                                  -- MEDIA CLIENTE ANO/MES
                              WITH SALDO_CONSOLIDADO(
                                    SELECT FS.ID_CLIENTE,
                                          DATEPART(YEAR FROM FS.DATA_SALDO) AS ANO,
                                          DATEPART(MONTH FROM FS.DATA_SALDO) AS MES,
                                          AVG(FS.SALDO) AS SALDO_MEDIO,
                                    FROM FATO_SALDO FS 
                                    GROUP BY   FS.ID_CLIENTE,DATEPART(YEAR FROM FS.DATA_SALDO), DATEPART(MONTH FROM FS.DATA_SALDO),        
                              )

                              -- calculo de pix por ANO/MES
                              WITH PIX_CONSOLIDADO(
                                    SELECT T.ID_CLIENTE,
                                          DATEPART(YEAR,TT.DATA) AS ANO,
                                          DATEPART(MONTH,TT.DATA) AS MES,
                                          COUNT(T.ID_FATO_TRANSACAO) AS QTD_TRANSACOES_PIX,
                                          SUM(T.VALOR_TRANSACAO) AS VALOR_TOTAL_PIX   
                                    FROM FATO_TRANSACAO T
                                    JOIN DIM_TEMPO TT
                                    ON T.ID_TEMPO_TRANSACAO = TT.ID_TEMPO
                                    GROUP BY  T.ID_CLIENTE,DATEPART(YEAR,TT.DATA),DATEPART(MONTH,TT.DATA)
                              )
                              2.1 CONSULTA
                              -- unificando os ctes para chegar na resposta de quantidade de transações via pix
                              SELECT C.NOME AS CLIENTE,
                                    S.ANO,
                                    S.MES,
                                    S.SALDO_MEDIO,
                                    P.QTD_TRANSACOES_PIX,
                                    P.VALOR_TOTAL_PIX 
                              FROM SALDO_CONSOLIDADO S 
                              JOIN PIX_CONSOLIDADO P
                              ON S.ID_CLIENTE = P.ID_CLIENTE
                              AND S.ANO = P.ANO
                              AND S.MES = P.MES
                              JOIN DIM_CLIENTE C
                              ON S.ID_CLIENTE = C.ID_CLIENTE 
                              WHERE S.SALDO_MEDIO > 10000
                              AND T.TIPO_TRANSACAO = 'PIX'
                              AND P.QTD_TRANSACOES_PIX >= 10 
                              ORDER BY SALDO_MEDIO DESC;
                                                
                        '''
      df_return_query_pix = spark.sql(query_transacao_pix)
      df_return_query_pix.show()

      df_query_historico_gerente = '''
                                                      --historico consulta 
                  SELECT  C.NOME AS CLIENTE,
                        C.SEGMENTO,
                        G.NOME_GERENTE,
                        A.NOME_AGENCIA, 
                        C.CLASS_RISCO ,
                        T.TIPO_TRANSACAO,
                        CAL.DATA_TRANSACAO
                  FROM FATO_TRANSACAO T 
                  JOIN DIM_CLIENTE C
                  ON T.ID_CLIENTE = C.ID_CLIENTE 
                  JOIN DIM_TEMPO TT
                  ON T.ID_TEMPO_TRANSACAO = TT.ID_TEMPO 
                  JOIN BRIGDE_CLIENTE_GERENTE BG 
                  ON C.ID_CLIENTE = BG.ID_CLIENTE 
                  JOIN DIM_GERENTE G 
                  ON BG.ID_GERENTE  = G.ID_GERENTE 
                  JOIN DIM_AGENCIA A 
                  ON G.ID_AGENCIA = A.ID_AGENCIA
                  WHERE TT.DATA BETWEEN BG.DATA_INICIO AND COALESCE(BG.DATA_FIM,'3000-12-31')
                        '''
      df_return_historico_gerente = spark.sql(df_query_historico_gerente)
      df_return_historico_gerente.show()

if __name__ == "__main__":
      main()