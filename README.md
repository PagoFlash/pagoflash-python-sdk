#Libreria Cliente Python para el API de [PagoFlash.com](http://pagoflash.com)

Aquí encontrará la información necesaria para integrar y utilizar el API de [PagoFlash](http://pagoflash.com) en su sitio web. Para utilizar nuestro método de pago debes **[crear una cuenta](https://app.pagoflash.com/profile/account_selection)** de negocios en nuestro site y registrar un **punto de venta**, con esto obtendras la **clave pública (key public)** y la **clave privada (key secret)**, necesarios para integrar el servicio en su sitio web. Si necesitas algún tipo de ayuda puedes envíar un correo a **contacto@pagoflash.com** con el asunto **Integración de botón de pago**.

##Requisitos
- Python 2.7

##Instalación

- Descargar el sdk de PagoFlash para python
- Importar el sdk en su script principal

##Pasos para la integración

Para hacer pruebas ingresa en nuestro sitio de pruebas y [regístra una cuenta de negocios](http://app-test2.pagoflash.com/profile/register/business), luego de llenar y confirmar tus datos, completa los datos de tu perfil, registra un punto de venta, llena los datos necesarios y una vez registrado el punto, la plataforma generará códigos **key_token** y **key_secret** que encontrarás en la pestaña **Integración** del punto de venta, utilízalos en el sdk como se muestra a continuación:

```python
//Importa el archivo pagoflas.api.client.php que contiene las clases que permiten la conexión con el API
from pagoflash.sdk import sdk
// url de tu sitio donde deberás procesar el pago
urlCallbacks = "http://www.misitio.com/procesar_pago.php"
// cadena de 32 caracteres generada por la aplicación, Ej. aslkasjlkjl2LKLKjkjdkjkljlk&as87
key_public = "tu_clave_publica"
// cadena de 20 caracteres generado por la aplicación. Ej. KJHjhKJH644GGr769jjh
key_secret = "tu_clave_secreta"
// Si deseas ejecutar en el entorno de producción pasar (false) en el 4to parametro
api = sdk(p_key_token=key_token, p_key_secret=key_secret, p_url_punto_venta=url_ok_redirect)


	//Cabecera de la transacción
	cabeceraDeCompra = {
        "pc_order_number":"001", # Alfanumerico de maximo 45 caracteres.
        "pc_amount": amount # Float, sin separadores de miles, utilizamos el punto (.) como separadores de Decimales. Maximo dos decimales
    }

	//Producto o productos que serán el motivo de la transacción

    ProductItems=[]
    product_1 = {
        'pr_id': order, #Id. de tu producto. Ej. 1
        'pr_name':name, #Nombre.  127 caracteres máximo.
        'pr_desc': description, #Descripción .  Maximo 230 caracteres.
        'pr_price': amount, #Precio individual del producto. sin separadores de miles utiliza el punto (.) como separadores de decimales. Máximo dos decimales.
        'pr_qty': qty, #Cantidad, Entero sin separadores de miles
        'pr_img': img, #Dirección de imagen. debe ser una dirección (url) válida para la imagen.
    }

	ProductItems.append(product_1)

	//La información conjunta para ser procesada
	pagoFlashRequestData={
	    'cabecera_de_compra': cabeceraDeCompra,
	    'productos_items': ProductItems,
	    'parameters': optionalParameters
	}

	//Se realiza el proceso de pago, devuelve JSON con la respuesta del servidor
	response = api.procesarPago(pagoFlashRequestData, request.META['HTTP_USER_AGENT'])
	pfResponse = json.loads(response)

	//Si es exitoso, genera y guarda un link de pago en (url_to_buy) el cual se usará para redirigir al formulario de pago
	if None == pfResponse or pfResponse['success'] == 0:
        //Manejo del error
    elif 1 == pfResponse['success']:
        return redirect(pfResponse['url_to_buy'])
```
    
##Documentación del sdk

###Parametros

- **key_public** *requerido*: identificador del punto de venta, se genera al crear un punto de venta en una cuenta tipo empresa de PagoFlash, formato: UOmRvAQ4FodjSfqd6trsvpJPETgT9hxZ 
- **key_secret** *requerido*: clave privada del punto de venta, se genera al crear un punto de venta en una cuenta tipo empresa de PagoFlash, formato: h0lmI11KlPpsVBCT8EZi
- **url_process** *requerido*: url del sitio al cual se realizara la llamada de retorno desde PagoFlash cuando se complete una transaccion.
- **test_mode**: parámetro booleano que indica si las transacciones se ralizaran en el entorno de pruebas o el real.

Utiliza estos números de tarjeta de crédito para realizar las pruebas:
###- Transacción exitosa:   2222444455556666
###- Transacción rechazada: 4444444444445555
(Puedes ingresar cualquier otra información relacionada con la tarjeta)

###Valores retornados por PagoFlash
Al finalizar la transacción retornamos un parámetro ('tk') con el cual podrán verificar si la transacción fue satisfactoria o no. Para ello existe el método en nuestro API llamado validarTokenDeTransaccion . A continuación definimos su uso.
```python
from pagoflash.sdk import sdk
// url de tu sitio donde deberás procesar el pago
url_process = "http://www.misitio.com/procesar_pago.php"
// cadena de 32 caracteres generada por la aplicación, Ej. aslkasjlkjl2LKLKjkjdkjkljlk&as87
key_public = "tu_clave_publica"
// cadena de 20 caracteres generado por la aplicación. Ej. KJHjhKJH644GGr769jjh
key_secret = "tu_clave_secreta"
test_mode = true
//el cuarto parámetro (true) es para activar el modo de pruebas, para desactivar colocar en **false**
api = sdk(key_public,key_secret, urlCallbacks,test_mode)

response = api->validarTokenDeTransaccion(request.get("tk"), request.META['HTTP_USER_AGENT'])
responseObj = json.loads(response)

if responseObj->cod:
    // Sucede cuando los parámetros para identificar el punto de venta no coinciden 
    // con los almacenados en la plataforma PagoFlash
	if responseObj->cod == 4:
		print "Parametros recibidos no coinciden"

	// Sucede cuando el token enviado para ser verificado no pertenece al punto de 
    // venta.
	elif responseObj->cod == 6:
		print "Transaccion no pertenece a su punto de venta"
		
	// Sucede cuando la transacción enviada para ser verificada no fue completada 
    // en la plataforma.
	elif responseObj->cod == 5:
		print "Esta transaccion no completada"

	// Sucede cuando la transacción enviada para ser verificada ya ha sido validada 
	elif responseObj->cod == 3:
		print "Transaccion ya ha sido validada"

	// Sucede cuando la transacción enviada para ser verificada fue completada 
    // de manera satisfactoria.
	elif responseObj->cod == 1:
		 print "Transaccion valida y procesada satisfactoriamente"
```
