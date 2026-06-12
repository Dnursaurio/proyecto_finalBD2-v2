import os
from pathlib import Path

print("Ingresa la ruta de la estructura del esquema relaciona (.txt)")
ruta_esquema = input()
ruta = Path(ruta_esquema)
if os.path.exists(ruta_esquema) and ruta.suffix == ".txt":
    print(f"el archivo en la ruta {ruta_esquema} SI existe")
    esquema = []
    with open(ruta_esquema, 'r') as archivo:
        peso_registro = 0
        for i in archivo:
            linea_limpia = i.strip()
            cajones = linea_limpia.split(',')
            esquema.append({"tipo": cajones[1], "longiud":int(cajones[2])})
            print(f"Campo: {cajones[0]} | Tipo de Dato: {cajones[1]}")
            peso_registro += int(cajones[2])
            print(f"El peso total de cada registro en el CSV sera de: {peso_registro} bytes")
    peso_registro += 1
    print(f"El peso total de cada registro en el CSV sera de: {peso_registro} bytes\n")
    print("Bien ahora cargue los datos del CSV (ingrese la ruta de su csv)")
    ruta_csv = input()
    ruta2 = Path(ruta_csv)
    if os.path.exists(ruta_csv) and ruta2.suffix == ".csv":
        print(f"El archivo en la ruta {ruta_csv} ha sido encontrado con exito")
        with open(ruta_csv,'r') as archivo_csv:
            next(archivo_csv)
            for i in archivo_csv:
                datos_fila = i.strip().split(',')
                if len(datos_fila) != len(esquema):
                    print(f"Fila rechazada: Tiene {len(datos_fila)} columnas, pero el esquema exige {len(esquema_columnas)}.")
                    continue
                try:
                    if esquema[0]["tipo"] == "int":
                        int(datos_fila[0])
                    print(f"Fila válida detectada: {datos_fila}")
                except ValueError:
                    print(f"Error de Tipo: El campo '{datos_fila[0]}' no es un entero válido.")
    else:
        print(f"El archivo en la ruta {ruta_csv} NO existe")
else:
    print(f"el archivo en la ruta {ruta_esquema} NO existe")
