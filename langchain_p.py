import sqlite3
import os
from langchain_openai import OpenAI, ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent

#os.environ["OPENAI_API_KEY"] = ""

def setup_database():
    conn = sqlite3.connect("autos.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS autos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT NOT NULL,
            modelo TEXT NOT NULL,
            año INTEGER NOT NULL,
            cilindrada REAL NOT NULL,
            precio REAL NOT NULL,
            combustible TEXT NOT NULL,
            transmisión TEXT NOT NULL,
            color TEXT,
            kilometraje REAL,
            puertas INTEGER,
            carrocería TEXT,
            UNIQUE(marca, modelo, año, cilindrada, precio)
        )
    ''')
    conn.commit()
    return conn

def insert_auto(conn, marca, modelo, año, cilindrada, precio, combustible, transmisión, color, kilometraje, puertas, carrocería):
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO autos (marca, modelo, año, cilindrada, precio, combustible, transmisión, color, kilometraje, puertas, carrocería)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (marca, modelo, año, cilindrada, precio, combustible, transmisión, color, kilometraje, puertas, carrocería))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"El auto {marca} {modelo} del año {año} ya existe en la base de datos.")

def populate_database(conn):
    autos = [
        ("Toyota", "Corolla", 2020, 1.8, 20000, "Gasolina", "Automática", "Blanco", 15000, 4, "Sedán"),
        ("Toyota", "Camry", 2021, 2.5, 28000, "Gasolina", "Automática", "Negro", 12000, 4, "Sedán"),
        ("Toyota", "RAV4", 2022, 2.5, 32000, "Híbrido", "Automática", "Rojo", 8000, 5, "SUV"),
        ("Ford", "Fiesta", 2019, 1.6, 13000, "Gasolina", "Manual", "Azul", 30000, 4, "Hatchback"),
        ("Ford", "Focus", 2020, 2.0, 25000, "Gasolina", "Automática", "Gris", 10000, 4, "Sedán"),
        ("Ford", "Explorer", 2021, 3.5, 40000, "Gasolina", "Automática", "Blanco", 15000, 5, "SUV"),
        ("Chevrolet", "Cruze", 2021, 1.4, 22000, "Diésel", "Automática", "Negro", 5000, 4, "Sedán"),
        ("Chevrolet", "Equinox", 2022, 2.0, 35000, "Gasolina", "Automática", "Azul", 9000, 5, "SUV"),
        ("Chevrolet", "Malibu", 2020, 1.5, 24000, "Gasolina", "Automática", "Rojo", 8000, 4, "Sedán"),
        ("Honda", "Civic", 2022, 2.0, 25000, "Híbrido", "Automática", "Rojo", 10000, 4, "Sedán"),
        ("Honda", "Accord", 2021, 2.0, 30000, "Híbrido", "Automática", "Negro", 11000, 4, "Sedán"),
        ("Honda", "CR-V", 2023, 1.5, 34000, "Híbrido", "Automática", "Blanco", 5000, 5, "SUV"),
        ("Tesla", "Model 3", 2023, 0.0, 35000, "Eléctrico", "Automática", "Gris", 500, 4, "Sedán"),
        ("Tesla", "Model S", 2022, 0.0, 80000, "Eléctrico", "Automática", "Negro", 7000, 4, "Sedán"),
        ("Tesla", "Model X", 2021, 0.0, 90000, "Eléctrico", "Automática", "Blanco", 10000, 5, "SUV"),
        ("BMW", "Series 3", 2020, 2.0, 45000, "Gasolina", "Automática", "Azul", 20000, 4, "Sedán"),
        ("BMW", "X5", 2021, 3.0, 60000, "Diésel", "Automática", "Negro", 15000, 5, "SUV"),
        ("BMW", "i3", 2019, 0.0, 40000, "Eléctrico", "Automática", "Blanco", 20000, 4, "Hatchback"),
        ("Mercedes", "A-Class", 2021, 1.4, 35000, "Gasolina", "Automática", "Gris", 12000, 4, "Sedán"),
        ("Mercedes", "GLE", 2022, 3.0, 70000, "Diésel", "Automática", "Negro", 5000, 5, "SUV"),
        ("Audi", "A4", 2020, 2.0, 45000, "Gasolina", "Automática", "Azul", 18000, 4, "Sedán"),
        ("Audi", "Q5", 2021, 2.0, 55000, "Gasolina", "Automática", "Rojo", 14000, 5, "SUV"),
        ("Volkswagen", "Golf", 2020, 1.4, 25000, "Gasolina", "Manual", "Blanco", 25000, 4, "Hatchback"),
        ("Volkswagen", "Tiguan", 2021, 2.0, 35000, "Gasolina", "Automática", "Gris", 8000, 5, "SUV"),
        ("Hyundai", "Elantra", 2020, 1.8, 20000, "Gasolina", "Automática", "Negro", 20000, 4, "Sedán"),
        ("Hyundai", "Tucson", 2022, 2.0, 30000, "Gasolina", "Automática", "Rojo", 6000, 5, "SUV"),
        ("Hyundai", "Kona", 2021, 1.6, 28000, "Híbrido", "Automática", "Azul", 10000, 4, "SUV"),
        ("Kia", "Rio", 2020, 1.4, 18000, "Gasolina", "Manual", "Blanco", 30000, 4, "Hatchback"),
        ("Kia", "Sportage", 2022, 2.0, 35000, "Gasolina", "Automática", "Gris", 12000, 5, "SUV"),
        ("Kia", "Sorento", 2021, 3.0, 40000, "Diésel", "Automática", "Negro", 15000, 5, "SUV"),
        ("Nissan", "Sentra", 2020, 1.6, 22000, "Gasolina", "Automática", "Azul", 15000, 4, "Sedán"),
        ("Nissan", "X-Trail", 2021, 2.5, 30000, "Gasolina", "Automática", "Blanco", 10000, 5, "SUV"),
        ("Nissan", "Leaf", 2023, 0.0, 40000, "Eléctrico", "Automática", "Verde", 5000, 4, "Hatchback"),
        ("Mazda", "3", 2020, 2.0, 25000, "Gasolina", "Manual", "Rojo", 20000, 4, "Sedán"),
        ("Mazda", "CX-5", 2021, 2.5, 35000, "Gasolina", "Automática", "Azul", 12000, 5, "SUV"),
        ("Mazda", "MX-5", 2022, 2.0, 30000, "Gasolina", "Manual", "Blanco", 5000, 2, "Convertible"),
        ("Jeep", "Wrangler", 2021, 3.6, 45000, "Gasolina", "Manual", "Verde", 8000, 5, "SUV"),
        ("Jeep", "Cherokee", 2020, 3.2, 40000, "Gasolina", "Automática", "Negro", 15000, 5, "SUV"),
        ("Jeep", "Compass", 2023, 2.0, 35000, "Gasolina", "Automática", "Gris", 3000, 5, "SUV"),
        ("Subaru", "Impreza", 2020, 2.0, 25000, "Gasolina", "Manual", "Azul", 18000, 4, "Sedán"),
        ("Subaru", "Outback", 2021, 2.5, 35000, "Gasolina", "Automática", "Rojo", 10000, 5, "SUV"),
        ("Subaru", "Forester", 2022, 2.5, 36000, "Gasolina", "Automática", "Blanco", 8000, 5, "SUV"),
        ("Fiat", "500", 2020, 1.2, 18000, "Gasolina", "Manual", "Amarillo", 25000, 2, "Hatchback"),
        ("Fiat", "Punto", 2021, 1.4, 20000, "Gasolina", "Manual", "Azul", 15000, 4, "Hatchback"),
        ("Renault", "Clio", 2020, 1.6, 22000, "Gasolina", "Manual", "Rojo", 18000, 4, "Hatchback"),
        ("Renault", "Duster", 2022, 2.0, 32000, "Gasolina", "Automática", "Gris", 7000, 5, "SUV"),
        ("Peugeot", "208", 2021, 1.6, 23000, "Gasolina", "Manual", "Blanco", 12000, 4, "Hatchback"),
        ("Peugeot", "3008", 2022, 1.6, 37000, "Híbrido", "Automática", "Negro", 5000, 5, "SUV"),
        ("Citroën", "C3", 2020, 1.2, 21000, "Gasolina", "Manual", "Verde", 17000, 4, "Hatchback"),
        ("Citroën", "C5 Aircross", 2021, 1.6, 35000, "Híbrido", "Automática", "Azul", 8000, 5, "SUV"),
        ("Volvo", "XC60", 2022, 2.0, 55000, "Híbrido", "Automática", "Blanco", 5000, 5, "SUV"),
        ("Volvo", "S60", 2021, 2.0, 48000, "Gasolina", "Automática", "Negro", 10000, 4, "Sedán"),
        ("Volvo", "V40", 2020, 1.5, 38000, "Gasolina", "Automática", "Gris", 12000, 4, "Hatchback"),
        ("Lexus", "RX", 2023, 3.5, 70000, "Híbrido", "Automática", "Negro", 2000, 5, "SUV"),
        ("Lexus", "NX", 2021, 2.5, 60000, "Híbrido", "Automática", "Blanco", 9000, 5, "SUV"),
        ("Alfa Romeo", "Giulia", 2020, 2.0, 50000, "Gasolina", "Automática", "Rojo", 15000, 4, "Sedán"),
        ("Alfa Romeo", "Stelvio", 2021, 2.2, 55000, "Diésel", "Automática", "Gris", 10000, 5, "SUV"),
        ("Jaguar", "XE", 2022, 2.0, 60000, "Gasolina", "Automática", "Negro", 4000, 4, "Sedán"),
        ("Jaguar", "F-Pace", 2023, 3.0, 70000, "Diésel", "Automática", "Blanco", 3000, 5, "SUV"),
        ("Porsche", "Macan", 2021, 2.0, 80000, "Gasolina", "Automática", "Gris", 5000, 5, "SUV"),
        ("Porsche", "Cayenne", 2022, 3.0, 95000, "Gasolina", "Automática", "Negro", 3000, 5, "SUV"),
        ("Porsche", "911", 2023, 3.8, 120000, "Gasolina", "Automática", "Rojo", 1000, 2, "Deportivo"),
    ]

    for auto in autos:
        insert_auto(conn, *auto)

def setup_agent():
    db = SQLDatabase.from_uri("sqlite:///autos.db")
    llm = ChatOpenAI(model="gpt-4o-mini")

    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    tools = toolkit.get_tools()

    SQL_PREFIX = """You are an agent designed to interact with a SQL database.
    Given an input question, create a syntactically correct SQLite query to run, then look at the results of the query and return the answer.
    Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
    You can order the results by a relevant column to return the most interesting examples in the database.
    Never query for all the columns from a specific table, only ask for the relevant columns given the question.
    You have access to tools for interacting with the database.
    Only use the given tools. Only use the information returned by the tools to construct your final answer.
    You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.
    """

    system_message = SystemMessage(content=SQL_PREFIX)
    agent = create_react_agent(llm, tools, messages_modifier=system_message)
    return agent

def ask_about_cars(agent, question):
    for response in agent.stream({"messages": [HumanMessage(content=question)]}):
        print(response)

if __name__ == "__main__":
    while True:
        conn = setup_database()
        populate_database(conn)

        agent = setup_agent()

        consulta = input('Haga su consulta: ')

        ask_about_cars(agent, consulta)
