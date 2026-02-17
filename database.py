import pyodbc
import os

def get_connection():
    try:
        # En la nube, usamos variables de entorno por seguridad
        # Si estas local, puedes reemplazarlos por los datos de tu servidor remoto
        server = os.getenv('DB_SERVER', 'tu-servidor-remoto.database.windows.net')
        database = os.getenv('DB_NAME', 'PerfumeriaDB')
        username = os.getenv('DB_USER', 'tu_usuario')
        password = os.getenv('DB_PASSWORD', 'tu_password')
        
        conn_str = (
            f"Driver={{ODBC Driver 17 for SQL Server}};"
            f"Server={server};"
            f"Database={database};"
            f"Uid={username};"
            f"Pwd={password};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )
        
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None
