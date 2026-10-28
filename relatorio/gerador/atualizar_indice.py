# Abre o .docx no LibreOffice, atualiza o índice (TOC) e salva o .docx final e um PDF de conferência.
import subprocess, time, sys, os, uno
from com.sun.star.beans import PropertyValue

ENTRADA, SAIDA_DOCX, SAIDA_PDF = (os.path.abspath(a) for a in sys.argv[1:4])

def prop(n, v):
    p = PropertyValue(); p.Name, p.Value = n, v; return p

proc = subprocess.Popen(["soffice", "--headless", "--invisible", "--norestore",
                         "-env:UserInstallation=file:///tmp/lo_toc_profile",
                         '--accept=socket,host=127.0.0.1,port=2002;urp;'])
ctx = None
for _ in range(60):
    try:
        local = uno.getComponentContext()
        res = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
        ctx = res.resolve("uno:socket,host=127.0.0.1,port=2002;urp;StarOffice.ComponentContext")
        break
    except Exception:
        time.sleep(0.5)
desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
doc = desktop.loadComponentFromURL(uno.systemPathToFileUrl(ENTRADA), "_blank", 0, (prop("Hidden", True),))
idx = doc.getDocumentIndexes()
for i in range(idx.getCount()):
    idx.getByIndex(i).update()
doc.refresh()
for i in range(idx.getCount()):   # segunda passada: números de página estáveis depois que o índice ocupa espaço
    idx.getByIndex(i).update()
doc.storeToURL(uno.systemPathToFileUrl(SAIDA_DOCX), (prop("FilterName", "MS Word 2007 XML"),))
doc.storeToURL(uno.systemPathToFileUrl(SAIDA_PDF), (prop("FilterName", "writer_pdf_Export"),))
doc.close(True)
try:
    desktop.terminate()
except Exception:
    pass
proc.wait(timeout=30)
print("índices atualizados:", idx.getCount())
