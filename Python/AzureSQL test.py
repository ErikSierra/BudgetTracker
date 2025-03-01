import pyodbc

server = "sierra.database.windows.net"
database = "Sierra"
username = "CloudSA3e269270"
password = "BuildLegos77"
driver = "{ODBC Driver 17 for SQL Server}"

connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"

try:
    conn = pyodbc.connect(connection_string)
    print("Connection successful!")
except Exception as e:
    print("Error while connecting:", e)