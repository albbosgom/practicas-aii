import urllib2
import re
import sqlite3
import Tkinter
import tkMessageBox
from Tkinter import *

def GrabHTML(url):
	try:
		f = urllib2.urlopen(url)
		r = f.read()
		f.close()
		return r
	except:
		return ""

def GrabFile(filename):
	try:
		f = open(filename, "r")
		r = f.read()
		f.close()
		return r
	except:
		return ""

def CutAfter(str1, str2):
	pos = str1.find(str2)
	return str1[pos+len(str2):]

def CutBefore(str1, str2):
	pos = str1.find(str2)
	return str1[:pos]

def DecodeUTF8(str1):
	try:
		return str1.decode('utf-8')
	except:
		return str1.replace('?','').decode('utf-8')

def DecodeCategories(cat):
	return cat[1:-1].split(',')

def DecodeDate(dv):
	m = re.match(r"^(\d\d\d\d)(\d\d)(\d\d)T", dv)
	return "%s/%s/%s" % m.group(3,2,1)

def DBOpen():
	return sqlite3.connect("games.db")

def DBOpenAndReset():
	db = DBOpen()
	db.execute("DROP TABLE IF EXISTS games;")
	db.execute('''
	CREATE TABLE games
	(
		OID     INTEGER NOT NULL PRIMARY KEY,
		gname   TEXT    NOT NULL,
		ggroup  TEXT    NOT NULL,
		gurl    TEXT    NOT NULL,
		gdate   TEXT    NOT NULL,
		grating INTEGER NOT NULL
	);
	''')
	db.execute("DROP TABLE IF EXISTS categories;")
	db.execute('''
	CREATE TABLE categories
	(
		game_OID  INTEGER NOT NULL,
		cname     TEXT    NOT NULL,
		FOREIGN KEY (game_OID) REFERENCES games(OID)
	);
	''')
	db.commit()
	return db

def _DBCategories(db, gameid):
	a = []
	for cat in db.execute("SELECT cname FROM categories WHERE game_OID = ?;", (gameid,)):
		a.append(cat)
	return a

def _DBParse(db, cursor):
	for t in cursor:
		yield (t[1], t[2], t[3], t[4], t[5], _DBCategories(db, t[0]))

def DBList():
	db = DBOpen()
	return _DBParse(db, db.execute("SELECT * FROM games;"))

def DBSearchByRating(m):
	db = DBOpen()
	return _DBParse(db, db.execute("SELECT * FROM games WHERE grating = ?;", (m,)))

def DBGetCategories():
	db = DBOpen()
	cursor = db.execute("SELECT DISTINCT cname FROM categories;")
	list = []
	for category in cursor:
		list.append(category[0])
	return list

def ScrapData():
	body = GrabFile("Lego2.txt")
	if body=="":
		body = GrabHTML("http://www.lego.com/es-es/games")
		if body=="":
			raise "Cannot load data!"
		tmp = open("Lego2.txt","w")
		tmp.write(body)
		tmp.close()
	
	body = CutAfter(body, '<ul id="gamesList" class="gamesList seperator">')
	body = CutBefore(body, '</ul>')
	urls = re.findall('<a href="(.+)"', body)
	groups = re.findall('<strong>(.+)</strong>', body)
	names = re.findall('<em>(.+)</em>', body)
	dates = re.findall('<p class="sortBynewest">(.+)</p>', body)
	ratings = re.findall('<p class="sortByrating">(.+)</p>', body)
	categories = re.findall('<p class="filterByCategory">(.+)</p>', body)
	
	db = DBOpenAndReset()
	for url,group,name,date,rating,category in zip(urls,groups,names,dates,ratings,categories):
		q = db.execute('INSERT INTO games (gname,ggroup,gurl,gdate,grating) VALUES (?,?,?,?,?);',\
			(DecodeUTF8(name), DecodeUTF8(group), DecodeUTF8(url), DecodeUTF8(DecodeDate(date)), int(rating)))
		gid = q.lastrowid
		for cat in DecodeCategories(category):
			db.execute('INSERT INTO categories (game_OID,cname) VALUES (?,?);',\
				(gid, DecodeUTF8(cat)))
	
	db.commit()
	return len(urls)

class MainWin(object):
	def __init__(self):
		w = Tkinter.Tk()
		btn = Tkinter.Button(w, text="Almacenar", command=self.btn_Almacenar)
		btn.pack(fill=Tkinter.X)
		btn = Tkinter.Button(w, text="Buscar", command=self.btn_Buscar)
		btn.pack(fill=Tkinter.X)
		btn = Tkinter.Button(w, text="Categoria", command=self.btn_Categoria)
		btn.pack(fill=Tkinter.X)
		self.title = "Practica 3"
		self.w = w
	
	def showinfo(self, txt):
		tkMessageBox.showinfo(self.title, txt)
	
	def showerror(self, txt):
		tkMessageBox.showerror(self.title, txt)
	
	def btn_Almacenar(self):
		try:
			nreg = ScrapData()
			self.showinfo("BD creada correctamente. Hay %d registros" % (nreg,))
		except:
			self.showerror("Hubo un error al almacenar los datos")
	
	def showList(self, gamelist):
		win = Tkinter.Toplevel()
		sb = Tkinter.Scrollbar(win)
		sb.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
		
		lb = Tkinter.Listbox(win, width=100, height=12, yscrollcommand=sb.set)
		lb.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH)
		sb.config(command=lb.yview)
		
		for game in gamelist:
			lb.insert(Tkinter.END, "Grupo: " + game[1])
			lb.insert(Tkinter.END, "Nombre: " + game[0])
			lb.insert(Tkinter.END, "Link: " + game[2])
			lb.insert(Tkinter.END, "Fecha: " + game[3])
			lb.insert(Tkinter.END, "Rating: " + str(game[4]))
			lb.insert(Tkinter.END, "Categs: " + str(game[5]))
			lb.insert(Tkinter.END, "")
		win.mainloop()
	
	def btn_Listar(self):
		try:
			self.showList(DBList())
		except:
			self.showerror("Hubo un error, intente almacenar los datos primero")
	
	def doSearch(self,dummy):
		try:
			rating = int(self.var.get())
			self.showList(DBSearchByRating(rating))
		except:
			self.showerror("Hubo un error")
	
	def doSearch2(self):
		self.doSearch(None)
	
	def btn_Buscar(self):
		win = Tkinter.Toplevel()
		lbl = Tkinter.Label(win, text="Introduzca el rating (d): ")
		lbl.pack(fill=Tkinter.X)
		self.var = Tkinter.StringVar()
		ctrl = Tkinter.Entry(win, textvariable=self.var)
		ctrl.bind("<Return>", self.doSearch)
		ctrl.pack(fill=Tkinter.X)
		ctrl = Tkinter.Button(win, text="Buscar", command=self.doSearch2)
		ctrl.pack(fill=Tkinter.X)
		win.mainloop()
		
		
	def btn_Categoria(self):
		win = Tkinter.Toplevel()
		categories = DBGetCategories()
		self.dict = {}
		for cat in categories:
			CheckVar = IntVar()
			C =  Checkbutton(win, text = cat, variable = CheckVar, \
                 onvalue = 1, offvalue = 0, \
                 width = 30)
			C.pack()
			self.dict[cat] = CheckVar
		search = Tkinter.Button(win, text ="Lanzar la busqueda", command = self.numeroCategorias)
		search.pack(fill = X)
		self.label = Tkinter.Label(win)
		self.label.pack()
		win.mainloop()
	
	def numeroCategorias(self):
		query = "SELECT count(*) FROM Games p"
		db = DBOpen()
		int = True
		categoriesChecked = []
		for cat in self.dict:
			var = self.dict[cat]
			if var.get()== 1:
				if int:
					query+=" WHERE (select count(*) FROM Categories q WHERE q.game_OID=p.OID and cname=?)>0"
					int = False
				else:
					query+=" OR (select count(*) FROM Categories q WHERE q.game_OID=p.OID and cname=?)>0"
				categoriesChecked.append(cat)
		query+=";"
		tupledCategories = tuple(categoriesChecked)	
		cursor = db.execute(query, tupledCategories)
		res = 0
		for number in cursor:
			res = number[0]
		self.label.config(text = str(res) + " juegos con las categorias seleccionadas.")

	
	def run(self):
		self.w.mainloop()

def main():
	app = MainWin()
	app.run()

main()
