import os
import csv
import re
import struct
import math

#
# ARBOL AVL
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
# DatabaseManager
#


class DatabaseManager:
    LIBRE = 0
    PARCIAL = 1
    LLENO = 2

    HEADER_SECTOR_SIZE = 1
    HEADER_GLOBAL_SIZE = 4
    HEADER_REGISTRO_SIZE = 4
    VARCHAR_NULL = 65535

    def __init__(self, disco):
        self.disco = disco
        self.schema = []
        self.cantidad_registros = 0

        self.sector_actual = 0
        self.off_tmp = self.HEADER_SECTOR_SIZE + self.HEADER_GLOBAL_SIZE

        # Metadatos solo de sectores usados.
        self.info_sectores = {}

        # Cache de índices AVL por atributo.
        self.indices_avl = {}

        # Restricciones del schema.
        self.primary_key = tuple()  # tupla de columnas que forman la PK
        self.unique_constraints = set()  # set de tuplas de columnas UNIQUE/PK
        self.check_constraints = []  # condiciones CHECK simples
        self.unique_values = {}  # valores ya vistos para PK/UNIQUE

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
        self.info_sectores = {}

    def asegurar_info_sector(self, sector_lineal):
        if sector_lineal not in self.info_sectores:
            header_size = self.inicio_datos_sector(sector_lineal)
            direccion = self.direccion_fisica_sector(sector_lineal)

            self.info_sectores[sector_lineal] = {
                "direccion": direccion,
                "capacidad": self.capacidad_sector(),
                "ocupado": header_size,
                "gap": 0,
                "elementos": [
                    {
                        "tipo": "HEADER",
                        "bytes": header_size
                    }
                ]
            }

        return self.info_sectores[sector_lineal]

    def registrar_elemento_registro(self, sector, id_registro, bytes_ocupados):
        info = self.asegurar_info_sector(sector)
        info["ocupado"] += bytes_ocupados

        self.asegurar_info_sector(sector)["elementos"].append({
            "tipo": "REGISTRO",
            "registro": id_registro,
            "bytes": bytes_ocupados
        })

    def registrar_gap(self, sector, bytes_gap):
        if bytes_gap <= 0:
            return

        info = self.asegurar_info_sector(sector)
        info["gap"] += bytes_gap

        info["elementos"].append({
            "tipo": "GAP",
            "bytes": bytes_gap
        })

    def escribir_estado_sector(self, sector, estado):
        self.disco.escribir(
            self.offset_real(sector, 0),
            bytes([estado])
        )
        self.asegurar_info_sector(sector)

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
        self.inicializar_info_sectores()
        self.indices_avl = {}
        self.unique_values = {}
        self.cantidad_registros = 0
        self.guardar_header_global()

        self.sector_actual = 0
        self.off_tmp = self.inicio_datos_sector(0)

        print("¡Headers inicializados instantáneamente con éxito!")

    def inicio_datos_sector(self, sector):
        if sector == 0:
            return self.HEADER_SECTOR_SIZE + self.HEADER_GLOBAL_SIZE
        return self.HEADER_SECTOR_SIZE

    def dividir_por_comas_sql(self, texto):
        partes = []
        actual = []
        nivel_parentesis = 0
        en_comilla = False
        comilla = ""

        for ch in texto:
            if ch in ("'", '\"'):
                if not en_comilla:
                    en_comilla = True
                    comilla = ch
                elif comilla == ch:
                    en_comilla = False

            if not en_comilla:
                if ch == "(":
                    nivel_parentesis += 1
                elif ch == ")":
                    nivel_parentesis -= 1
                elif ch == "," and nivel_parentesis == 0:
                    partes.append("".join(actual).strip())
                    actual = []
                    continue

            actual.append(ch)

        if actual:
            partes.append("".join(actual).strip())

        return partes

    def limpiar_identificador(self, texto):
        return texto.strip().strip('`').strip('"').strip()

    def extraer_columnas_parentesis(self, texto):
        inicio = texto.find("(")
        fin = texto.rfind(")")

        if inicio == -1 or fin == -1 or fin <= inicio:
            raise ValueError("Restricción inválida: faltan paréntesis")

        dentro = texto[inicio + 1:fin]
        return [self.limpiar_identificador(c) for c in self.dividir_por_comas_sql(dentro)]

    def obtener_columna(self, nombre):
        for columna in self.schema:
            if columna["nombre"] == nombre:
                return columna
        return None

    def marcar_columna_not_null(self, nombre):
        col = self.obtener_columna(nombre)
        if col:
            col["not_null"] = True

    def marcar_columna_primary_key(self, nombre):
        col = self.obtener_columna(nombre)
        if col:
            col["primary_key"] = True
            col["not_null"] = True

    def marcar_columna_unique(self, nombre):
        col = self.obtener_columna(nombre)
        if col:
            col["unique"] = True

    def parsear_valor_default(self, valor):
        valor = valor.strip().rstrip(",")

        if (valor.startswith("'") and valor.endswith("'")) or (valor.startswith('"') and valor.endswith('"')):
            return valor[1:-1]

        if valor.upper() == "NULL":
            return "NULL"

        return valor

    def extraer_parentesis_balanceado(self, texto, inicio_parentesis):
        nivel = 0
        en_comilla = False
        comilla = ""

        for i in range(inicio_parentesis, len(texto)):
            ch = texto[i]

            if ch in ("'", '\"'):
                if not en_comilla:
                    en_comilla = True
                    comilla = ch
                elif comilla == ch:
                    en_comilla = False

            if en_comilla:
                continue

            if ch == "(":
                nivel += 1
            elif ch == ")":
                nivel -= 1
                if nivel == 0:
                    return texto[inicio_parentesis + 1:i], i

        raise ValueError("Paréntesis no balanceados en CHECK")

    def extraer_check_inline(self, restricciones):
        m = re.search(r"\bCHECK\s*\(", restricciones, re.IGNORECASE)
        if not m:
            return None

        inicio_parentesis = restricciones.find("(", m.start())
        expr, _ = self.extraer_parentesis_balanceado(restricciones, inicio_parentesis)
        return expr

    def parsear_check(self, expr):
        expr = expr.strip()
        inicio = expr.upper().find("CHECK")
        if inicio != -1:
            inicio_parentesis = expr.find("(", inicio)
            if inicio_parentesis == -1:
                raise ValueError(f"CHECK inválido: {expr}")
            expr, _ = self.extraer_parentesis_balanceado(expr, inicio_parentesis)

        if expr.startswith("(") and expr.endswith(")"):
            expr = expr[1:-1].strip()

        # Soporte intencionalmente simple para el proyecto
        if re.search(r"\b(IN|AND|OR|BETWEEN|LIKE)\b", expr, re.IGNORECASE):
            raise ValueError(f"CHECK no soportado por este simulador: {expr}")

        m = re.match(
            r"^([A-Za-z_][A-Za-z0-9_]*)\s*(>=|<=|<>|!=|=|>|<)\s*(.+)$",
            expr
        )

        if not m:
            raise ValueError(f"CHECK no soportado por este simulador: {expr}")

        return {
            "columna": m.group(1),
            "op": m.group(2),
            "valor": self.parsear_valor_default(m.group(3))
        }

    def cargar_schema(self, ruta_txt):
        with open(ruta_txt, "r", encoding="utf-8") as archivo:
            contenido = archivo.read()

        inicio = contenido.find("(")
        fin = contenido.rfind(")")

        if inicio == -1 or fin == -1:
            raise ValueError("CREATE TABLE inválido")

        cuerpo = contenido[inicio + 1:fin]
        definiciones = self.dividir_por_comas_sql(cuerpo)

        self.schema = []
        self.primary_key = tuple()
        self.unique_constraints = set()
        self.check_constraints = []
        self.unique_values = {}
        restricciones_tabla = []

        for definicion in definiciones:
            definicion = definicion.strip().replace(";", "")
            if not definicion:
                continue

            upper = definicion.upper()

            if upper.startswith("CONSTRAINT"):
                partes = definicion.split(None, 2)
                if len(partes) < 3:
                    raise ValueError(f"CONSTRAINT inválida: {definicion}")
                restricciones_tabla.append(partes[2].strip())
                continue

            if upper.startswith("PRIMARY KEY") or upper.startswith("UNIQUE") or upper.startswith("CHECK"):
                restricciones_tabla.append(definicion)
                continue

            m = re.match(
                r"^([A-Za-z_][A-Za-z0-9_]*)\s+"
                r"(INT|FLOAT|DECIMAL\s*\(\s*\d+\s*,\s*\d+\s*\)|CHAR\s*(?:\[\s*\d+\s*\]|\(\s*\d+\s*\))|VARCHAR\s*(?:\[\s*\d+\s*\]|\(\s*\d+\s*\)))"
                r"\s*(.*)$",
                definicion,
                re.IGNORECASE
            )

            if not m:
                raise ValueError(f"Definición de columna inválida: {definicion}")

            nombre = self.limpiar_identificador(m.group(1))
            tipo = re.sub(r"\s+", "", m.group(2).upper())
            restricciones = m.group(3).strip()

            if tipo == "INT":
                tipo_base = "INT"
                tamaño = 4

            elif tipo == "FLOAT":
                tipo_base = "FLOAT"
                tamaño = 4

            elif tipo.startswith("DECIMAL"):
                # Se almacena como FLOAT de 4 bytes 
                tipo_base = "FLOAT"
                tamaño = 4

            elif tipo.startswith("CHAR"):
                tipo_base = "CHAR"
                match = re.search(r"CHAR(?:\[|\()(\d+)(?:\]|\))", tipo)
                if not match:
                    raise ValueError("CHAR debe tener tamaño. Ej: CHAR[30]")
                tamaño = int(match.group(1))

            elif tipo.startswith("VARCHAR"):
                tipo_base = "VARCHAR"
                match = re.search(r"VARCHAR(?:\[|\()(\d+)(?:\]|\))", tipo)
                if not match:
                    raise ValueError("VARCHAR debe tener tamaño. Ej: VARCHAR[50]")
                tamaño = int(match.group(1))
                if tamaño >= self.VARCHAR_NULL:
                    raise ValueError("VARCHAR debe ser menor a 65535 bytes")

            else:
                raise ValueError(f"Tipo no soportado: {tipo}")

            if tipo_base in ("INT", "FLOAT") and tamaño > self.capacidad_sector() - self.HEADER_SECTOR_SIZE:
                raise ValueError(
                    f"El atributo '{nombre}' ocupa {tamaño} bytes, "
                    f"pero el sector solo tiene "
                    f"{self.capacidad_sector() - self.HEADER_SECTOR_SIZE} bytes útiles"
                )

            columna = {
                "nombre": nombre,
                "tipo": tipo_base,
                "tamaño": tamaño,
                "not_null": False,
                "primary_key": False,
                "unique": False,
                "default": None,
                "checks": []
            }

            restricciones_upper = restricciones.upper()

            if "NOT NULL" in restricciones_upper:
                columna["not_null"] = True

            if "PRIMARY KEY" in restricciones_upper:
                columna["primary_key"] = True
                columna["not_null"] = True
                self.primary_key = (nombre,)

            if re.search(r"\bUNIQUE\b", restricciones_upper):
                columna["unique"] = True
                self.unique_constraints.add((nombre,))

            m_default = re.search(
                r"\bDEFAULT\s+('(?:[^']*)'|\"(?:[^\"]*)\"|[^\s]+)",
                restricciones,
                re.IGNORECASE
            )
            if m_default:
                columna["default"] = self.parsear_valor_default(m_default.group(1))

            expr_check = self.extraer_check_inline(restricciones)
            if expr_check is not None:
                columna["checks"].append(self.parsear_check(expr_check))

            self.schema.append(columna)

        for restriccion in restricciones_tabla:
            upper = restriccion.upper()

            if upper.startswith("PRIMARY KEY"):
                columnas = self.extraer_columnas_parentesis(restriccion)
                self.primary_key = tuple(columnas)
                for col in columnas:
                    self.marcar_columna_primary_key(col)

            elif upper.startswith("UNIQUE"):
                columnas = self.extraer_columnas_parentesis(restriccion)
                self.unique_constraints.add(tuple(columnas))
                for col in columnas:
                    self.marcar_columna_unique(col)

            elif upper.startswith("CHECK"):
                self.check_constraints.append(self.parsear_check(restriccion))

            else:
                raise ValueError(f"Restricción de tabla no soportada: {restriccion}")

        if self.primary_key:
            self.unique_constraints.add(tuple(self.primary_key))

        # Validar que las columnas mencionadas existan.
        nombres = {c["nombre"] for c in self.schema}
        for col in self.primary_key:
            self.marcar_columna_primary_key(col)
            if col not in nombres:
                raise ValueError(f"PRIMARY KEY usa columna inexistente: {col}")
        for restr in self.unique_constraints:
            for col in restr:
                if col not in nombres:
                    raise ValueError(f"UNIQUE usa columna inexistente: {col}")
        for chk in self.check_constraints:
            if chk["columna"] not in nombres:
                raise ValueError(f"CHECK usa columna inexistente: {chk['columna']}")
        for col in self.schema:
            for chk in col["checks"]:
                if chk["columna"] not in nombres:
                    raise ValueError(f"CHECK usa columna inexistente: {chk['columna']}")

        print("Schema cargado:")
        for columna in self.schema:
            print(columna)

        if self.primary_key:
            print("PRIMARY KEY:", self.primary_key)
        if self.unique_constraints:
            print("UNIQUE:", self.unique_constraints)
        if self.check_constraints:
            print("CHECK:", self.check_constraints)

    def es_null(self, valor):
        valor = valor.strip()
        return valor == "" or valor.upper() == "NULL"

    def tam_bitmap_nulls(self):
        return math.ceil(len(self.schema) / 8)

    def marcar_null_bitmap(self, bitmap, indice_columna):
        bitmap[indice_columna // 8] |= (1 << (indice_columna % 8))

    def es_null_en_bitmap(self, bitmap, indice_columna):
        return (bitmap[indice_columna // 8] & (1 << (indice_columna % 8))) != 0

    def campo_a_bytes(self, valor, columna):
        tipo = columna["tipo"]
        tamaño = columna["tamaño"]

        # IMPORTANTE:
        # El NULL ya no se identifica mirando los bytes del campo
        # Ahora se identifica con el bitmap de NULLS del registro
        # Por eso aqui si el valor es NULL, solo se escribe relleno
        # para conservar el formato físico del campo.
        if tipo == "INT":
            if self.es_null(valor):
                return b'\0' * 4
            return int(valor).to_bytes(4, "little", signed=True)

        elif tipo == "FLOAT":
            if self.es_null(valor):
                return b'\0' * 4
            return struct.pack("f", float(valor))

        elif tipo == "CHAR":
            if self.es_null(valor):
                return b'\0' * tamaño
            texto = valor.encode("utf-8")
            return texto[:tamaño].ljust(tamaño, b'\0')

        elif tipo == "VARCHAR":
            if self.es_null(valor):
                # NULL se marca en el bitmap.
                # En el campo solo guardamos longitud 0.
                return (0).to_bytes(2, "little", signed=False)

            texto = valor.encode("utf-8")

            if len(texto) > tamaño:
                raise ValueError(
                    f"VARCHAR excede su tamaño máximo: {len(texto)} > {tamaño}"
                )

            return len(texto).to_bytes(2, "little", signed=False) + texto

    def bytes_a_campo_fijo(self, datos, columna):
        tipo = columna["tipo"]

        # Ya no se detecta NULL aquí.
        # Si un campo es NULL, eso se decide antes usando el bitmap.
        if tipo == "INT":
            return int.from_bytes(datos, "little", signed=True)

        elif tipo == "FLOAT":
            return struct.unpack("f", datos)[0]

        elif tipo == "CHAR":
            return datos.decode("utf-8").rstrip('\0')

    def serializar_registro_por_partes(self, fila):
        campos = []
        bitmap = bytearray(self.tam_bitmap_nulls())

        # El payload includes:
        # 1) bitmap de NULLs
        # 2) bytes de todos los campos
        tam_payload = len(bitmap)

        for i, (valor, columna) in enumerate(zip(fila, self.schema)):
            if self.es_null(valor):
                self.marcar_null_bitmap(bitmap, i)

            datos = self.campo_a_bytes(valor, columna)
            fragmentable = columna["tipo"] in ("CHAR", "VARCHAR")

            campos.append({
                "nombre": columna["nombre"],
                "datos": datos,
                "fragmentable": fragmentable
            })

            tam_payload += len(datos)

        header_registro = tam_payload.to_bytes(
            self.HEADER_REGISTRO_SIZE,
            "little",
            signed=False
        )

        return [
            {
                "nombre": "HEADER_REGISTRO",
                "datos": header_registro,
                "fragmentable": False
            },
            {
                "nombre": "NULL_BITMAP",
                "datos": bytes(bitmap),
                "fragmentable": False
            }
        ] + campos

    def convertir_valor_para_comparar(self, valor, columna):
        if valor is None:
            return None

        if isinstance(valor, str) and self.es_null(valor):
            return None

        tipo = columna["tipo"]

        if tipo == "INT":
            return int(valor)
        elif tipo == "FLOAT":
            return float(valor)
        else:
            return str(valor)

    def evaluar_check(self, fila_dict, check):
        columna = self.obtener_columna(check["columna"])
        valor_izq = fila_dict.get(check["columna"])

        # En SQL, CHECK con NULL no falla; lo controla NOT NULL si corresponde.
        if valor_izq is None:
            return True

        valor_der = self.convertir_valor_para_comparar(check["valor"], columna)
        op = check["op"]

        if op == ">":
            return valor_izq > valor_der
        if op == ">=":
            return valor_izq >= valor_der
        if op == "<":
            return valor_izq < valor_der
        if op == "<=":
            return valor_izq <= valor_der
        if op == "=":
            return valor_izq == valor_der
        if op in ("!=", "<>"):
            return valor_izq != valor_der

        return False

    def clave_restriccion(self, fila_dict, columnas):
        valores = []
        for col in columnas:
            valores.append(fila_dict.get(col))
        return tuple(valores)

    def inicializar_unique_values_si_falta(self):
        for restr in self.unique_constraints:
            llave = tuple(restr)
            if llave not in self.unique_values:
                self.unique_values[llave] = set()

    def registrar_valores_unicos(self, fila_dict):
        self.inicializar_unique_values_si_falta()

        for restr in self.unique_constraints:
            llave = tuple(restr)
            clave = self.clave_restriccion(fila_dict, restr)

            # UNIQUE permite varios NULL; PRIMARY KEY no, porque ya fue validada como NOT NULL.
            if any(v is None for v in clave) and tuple(restr) != tuple(self.primary_key):
                continue

            self.unique_values[llave].add(clave)

    def validar_fila(self, fila):
        if len(fila) > len(self.schema):
            print("Fila rechazada: tiene más columnas que el schema")
            return False

        # Si faltan columnas al final, se rellenan para poder aplicar DEFAULT o NULL.
        while len(fila) < len(self.schema):
            fila.append("")

        try:
            fila_dict = {}

            for i, columna in enumerate(self.schema):
                valor = fila[i].strip()

                if self.es_null(valor) and columna.get("default") is not None:
                    valor = str(columna["default"])
                    fila[i] = valor

                if columna.get("not_null") and self.es_null(valor):
                    print(f"Fila rechazada: columna NOT NULL vacía: {columna['nombre']}")
                    return False

                if self.es_null(valor):
                    fila_dict[columna["nombre"]] = None
                    continue

                tipo = columna["tipo"]
                tamaño = columna["tamaño"]

                if tipo == "INT":
                    fila_dict[columna["nombre"]] = int(valor)

                elif tipo == "FLOAT":
                    fila_dict[columna["nombre"]] = float(valor)

                elif tipo in ("CHAR", "VARCHAR"):
                    texto = valor.encode("utf-8")
                    if len(texto) > tamaño:
                        print(f"Fila rechazada: {columna['nombre']} excede {tamaño} bytes")
                        return False
                    fila_dict[columna["nombre"]] = valor

            for columna in self.schema:
                for check in columna.get("checks", []):
                    if not self.evaluar_check(fila_dict, check):
                        print(f"Fila rechazada: CHECK falló en {check}")
                        return False

            for check in self.check_constraints:
                if not self.evaluar_check(fila_dict, check):
                    print(f"Fila rechazada: CHECK falló en {check}")
                    return False

            self.inicializar_unique_values_si_falta()
            for restr in self.unique_constraints:
                llave = tuple(restr)
                clave = self.clave_restriccion(fila_dict, restr)

                if any(v is None for v in clave) and tuple(restr) != tuple(self.primary_key):
                    continue

                if clave in self.unique_values[llave]:
                    if tuple(restr) == tuple(self.primary_key):
                        print(f"Fila rechazada: PRIMARY KEY duplicada {restr} = {clave}")
                    else:
                        print(f"Fila rechazada: UNIQUE duplicado {restr} = {clave}")
                    return False

            self.registrar_valores_unicos(fila_dict)
            return True

        except ValueError:
            print("Fila rechazada: tipo de dato inválido")
            return False

    def verificar_disco_lleno(self):
        if self.sector_actual >= self.disco.get_total_sectores():
            raise Exception("Disco lleno")

    def avanzar_a_siguiente_sector(self):
        self.sector_actual += 1
        self.verificar_disco_lleno()
        self.off_tmp = self.inicio_datos_sector(self.sector_actual)

    def escribir_atributo_no_fragmentable(self, atributo, id_registro):
        if len(atributo) > self.capacidad_sector() - self.HEADER_SECTOR_SIZE:
            raise Exception("El atributo no fragmentable no cabe en un sector")

        self.verificar_disco_lleno()

        if self.off_tmp == self.capacidad_sector():
            self.escribir_estado_sector(self.sector_actual, self.LLENO)
            self.avanzar_a_siguiente_sector()

        espacio_actual = self.capacidad_sector() - self.off_tmp

        if len(atributo) > espacio_actual:
            self.registrar_gap(self.sector_actual, espacio_actual)
            self.escribir_estado_sector(self.sector_actual, self.PARCIAL)
            self.avanzar_a_siguiente_sector()

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
            if self.sector_actual + 1 < self.disco.get_total_sectores():
                self.sector_actual += 1
                self.off_tmp = self.inicio_datos_sector(self.sector_actual)
        else:
            self.escribir_estado_sector(self.sector_actual, self.PARCIAL)

    def escribir_atributo_fragmentable(self, atributo, id_registro):
        restante = atributo

        while restante:
            self.verificar_disco_lleno()

            if self.off_tmp == self.capacidad_sector():
                self.escribir_estado_sector(self.sector_actual, self.LLENO)
                self.avanzar_a_siguiente_sector()

            espacio_actual = self.capacidad_sector() - self.off_tmp

            if espacio_actual <= 0:
                self.escribir_estado_sector(self.sector_actual, self.LLENO)
                self.avanzar_a_siguiente_sector()
                continue

            porcion = restante[:espacio_actual]
            restante = restante[espacio_actual:]

            offset = self.offset_real(self.sector_actual, self.off_tmp)
            self.disco.escribir(offset, porcion)

            self.registrar_elemento_registro(
                self.sector_actual,
                id_registro,
                len(porcion)
            )

            self.off_tmp += len(porcion)

            if self.off_tmp == self.capacidad_sector():
                self.escribir_estado_sector(self.sector_actual, self.LLENO)
                if restante and self.sector_actual + 1 < self.disco.get_total_sectores():
                    self.avanzar_a_siguiente_sector()
            else:
                self.escribir_estado_sector(self.sector_actual, self.PARCIAL)

    def escribir_atributo(self, atributo_info, id_registro):
        datos = atributo_info["datos"]

        if atributo_info["fragmentable"]:
            self.escribir_atributo_fragmentable(datos, id_registro)
        else:
            self.escribir_atributo_no_fragmentable(datos, id_registro)

    def escribir_registro(self, fila, id_registro):
        atributos = self.serializar_registro_por_partes(fila)

        for atributo in atributos:
            self.escribir_atributo(atributo, id_registro)

    def cargar_csv(self, ruta_csv):
        self.indices_avl = {}

        if len(self.schema) == 0:
            print("Primero debes cargar el schema")
            return

        with open(ruta_csv, "r", newline="", encoding="utf-8") as archivo_csv:
            lector = csv.reader(archivo_csv)

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

    def leer_bytes_no_fragmentado(self, sector_actual, off_tmp, tamaño):
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

    def leer_bytes_fragmentado(self, sector_actual, off_tmp, tamaño):
        partes = []
        restante = tamaño

        while restante > 0:
            if sector_actual >= self.disco.get_total_sectores():
                raise Exception("Lectura fuera del disco")

            if off_tmp == self.capacidad_sector():
                sector_actual += 1
                if sector_actual >= self.disco.get_total_sectores():
                    raise Exception("Lectura fuera del disco")
                off_tmp = self.inicio_datos_sector(sector_actual)

            espacio_actual = self.capacidad_sector() - off_tmp
            por_leer = min(restante, espacio_actual)

            offset = self.offset_real(sector_actual, off_tmp)
            partes.append(self.disco.leer(offset, por_leer))

            off_tmp += por_leer
            restante -= por_leer

            if off_tmp == self.capacidad_sector():
                sector_actual += 1
                if sector_actual < self.disco.get_total_sectores():
                    off_tmp = self.inicio_datos_sector(sector_actual)

        return b"".join(partes), sector_actual, off_tmp

    # Alias para compatibilidad con nombres anteriores.
    def leer_bytes_logico(self, sector_actual, off_tmp, tamaño):
        return self.leer_bytes_no_fragmentado(sector_actual, off_tmp, tamaño)

    def leer_registro_en_posicion(self, sector_actual, off_tmp):
        header, sector_actual, off_tmp = self.leer_bytes_no_fragmentado(
            sector_actual,
            off_tmp,
            self.HEADER_REGISTRO_SIZE
        )

        tamaño_payload = int.from_bytes(header, "little", signed=False)

        bitmap, sector_actual, off_tmp = self.leer_bytes_no_fragmentado(
            sector_actual,
            off_tmp,
            self.tam_bitmap_nulls()
        )

        bytes_consumidos_payload = len(bitmap)
        registro = {}

        for i, columna in enumerate(self.schema):
            tipo = columna["tipo"]
            campo_es_null = self.es_null_en_bitmap(bitmap, i)

            if tipo in ("INT", "FLOAT"):
                datos, sector_actual, off_tmp = self.leer_bytes_no_fragmentado(
                    sector_actual,
                    off_tmp,
                    columna["tamaño"]
                )
                bytes_consumidos_payload += columna["tamaño"]

                if campo_es_null:
                    registro[columna["nombre"]] = None
                else:
                    registro[columna["nombre"]] = self.bytes_a_campo_fijo(datos, columna)

            elif tipo == "CHAR":
                datos, sector_actual, off_tmp = self.leer_bytes_fragmentado(
                    sector_actual,
                    off_tmp,
                    columna["tamaño"]
                )
                bytes_consumidos_payload += columna["tamaño"]

                if campo_es_null:
                    registro[columna["nombre"]] = None
                else:
                    registro[columna["nombre"]] = self.bytes_a_campo_fijo(datos, columna)

            elif tipo == "VARCHAR":
                longitud_bytes, sector_actual, off_tmp = self.leer_bytes_fragmentado(
                    sector_actual,
                    off_tmp,
                    2
                )
                bytes_consumidos_payload += 2

                longitud = int.from_bytes(longitud_bytes, "little", signed=False)

                if campo_es_null:
                    if longitud != 0:
                        raise Exception(
                            f"VARCHAR NULL corrupto en columna '{columna['nombre']}': "
                            f"longitud esperada 0, longitud encontrada {longitud}"
                        )
                    registro[columna["nombre"]] = None
                else:
                    if longitud > columna["tamaño"]:
                        raise Exception(
                            f"VARCHAR corrupto en columna '{columna['nombre']}': "
                            f"{longitud} > {columna['tamaño']}"
                        )

                    datos, sector_actual, off_tmp = self.leer_bytes_fragmentado(
                        sector_actual,
                        off_tmp,
                        longitud
                    )

                    bytes_consumidos_payload += longitud
                    registro[columna["nombre"]] = datos.decode("utf-8")
                    
        if bytes_consumidos_payload != tamaño_payload:
            raise Exception("Registro variable corrupto o schema incompatible")

        return registro, sector_actual, off_tmp

    def construir_indice_avl(self, nombre_atributo):
        if nombre_atributo in self.indices_avl:
            return self.indices_avl[nombre_atributo]

        arbol = CBinTree()
        sector_actual = 0
        off_tmp = self.inicio_datos_sector(0)

        for _ in range(self.cantidad_registros):
            sector_inicio = sector_actual
            offset_inicio = off_tmp

            registro, sector_actual, off_tmp = self.leer_registro_en_posicion(
                sector_actual,
                off_tmp
            )

            valor_indice = registro[nombre_atributo]

            # No indexamos NULL para evitar comparaciones ambiguas.
            if valor_indice is not None:
                arbol.ins(valor_indice, sector_inicio, offset_inicio)

        self.indices_avl[nombre_atributo] = arbol
        return arbol

    def leer_registros(self):
        registros = []

        sector_actual = 0
        off_tmp = self.inicio_datos_sector(0)

        for _ in range(self.cantidad_registros):
            registro, sector_actual, off_tmp = self.leer_registro_en_posicion(
                sector_actual,
                off_tmp
            )
            registros.append(registro)

        return registros

    def mostrar_registros(self):
        registros = self.leer_registros()

        for registro in registros:
            print(registro)

    def mostrar_estado_sectores(self):
        usados = sorted(self.info_sectores.keys())

        print(f"Total de sectores lógicos: {self.disco.get_total_sectores()}")
        print(f"Sectores usados/registrados: {len(usados)}")
        print("Se muestran solo los sectores usados para evitar recorrer discos grandes.")

        if not usados:
            print("Todos los sectores están libres lógicamente.")
            return

        for sector_lineal in usados:
            estado = self.leer_estado_sector(sector_lineal)
            texto = self.estado_a_texto(estado)
            direccion = self.direccion_fisica_sector(sector_lineal)

            print(
                f"Plato {direccion['plato']} | "
                f"Superficie {direccion['superficie']} | "
                f"Pista {direccion['pista']} | "
                f"Sector {direccion['sector']}: {texto}"
            )

    def obtener_info_sector(self, sector_lineal):
        if sector_lineal < 0 or sector_lineal >= self.disco.get_total_sectores():
            raise ValueError("Sector inválido")

        return self.asegurar_info_sector(sector_lineal)

    def obtener_info_sectores(self):
        return self.info_sectores

    def mostrar_info_sectores(self):
        if not self.info_sectores:
            print("No hay sectores usados todavía.")
            return

        for sector_lineal in sorted(self.info_sectores):
            info = self.info_sectores[sector_lineal]
            consumido = info["ocupado"] + info["gap"]
            libre = info["capacidad"] - consumido
            direccion = info["direccion"]
            estado = self.leer_estado_sector(sector_lineal)
            texto_estado = self.estado_a_texto(estado)
            print(
                f"Plato {direccion['plato']} | "
                f"Superficie {direccion['superficie']} | "
                f"Pista {direccion['pista']} | "
                f"Sector {direccion['sector']} "
                f"{texto_estado} | "
                f"Datos/Header: {info['ocupado']}/{info['capacidad']} bytes | "
                f"Gap: {info['gap']} bytes | "
                f"Consumido: {consumido}/{info['capacidad']} bytes | "
                f"Libre: {libre} bytes"
            )

            totales = {}

            for elemento in info["elementos"]:
                if elemento["tipo"] == "REGISTRO":
                    reg = elemento["registro"]
                    totales[reg] = totales.get(reg, 0) + elemento["bytes"]
                else:
                    print(f"  {elemento['tipo']}: {elemento['bytes']} bytes")

            for reg, total in totales.items():
                print(f"  REGISTRO {reg}: {total} bytes")

    def leer_registro_desde(self, sector_inicio, offset_inicio):
        registro, _, _ = self.leer_registro_en_posicion(sector_inicio, offset_inicio)
        return registro

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
            reg = self.leer_registro_desde(direccion["sector"], direccion["offset"])
            ubicacion = self.direccion_fisica_sector(direccion["sector"])

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


# Interfaz por consola
def menu_interactivo():
    print("=" * 50)
    print("  CONFIGURACIÓN DE GEOMETRÍA DEL DISCO RÍGIDO (Potencias de 2)")
    print("=" * 50)
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
        print("\n" + "=" * 50)
        print("SISTEMA DE GESTIÓN DE BASES DE DATOS FÍSICAS")
        print("=" * 50)
        print("1. Cargar Esquema de la Tabla (schema.txt)")
        print("2. Poblar desde Archivo de Datos (datos.csv)")
        print("3. Mostrar Todos los Registros Almacenados")
        print("4. Ver Estado Físico de Sectores (Hardware)")
        print("5. Ver Detalle de Consumo de Sectores (Gaps/Headers)")
        print("6. Búsqueda Puntual (Indexada con Árbol AVL)")
        print("7. Búsqueda por Rango (Indexada con Árbol AVL)")
        print("8. Salir y Destruir Disco Dat")
        print("=" * 50)

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


#
# INTERFAZ DE ESCRITORIO (Tkinter)
# Se abre solo, en una ventana nueva, al correr este archivo (botón Run de PyCharm
# o "python mainv3.py" en la terminal). No usa navegador ni servidor.
#

import io
from contextlib import redirect_stdout
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk  # Importado para estructurar el espacio físico pedido


def _ejecutar_silencioso(func, *args, **kwargs):
    buf = io.StringIO()
    with redirect_stdout(buf):
        resultado = func(*args, **kwargs)
    return resultado, buf.getvalue().strip()


class AplicacionDisco:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Disco - BD2")
        self.disco = None
        self.db = None

        # --- 1. Crear disco ---
        frame_disco = tk.LabelFrame(root, text="1. Crear disco")
        frame_disco.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_disco, text="Platos (2^p):").grid(row=0, column=0, padx=3)
        self.entry_p = tk.Entry(frame_disco, width=4)
        self.entry_p.insert(0, "0")
        self.entry_p.grid(row=0, column=1)

        tk.Label(frame_disco, text="Pistas (2^t):").grid(row=0, column=2, padx=3)
        self.entry_t = tk.Entry(frame_disco, width=4)
        self.entry_t.insert(0, "0")
        self.entry_t.grid(row=0, column=3)

        tk.Label(frame_disco, text="Sectores (2^s):").grid(row=0, column=4, padx=3)
        self.entry_s = tk.Entry(frame_disco, width=4)
        self.entry_s.insert(0, "8")
        self.entry_s.grid(row=0, column=5)

        tk.Label(frame_disco, text="Bytes/sector (2^c):").grid(row=0, column=6, padx=3)
        self.entry_c = tk.Entry(frame_disco, width=4)
        self.entry_c.insert(0, "8")
        self.entry_c.grid(row=0, column=7)

        tk.Button(frame_disco, text="Crear disco", command=self.crear_disco).grid(row=0, column=8, padx=5)
        tk.Button(frame_disco, text="Destruir disco", command=self.destruir_disco).grid(row=0, column=9, padx=5)

        # --- 2. Cargar schema y datos ---
        frame_carga = tk.LabelFrame(root, text="2. Cargar schema y datos")
        frame_carga.pack(fill="x", padx=10, pady=5)

        tk.Button(frame_carga, text="Cargar schema (.txt)", command=self.cargar_schema).pack(side="left", padx=5,
                                                                                             pady=5)
        tk.Button(frame_carga, text="Cargar datos (.csv)", command=self.cargar_csv).pack(side="left", padx=5, pady=5)
        tk.Button(frame_carga, text="Ver registros", command=self.ver_registros).pack(side="left", padx=5, pady=5)

        # --- 3. Buscar ---
        frame_busq = tk.LabelFrame(root, text="3. Buscar")
        frame_busq.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_busq, text="Atributo:").grid(row=0, column=0, padx=3, sticky="e")
        self.entry_attr = tk.Entry(frame_busq, width=22)
        self.entry_attr.grid(row=0, column=1, padx=3)

        self.modo_busqueda = tk.StringVar(value="puntual")
        tk.Radiobutton(frame_busq, text="Puntual", variable=self.modo_busqueda, value="puntual").grid(row=0, column=2)
        tk.Radiobutton(frame_busq, text="Rango", variable=self.modo_busqueda, value="rango").grid(row=0, column=3)

        tk.Label(frame_busq, text="Valor / Mínimo:").grid(row=1, column=0, padx=3, sticky="e")
        self.entry_valor = tk.Entry(frame_busq, width=22)
        self.entry_valor.grid(row=1, column=1, padx=3)

        tk.Label(frame_busq, text="Máximo (si es rango):").grid(row=1, column=2, padx=3, sticky="e")
        self.entry_maximo = tk.Entry(frame_busq, width=22)
        self.entry_maximo.grid(row=1, column=3, padx=3)

        tk.Button(frame_busq, text="Buscar", command=self.buscar).grid(row=1, column=4, padx=5)

        # --- Salida de texto ---
        frame_salida = tk.LabelFrame(root, text="Resultado")
        frame_salida.pack(fill="both", expand=True, padx=10, pady=5)

        self.texto_salida = scrolledtext.ScrolledText(frame_salida, height=12)
        self.texto_salida.pack(fill="both", expand=True, padx=5, pady=5)

        # --- NUEVO ESPACIO PEDIDO: Ubicaciones en disco de los datos consultados ---
        frame_ubicaciones = tk.LabelFrame(frame_salida, text="Ubicación Física de Datos Consultados en Disco")
        frame_ubicaciones.pack(fill="x", side="bottom", padx=5, pady=5)

        columnas_tabla = ("registro", "plato", "superficie", "pista", "sector", "offset")
        self.tabla_direcciones = ttk.Treeview(frame_ubicaciones, columns=columnas_tabla, show="headings", height=5)
        self.tabla_direcciones.pack(fill="both", expand=True, padx=5, pady=5)

        self.tabla_direcciones.heading("registro", text="Registro")
        self.tabla_direcciones.heading("plato", text="Plato")
        self.tabla_direcciones.heading("superficie", text="Superficie")
        self.tabla_direcciones.heading("pista", text="Pista")
        self.tabla_direcciones.heading("sector", text="Sector")
        self.tabla_direcciones.heading("offset", text="Offset Interno")

        self.tabla_direcciones.column("registro", width=250, anchor="w")
        self.tabla_direcciones.column("plato", width=60, anchor="center")
        self.tabla_direcciones.column("superficie", width=80, anchor="center")
        self.tabla_direcciones.column("pista", width=60, anchor="center")
        self.tabla_direcciones.column("sector", width=60, anchor="center")
        self.tabla_direcciones.column("offset", width=90, anchor="center")

    # ------------------------------------------------------------------
    def log(self, texto):
        self.texto_salida.delete("1.0", tk.END)
        self.texto_salida.insert(tk.END, texto)

    def agregar_log(self, texto):
        self.texto_salida.insert(tk.END, texto)

    # ------------------------------------------------------------------
    def crear_disco(self):
        try:
            p = int(self.entry_p.get())
            t = int(self.entry_t.get())
            s = int(self.entry_s.get())
            c = int(self.entry_c.get())
        except ValueError:
            messagebox.showerror("Error", "Los valores de geometría deben ser números enteros.")
            return

        self.disco = DISK(p, t, s, c)
        _ejecutar_silencioso(self.disco.formateador)
        self.db = DatabaseManager(self.disco)
        _ejecutar_silencioso(self.db.inicializar_headers)
        self.log(
            f"Disco creado.\n"
            f"Capacidad total: {self.disco.capacidad_total():,} bytes\n"
            f"Sectores totales: {self.disco.get_total_sectores():,}\n"
        )
        for item in self.tabla_direcciones.get_children():
            self.tabla_direcciones.delete(item)

    def destruir_disco(self):
        if self.disco:
            self.disco.eliminar_disco()
            self.disco = None
            self.db = None
            self.log("Disco destruido.\n")
            for item in self.tabla_direcciones.get_children():
                self.tabla_direcciones.delete(item)
        else:
            messagebox.showinfo("Sin disco", "No hay ningún disco creado todavía.")

    def cargar_schema(self):
        if not self.db:
            messagebox.showwarning("Falta el disco", "Primero crea el disco.")
            return

        ruta = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
        if not ruta:
            return

        try:
            _ejecutar_silencioso(self.db.cargar_schema, ruta)
        except Exception as e:
            messagebox.showerror("Error al cargar schema", str(e))
            return

        texto = f"Schema cargado: {len(self.db.schema)} columnas.\n\n"
        for col in self.db.schema:
            texto += f"- {col['nombre']}: {col['tipo']} ({col['tamaño']} bytes)\n"
        self.log(texto)

    def cargar_csv(self):
        if not self.db or not self.db.schema:
            messagebox.showwarning("Falta el schema", "Primero carga el schema.")
            return

        ruta = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv")])
        if not ruta:
            return

        try:
            _, log = _ejecutar_silencioso(self.db.cargar_csv, ruta)
        except Exception as e:
            messagebox.showerror("Error al cargar CSV", str(e))
            return

        rechazadas = [l for l in log.splitlines() if "rechazada" in l]
        texto = f"Registros insertados: {self.db.cantidad_registros}\n"
        if rechazadas:
            texto += f"\nFilas rechazadas ({len(rechazadas)}):\n"
            texto += "\n".join(rechazadas)
        self.log(texto)

    def ver_registros(self):
        if not self.db or self.db.cantidad_registros == 0:
            messagebox.showinfo("Sin datos", "Todavía no hay registros cargados.")
            return

        registros, _ = _ejecutar_silencioso(self.db.leer_registros)
        texto = ""
        for i, r in enumerate(registros, 1):
            texto += f"{i}. {r}\n"
        self.log(texto)

    def buscar(self):
        if not self.db or not self.db.schema:
            messagebox.showwarning("Falta el schema", "Primero carga el schema y los datos.")
            return

        atributo = self.entry_attr.get().strip()
        if not atributo:
            messagebox.showwarning("Falta el atributo", "Escribe el nombre del atributo a buscar.")
            return

        # Limpiar tabla física previa antes de una nueva búsqueda
        for item in self.tabla_direcciones.get_children():
            self.tabla_direcciones.delete(item)

        if self.modo_busqueda.get() == "puntual":
            valor = self.entry_valor.get().strip()
            resultados, log = _ejecutar_silencioso(self.db.find, atributo, valor)
        else:
            minimo = self.entry_valor.get().strip()
            maximo = self.entry_maximo.get().strip()
            resultados, log = _ejecutar_silencioso(self.db.find_range, atributo, minimo, maximo)

        if not resultados:
            self.log(log if log else "Sin resultados.\n")
            return

        texto = f"{len(resultados)} resultado(s):\n\n"
        for r in resultados:
            texto += f"{r['datos']}\n   (sector {r['ubicacion_fisica']['sector']})\n\n"
            
            # Insertar dinámicamente las ubicaciones de hardware mapeadas en la nueva tabla dedicada
            self.tabla_direcciones.insert(
                "",
                "end",
                values=(
                    str(r['datos']),
                    r['ubicacion_fisica']['plato'],
                    r['ubicacion_fisica']['superficie'],
                    r['ubicacion_fisica']['pista'],
                    r['ubicacion_fisica']['sector'],
                    r['ubicacion_fisica']['offset_interno']
                )
            )
        self.log(texto)


def lanzar_interfaz():
    root = tk.Tk()
    AplicacionDisco(root)
    root.mainloop()


if __name__ == "__main__":
    lanzar_interfaz()
