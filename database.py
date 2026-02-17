import pyodbc

def get_connection():
    try:
        # Configuración basada en tu instancia: DESKTOP-BOI3R9R\MSSQLSERVER01
        conn = pyodbc.connect(
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=DESKTOP-BOI3R9R\\MSSQLSERVER01;"
            "Database=PerfumeriaDB;"
            "Trusted_Connection=yes;"
        )
        return conn
    except Exception as e:
        print(f"Error de conexión a SQL Server: {e}")
        return None