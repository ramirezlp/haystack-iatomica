import sqlite3
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import FARMReader, BM25Retriever
from haystack.pipelines import ExtractiveQAPipeline
import json
import time

def create_auto_db():
    print("[INFO] Creando base de datos y tabla de autos...")
    conn = sqlite3.connect('autos.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS autos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT,
            modelo TEXT,
            año INTEGER,
            precio REAL,
            motor TEXT,
            tipo_combustible TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("[INFO] Base de datos creada con éxito.")

def insert_auto_examples():
    print("[INFO] Insertando autos de ejemplo en la base de datos...")
    conn = sqlite3.connect('autos.db')
    cursor = conn.cursor()

    autos_data = [
        ('Toyota', 'Corolla', 2020, 15000, '1.8L', 'Gasolina'),
        ('Ford', 'Mustang', 2021, 30000, '5.0L', 'Gasolina'),
        ('Tesla', 'Model 3', 2021, 40000, 'Eléctrico', 'Eléctrico'),
        ('Honda', 'Civic', 2019, 18000, '2.0L', 'Gasolina'),
        ('BMW', 'Serie 3', 2020, 35000, '2.0L', 'Gasolina'),
        ('Chevrolet', 'Camaro', 2021, 32000, '6.2L', 'Gasolina'),
        ('Nissan', 'Leaf', 2020, 28000, 'Eléctrico', 'Eléctrico'),
        ('Audi', 'A4', 2020, 34000, '2.0L', 'Gasolina'),
        ('Mercedes-Benz', 'Clase C', 2021, 37000, '2.0L', 'Gasolina'),
        ('Hyundai', 'Elantra', 2020, 19000, '2.0L', 'Gasolina'),
        ('Volkswagen', 'Golf', 2020, 22000, '1.4L', 'Gasolina'),
        ('Mazda', 'Mazda3', 2021, 21000, '2.5L', 'Gasolina'),
        ('Kia', 'Forte', 2020, 17000, '2.0L', 'Gasolina'),
        ('Subaru', 'Impreza', 2020, 20000, '2.0L', 'Gasolina'),
        ('Volvo', 'S60', 2021, 36000, '2.0L', 'Gasolina'),
        ('Lexus', 'IS', 2021, 38000, '2.0L', 'Gasolina'),
        ('Jaguar', 'XE', 2020, 39000, '2.0L', 'Gasolina'),
        ('Porsche', 'Cayman', 2021, 60000, '2.0L', 'Gasolina'),
        ('Ferrari', '488', 2021, 250000, '3.9L', 'Gasolina'),
        ('Lamborghini', 'Huracan', 2021, 300000, '5.2L', 'Gasolina'),
    ]

    cursor.executemany('''
        INSERT INTO autos (marca, modelo, año, precio, motor, tipo_combustible) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', autos_data)

    conn.commit()
    conn.close()
    print("[INFO] Autos insertados con éxito.")

def get_auto_data():
    print("[INFO] Obteniendo datos de autos de la base de datos...")
    conn = sqlite3.connect('autos.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM autos")
    autos = cursor.fetchall()
    conn.close()

    documents = []
    for auto in autos:
        doc = {
            "content": f"El {auto[1]} {auto[2]} es un auto del año {auto[3]} con un motor de {auto[5]} y cuesta {auto[4]} USD. Funciona con {auto[6]}.",
            "meta": {
                "marca": auto[1],
                "modelo": auto[2],
                "año": auto[3],
                "precio": auto[4],
                "motor": auto[5],
                "tipo_combustible": auto[6]
            }
        }
        documents.append(doc)
    
    print(f"[INFO] {len(documents)} autos cargados en memoria.")
    return documents

def run_haystack():
    create_auto_db()
    insert_auto_examples()

    print("[INFO] Iniciando el document store con BM25 activado...")
    document_store = InMemoryDocumentStore(use_bm25=True)

    docs = get_auto_data()

    print("[INFO] Indexando documentos en el store...")
    document_store.write_documents(docs)
    print("[INFO] Documentos indexados con éxito.")

    print("[INFO] Configurando el retriever y el reader...")
    retriever = BM25Retriever(document_store=document_store)
    reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2")
    pipe = ExtractiveQAPipeline(reader, retriever)

    print("[INFO] Haciendo consulta: '¿Cuál es el auto más barato?'...")
    query = "¿Cuál es el auto más barato?"
    result = pipe.run(query=query, params={"Retriever": {"top_k": 10}, "Reader": {"top_k": 1}})

    print("Respuesta:", result["answers"][0].answer)
    print("[INFO] Proceso completado.")

run_haystack()
