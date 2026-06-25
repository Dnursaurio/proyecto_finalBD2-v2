import os
import csv
import re
import struct
import math


#
#ARBOL AVL
#

from collections import deque


class CNode:
    def __init__(self, v, sector, offset):
        self.v = v

        self.direcciones = [
            {
                "sector": sector,
                "offset": offset
            }
        ]

        self.alt = 1
        self.des = 0

        self.nodes = [None, None]


class CBinTree:
    def __init__(self):
        self.root = None

    def altura(self, n):
        return n.alt if n else 0

    def actualizar(self, n):
        if not n:
            return

        alt_izq = self.altura(n.nodes[0])
        alt_der = self.altura(n.nodes[1])

        n.alt = 1 + max(alt_izq, alt_der)
        n.des = alt_der - alt_izq

    def rotar_izquierda(self, n):
        nuevo_root = n.nodes[1]
        temp = nuevo_root.nodes[0]

        nuevo_root.nodes[0] = n
        n.nodes[1] = temp

        self.actualizar(n)
        self.actualizar(nuevo_root)

        return nuevo_root

    def rotar_derecha(self, n):
        nuevo_root = n.nodes[0]
        temp = nuevo_root.nodes[1]

        nuevo_root.nodes[1] = n
        n.nodes[0] = temp

        self.actualizar(n)
        self.actualizar(nuevo_root)

        return nuevo_root

    def balancear(self, n):
        self.actualizar(n)

        if n.des == 2:
            if n.nodes[1].des < 0:
                n.nodes[1] = self.rotar_derecha(n.nodes[1])
            return self.rotar_izquierda(n)

        if n.des == -2:
            if n.nodes[0].des > 0:
                n.nodes[0] = self.rotar_izquierda(n.nodes[0])
            return self.rotar_derecha(n)

        return n

    def ins(self, x, sector, offset):
        self.root = self._insertar(
            self.root,
            x,
            sector,
            offset
        )

    def _insertar(self, n, x, sector, offset):
        if not n:
            return CNode(x, sector, offset)

        if x == n.v:
            n.direcciones.append({
                "sector": sector,
                "offset": offset
            })
            return n

        if x < n.v:
            n.nodes[0] = self._insertar(
                n.nodes[0],
                x,
                sector,
                offset
            )
        else:
            n.nodes[1] = self._insertar(
                n.nodes[1],
                x,
                sector,
                offset
            )

        return self.balancear(n)

    def find_node(self, x):
        actual = self.root

        while actual:
            if x == actual.v:
                return actual

            if x < actual.v:
                actual = actual.nodes[0]
            else:
                actual = actual.nodes[1]

        return None
    
    def find(self, x):
        nodo = self.find_node(x)

        if nodo:
            return nodo.direcciones

        return []


    def buscar_rango(self, minimo, maximo):
        resultado = []
        self._buscar_rango(
            self.root,
            minimo,
            maximo,
            resultado
        )
        return resultado

    def _buscar_rango(self, n, minimo, maximo, resultado):
        if not n:
            return

        if minimo < n.v:
            self._buscar_rango(
                n.nodes[0],
                minimo,
                maximo,
                resultado
            )

        if minimo <= n.v <= maximo:
            for direccion in n.direcciones:
                resultado.append({
                    "valor": n.v,
                    "sector": direccion["sector"],
                    "offset": direccion["offset"]
                })

        if n.v < maximo:
            self._buscar_rango(
                n.nodes[1],
                minimo,
                maximo,
                resultado
            )

    def height2(self, n):
        if not n:
            return 0

        return 1 + max(
            self.height2(n.nodes[0]),
            self.height2(n.nodes[1])
        )

    def inorder(self, n):
        if not n:
            return

        self.inorder(n.nodes[0])

        print(
            f"Valor: {n.v} | "
            f"Direcciones: {n.direcciones} | "
            f"Altura: {n.alt} | "
            f"Des: {n.des}"
        )

        self.inorder(n.nodes[1])

    def print(self):
        self.inorder(self.root)
        print("Altura total:", self.height2(self.root))

    def print_levels(self):
        if not self.root:
            print("Árbol vacío")
            return

        q = deque()
        q.append(self.root)

        while q:
            actual = q.popleft()

            print(
                f"{actual.v} "
                f"({len(actual.direcciones)} dir)",
                end=" "
            )

            if actual.nodes[0]:
                q.append(actual.nodes[0])

            if actual.nodes[1]:
                q.append(actual.nodes[1])

        print()
#
# DISCO
#


class DISK:

    def __init__(self, p, t, s, c, nombre_archivo="disco.dat"):
        self.nro_platos = 2 ** p
        self.nro_superficies = 2 * self.nro_platos
        self.nro_pistas = 2 ** t
        self.nro_sectores = 2 ** s
        self.capacidad_sector = 2 ** c
        self.nombre_archivo = nombre_archivo

    def capacidad_total(self):
        return (
            self.nro_superficies *
            self.nro_pistas *
            self.nro_sectores *
            self.capacidad_sector
        )

    def get_total_sectores(self):
        return (
            self.nro_superficies *
            self.nro_pistas *
            self.nro_sectores
        )

    def get_capacidad_sector(self):
        return self.capacidad_sector

    def formateador(self):
        print("Creando su disco :)")

        print(f"Platos: {self.nro_platos}")
        print(f"Superficies: {self.nro_superficies}")
        print(f"Pistas por superficie: {self.nro_pistas}")
        print(f"Sectores por pista: {self.nro_sectores}")
        print(f"Capacidad por sector: {self.capacidad_sector} bytes")
        print(f"Total de sectores: {self.get_total_sectores()}")
        print(f"Capacidad total: {self.capacidad_total()} bytes")

        with open(self.nombre_archivo, "wb") as archivo:
            archivo.seek(self.capacidad_total() - 1)
            archivo.write(b'\0')

    def eliminar_disco(self):
        if os.path.exists(self.nombre_archivo):
            os.remove(self.nombre_archivo)
            print("Disco eliminado")

    def existe_disco(self):
        return os.path.exists(self.nombre_archivo)

    def validar_offset(self, offset):
        if offset < 0 or offset >= self.capacidad_total():
            raise ValueError("Offset inválido")

    def validar_rango(self, offset, cantidad):
        if offset < 0:
            raise ValueError("Offset inválido")

        if cantidad < 0:
            raise ValueError("Cantidad inválida")

        if offset + cantidad > self.capacidad_total():
            raise Exception("Operación fuera de la capacidad del disco")

    def validar_sector_lineal(self, sector_lineal):
        if sector_lineal < 0 or sector_lineal >= self.get_total_sectores():
            raise ValueError("Sector lineal inválido")

    def direccion_a_lineal(self, superficie, pista, sector):
        if superficie < 0 or superficie >= self.nro_superficies:
            raise ValueError("Superficie inválida")

        if pista < 0 or pista >= self.nro_pistas:
            raise ValueError("Pista inválida")

        if sector < 0 or sector >= self.nro_sectores:
            raise ValueError("Sector inválido")

        return (
            superficie * self.nro_pistas * self.nro_sectores
            + pista * self.nro_sectores
            + sector
        )

    def lineal_a_direccion(self, sector_lineal):
        self.validar_sector_lineal(sector_lineal)

        superficie = sector_lineal // (
            self.nro_pistas * self.nro_sectores
        )

        resto = sector_lineal % (
            self.nro_pistas * self.nro_sectores
        )

        pista = resto // self.nro_sectores
        sector = resto % self.nro_sectores

        return superficie, pista, sector

    def desplazamiento(self, superficie, pista, sector):
        sector_lineal = self.direccion_a_lineal(
            superficie,
            pista,
            sector
        )

        return sector_lineal * self.capacidad_sector

    def offset_sector_lineal(self, sector_lineal):
        self.validar_sector_lineal(sector_lineal)

        return sector_lineal * self.capacidad_sector

    def escribir(self, offset, datos):
        self.validar_rango(offset, len(datos))

        if not self.existe_disco():
            raise FileNotFoundError("ERROR: Disco no encontrado")

        with open(self.nombre_archivo, "r+b") as archivo:
            archivo.seek(offset)
            archivo.write(datos)

    def leer(self, offset, cantidad):
        self.validar_rango(offset, cantidad)

        if not self.existe_disco():
            raise FileNotFoundError("ERROR: Disco no encontrado")

        with open(self.nombre_archivo, "rb") as archivo:
            archivo.seek(offset)
            return archivo.read(cantidad)

    def leer_sector(self, sector_lineal):
        offset = self.offset_sector_lineal(sector_lineal)

        return self.leer(
            offset,
            self.capacidad_sector
        )
    

#
#DatabaseManager
#

class DatabaseManager:

    LIBRE = 0
    PARCIAL = 1
    LLENO = 2

    HEADER_SECTOR_SIZE = 1
    HEADER_GLOBAL_SIZE = 4

    def __init__(self, disco):
        self.disco = disco
        self.schema = []
        self.cantidad_registros = 0

        self.sector_actual = 0
        self.off_tmp = self.HEADER_SECTOR_SIZE + self.HEADER_GLOBAL_SIZE

        self.info_sectores = []
        self.inicializar_info_sectores()

    def capacidad_sector(self):
        return self.disco.get_capacidad_sector()

    def offset_real(self, sector, offset):
        return self.disco.offset_sector_lineal(sector) + offset

    def estado_a_texto(self, estado):
        if estado == self.LIBRE:
            return "LIBRE"
        elif estado == self.PARCIAL:
            return "PARCIAL"
        elif estado == self.LLENO:
            return "LLENO"
        return "DESCONOCIDO"

    def direccion_fisica_sector(self, sector_lineal):
        superficie, pista, sector = self.disco.lineal_a_direccion(sector_lineal)

        return {
            "plato": superficie // 2,
            "superficie": superficie % 2,
            "pista": pista,
            "sector": sector
        }

    def inicializar_info_sectores(self):
        self.info_sectores = []

        for sector_lineal in range(self.disco.get_total_sectores()):
            header_size = self.inicio_datos_sector(sector_lineal)
            direccion = self.direccion_fisica_sector(sector_lineal)

            self.info_sectores.append({
                "direccion": direccion,
                "estado": "LIBRE",
                "capacidad": self.capacidad_sector(),
                "ocupado": header_size,
                "gap": 0,
                "elementos": [
                    {
                        "tipo": "HEADER",
                        "bytes": header_size
                    }
                ]
            })

    def actualizar_info_estado(self, sector, estado):
        self.info_sectores[sector]["estado"] = self.estado_a_texto(estado)

    def registrar_elemento_registro(self, sector, id_registro, bytes_ocupados):
        self.info_sectores[sector]["ocupado"] += bytes_ocupados

        self.info_sectores[sector]["elementos"].append({
            "tipo": "REGISTRO",
            "registro": id_registro,
            "bytes": bytes_ocupados
        })

    def registrar_gap(self, sector, bytes_gap):
        if bytes_gap <= 0:
            return

        self.info_sectores[sector]["gap"] += bytes_gap

        self.info_sectores[sector]["elementos"].append({
            "tipo": "GAP",
            "bytes": bytes_gap
        })

    def escribir_estado_sector(self, sector, estado):
        self.disco.escribir(
            self.offset_real(sector, 0),
            bytes([estado])
        )

        self.actualizar_info_estado(sector, estado)

    def leer_estado_sector(self, sector):
        dato = self.disco.leer(
            self.offset_real(sector, 0),
            1
        )

        if dato == b'':
            return None

        return dato[0]

    def guardar_header_global(self):
        self.disco.escribir(
            self.offset_real(0, self.HEADER_SECTOR_SIZE),
            self.cantidad_registros.to_bytes(
                4,
                "little",
                signed=False
            )
        )

    def cargar_header_global(self):
        datos = self.disco.leer(
            self.offset_real(0, self.HEADER_SECTOR_SIZE),
            4
        )

        self.cantidad_registros = int.from_bytes(
            datos,
            "little",
            signed=False
        )

    def inicializar_headers(self):
        # 1. Inicializamos la estructura en memoria RAM (esto es rápido)
        self.inicializar_info_sectores()
        self.cantidad_registros = 0
        self.guardar_header_global()

        # 4. Reseteamos los punteros de escritura
        self.sector_actual = 0
        self.off_tmp = self.inicio_datos_sector(0)
        
        print("¡Headers inicializados instantáneamente con éxito!")

    def inicio_datos_sector(self, sector):
        if sector == 0:
            return self.HEADER_SECTOR_SIZE + self.HEADER_GLOBAL_SIZE

        return self.HEADER_SECTOR_SIZE

    def cargar_schema(self, ruta_txt):
        with open(ruta_txt, "r", encoding="utf-8") as archivo:
            contenido = archivo.read()

        inicio = contenido.find("(")
        fin = contenido.rfind(")")

        if inicio == -1 or fin == -1:
            raise ValueError("CREATE TABLE inválido")

        cuerpo = contenido[inicio + 1:fin]
        campos = cuerpo.split(",")

        self.schema = []

        for campo in campos:
            partes = campo.strip().replace(";", "").split()

            nombre = partes[0]
            tipo = partes[1].upper()

            if tipo == "INT":
                tipo_base = "INT"
                tamaño = 4

            elif tipo == "FLOAT":
                tipo_base = "FLOAT"
                tamaño = 4

            elif tipo.startswith("CHAR"):
                tipo_base = "STRING"
                match = re.search(r"CHAR\[(\d+)\]", tipo)

                if not match:
                    raise ValueError("CHAR debe tener tamaño. Ej: CHAR[30]")

                tamaño = int(match.group(1))

            elif tipo.startswith("VARCHAR"):
                tipo_base = "STRING"
                match = re.search(r"VARCHAR\[(\d+)\]", tipo)

                if not match:
                    raise ValueError("VARCHAR debe tener tamaño. Ej: VARCHAR[50]")

                tamaño = int(match.group(1))

            else:
                raise ValueError(f"Tipo no soportado: {tipo}")

            if tamaño > self.capacidad_sector() - self.HEADER_SECTOR_SIZE:
                raise ValueError(
                    f"El atributo '{nombre}' ocupa {tamaño} bytes, "
                    f"pero el sector solo tiene "
                    f"{self.capacidad_sector() - self.HEADER_SECTOR_SIZE} bytes útiles"
                )

            self.schema.append({
                "nombre": nombre,
                "tipo": tipo_base,
                "tamaño": tamaño
            })

        print("Schema cargado:")
        for columna in self.schema:
            print(columna)

    def es_null(self, valor):
        valor = valor.strip()
        return valor == "" or valor.upper() == "NULL"

    def campo_a_bytes(self, valor, columna):
        tipo = columna["tipo"]
        tamaño = columna["tamaño"]

        if self.es_null(valor):
            return b'\0' * tamaño

        if tipo == "INT":
            return int(valor).to_bytes(4, "little", signed=True)

        elif tipo == "FLOAT":
            return struct.pack("f", float(valor))

        elif tipo == "STRING":
            texto = valor.encode("utf-8")
            return texto[:tamaño].ljust(tamaño, b'\0')

    def bytes_a_campo(self, datos, columna):
        tipo = columna["tipo"]
        tamaño = columna["tamaño"]

        if datos == b'\0' * tamaño:
            return None

        if tipo == "INT":
            return int.from_bytes(datos, "little", signed=True)

        elif tipo == "FLOAT":
            return struct.unpack("f", datos)[0]

        elif tipo == "STRING":
            return datos.decode("utf-8").rstrip('\0')

    def serializar_registro_por_partes(self, fila):
        atributos = []

        for valor, columna in zip(fila, self.schema):
            atributos.append(self.campo_a_bytes(valor, columna))

        return atributos

    def validar_fila(self, fila):
        if len(fila) != len(self.schema):
            return False

        try:
            for valor, columna in zip(fila, self.schema):

                if self.es_null(valor):
                    continue

                tipo = columna["tipo"]
                tamaño = columna["tamaño"]

                if tipo == "INT":
                    int(valor)

                elif tipo == "FLOAT":
                    float(valor)

                elif tipo == "STRING":
                    texto = valor.encode("utf-8")

                    if len(texto) > tamaño:
                        return False

            return True

        except ValueError:
            return False

    def verificar_disco_lleno(self):
        if self.sector_actual >= self.disco.get_total_sectores():
            raise Exception("Disco lleno")

    def escribir_atributo(self, atributo, id_registro):
        if len(atributo) > self.capacidad_sector() - self.HEADER_SECTOR_SIZE:
            raise Exception("El atributo no cabe en un sector")

        self.verificar_disco_lleno()

        espacio_actual = self.capacidad_sector() - self.off_tmp

        if len(atributo) > espacio_actual:
            self.registrar_gap(self.sector_actual, espacio_actual)
            self.escribir_estado_sector(self.sector_actual, self.PARCIAL)

            self.sector_actual += 1
            self.verificar_disco_lleno()

            self.off_tmp = self.inicio_datos_sector(self.sector_actual)

        offset = self.offset_real(self.sector_actual, self.off_tmp)

        self.disco.escribir(offset, atributo)

        self.registrar_elemento_registro(
            self.sector_actual,
            id_registro,
            len(atributo)
        )

        self.off_tmp += len(atributo)

        if self.off_tmp == self.capacidad_sector():
            self.escribir_estado_sector(self.sector_actual, self.LLENO)

            self.sector_actual += 1

            if self.sector_actual < self.disco.get_total_sectores():
                self.off_tmp = self.inicio_datos_sector(self.sector_actual)

        else:
            self.escribir_estado_sector(self.sector_actual, self.PARCIAL)

    def escribir_registro(self, fila, id_registro):
        atributos = self.serializar_registro_por_partes(fila)

        for atributo in atributos:
            self.escribir_atributo(atributo, id_registro)

    def cargar_csv(self, ruta_csv):
        if len(self.schema) == 0:
            print("Primero debes cargar el schema")
            return

        with open(ruta_csv, "r", newline="", encoding="utf-8") as archivo_csv:
            lector = csv.reader(archivo_csv)

            next(lector)

            for fila in lector:
                if not self.validar_fila(fila):
                    print("Fila rechazada:", fila)
                    continue

                id_registro = self.cantidad_registros
                self.escribir_registro(fila, id_registro)

                self.cantidad_registros += 1

        self.guardar_header_global()

        print("CSV cargado correctamente")
        print("Registros insertados:", self.cantidad_registros)

    def leer_bytes_logico(self, sector_actual, off_tmp, tamaño):
        espacio_actual = self.capacidad_sector() - off_tmp

        if tamaño > espacio_actual:
            sector_actual += 1

            if sector_actual >= self.disco.get_total_sectores():
                raise Exception("Lectura fuera del disco")

            off_tmp = self.inicio_datos_sector(sector_actual)

        offset = self.offset_real(sector_actual, off_tmp)

        datos = self.disco.leer(offset, tamaño)

        off_tmp += tamaño

        if off_tmp == self.capacidad_sector():
            sector_actual += 1

            if sector_actual < self.disco.get_total_sectores():
                off_tmp = self.inicio_datos_sector(sector_actual)

        return datos, sector_actual, off_tmp

    def construir_indice_avl(self, nombre_atributo):
        arbol = CBinTree()
        sector_actual = 0
        off_tmp = self.inicio_datos_sector(0)

        for _ in range(self.cantidad_registros):
            sector_inicio = sector_actual
            offset_inicio = off_tmp

            registro = {}
            for columna in self.schema:
                datos, sector_actual, off_tmp = self.leer_bytes_logico(
                    sector_actual, off_tmp, columna["tamaño"]
                )
                registro[columna["nombre"]] = self.bytes_a_campo(datos, columna)

            arbol.ins(
                registro[nombre_atributo],
                sector_inicio,
                offset_inicio
            )
        return arbol

    def leer_registros(self):
        registros = []

        sector_actual = 0
        off_tmp = self.inicio_datos_sector(0)

        for _ in range(self.cantidad_registros):
            registro = {}

            for columna in self.schema:
                tamaño = columna["tamaño"]

                datos, sector_actual, off_tmp = self.leer_bytes_logico(
                    sector_actual,
                    off_tmp,
                    tamaño
                )

                registro[columna["nombre"]] = self.bytes_a_campo(datos, columna)

            registros.append(registro)

        return registros

    def mostrar_registros(self):
        registros = self.leer_registros()

        for registro in registros:
            print(registro)

    def mostrar_estado_sectores(self):
        for sector_lineal in range(self.disco.get_total_sectores()):
            estado = self.leer_estado_sector(sector_lineal)
            texto = self.estado_a_texto(estado)
            direccion = self.direccion_fisica_sector(sector_lineal)

            print(
            f"Plato {direccion['plato']} | "
            f"Superficie {direccion['superficie']} | "
            f"Pista {direccion['pista']} | "
            f"Sector {direccion['sector']}: {texto}")

    def obtener_info_sector(self, sector_lineal):
        if sector_lineal < 0 or sector_lineal >= self.disco.get_total_sectores():
            raise ValueError("Sector inválido")

        return self.info_sectores[sector_lineal]

    def obtener_info_sectores(self):
        return self.info_sectores

    def mostrar_info_sectores(self):
        for info in self.info_sectores:
            consumido = info["ocupado"] + info["gap"]
            direccion = info["direccion"]

            print(
                f"Plato {direccion['plato']} | "
                f"Superficie {direccion['superficie']} | "
                f"Pista {direccion['pista']} | "
                f"Sector {direccion['sector']} "
                f"{info['estado']} | "
                f"Datos/Header: {info['ocupado']}/{info['capacidad']} bytes | "
                f"Gap: {info['gap']} bytes | "
                f"Consumido: {consumido}/{info['capacidad']} bytes"
            )

            for elemento in info["elementos"]:
                if elemento["tipo"] == "REGISTRO":
                    print(
                        f"  REGISTRO {elemento['registro']}: "
                        f"{elemento['bytes']} bytes"
                    )
                else:
                    print(
                        f"  {elemento['tipo']}: "
                        f"{elemento['bytes']} bytes"
                    )
    #leer un registro
    def leer_registro_desde(self, sector_inicio, offset_inicio):
        registro = {}

        sector_actual = sector_inicio
        off_tmp = offset_inicio

        for columna in self.schema:
            tamaño = columna["tamaño"]

            datos, sector_actual, off_tmp = self.leer_bytes_logico(
                sector_actual,
                off_tmp,
                tamaño
            )

            registro[columna["nombre"]] = self.bytes_a_campo(
                datos,
                columna
            )

        return registro
    #find
    def existe_atributo(self, nombre_atributo):
        for columna in self.schema:
            if columna["nombre"] == nombre_atributo:
                return True

        return False
    def find(self, nombre_atributo, valor_buscado):
        if not self.existe_atributo(nombre_atributo):
            print("Atributo no encontrado")
            return []

        col = next(c for c in self.schema if c["nombre"] == nombre_atributo)
        try:
            if col["tipo"] == "INT":
                valor_buscado = int(valor_buscado)
            elif col["tipo"] == "FLOAT":
                valor_buscado = float(valor_buscado)
        except ValueError:
            print(f"Error: El valor '{valor_buscado}' no puede convertirse a {col['tipo']}.")
            return []

        arbol = self.construir_indice_avl(nombre_atributo)
        direcciones = arbol.find(valor_buscado)

        resultados = []
        for direccion in direcciones:
            # Leemos los datos del registro
            reg = self.leer_registro_desde(direccion["sector"], direccion["offset"])
            
            # Convertimos el sector lineal a coordenadas físicas reales del disco
            ubicacion = self.direccion_fisica_sector(direccion["sector"])
            # Empaquetamos todo de forma elegante
            resultados.append({
                "datos": reg,
                "ubicacion_fisica": {
                    "plato": ubicacion["plato"],
                    "superficie": ubicacion["superficie"],
                    "pista": ubicacion["pista"],
                    "sector": ubicacion["sector"],
                    "offset_interno": direccion["offset"]
                }
            })
            
        return resultados
    #busqueda por rango
    def find_range(self, nombre_atributo, minimo, maximo):
        if not self.existe_atributo(nombre_atributo):
            print("Atributo no encontrado")
            return []

        col = next(c for c in self.schema if c["nombre"] == nombre_atributo)
        if col["tipo"] == "INT":
            minimo, maximo = int(minimo), int(maximo)
        elif col["tipo"] == "FLOAT":
            minimo, maximo = float(minimo), float(maximo)

        arbol = self.construir_indice_avl(nombre_atributo)
        direcciones = arbol.buscar_rango(minimo, maximo)

        resultados = []
        for dir in direcciones:
            reg = self.leer_registro_desde(dir["sector"], dir["offset"])
            ubicacion = self.direccion_fisica_sector(dir["sector"])
            
            resultados.append({
                "datos": reg,
                "ubicacion_fisica": {
                    "plato": ubicacion["plato"],
                    "superficie": ubicacion["superficie"],
                    "pista": ubicacion["pista"],
                    "sector": ubicacion["sector"],
                    "offset_interno": dir["offset"]
                }
            })
        return resultados


#Interfaz por consola
def menu_interactivo():
    print("="*50)
    print("  CONFIGURACIÓN DE GEOMETRÍA DEL DISCO RÍGIDO (Potencias de 2)")
    print("="*50)
    try:
        p = int(input("Exponente de platos (2^p platos) [Por defecto 0 -> 1 plato]: ").strip() or "0")
        t = int(input("Exponente de pistas (2^t pistas) [Por defecto 0 -> 1 pista]: ").strip() or "0")
        s = int(input("Exponente de sectores (2^s sectores) [Por defecto 4 -> 16 sec]: ").strip() or "4")
        c = int(input("Exponente de bytes por sector (2^c bytes) [Por defecto 5 -> 32 bytes]: ").strip() or "5")
    except ValueError:
        print("Valores erróneos. Usando valores por defecto (0, 0, 4, 5).")
        p, t, s, c = 0, 0, 4, 5

    disco = DISK(p, t, s, c)
    disco.formateador()
    db = DatabaseManager(disco)
    db.inicializar_headers()

    while True:
        print("\n" + "="*50)
        print("SISTEMA DE GESTIÓN DE BASES DE DATOS FÍSICAS")
        print("="*50)
        print("1. Cargar Esquema de la Tabla (schema.txt)")
        print("2. Poblar desde Archivo de Datos (datos.csv)")
        print("3. Mostrar Todos los Registros Almacenados")
        print("4. Ver Estado Físico de Sectores (Hardware)")
        print("5. Ver Detalle de Consumo de Sectores (Gaps/Headers)")
        print("6. Búsqueda Puntual (Indexada con Árbol AVL)")
        print("7. Búsqueda por Rango (Indexada con Árbol AVL)")
        print("8. Salir y Destruir Disco Dat")
        print("="*50)
        
        opcion = input("Seleccione una opción estratégica (1-8): ").strip()

        if opcion == "1":
            ruta = input("Ruta del archivo de esquema [schema.txt]: ").strip() or "schema.txt"
            if os.path.exists(ruta):
                db.cargar_schema(ruta)
            else:
                print("Archivo de esquema no encontrado.")

        elif opcion == "2":
            ruta = input("Ruta del archivo de datos CSV [datos.csv]: ").strip() or "datos.csv"
            if os.path.exists(ruta):
                db.cargar_csv(ruta)
                print(f"Población completada. Registros en disco: {db.cantidad_registros}")
            else:
                print("Archivo CSV no encontrado.")

        elif opcion == "3":
            print("\n=== REGISTROS LEÍDOS DESDE EL DISCO ===")
            registros = db.leer_registros()
            if not registros: print("Disco vacío o sin registros.")
            for r in registros: print(r)

        elif opcion == "4":
            print("\n=== MAPA GEOMÉTRICO DEL DISCO ===")
            db.mostrar_estado_sectores()

        elif opcion == "5":
            print("\n=== INSPECTOR DETALLADO DE FRAGMENTACIÓN ===")
            db.mostrar_info_sectores()

        elif opcion == "6":
            if not db.schema:
                print("Cargue el esquema primero.")
                continue
            attr = input("Nombre del atributo a buscar: ").strip()
            val = input("Valor exacto buscado: ").strip()
            print("\nBuscando con el Índice AVL...")
            res = db.find(attr, val)
            print(f"Resultados encontrados ({len(res)}):")
            for r in res: print(r)

        elif opcion == "7":
            if not db.schema:
                print("Cargue el esquema primero.")
                continue
            attr = input("Nombre del atributo para el rango: ").strip()
            min_val = input("Valor mínimo del límite: ").strip()
            max_val = input("Valor máximo del límite: ").strip()
            print("\nEjecutando recorrido en rango sobre el Árbol AVL...")
            res = db.find_range(attr, min_val, max_val)
            print(f"Resultados encontrados en el rango ({len(res)}):")
            for r in res: print(r)

        elif opcion == "8":
            disco.eliminar_disco()
            print("Operación terminada. Disco destruido limpiamente.")
            break
        else:
            print("Opción inválida, intente de nuevo.")

if __name__ == "__main__":
    menu_interactivo()

