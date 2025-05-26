const data = [
  {
    record_date: "2025-05-19",
    warehouse_name: "Warehouse A",
    source_name: "CCTV-1",
    shift_id: 1,
    shift_name: "Pagi",
    bag_type: "Bag",
    total_quantity: 11,
  },
  {
    record_date: "2025-05-19",
    warehouse_name: "Warehouse A",
    source_name: "CCTV-1",
    shift_id: 1,
    shift_name: "Pagi",
    bag_type: "Granul",
    total_quantity: 11,
  },
  {
    record_date: "2025-05-19",
    warehouse_name: "Warehouse A",
    source_name: "CCTV-2",
    shift_id: 1,
    shift_name: "Pagi",
    bag_type: "Bag",
    total_quantity: 13,
  },
  {
    record_date: "2025-05-19",
    warehouse_name: "Warehouse A",
    source_name: "CCTV-2",
    shift_id: 1,
    shift_name: "Pagi",
    bag_type: "Granul",
    total_quantity: 12,
  },
  {
    record_date: "2025-05-19",
    warehouse_name: "Warehouse A",
    source_name: "CCTV-2",
    shift_id: 1,
    shift_name: "Pagi",
    bag_type: "Subsidi",
    total_quantity: 1,
  },
  {
    record_date: "2025-05-19",
    warehouse_name: "Warehouse A",
    source_name: "CCTV-1",
    shift_id: 2,
    shift_name: "Siang",
    bag_type: "Bag",
    total_quantity: 9,
  },
  {
    record_date: "2025-05-19",
    warehouse_name: "Warehouse A",
    source_name: "CCTV-1",
    shift_id: 2,
    shift_name: "Siang",
    bag_type: "Granul",
    total_quantity: 9,
  },
  {
    record_date: "2025-05-19",
    warehouse_name: "Warehouse A",
    source_name: "CCTV-2",
    shift_id: 2,
    shift_name: "Siang",
    bag_type: "Bag",
    total_quantity: 7,
  },
  {
    record_date: "2025-05-19",
    warehouse_name: "Warehouse A",
    source_name: "CCTV-2",
    shift_id: 2,
    shift_name: "Siang",
    bag_type: "Granul",
    total_quantity: 7,
  },
  {
    record_date: "2025-05-19",
    warehouse_name: "Warehouse A",
    source_name: "CCTV-1",
    shift_id: 3,
    shift_name: "Malam",
    bag_type: "Bag",
    total_quantity: 9,
  },
  {
    record_date: "2025-05-19",
    warehouse_name: "Warehouse A",
    source_name: "CCTV-1",
    shift_id: 3,
    shift_name: "Malam",
    bag_type: "Granul",
    total_quantity: 9,
  },
  {
    record_date: "2025-05-19",
    warehouse_name: "Warehouse A",
    source_name: "CCTV-2",
    shift_id: 3,
    shift_name: "Malam",
    bag_type: "Bag",
    total_quantity: 10,
  },
  {
    record_date: "2025-05-19",
    warehouse_name: "Warehouse A",
    source_name: "CCTV-2",
    shift_id: 3,
    shift_name: "Malam",
    bag_type: "Granul",
    total_quantity: 10,
  },
  {
    record_date: "2025-05-20",
    warehouse_name: "Warehouse A",
    source_name: "CCTV-3",
    shift_id: 1,
    shift_name: "Pagi",
    bag_type: "Bag",
    total_quantity: 3,
  },
  {
    record_date: "2025-05-20",
    warehouse_name: "Warehouse A",
    source_name: "CCTV-3",
    shift_id: 1,
    shift_name: "Pagi",
    bag_type: "Granul",
    total_quantity: 3,
  },
  {
    record_date: "2025-05-21",
    warehouse_name: "Warehouse A",
    source_name: "CCTV-3",
    shift_id: 1,
    shift_name: "Pagi",
    bag_type: "Bag",
    total_quantity: 1,
  },
  {
    record_date: "2025-05-21",
    warehouse_name: "Warehouse A",
    source_name: "CCTV-3",
    shift_id: 1,
    shift_name: "Pagi",
    bag_type: "Granul",
    total_quantity: 1,
  },
];

const chartDataMap = {};

// Merubah Format Data
data.forEach((item) => {
  const shift = item.shift_name;
  const source = item.source_name.toLowerCase().replace(/\W+/g, "_"); // CCTV-1 → cctv_1
  const bagType = item.bag_type.toLowerCase(); // Bag → bag

  if (bagType === "bag") return; // Skip jenis "Bag" (sesuai logika kamu)

  const key = shift;
  if (!chartDataMap[key]) {
    chartDataMap[key] = { shift: shift };
  }

  const columnName = `${source}_total_${bagType}`;

  if (!chartDataMap[key][columnName]) {
    chartDataMap[key][columnName] = 0;
  }

  chartDataMap[key][columnName] += item.total_quantity;
});


// Ubah object jadi array
const chartDataFix = Object.values(chartDataMap);

console.log(chartDataFix)
