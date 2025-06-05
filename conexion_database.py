import pyodbc

def get_connection():
    server = r'CARLOS\SQLEXPRES'# JHOSEP\MSSQLSERVER01  PARZIVAL\SQLEXPRESS01  PC-DAVID  CARLOS\SQLEXPRES
    database = 'bd_corcho'
    driver = '{ODBC Driver 17 for SQL Server}'
    conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    return pyodbc.connect(conn_str)
