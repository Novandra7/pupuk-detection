import pyodbc
from datetime import time

class Database:
    def __init__(self):
        self.con = pyodbc.connect(
            'DRIVER={ODBC Driver 18 for SQL Server};'
            'SERVER=12.7.25.11;'
            'DATABASE=db_pklti;'
            'UID=pklti_u;'
            'PWD=K0neksi4man12!;'
            'TrustServerCertificate=yes;'
        )
        self.cursor = self.con.cursor()

    def read_records(self, id):
        self.cursor.execute("SELECT * FROM tr_fertilizer_records WHERE ms_cctv_sources_id = ?", id)
        columns = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def read_temp_data_format(self):
        self.cursor.execute("SELECT TOP 0 * FROM tr_fertilizer_records")
        columns = [desc[0] for desc in self.cursor.description if desc[0] != 'id']
        return {col: None for col in columns}

    def read_formatted_records(self, id_warehouse, date=None, name=None, shift=None, now=False):
        query = """
        SELECT
            CAST(r.timestamp AS DATE) AS record_date, 
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
            w.id = ?
        """

        params = [id_warehouse]

        if now:
            query += " AND CAST(r.timestamp AS DATE) = CAST(GETDATE() AS DATE)"
        if date is not None:
            query += " AND CAST(r.timestamp AS DATE) = ?"
            params.append(date)
        if name is not None:
            query += " AND c.source_name = ?"
            params.append(name)
        if shift is not None:
            query += " AND s.shift_name = ?"
            params.append(shift)

        query += """
            GROUP BY
                CAST(r.timestamp AS DATE),
                w.warehouse_name,
                c.source_name,
                s.id,
                s.shift_name,
                b.bag_type
            ORDER BY
                record_date ASC,
                s.id ASC;
        """

        self.cursor.execute(query, tuple(params))
        columns = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def read_cctv_sources(self):
        self.cursor.execute("SELECT * FROM ms_cctv_sources")
        columns = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def read_cctv_sources_by_warehouse_id(self, id):
        self.cursor.execute("SELECT * FROM ms_cctv_sources WHERE ms_warehouse_id = ?", id)
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
            if isinstance(data["start_time"], time):
                data["start_time"] = data["start_time"].strftime("%H:%M:%S")
            if isinstance(data["end_time"], time):
                data["end_time"] = data["end_time"].strftime("%H:%M:%S")
            new_data.append(data)
        return new_data

    def write_record(self, data: tuple):
        query = """
        INSERT INTO tr_fertilizer_records (ms_shift_id, ms_cctv_sources_id, ms_bag_id, quantity, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, data)
        self.conn.commit()
        if self.cursor.rowcount > 0:
            return True
        else:
            return "failed to insert data"

    def close_connection(self):
        self.cursor.close()
        self.conn.close()