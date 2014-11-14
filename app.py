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

##Imports del framework para la aplicacion web Flask, interaccion con archivos del disco os
from flask import Flask, request, redirect, url_for, abort, session, render_template, flash
from werkzeug.utils import secure_filename
import os
import couchdb
from couchdb.design import ViewDefinition
import sys

##Variables para utilizar la base de datos CouchDB
couch = couchdb.Server()
couch = couchdb.Server('http://192.168.0.133:5984/')

db = couch['articulos']#Tomar una base existente

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
			#if articulos.find({"Nombre":Nombre}).count() > 0 or articulos.find({"ImgPath":imgPath}).count() > 0:
			#	return redirect(url_for('error'))
			#else:
			info = [Nombre,Descripcion,Vendedor]
				#Descripcion = Descripcion.split()
			doc = {"Nombre":Nombre,"Descripcion":Descripcion,"Vendedor":Vendedor}
			db.save(doc)
			f = open('/home/josue/prueba/static/uploads/'+imgPath,'rb')
			db.put_attachment(doc,f,imgPath)
			ide = str(doc['_id'])
			return render_template('felicidades.html',imgPath=imgPath,info=info,ide=ide)
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
	map_fun = '''function(doc) {emit([doc.Nombre,doc.Descripcion,doc.Vendedor,doc._id,doc._attachments], null);}'''
	for r in db.query(map_fun):
		l=[]
		l.append(str(r.key[0]))
		l.append(str(r.key[1]))
		l.append(str(r.key[2]))
		l.append(str(r.key[3]))
		for nombreImagen in r.key[4]:
			l.append(nombreImagen)
		todos.append(l)
	return render_template('consultar.html',todos=todos)

##Funcion para mostrar las top 10 palabras mas mencionadas en las descripciones de los articulos en la BD. Output: consultarTop10.html
@app.route('/top10', methods=['GET', 'POST'])
def consultarTop10():
	dicc=mapp()
	return render_template('consultarTop10.html',todos=dicc)


#----------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------			BACKEND		   --------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------

#Manejo de BD CouchDB

##couch.create('')
##doc = {"Nombre": "yoyo","Descripcion": ["pequeno","lindo"],"Vendedor": "jeison"}

##db.save(doc)

##for each in db:
##    print each['Descripcion']



##map_fun = '''function(doc) {emit(doc._attachments, null);}'''
##for row in db.query(map_fun):
##    print (row.key)


def mapp():
    palabras=[]
    map_='''function(doc) {emit (doc.Descripcion.toLowerCase().match(/([a-z]+)/g),doc.Vendedor); }'''

    for row in db.query(map_):
    ##    print (row.key)
        cont=0
        while cont<len(row.key):
            palabras.append(row.key[cont])
            cont+=1
    return reducee(palabras)

def reducee(palabras):
    superlista=[]
    cont=[]
    while palabras!=[]:
        if verifica(palabras[0],superlista)>=0:
            superlista[verifica(palabras[0],superlista)][1]+=1
            palabras=palabras[1:]
        else:
            superlista.append([palabras[0],1])
            palabras=palabras[1:]
    x=sorted(superlista, key=lambda orden:orden[1], reverse=True)
    return x[:10]
    
def verifica(word,superlista):
    cont=0
    while cont<len(superlista):
        if superlista[cont][0]==word:
            return cont
        else:
            cont+=1
    return -1

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
	app.run(host='192.168.0.133') #CAMBIAR ESTE IP POR EL ACTUAL
