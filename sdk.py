#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import requests
import urlparse
import json
from Crypto.Hash import HMAC,SHA256
from sdk_parameters import GLOBAL_PARAMETERS

def encript_width_secret(value,secret_key):
    maker=HMAC.new(secret_key, digestmod=SHA256)
    maker.update(value)
    return maker.hexdigest()

class PagoFlashHTTPRequest(object):
    headers={
        'User-Agent': 'pagoflash/SDK'
    }
    data={}
    requestFormat="JSON"
    
    def addHeader(self, key, val):
        self.headers[key]=val
        
    def setData(self, data):
        self.data=data
        
    def send(self, url):
        data_string=json.dumps(self.data)
        self._codigo_error = '0'
        r=None
        
        if "JSON" == self.requestFormat:
            self.addHeader('Content-Type','application/json')
            self.addHeader('Content-Length', str(len(data_string)))
            s = requests.Session()
            r = s.post(url, data=data_string, headers=self.headers, verify=False)
        else:
            s = requests.Session()
            r = s.post(url, data=self.data, headers=self.headers, verify=False)
        if r:
            return r.content
        else:
            return None

class PagoFlashTokenBuilder(object):
    order_info={}
    products=[]
    parameters={}
    authParams={}
    
    def __init__(self, key_token, key_secret):
        self.authParams={}
        self.authParams["KEY_TOKEN"]=key_token
        self.authParams["KEY_SECRET"]=key_secret
        self.products=[]
        self.parameters={}
        self.order_info={}
        
    
    def setUrlOKRedirect(self, url_ok_redirect):
        self.parameters["url_ok_redirect"]=url_ok_redirect

    def setUrlOKRequest(self, url_ok_request):
        self.parameters["url_ok_request"]=url_ok_request
        
    def setOrderInformation(self, pc_order_number, pc_amount):
        self.order_info={
            "PC_ORDER_NUMBER": pc_order_number,
            "PC_AMOUNT": pc_amount
        }

    def addParams(self, parameters):
        self.parameters.update(parameters)
        
    def addProduct(self, pr_name, pr_desc, pr_price, pr_qty, pr_img):
        self.products.append({
            'pr_name': pr_name, # Nombre.  127 char max.
            'pr_desc': pr_desc, # Descripci�n .  Maximo 230 caracteres.
            'pr_price': pr_price, # Precio individual. Float, sin separadores de miles, utilizamos el punto (.) como separadores de Decimales. M�ximo dos decimales
            'pr_qty': pr_qty, # Cantidad, Entero sin separadores de miles  
            'pr_img': pr_img, # Direcci�n de imagen.  Debe ser una direcci�n (url) v�lida para la imagen.   
        })
    
    def send(self, domain):
        request= PagoFlashHTTPRequest()
        key_to_encript=str(self.order_info["PC_AMOUNT"])+str(self.order_info["PC_ORDER_NUMBER"])+str(self.authParams["KEY_TOKEN"])
        encripted_key=encript_width_secret(key_to_encript, str(self.authParams["KEY_SECRET"]))
        dataToSend=self.order_info
        dataToSend["PRODUCTS"]=self.products
        dataToSend["PARAMETERS"]=self.parameters
        
        request.setData(dataToSend)
        request.addHeader("X-Signature", encripted_key)
        request.addHeader("X-Auth-Token", self.authParams["KEY_TOKEN"])
        url=domain+'/payment/generate-token'
        return request.send(url)
    
class PagoFlashVerifyToken(object):
    requiredParams={}
    authParams={}
    
    def __init__(self, key_token, key_secret):
        self.authParams["KEY_TOKEN"]=key_token
        self.authParams["KEY_SECRET"]=key_secret
        
    def setTransactionToken(self, transaction_token):
        self.requiredParams['SELL_TOKEN']=transaction_token
        
    def send(self, domain):
        request= PagoFlashHTTPRequest()
        key_to_encript=str(self.requiredParams['SELL_TOKEN'])+str(self.authParams["KEY_TOKEN"])
        encripted_key=encript_width_secret(key_to_encript, str(self.authParams["KEY_SECRET"]))
        
        postData=self.requiredParams
        
        request.setData(postData)
        request.addHeader("X-Signature", encripted_key)
        request.addHeader("X-Auth-Token", self.authParams["KEY_TOKEN"])
        url=domain+'/payment/validate-payment'
        return request.send(url)

class sdk(object):
    
    _key_token=None
    _key_secret=None
    _modo_prueba = False
    _url_punto_venta=None
    _codigo_error=None
    _env='dev'
    
    GLOBAL_PARAMETERS=GLOBAL_PARAMETERS
    
    def __init__(self, p_key_token, p_key_secret, p_url_punto_venta, p_modo_prueba=False):
        self._codigo_error = '0'
        self._key_secret=p_key_secret
        self._key_token=p_key_token
        self._url_punto_venta=p_url_punto_venta
        self._modo_prueba=p_modo_prueba
        self.GLOBAL_PARAMETERS=GLOBAL_PARAMETERS
        
        if self._modo_prueba:
            self._env='dev'
        else:
            self._env='prod'
    
    def procesarPago(self, p_datos, p_navegador):
        TokenBuilder = PagoFlashTokenBuilder(self._key_token, self._key_secret)
        TokenBuilder.setOrderInformation(p_datos['cabecera_de_compra']['pc_order_number'], p_datos['cabecera_de_compra']['pc_amount'])
        for item in p_datos['productos_items']:
            TokenBuilder.addProduct(
                item['pr_name'],
                item['pr_desc'],
                item['pr_price'],
                item['pr_qty'],
                item['pr_img']
            )
            
        if p_datos['parameters']:
            TokenBuilder.addParams(p_datos['parameters'])

            #TokenBuilder.setUrlOKRedirect(p_datos['parameters']['url_ok_redirect'])
            #TokenBuilder.setUrlOKRequest(p_datos['parameters']['url_ok_request'])

        response=TokenBuilder.send(self.GLOBAL_PARAMETERS[self._env]["domain"])
        return response
    
    def validarTokenDeTransaccion(self, token_de_transaction, p_navegador):
        VerifyToken=PagoFlashVerifyToken(self._key_token, self._key_secret)
        VerifyToken.setTransactionToken(token_de_transaction)
        response=VerifyToken.send(self.GLOBAL_PARAMETERS[self._env]["domain"])
        return response
    
