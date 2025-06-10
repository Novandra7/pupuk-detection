from datetime import datetime, timedelta
import random

# Parameter awal
start_time = datetime(2025, 5, 21, 8, 0, 0)
num_days = 1
entries_per_day = 10
cctv_sources = [1, 2, 3]
shift_ids = [1, 2, 3]
bag_ids = {"bag": 2, "granull": 3, "subsidi": 4}

lines = []

for day in range(num_days):
    base_time = start_time + timedelta(days=day)
    for i in range(entries_per_day):
        ms_cctv_sources_id = random.choice(cctv_sources)
        ms_shift_id = random.choice(shift_ids)
        timestamp = base_time + timedelta(minutes=i * 60)

        pupuk_list = ["granull", "subsidi", "bag"]
        random.shuffle(pupuk_list) 

        for pupuk in pupuk_list:
            if random.random() < 0.8:
                ms_bag_id = bag_ids[pupuk]
                sql = (
                    f"INSERT INTO tr_fertilizer_records (ms_cctv_sources_id, ms_shift_id, ms_bag_id, quantity, timestamp) "
                    f"VALUES ({ms_cctv_sources_id}, {ms_shift_id}, {ms_bag_id}, 1, '{timestamp.strftime('%Y-%m-%d %H:%M:%S')}');"
                )
                lines.append(sql)

# Simpan sebagai file SQL
with open("insert_dummy_data_varied_days.sql", "a") as f:
    f.write("\n".join(lines))

print("File insert_dummy_data_varied_days.sql berhasil dibuat.")
