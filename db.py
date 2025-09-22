import sqlite3

def init_db():
    conn = sqlite3.connect("contracts.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        summary TEXT,
        renewal_date TEXT,
        termination_date TEXT,
        risk_level TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Clauses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_id INTEGER,
        clause_type TEXT,
        text TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS RiskyTerms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_id INTEGER,
        text TEXT
    )
    """)
    conn.commit()
    conn.close()



def insert_contract(name, summary, renewal_date, termination_date, risk_level):
    conn = sqlite3.connect("contracts.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO Contracts (name, summary, renewal_date, termination_date, risk_level)
    VALUES (?, ?, ?, ?, ?)
    """, (name, summary, renewal_date, termination_date, risk_level))
    conn.commit()
    contract_id = cursor.lastrowid
    conn.close()
    return contract_id



def insert_clause(contract_id, clause_type, text):
    conn = sqlite3.connect("contracts.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO Clauses (contract_id, clause_type, text)
    VALUES (?, ?, ?)
    """, (contract_id, clause_type, text))
    conn.commit()
    conn.close()


def insert_risky_term(contract_id, term):
    conn = sqlite3.connect("contracts.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO RiskyTerms (contract_id, term)
    VALUES (?, ?)
    """, (contract_id, term))
    conn.commit()
    conn.close()
