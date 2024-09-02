import openpyxl

ruta_plantilla = r"C:\Users\adria\Documents\programacion\interfaz-web\DATABASE\NDE\NDE._PLANTILLA\Copy_of_NDE._PLANTILLA.xlsx"
libro = openpyxl.load_workbook(ruta_plantilla)
ruta_guardar = r"C:\Users\adria\Documents\programacion\interfaz-web\DATABASE\NDE\test_output.xlsx"
libro.save(ruta_guardar)
