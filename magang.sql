CREATE TABLE `ms_cctv_sources` (
  `id` integer PRIMARY KEY,
  `ms_warehouse_id` integer,
  `source_name` varchar(255),
  `url_streaming` varchar(255),
  `endpoint` varchar(255),
  `delete_status` boolean
);

CREATE TABLE `ms_warehouse` (
  `id` integer PRIMARY KEY,
  `warehouse_name` varchar(255),
  `delete_status` boolean
);

CREATE TABLE `ms_shift` (
  `id` integer PRIMARY KEY,
  `shift_name` varchar(255),
  `start_time` datetime,
  `end_time` datetime
);

CREATE TABLE `tr_fertilizer_records` (
  `id` integer PRIMARY KEY,
  `ms_cctv_sources_id` integer,
  `ms_shift_id` integer,
  `bag` integer,
  `granul` integer,
  `subsidi` integer,
  `prill` integer,
  `datetime` timestamp,
  `delete_status` boolean
);

ALTER TABLE `tr_fertilizer_records` ADD FOREIGN KEY (`ms_cctv_sources_id`) REFERENCES `ms_cctv_sources` (`id`);

ALTER TABLE `ms_cctv_sources` ADD FOREIGN KEY (`ms_warehouse_id`) REFERENCES `ms_warehouse` (`id`);

ALTER TABLE `tr_fertilizer_records` ADD FOREIGN KEY (`ms_shift_id`) REFERENCES `ms_shift` (`id`);

INSERT INTO `ms_warehouse` (`id`, `warehouse_name`, `delete_status`) VALUES
(1, 'Warehouse A', 0),
(2, 'Warehouse B', 0),
(3, 'Warehouse C', 0);

INSERT INTO `ms_shift` (`id`, `shift_name`, `start_time`, `end_time`) VALUES
(1, 'Pagi', '2025-04-23 00:00:00', '2025-04-23 08:00:00'),
(2, 'Siang', '2025-04-23 08:00:00', '2025-04-23 16:00:00'),
(3, 'Malam', '2025-04-23 16:00:00', '2025-04-24 00:00:00');

INSERT INTO `ms_cctv_sources` (`id`,`ms_warehouse_id`,`source_name`, `url_streaming`, `endpoint`,`delete_status`) VALUES
(1, 1, 'CCTV 1', 'rtsp://pkl:futureisours2025@36.37.123.19:554/Streaming/Channels/101/', 'Kamera1', 0),
(2, 2, 'CCTV 2', 'rtsp://vendor:Bontangpkt2025@36.37.123.10:554/Streaming/Channels/101/', 'Kamera2', 0),
(3, 3, 'CCTV 3', '', 'video',0);

INSERT INTO `tr_fertilizer_records` (`id`, `ms_cctv_sources_id`,`ms_shift_id`, `bag`, `granul`, `subsidi`, `prill`, `datetime`) VALUES
(1, 1, 1, 300, 100, 200, 150, '2025-04-23 00:00:00'),
(2, 1, 1, 310, 120, 210, 145, '2025-04-23 01:00:00'),
(3, 1, 1, 305, 90, 195, 160, '2025-04-23 02:00:00'),
(4, 1, 1, 315, 110, 220, 155, '2025-04-23 03:00:00'),
(5, 1, 1, 290, 95, 200, 140, '2025-04-23 04:00:00'),
(6, 2, 1, 250, 80, 160, 120, '2025-04-23 00:00:00'),
(7, 2, 1, 260, 90, 170, 130, '2025-04-23 01:00:00'),
(8, 2, 1, 270, 100, 180, 140, '2025-04-23 02:00:00'),
(9, 2, 1, 280, 110, 190, 150, '2025-04-23 03:00:00'),
(10, 2, 2, 290, 120, 200, 160, '2025-04-23 04:00:00'),
(11, 3, 2, 220, 70, 140, 110, '2025-04-23 00:00:00'),
(12, 3, 2, 220, 70, 140, 110, '2025-04-23 01:00:00'),
(13, 3, 2, 220, 70, 140, 110, '2025-04-23 02:00:00'),
(14, 3, 2, 220, 70, 140, 110, '2025-04-23 03:00:00'),
(15, 3, 2, 220, 70, 140, 110, '2025-04-23 04:00:00'),
(16, 1, 3, 295, 105, 215, 150, '2025-04-23 05:00:00'),
(17, 1, 3, 285, 85, 205, 135, '2025-04-23 06:00:00'),
(18, 2, 3, 300, 130, 210, 170, '2025-04-23 05:00:00'),
(19, 2, 3, 310, 140, 220, 180, '2025-04-23 06:00:00'),
(20, 3, 3, 220, 70, 140, 110, '2025-04-23 05:00:00');
