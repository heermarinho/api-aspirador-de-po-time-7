from flask import Flask
from flask_restful import Resource, Api
from flask_restful import Resource, Api,reqparse

from flask import Flask
from flask_cors import CORS
import dataset
import numpy as np
from random import choice

app = Flask(__name__)
api = Api(app)
CORS(app)


endpoint = 'aws rds '

class sellers(Resource):
    # montar regra para pegar id sellers
    def get(self):
        db = dataset.connect(endpoint)
        # select  idlojista from      tlb_lojista; # por limite 10
        count = 0
        id_seller  = list()
        for linha in db['tlb_lojista']:
            count = count + 1
            if count > 20:
                break
            id_seller.append(linha['idlojista'])    
                
        return id_seller


class visao_geral_pedidos(Resource): #'/<string:todo_id>'
    # receber id seller e lista no db
    # 
    def get(self,idlojista):
        db = dataset.connect(endpoint)
        visao_geral = {"pedidos":0}
        list_data_geral = list() 
        for linha in db['visao_geral_pedidos_classificacao']:
            if int(idlojista) == linha['IdLojista']:
                     value =  {
                        "id": int(linha['IdPedido']),
                        "idCompra": int(linha['IdCompraEntrega']),
                        "classificacao": "critico" if linha['Classificacao'] == 1 else 'medio',
                        "score": round(float(linha['Score']) * 100,2) 
                     }
                     list_data_geral.append(value)       
        
        list_forma_pagto = list()
        for linha in db['tlb_forma_pgto']:
            if int(idlojista) == linha['IdLojista']:
                value  = {
                    "label":linha['FormaPagamento'],
                    "number":linha['QuantidadePedidos']
                }
                list_forma_pagto.append(value)
     
        valocimetro = list()   
        for linha in db['tbl_porcentagem_pedidos_criticos']:
            if idlojista == linha['IdLojista']:
                 valocimetro.append(float(linha['PorcentagemPedidosCríticos']))
        
        if len(valocimetro) > 0:
            final_valocimetro = round(100 - (np.min(valocimetro) * 100),2)
            
        final_valocimetro = choice(range(100)) 
        
        list_motivos = list()
        value_motivos = [{  # 0 
                     "label": "Cancelamento" , 
                     "number": 0
                },  # 1 
                { 
                     "label": "Troca" , 
                     "number": 0
                },   # 2 
                { 
                     "label": "Retorno" , 
                     "number": 0
                },
        ]
        for linha in db['tbl_motivos']:
            #print(linha['IdLojista'],type(linha['IdLojista']))
            if int(idlojista) == linha['IdLojista']:
                #print(linha['Motivos'],type(linha['Motivos']))
                flag = 0 
                if linha['Motivos'] == 1:
                    flag = "Cancelamento"
                    value_motivos[0]['number'] = value_motivos[0]['number'] + 1
                if linha['Motivos'] == 2:
                    flag = "Troca"
                    value_motivos[1]['number'] = value_motivos[1]['number'] + 1
                if linha['Motivos'] == 3:
                    flag = "Retorno"
                    value_motivos[2]['number'] = value_motivos[2]['number'] + 1
       
        nps_list = list()
        for linha in db['tlb_nps_score_line']:
            if int(idlojista) == linha['IdLojista']:
                ano,mes,dia = linha['Data'].split("-")
                value = {
                    "label":"{}/{}/{}".format(dia,mes,ano),
                    "number":float(linha['NPS'])
                }
                nps_list.append(value)
                
        list_canais_vendas = list()
        value_canais = [{  # 0 
                     "label": "MOBI" , 
                     "number": 0
                },  # 1 
                { 
                     "label": "SITE" , 
                     "number": 0
                },   # 2 
                { 
                     "label": "APP" , 
                     "number": 0
                },
                { 
                     "label": "TVEN" , 
                     "number": 0
                },
        ]
        for linha in db['tlb_canal_vendas']:
            if int(idlojista) == linha['IdLojista']:
                if linha['CanalVenda'] == 'MOBI':
                    value_canais[0]['number'] = value_canais[0]['number'] + 1
                
                if linha['CanalVenda'] == 'SITE':
                    value_canais[1]['number'] = value_canais[1]['number'] + 1
                
                if linha['CanalVenda'] == 'APP':
                    value_canais[2]['number'] = value_canais[2]['number'] + 1
                
                if linha['CanalVenda'] == 'TVEN':
                    value_canais[3]['number'] = value_canais[3]['number'] + 1

                          
        result = {
                "pedidos":list_data_geral,
                "formaPagamento":list_forma_pagto,
                "velocimetro": choice(range(100)),
                "motivosAtritos": value_motivos,
                "ultimasAvaliacoes": nps_list[-30:],
                "canaisVenda": value_canais
               }
        
        return result ,200

    

class list_data(Resource):
    # receber id seller e lista no db
    # 
    def get(self):
        return {'list': 'world'}

class status(Resource):
    # prova de vida status api 
    def get(self):
        return {'status': 'world'}


api.add_resource(sellers, '/api/v1/aspirador/sellers/idlojistas')

api.add_resource(list_data, '/api/v1/aspirador/list_data')

api.add_resource(visao_geral_pedidos, '/api/v1/aspirador/sellers/<string:idlojista>')


api.add_resource(status, '/')



if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8521,debug=True)
