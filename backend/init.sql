-- 书驿云桥数据库初始化脚本

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS book_bridge CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE book_bridge;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 图书表
CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(100) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    category VARCHAR(50),
    publisher VARCHAR(100),
    publish_date DATE,
    description TEXT,
    cover_image VARCHAR(255),
    status ENUM('available', 'borrowed', 'reserved') DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    order_type ENUM('borrow', 'return', 'donate'),
    status ENUM('pending', 'approved', 'rejected', 'completed'),
    borrow_date DATE,
    return_date DATE,
    actual_return_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- 碳积分表
CREATE TABLE IF NOT EXISTS carbon_points (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    points INT NOT NULL,
    type ENUM('earn', 'spend'),
    reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 配送表
CREATE TABLE IF NOT EXISTS delivery (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    delivery_status ENUM('pending', 'processing', 'delivered'),
    tracking_number VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);

-- 慈善表
CREATE TABLE IF NOT EXISTS charity (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    target_amount DECIMAL(10, 2),
    current_amount DECIMAL(10, 2) DEFAULT 0,
    start_date DATE,
    end_date DATE,
    status ENUM('active', 'completed', 'cancelled'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 学习笔记表
CREATE TABLE IF NOT EXISTS study_notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- 支持表
CREATE TABLE IF NOT EXISTS support (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type ENUM('feedback', 'suggestion', 'bug'),
    content TEXT,
    status ENUM('pending', 'processing', 'resolved'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_books_status ON books(status);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_book_id ON orders(book_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_carbon_points_user_id ON carbon_points(user_id);
CREATE INDEX idx_delivery_order_id ON delivery(order_id);
CREATE INDEX idx_study_notes_user_id ON study_notes(user_id);
CREATE INDEX idx_study_notes_book_id ON study_notes(book_id);
CREATE INDEX idx_support_user_id ON support(user_id);
CREATE INDEX idx_support_status ON support(status);

-- 插入默认数据
-- 插入默认用户
INSERT IGNORE INTO users (username, email, password, role) VALUES
('admin', 'admin@bookbridge.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'admin'), -- 密码: admin123
('user', 'user@bookbridge.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'user'); -- 密码: user123

-- 插入默认图书
INSERT IGNORE INTO books (title, author, isbn, category, publisher, publish_date, description, status) VALUES
('Python编程从入门到实践', 'Eric Matthes', '9787115428028', '编程', '人民邮电出版社', '2016-12-01', 'Python入门经典书籍', 'available'),
('Java核心技术', 'Cay S. Horstmann', '9787111641247', '编程', '机械工业出版社', '2019-01-01', 'Java核心技术书籍', 'available'),
('数据结构与算法分析', 'Mark Allen Weiss', '9787302437370', '编程', '清华大学出版社', '2014-01-01', '数据结构与算法经典书籍', 'available'),
('计算机网络', 'Andrew S. Tanenbaum', '9787111526963', '网络', '机械工业出版社', '2017-01-01', '计算机网络经典书籍', 'available'),
('操作系统概念', 'Abraham Silberschatz', '9787111544212', '操作系统', '机械工业出版社', '2017-01-01', '操作系统经典书籍', 'available');

-- 插入默认慈善项目
INSERT IGNORE INTO charity (name, description, target_amount, start_date, end_date, status) VALUES
('图书捐赠计划', '为贫困地区学校捐赠图书', 10000.00, '2024-01-01', '2024-12-31', 'active'),
('环保图书回收', '回收旧图书并分类处理', 5000.00, '2024-01-01', '2024-12-31', 'active');

-- 插入默认碳积分记录
INSERT IGNORE INTO carbon_points (user_id, points, type, reason) VALUES
(1, 100, 'earn', '注册奖励'),
(2, 100, 'earn', '注册奖励');
