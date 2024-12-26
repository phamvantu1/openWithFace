-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th12 26, 2024 lúc 02:05 PM
-- Phiên bản máy phục vụ: 10.4.32-MariaDB
-- Phiên bản PHP: 8.0.30

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
(1, 'Pass', 'keypad', 'success', '2024-12-26 06:26:50', NULL, 'http://192.168.102.3:5000/getimages/20241226132650.jpg'),
(2, '206 1 165 29', 'card', 'success', '2024-12-26 06:27:47', 1, 'http://192.168.102.3:3000/images/1735194466404.jpg'),
(3, 'Pass', 'keypad', 'success', '2024-12-26 06:28:32', NULL, 'http://192.168.102.3:5000/getimages/20241226132832.jpg'),
(4, 'Emcjf', 'card', 'success', '2024-12-26 06:29:17', 1, 'http://192.168.102.3:3000/images/1735194557112.jpg'),
(5, 'openByAPP', 'web', 'success', '2024-12-26 06:29:59', NULL, 'http://192.168.102.3:5000/getimages/20241226132952.jpg'),
(6, 'openByAPP', 'web', 'success', '2024-12-26 06:30:29', NULL, 'http://192.168.102.3:5000/getimages/20241226133022.jpg'),
(7, 'openByAPP', 'web', 'success', '2024-12-26 06:31:06', NULL, 'http://192.168.102.3:5000/getimages/20241226133058.jpg'),
(8, 'Pass', 'keypad', 'success', '2024-12-26 08:52:32', NULL, 'http://192.168.102.3:5000/getimages/20241226155232.jpg'),
(9, 'Pass', 'keypad', 'success', '2024-12-26 08:52:52', NULL, 'http://192.168.102.3:5000/getimages/20241226155252.jpg'),
(10, 'Pass', 'keypad', 'success', '2024-12-26 08:55:47', NULL, NULL),
(11, 'Pass', 'keypad', 'success', '2024-12-26 08:57:21', NULL, 'http://192.168.102.3:5000/getimages/20241226155720.jpg'),
(12, '', '', 'failure', '2024-12-26 09:02:11', NULL, 'http://192.168.102.3:5000/getimages/20241226160211.jpg'),
(13, '', '', 'failure', '2024-12-26 09:02:23', NULL, 'http://192.168.102.3:5000/getimages/20241226160222.jpg'),
(14, '', '', 'failure', '2024-12-26 09:02:28', NULL, 'http://192.168.102.3:5000/getimages/20241226160227.jpg'),
(15, '', '', 'failure', '2024-12-26 09:03:12', NULL, 'http://192.168.102.3:5000/getimages/20241226160312.jpg'),
(16, '', '', 'failure', '2024-12-26 09:06:01', NULL, 'http://192.168.102.3:5000/getimages/20241226160601.jpg'),
(17, '', '', 'failure', '2024-12-26 09:06:20', NULL, 'http://192.168.102.3:5000/getimages/20241226160620.jpg'),
(18, '', '', 'failure', '2024-12-26 09:08:12', NULL, 'http://192.168.102.3:5000/getimages/20241226160812.jpg'),
(19, '', '', 'failure', '2024-12-26 09:09:08', NULL, 'http://192.168.102.3:5000/getimages/20241226160908.jpg'),
(20, '', '', 'failure', '2024-12-26 09:12:36', NULL, 'http://192.168.102.3:5000/getimages/20241226161236.jpg'),
(21, '', '', 'failure', '2024-12-26 09:19:49', NULL, 'http://192.168.102.3:5000/getimages/20241226161949.jpg'),
(22, '', '', 'failure', '2024-12-26 09:20:05', NULL, 'http://192.168.102.3:5000/getimages/20241226162004.jpg'),
(23, '', '', 'failure', '2024-12-26 09:20:50', NULL, 'http://192.168.102.3:5000/getimages/20241226162049.jpg'),
(24, '', '', 'failure', '2024-12-26 09:24:08', NULL, 'http://192.168.102.3:5000/getimages/20241226162408.jpg'),
(25, 'Pass', 'keypad', 'success', '2024-12-26 09:24:50', NULL, 'http://192.168.102.3:5000/getimages/20241226162450.jpg'),
(26, 'openByAPP', 'web', 'success', '2024-12-26 09:53:49', NULL, 'http://192.168.102.3:5000/getimages/20241226165349.jpg'),
(27, 'openByAPP', 'web', 'success', '2024-12-26 10:15:59', NULL, 'http://192.168.102.3:5000/getimages/20241226171558.jpg'),
(28, 'openByAPP', 'web', 'success', '2024-12-26 11:21:28', NULL, 'http://192.168.102.3:5000/getimages/20241226182126.jpg'),
(29, 'Pass', 'keypad', 'success', '2024-12-26 11:25:44', NULL, 'http://192.168.102.3:5000/getimages/20241226182544.jpg'),
(30, 'openByAPP', 'web', 'success', '2024-12-26 11:53:01', NULL, 'http://192.168.102.3:5000/getimages/20241226185259.jpg'),
(31, 'Pass', 'keypad', 'success', '2024-12-26 11:58:21', NULL, 'http://192.168.102.3:5000/getimages/20241226185821.jpg'),
(32, 'FAILURE', '', 'failure', '2024-12-26 11:58:52', NULL, 'http://192.168.102.3:5000/getimages/20241226185852.jpg'),
(33, 'Emcjf', 'card', 'success', '2024-12-26 12:06:21', 1, 'http://192.168.102.3:3000/images/1735214780955.jpg'),
(34, 'Emcjf', 'card', 'success', '2024-12-26 12:07:18', 1, 'http://192.168.102.3:3000/images/1735214838347.jpg');

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
(29, 'the2s', 'asdasddsf', '2024-12-16', 2),
(31, 'qwrq', '12321', '2024-12-24', 1),
(32, 'Emcjf', '206 1 165 29', '2024-12-26', 1),
(33, 'THE CUA TRUNG', '2031232', '2024-12-26', 1),
(34, 'ther cua hoa', '20312012', '2024-12-26', 24);

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
  `role` varchar(50) DEFAULT 'user',
  `email` varchar(255) DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `user_iot`
--

INSERT INTO `user_iot` (`id`, `ten`, `user`, `password`, `passdoor`, `role`, `email`, `phone_number`) VALUES
(1, 'trung1', 'A', '1', '12', 'admin', 'hoangviettrunghanam@gmail.com', '0888779837'),
(10, 'adsdasd', 'asdasd', '13123', '12313', 'user', NULL, NULL),
(11, '123123', '13122232', '111', '21212', 'user', NULL, NULL),
(12, '12312312', '12313', '1231232', '123123', 'user', NULL, NULL),
(13, 'Ha', 'Hhgugg', '123', '12', 'user', NULL, NULL),
(14, 'Ha', 'Hhgugg1', '123', '12', 'user', NULL, NULL),
(15, 'Ha', 'Hhgugg1l', '123', '12', 'user', NULL, NULL),
(16, 'Ha', 'Hhgugg1l6', '123', '12', 'user', NULL, NULL),
(17, 'Ha', 'Whdg', '123', '12', 'user', NULL, NULL),
(18, 'Ha', 'Whdgdhh', '123', '12', 'user', NULL, NULL),
(19, 'Wtdgx', 'Qttey', '152', '14526', 'user', NULL, NULL),
(21, '123123', '123123', '31231231', '122321', 'user', NULL, NULL),
(22, '2121212212122', '121212121212', '121212', '12121', 'user', NULL, NULL),
(24, 'huy hoa', 'hoa03', '1', '1', 'user', 'huyhoa03@gmail.com', '096191418232');

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=35;

--
-- AUTO_INCREMENT cho bảng `card_lock`
--
ALTER TABLE `card_lock`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=35;

--
-- AUTO_INCREMENT cho bảng `user_iot`
--
ALTER TABLE `user_iot`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
