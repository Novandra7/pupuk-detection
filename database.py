import mysql.connector
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",  
            user="root",           
            password="",           
            database="data_pupuk"
        )   
        self.cursor = self.conn.cursor()
        
    def read_data(self):
        self.cursor.execute("SELECT * FROM pupuk")
        return self.cursor.fetchall()
    
    def write_data(self, data:tuple):
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = "INSERT INTO pupuk VALUES (NULL, %s, %s, %s, %s);"
        self.cursor.execute(query, data + (time,))
        self.conn.commit()
        if self.cursor.rowcount > 0:
            return True
        else:
            return "failed to insert data"

    def close_connection(self):
        self.cursor.close()
        self.conn.close()