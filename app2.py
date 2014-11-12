'''________________________________________________________________________
					
					Instituto Tecnologico de Costa Rica
					     Lenguajes de Programacion	
					     Tercera Tarea Programada 
					     App Web en Python-SML
					
					Realizado por: 
					        * Josue Espinoza Castro 
						* Mauricio Gamboa Cubero
						* Andres Pacheco Quesada

					Junio del 2014
__________________________________________________________________________'''

##Imports del framework para la aplicacion web Flask, interaccion con archivos del disco os, para la consulta del top10 de palabras b.son, y la base de datos mongoDB pymongo
from flask import Flask, request, redirect, url_for, abort, session, render_template, flash
from werkzeug.utils import secure_filename
import os
import pymongo
from pymongo import MongoClient
from bson.son import SON

##Variables para utilizar la base de datos MongoDB
client = MongoClient()
db = client.articulos
articulos = db.articulos

##Configuracion de guardar archivos
UPLOAD_FOLDER = '/home/josue/prueba/static'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif','JPG','JPEG','GIF','PNG'])

##Nombre de la aplicacion: Bumbur
app = Flask("BDA")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#----------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------			FRONTEND	   ------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------

##URL y funcion para home. Output: home.html
@app.route('/', methods=['GET', 'POST'])
def home():
	return render_template('home.html')

##Funcion para ingresar un nuevo articulo. Output: felicidades.html o redirect a funcion error
@app.route('/nuevoArticulo', methods=['GET', 'POST'])
def nuevoArticulo():
	if request.method == 'POST':
		file = request.files['file']
		if file and archivoPermitido(file.filename):
			#print("Es archivoPermitido")
			imgPath = secure_filename(file.filename)
			#print("Nombre = ",nombre)
			file.save(os.path.join('/home/josue/prueba/static/uploads', imgPath))
			#print("Nombre del archivo: ",nombre)
			Nombre = request.form['Articulo']
			Descripcion = request.form['Descripcion']
			Vendedor = request.form['Vendedor']
			if articulos.find({"Nombre":Nombre}).count() > 0 or articulos.find({"ImgPath":imgPath}).count() > 0:
				return redirect(url_for('error'))
			else:
				info = [Nombre,Descripcion,Vendedor]
				Descripcion = Descripcion.split()
				nuevoArt = {"Nombre":Nombre,"Descripcion":Descripcion,"Vendedor":Vendedor,"ImgPath":imgPath}
				articulo_id = articulos.insert(nuevoArt)
				#print("Numero de articulos al momento: ",articulos.count())
				return render_template('felicidades.html',imgPath=imgPath,info=info)
		else:
			return redirect(url_for('error'))

##Funcion para mostrar un mensaje de error despues de insertal mal un articulo. Output: error.html
@app.route('/error', methods=['GET', 'POST'])
def error():
	return render_template('error.html')

##Funcion para mostrar todos los articulos en la BD. Output: consultar.html
@app.route('/consultar', methods=['GET', 'POST'])
def consultar():
	todos = []
	for articulo in articulos.find():
		todos.append([])
		nombre = str(articulo["Nombre"])
		descripcion = str(' '.join(list(articulo["Descripcion"])))
		vendedor = str(articulo["Vendedor"])
		imgPath = str(articulo["ImgPath"])
		todos[-1].append(nombre)
		todos[-1].append(descripcion)
		todos[-1].append(vendedor)
		todos[-1].append(imgPath)
	return render_template('consultar.html',todos=todos)

##Funcion para mostrar las top 10 palabras mas mencionadas en las descripciones de los articulos en la BD. Output: consultarTop10.html
@app.route('/top10', methods=['GET', 'POST'])
def consultarTop10():
	##CONSULTA TOP 10 con aggregate
	consulta = db.articulos.aggregate([{"$unwind": "$Descripcion"},{"$group": {"_id": "$Descripcion", "count": {"$sum": 1}}},{"$sort": SON([("count", -1), ("_id", -1)])}])
	lista = list(consulta['result'])
	listalimitada = lista[:10]
	dicc = []
	for a in listalimitada:
		palabrayaparicion = []
		palabrayaparicion.append(str(a["_id"]))
		palabrayaparicion.append(a["count"])
		dicc.append(palabrayaparicion)
	return render_template('consultarTop10.html',todos=dicc)

##CON MAPREDUCE * no listo *

##mapper = Code("""function(){this.Descripcion.forEach(function(z){emit(z,1);});}""") 
##reducer = Code('function(key,values){var total=0; for (var i=0; i<values.length;i++){total += values[i];}return total;}', {})
##result = db.articulos.map_reduce(mapper,reducer,"myresults")
##result = db.articulos.map_reduce(mapper,reducer,"myresults",query={{"$sort": SON([("value", -1), ("_id", -1)])}})

#----------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------			BACKEND		   --------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------

#Funcion que evalua la extension sml del archivo
def archivoPermitido(nombre):
	boolean = '.' in nombre and nombre.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
	return boolean

##Funcion para borrar un archivo en uploads despues de ser evaluado
def borrarArchivo(nombre):
	os.remove("/home/prueba/static/"+nombre)

#----------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------			MAIN				-----------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------
##

##main de la aplicacion
if __name__ == '__main__':
	app.debug = True
	app.run(host='192.168.0.51') #CAMBIAR ESTE IP POR EL ACTUAL
