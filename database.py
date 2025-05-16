import mysql.connector
from datetime import datetime
from datetime import timedelta


class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",  
            user="root",           
            password="",           
            database="fertilizer_db"
        )   
        self.cursor = self.conn.cursor()
        
    def read_records(self, id):
        self.cursor.execute("SELECT * FROM tr_fertilizer_records WHERE ms_cctv_sources_id = %s", (id,))
        columns = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    
    def read_formatted_records(self, id):
        query = """
            SELECT
                w.id AS warehouse_id,
                w.warehouse_name,
                c.id AS cctv_id,
                c.source_name,
                r.ms_shift_id,
                s.shift_name AS shift_name,
                SUM(r.bag) AS total_bag,
                SUM(r.granul) AS total_granul,
                SUM(r.subsidi) AS total_subsidi,
                SUM(r.prill) AS total_prill,
                MIN(r.datetime) AS start_time,
                MAX(r.datetime) AS end_time
            FROM
                ms_warehouse w
            JOIN ms_cctv_sources c ON
                c.ms_warehouse_id = w.id
            LEFT JOIN tr_fertilizer_records r ON
                r.ms_cctv_sources_id = c.id
            LEFT JOIN ms_shift s ON
                r.ms_shift_id = s.id
            WHERE
                w.id = %s
            GROUP BY
                w.id,
                w.warehouse_name,
                c.id,
                c.source_name,
                r.ms_shift_id,
                s.shift_name
            ORDER BY
                c.id ASC,
                r.ms_shift_id ASC;
        """
        self.cursor.execute(query, (id,))
        columns = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def read_curdate_records(self,id):
        query = """
        SELECT
            fr.ms_shift_id,
            s.shift_name,
            SUM(fr.bag) AS total_bag,
            SUM(fr.granul) AS total_granul,
            SUM(fr.subsidi) AS total_subsidi,
            SUM(fr.prill) AS total_prill
        FROM
            tr_fertilizer_records fr
        JOIN ms_cctv_sources cs ON
            fr.ms_cctv_sources_id = cs.id
        JOIN ms_shift s ON
            fr.ms_shift_id = s.id
        WHERE
            cs.id = %s
        GROUP BY
            fr.ms_shift_id, s.shift_name;                           
        """
        self.cursor.execute(query,(id,))
        columns = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def read_cctv_sources(self):
        self.cursor.execute("SELECT * FROM ms_cctv_sources")
        columns = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
   
    def read_cctv_sources_by_warehouse_id(self,id):
        self.cursor.execute("SELECT * FROM ms_cctv_sources WHERE ms_warehouse_id = %s", (id,))
        columns = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def read_warehouse(self):
        self.cursor.execute("SELECT * FROM ms_warehouse")
        columns = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def read_shift(self):
        self.cursor.execute("SELECT * FROM ms_shift")
        columns = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        new_data = []
        for data in [dict(zip(columns, row)) for row in rows]:
            if isinstance(data["start_time"], timedelta):
                data["start_time"] = str(data["start_time"])
            if isinstance(data["end_time"], timedelta):
                data["end_time"] = str(data["end_time"])
            new_data.append(data)
        return new_data
    
    def write_record(self, data:tuple):
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = "INSERT INTO tr_fertilizer_records VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, NULL);"
        self.cursor.execute(query, data + (time,))
        self.conn.commit()
        if self.cursor.rowcount > 0:
            return True
        else:
            return "failed to insert data"
    
    def get_column_names(self):
        self.cursor.execute("SHOW COLUMNS FROM tr_fertilizer_records")
        return [column[0] for column in self.cursor.fetchall()]

    def close_connection(self):
        self.cursor.close()
        self.conn.close()