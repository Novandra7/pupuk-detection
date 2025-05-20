import mysql.connector
from datetime import datetime
from datetime import timedelta


class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",  
            user="root",           
            password="",           
            database="pupuk_baru"
        )   
        self.cursor = self.conn.cursor()
        
    def read_records(self, id):
        self.cursor.execute("SELECT * FROM tr_fertilizer_records WHERE ms_cctv_sources_id = %s", (id,))
        columns = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    
    def read_temp_data_format(self):
        self.cursor.execute("SELECT * FROM tr_fertilizer_records LIMIT 0")
        columns = [desc[0] for desc in self.cursor.description if desc[0] != 'id']
        return {col: None for col in columns}
    
    def read_formatted_records(self, id_warehouse, id_shift=None):
        query = """
        SELECT
            DATE(r.timestamp) AS record_date, 
            w.warehouse_name,
            c.source_name,
            s.id AS shift_id,
            s.shift_name,
            b.bag_type,
            SUM(r.quantity) AS total_quantity
        FROM
            tr_fertilizer_records r
        INNER JOIN ms_shift s ON
            r.ms_shift_id = s.id
        INNER JOIN ms_cctv_sources c ON
            r.ms_cctv_sources_id = c.id
        INNER JOIN ms_bag b ON
            r.ms_bag_id = b.id
        INNER JOIN ms_warehouse w ON
            c.ms_warehouse_id = w.id
        WHERE
            w.id = %s
     
        """

        params = [id_warehouse]

        if id_shift is not None:
            query += " AND r.ms_shift_id = %s"
            params.append(id_shift)

        query += """
            GROUP BY
                DATE(r.timestamp),             
                w.warehouse_name,
                c.source_name,
                s.id,
                s.shift_name,
                b.bag_type
            ORDER BY
                record_date ASC,                 
                s.id ASC;
        """

        self.cursor.execute(query, params)
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
            cs.id = %s AND
            DATE(fr.datetime) = CURDATE()
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
   
    def read_bag(self):
        self.cursor.execute("SELECT * FROM ms_bag")
        columns = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def read_shift(self):
        self.cursor.execute("SELECT * FROM ms_shift WHERE is_active = 1")
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
        query = "INSERT INTO tr_fertilizer_records VALUES (NULL, %s, %s, %s, %s, %s);"
        self.cursor.execute(query, data)
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