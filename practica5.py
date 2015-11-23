import urllib2
import sqlite3
from bs4 import BeautifulSoup
import Tkinter
import tkMessageBox

#url = "http://singluten.com/"
def guardarUrl(url):
    f = urllib2.urlopen(url)
    f2 = open("singluten.html", "w")
    f2.writelines(f)
    f2.close()

def crearBaseDeDatos():
    success = 0
    try:
        connection = sqlite3.connect("singluten.db")
        connection.execute("DROP TABLE IF EXISTS Categorias;")
        connection.execute('''CREATE TABLE Categorias
           (NAME     TEXT NOT NULL PRIMARY KEY,
           DESCRIPTION TEXT NOT NULL,
           LINK          TEXT     NOT NULL );''')
        connection.execute("DROP TABLE IF EXISTS Productos;")
        connection.execute('''CREATE TABLE Productos
           (NAME     TEXT NOT NULL,
           PrecioFinal TEXT NOT NULL,
           PrecioAntiguo TEXT,
           Descuento FLOAT,
           Categoria TEXT NOT NULL,
           FOREIGN KEY (Categoria) REFERENCES Categorias(Name) );''')
        
        try:
            f2 = open("singluten.html", "r")
        except:
            guardarUrl("http://singluten.com/")
            f2 = open("singluten.html", "r")
        html = f2.read()
        f2.close()
        soup = BeautifulSoup(html, 'html.parser')
        # Primero cogemos las categorias
        text = soup.find(id="left_column")
        # Luego metemos cada categoria en la tabla
        categories = text.find_all("li")
        for category in categories:
            enlace = category.a.get('href').strip()
            nombre = category.a.get_text().strip()
            descripcion = category.a.get('title').strip()
            connection.execute("INSERT INTO Categorias (LINK, NAME, DESCRIPTION) VALUES (?,?, ?)", (unicode(enlace), unicode(nombre), unicode(descripcion)))
        connection.commit()
        
        # Ahora iteramos en la base de datos por cada categoria para meter los productos de cada categoria:
        
        categorias = connection.execute("SELECT * FROM Categorias")
        for category in categorias:
            f = urllib2.urlopen(category[2])
            soup = BeautifulSoup(f, 'html.parser')
            text = soup.find(class_="hidden", id="nb_item")
            if text != None:
                f = urllib2.urlopen(category[2]+"?n="+text['value'])
                soup = BeautifulSoup(f, 'html.parser') 
            products = soup.find_all(class_="product-container")
            for product in products:
                nombre = product.find(class_="product-name")['title']
                price = product.find(itemprop="price")
                if price != None:
                    price = price.get_text().strip()
                oldprice = product.find(class_="old-price product-price")
                if oldprice != None:
                    oldprice = oldprice.get_text().strip()
                descuento = product.find(class_="price-percent-reduction")
                if descuento != None:
                    descuento = float(descuento.get_text().strip()[1:-1])
                
                connection.execute("INSERT INTO Productos (NAME, PrecioFinal, PrecioAntiguo, Descuento, Categoria) VALUES (?,?, ?,?,?)", (unicode(nombre), unicode(price), unicode(oldprice), descuento, unicode(category[0])))
        connection.commit()
        tkMessageBox.showinfo( "Database info", "Database was successfully filled") 
        connection.close()
        
    except Exception as e:
        tkMessageBox.showinfo( "Database info", "Operation was unsuccessful" + e.message) 
        success = -1
    return success

def buscarProductos(Categoria):
    connection = sqlite3.connect("singluten.db")
    productos = connection.execute("SELECT NAME,PrecioFinal FROM Productos WHERE Categoria = ?", (Categoria,))
    pos = 1
    panel = Tkinter.Toplevel()
    panel.wm_title("Productos en "+Categoria)
    scrollbar = Tkinter.Scrollbar(panel)
    scrollbar.pack(side = Tkinter.RIGHT, fill=Tkinter.Y)
    L1 = Tkinter.Listbox(panel, width=60, height=23, yscrollcommand = scrollbar.set)
    scrollbar.config( command = L1.yview )
    for product in productos:
        L1.insert(pos, product[0])
        pos+=1
        price = product[1]
        if(price != None):
            L1.insert(pos, price)
            pos+=1
            
        L1.insert(pos, "")
        pos+=1
            
    L1.pack()

def buscarProductosEnOferta(Categoria):
    connection = sqlite3.connect("singluten.db")
    categorias = connection.execute("SELECT * FROM Categorias WHERE Name = ?", (Categoria,))
    for category in categorias:
        link = category[2]
    f = urllib2.urlopen(link)
    soup = BeautifulSoup(f, 'html.parser')
    text = soup.find(class_="hidden", id="nb_item")
    if text != None:
        f = urllib2.urlopen(link+"?n="+text['value'])
        soup = BeautifulSoup(f, 'html.parser') 
    products = soup.find_all(class_="product-container")
    pos = 1
    panel = Tkinter.Toplevel()
    panel.wm_title("Ofertas en "+Categoria)
    scrollbar = Tkinter.Scrollbar(panel)
    scrollbar.pack(side = Tkinter.RIGHT, fill=Tkinter.Y)
    L1 = Tkinter.Listbox(panel, width=60, height=23, yscrollcommand = scrollbar.set)
    scrollbar.config( command = L1.yview )
    for product in products:
        if product.find(class_="old-price product-price") != None:
                        
            L1.insert(pos, product.find(class_="product-name")['title'])
            pos+=1
            L1.insert(pos, "Precio antiguo: " + product.find(class_="old-price product-price").get_text().strip())
            pos+=1  
            L1.insert(pos, "Precio en oferta: " + product.find(itemprop="price").get_text().strip())
            pos+=1            
            L1.insert(pos, "")
            pos+=1    

    L1.pack()  


def app():
    top = Tkinter.Tk()
    top.wm_title("Buscador de Sin Gluten")

    almacenar = Tkinter.Button(top,  text ="Almacenar categorias", command = crearBaseDeDatos)    
    almacenar.pack(fill=Tkinter.X)
    
    def buscar():
        panel = Tkinter.Toplevel()
        L1 = Tkinter.Listbox(panel, width=30, height=23)
        connection = sqlite3.connect("singluten.db")
        categorias = connection.execute("SELECT * FROM Categorias")
        
        pos = 1
        for category in categorias:
            L1.insert(pos, category[0].strip()) 
        L1.pack()
        E1 = Tkinter.Button(panel, text ="Buscar productos en la categoria", command = lambda: buscarProductos(L1.get(L1.curselection()[0])))
        connection.close()
        E1.pack(fill = Tkinter.X)
    buscar = Tkinter.Button(top, text="Buscar por categorias", command = buscar)
    buscar.pack(fill=Tkinter.X)
    
    def buscarOfertas():
        panel = Tkinter.Toplevel()
        lbl = Tkinter.Label(panel, text="Introduzca el descuento: ")
        lbl.pack(fill=Tkinter.X)
        var = Tkinter.StringVar()
        def hacerBsqueda(desc):
            pos = 1
            panel = Tkinter.Toplevel()
            panel.wm_title("Descuento del -" + desc + "%")
            scrollbar = Tkinter.Scrollbar(panel)
            scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
            L1 = Tkinter.Listbox(panel, width=60, height=23, yscrollcommand=scrollbar.set)
            scrollbar.config(command=L1.yview)
            connection = sqlite3.connect("singluten.db")
            cursor = connection.execute("SELECT * from Productos where Descuento NOT NULL AND Descuento>=?1;", (float(desc),))
            for product in cursor:
                L1.insert(pos, product[0])
                pos += 1
                L1.insert(pos, "Precio antiguo: " + product[2])
                pos += 1  
                L1.insert(pos, "Precio en oferta: " + product[1])
                pos += 1
                L1.insert(pos, "Descuento: -" + str(product[3]) + "%")
                pos += 1
                L1.insert(pos, "Categoria: " + product[4])
                pos += 1
                L1.insert(pos, "")
                pos += 1
            L1.pack(fill=Tkinter.X)
            panel.mainloop()
        ctrl = Tkinter.Entry(panel, textvariable=var)
        ctrl.bind("<Return>", lambda(x): hacerBsqueda(var.get()))
        ctrl.pack(fill=Tkinter.X)
        panel.mainloop()
    buscar = Tkinter.Button(top, text="Buscar ofertas", command = buscarOfertas)
    buscar.pack(fill=Tkinter.X)
    
    
    
    top.mainloop()
    

app()