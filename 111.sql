-- Tạo cơ sở dữ liệu
CREATE DATABASE smartdoor;

-- Sử dụng cơ sở dữ liệu
USE smartdoor;

-- Tạo bảng user_iot
CREATE TABLE user_iot (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ten VARCHAR(100) NOT NULL,
    user VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Tạo bảng card_lock
CREATE TABLE card_lock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ten VARCHAR(100) NOT NULL,
    id_the VARCHAR(50) NOT NULL UNIQUE,
    ngaytao DATE NOT NULL
);

-- Tạo bảng action
CREATE TABLE action (
    id INT AUTO_INCREMENT PRIMARY KEY,
    card_number VARCHAR(255) NULL,  -- Số thẻ, có thể để NULL
    action_type ENUM('keypad', 'web', 'card', 'faceID') NOT NULL,  -- Kiểu hành động mở cửa
    status ENUM('success', 'failure') NOT NULL,           -- Trạng thái mở cửa
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP          -- Thời gian thực hiện hành động
);

USE smartdoor;
ALTER TABLE user_iot
ADD COLUMN passdoor VARCHAR(255) NOT NULL;
-- DELETE FROM user_iot WHERE id IN (1,2,3,4,5);
-- ALTER TABLE user_iot AUTO_INCREMENT = 1;
USE smartdoor;
INSERT INTO user_iot (ten, user, password,passdoor) VALUES
('Nguyễn Văn A', 'userA', '12345678','12345678');
