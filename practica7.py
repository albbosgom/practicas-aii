import os.path
import Tkinter
from whoosh.index import create_in
from whoosh.fields import * 
from whoosh.qparser import QueryParser
def parseMail(mail):
    correo = mail
    if "arroba" in mail:
        correo = mail.replace("arroba", "@")
    return correo
    

def app():
    top = Tkinter.Tk()
    top.wm_title("Buscador de correos")
    def createSchema(var):
        schema = Schema(mailFrom=TEXT(stored=True), mailTo=KEYWORD(stored=True), date=DATETIME(stored=True), subject=TEXT(stored=True), content=TEXT(stored=True))
        ix = create_in("Correos", schema)
        writer = ix.writer()
        files = os.listdir("Correos")
        for archivo in files:
            if archivo.endswith(".txt"):
                f = open("Correos/"+archivo, "r")
                writer.add_document(mailFrom=unicode(parseMail(f.readline())), mailTo=unicode(parseMail(f.readline())),
                                    date= unicode(f.readline()), subject= unicode(f.readline()),
                                    content=unicode(f.readlines()))
                f.close()
        writer.commit()
        
        schema2 = Schema(mail=TEXT(stored=True), name=TEXT(stored=True))
        ix2 = create_in("Agenda", schema2)
        writer2 = ix2.writer()
        files = os.listdir("Agenda")
        for archivo in files:
            if archivo.endswith(".txt"):
                f = open("Agenda/"+archivo, "r")
                f2 = f.read()
                lines = f2.splitlines()
                mail = ""
                name = ""
                for i, line in enumerate(lines):
                    if i%2 == 0:
                        mail = parseMail(line)
                    else:
                        name = line
                        writer2.add_document(mail=unicode(mail), name=unicode(name))
                f.close()
        writer2.commit()
        
        
        with ix.searcher() as searcher:
            query = QueryParser("name", ix2.schema)
            qp = query.parse(unicode(var))
            
            with ix2.searcher() as s:
                results = s.search(qp)
                mail = results[0]["mail"]
            query = QueryParser("mailTo", ix.schema).parse(mail)
            results = searcher.search(query)
            panel = Tkinter.Toplevel()
            scrollbar = Tkinter.Scrollbar(panel)
            scrollbar.pack(side = Tkinter.RIGHT, fill=Tkinter.Y)
            listado = Tkinter.Text(panel, width=150, height=30, yscrollcommand = scrollbar.set)
            i = 1
            for result in results:
                listado.insert(Tkinter.INSERT, "Mail from: "+result["mailFrom"])
                listado.insert(Tkinter.INSERT, "Mail to: "+result["mailTo"])
                listado.insert(Tkinter.INSERT, "Subject: "+result["subject"])
                date = result["date"]
                listado.insert(Tkinter.INSERT, "Date: "+date[:4]+"-"+date[4:6]+"-"+date[6:])
                listado.insert(Tkinter.INSERT, "Content: ")
                content = re.findall("'([^']*)'", result["content"])
                last = content[-1]
                i += 1
                for line in content:
                    if line is not last:
                        line = line[:-2]
                    listado.insert(Tkinter.INSERT,  line+"\n")
                listado.insert(Tkinter.INSERT, "\n")
            listado.insert(Tkinter.INSERT, "Este remitente ha enviado "+ str(i-1) +" correos.")
            scrollbar.config( command = listado.yview )  
            listado.pack()  
    
    def buscarPorRemitente():
        panel = Tkinter.Toplevel()
        lbl = Tkinter.Label(panel, text="Introduzca nombre y apellidos: ")
        lbl.pack(fill=Tkinter.X)
        var = Tkinter.StringVar()
        ctrl = Tkinter.Entry(panel, textvariable=var)
        ctrl.bind("<Return>", lambda(x): createSchema(var.get()))
        ctrl.pack(fill=Tkinter.X)
        panel.mainloop()

    
    def searchSubject(var):
        schema = Schema(mailFrom=TEXT(stored=True), mailTo=KEYWORD(stored=True), date=TEXT(stored=True), subject=TEXT(stored=True), content=TEXT(stored=True))
        ix = create_in("Correos", schema)
        writer = ix.writer()
        files = os.listdir("Correos")
        for archivo in files:
            if archivo.endswith(".txt"):
                f = open("Correos/"+archivo, "r")
                writer.add_document(mailFrom=unicode(parseMail(f.readline())), mailTo=unicode(parseMail(f.readline())),
                                    date= unicode(f.readline()), subject= unicode(f.readline()),
                                    content=unicode(f.readlines()))
                f.close()
        writer.commit()
        query = QueryParser("subject", ix.schema).parse(var)
        results = ix.searcher().search(query)
        panel = Tkinter.Toplevel()
        scrollbar = Tkinter.Scrollbar(panel)
        scrollbar.pack(side = Tkinter.RIGHT, fill=Tkinter.Y)
        listado = Tkinter.Text(panel, width=100, height=30, yscrollcommand = scrollbar.set)
        for result in results:
            listado.insert(Tkinter.INSERT, "Mail from: "+result["mailFrom"])
            listado.insert(Tkinter.INSERT, "Mail to: "+result["mailTo"])
            date = result["date"]
            listado.insert(Tkinter.INSERT, "Date: "+date[:4]+"-"+date[4:6]+"-"+date[6:])
            listado.insert(Tkinter.INSERT, "Subject: "+result["subject"])
            listado.insert(Tkinter.INSERT, "Content: ")
            content = re.findall("'([^']*)'", result["content"])
            last = content[-1]
            for line in content:
                if line is not last:
                    line = line[:-2]
                listado.insert(Tkinter.INSERT,  line+"\n")
            listado.insert(Tkinter.INSERT, "\n")
        scrollbar.config( command = listado.yview )  
        listado.pack()  


    remitente = Tkinter.Button(top, text ="Buscar correos por remitente", command = buscarPorRemitente)    
    remitente.pack(fill=Tkinter.X)
    def buscarPorAsunto():
        panel = Tkinter.Toplevel()
        lbl = Tkinter.Label(panel, text="Introduzca asunto del correo: ")
        lbl.pack(fill=Tkinter.X)
        var = Tkinter.StringVar()
        ctrl = Tkinter.Entry(panel, textvariable=var)
        ctrl.bind("<Return>", lambda(x): searchSubject(var.get()))
        ctrl.pack(fill=Tkinter.X)
        panel.mainloop()
    asunto = Tkinter.Button(top, text="Buscar correos por asunto", command = buscarPorAsunto)
    asunto.pack(fill=Tkinter.X)
    
    def searchByRank(entry):
        schema = Schema(mailFrom=TEXT(stored=True), mailTo=KEYWORD(stored=True), date=DATETIME(stored=True), subject=TEXT(stored=True), content=TEXT(stored=True))
        ix = create_in("Correos", schema)
        writer = ix.writer()
        files = os.listdir("Correos")
        for archivo in files:
            if archivo.endswith(".txt"):
                f = open("Correos/"+archivo, "r")
                writer.add_document(mailFrom=unicode(parseMail(f.readline())), mailTo=unicode(parseMail(f.readline())),
                                    date= unicode(f.readline()), subject= unicode(f.readline()),
                                    content=unicode(f.readlines()))
                f.close()
        writer.commit()
        subtop1 = Tkinter.Tk()
        scrollbarY = Tkinter.Scrollbar(subtop1)
        scrollbarX = Tkinter.Scrollbar(subtop1, orient=Tkinter.HORIZONTAL)
        scrollbarY.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        scrollbarX.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
        LB1 = Tkinter.Listbox(subtop1, width=80, height=12, yscrollcommand=scrollbarY.set, xscrollcommand=scrollbarX.set)
        scrollbarY.config(command=LB1.yview)
        scrollbarX.config(command=LB1.xview)
        fechas = entry.split("-")
        flinferior = fechas[0]
        flisuperior = fechas[1]
        qp = QueryParser('date', schema= ix.schema)
        q = qp.parse(u"date:["+flinferior+" to "+ flisuperior+"]")
        with ix.searcher() as s:
                results = s.search(q)
                i = 1
                pos = 1
                for result in results:
                    LB1.insert(pos, "Correo "+ str(i))
                    pos += 1
                    LB1.insert(pos, "Remitentes: "+ result['mailFrom'])
                    pos += 1
                    LB1.insert(pos, "Destinatarios: "+ result['mailTo'])
                    pos += 1
                    LB1.insert(pos, "Subject: "+ result['subject'])
                    pos += 1
                    LB1.insert(pos, "\n")
                    pos += 1
                    i += 1
                LB1.insert(pos, "En este rango de fechas se han enviado "+ str(i-1) +" correos.")
                pos += 1
        LB1.pack()
        subtop1.mainloop()
        
    
    def buscarPorRangoFecha():
        var = Tkinter.StringVar(value='YYYYMMDD-YYYYMMDD')
        panel = Tkinter.Toplevel()
        L1 = Tkinter.Label(panel, text="Introduzca las dos fechas"+"\n"+ "separadas por un guion, "+"\n"+ "en el siguiente formato:")
        E1 = Tkinter.Entry(panel, width=25, textvariable = var)
        def buscar():
            searchByRank(var.get())
        B1 = Tkinter.Button(panel, text ="Buscar", command = buscar)
        L1.pack(side = Tkinter.LEFT)
        B1.pack(side = Tkinter.RIGHT)
        E1.pack(side = Tkinter.RIGHT)
    
    byRango = Tkinter.Button(top, text ="Buscar correos por rango de fecha", command = buscarPorRangoFecha)    
    byRango.pack(fill=Tkinter.X)
    
    top.mainloop()
    

app()
