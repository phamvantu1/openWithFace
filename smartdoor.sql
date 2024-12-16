-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th12 01, 2024 lúc 01:54 PM
-- Phiên bản máy phục vụ: 10.4.32-MariaDB
-- Phiên bản PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Cơ sở dữ liệu: `smartdoor`
--

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `action`
--

CREATE TABLE `action` (
  `id` int(11) NOT NULL,
  `card_number` varchar(255) DEFAULT NULL,
  `action_type` enum('keypad','web','card','faceID') NOT NULL,
  `status` enum('success','failure') NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `user_id` int(11) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `action`
--

INSERT INTO `action` (`id`, `card_number`, `action_type`, `status`, `timestamp`, `user_id`, `image`) VALUES
(11, 'trung', 'card', 'success', '2024-12-01 12:53:13', 1, NULL);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `card_lock`
--

CREATE TABLE `card_lock` (
  `id` int(11) NOT NULL,
  `ten` varchar(100) NOT NULL,
  `id_the` varchar(50) NOT NULL,
  `ngaytao` date NOT NULL,
  `user_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `card_lock`
--

INSERT INTO `card_lock` (`id`, `ten`, `id_the`, `ngaytao`, `user_id`) VALUES
(25, 'trung', '123', '2024-12-01', 1);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `user_iot`
--

CREATE TABLE `user_iot` (
  `id` int(11) NOT NULL,
  `ten` varchar(100) NOT NULL,
  `user` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `passdoor` varchar(255) NOT NULL,
  `role` varchar(50) DEFAULT 'user'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `user_iot`
--

INSERT INTO `user_iot` (`id`, `ten`, `user`, `password`, `passdoor`, `role`) VALUES
(1, 'Nguyễn Văn A', 'userA', '12345678', '12', 'user');

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `action`
--
ALTER TABLE `action`
  ADD PRIMARY KEY (`id`);

--
-- Chỉ mục cho bảng `card_lock`
--
ALTER TABLE `card_lock`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `id_the` (`id_the`);

--
-- Chỉ mục cho bảng `user_iot`
--
ALTER TABLE `user_iot`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user` (`user`);

--
-- AUTO_INCREMENT cho các bảng đã đổ
--

--
-- AUTO_INCREMENT cho bảng `action`
--
ALTER TABLE `action`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT cho bảng `card_lock`
--
ALTER TABLE `card_lock`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;

--
-- AUTO_INCREMENT cho bảng `user_iot`
--
ALTER TABLE `user_iot`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
