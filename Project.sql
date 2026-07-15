CREATE DATABASE PROJECT;
USE PROJECT;
CREATE TABLE categories (
    category_id     INT AUTO_INCREMENT PRIMARY KEY,
    category_name   VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO categories (category_name) VALUES
('Road Pothole'), ('Garbage'), ('Drainage');


CREATE TABLE users (
    user_id         INT AUTO_INCREMENT PRIMARY KEY,
    full_name       VARCHAR(100) NOT NULL,
    email           VARCHAR(100) NOT NULL UNIQUE,
    phone           VARCHAR(20) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,   
    account_status  ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE admins (
    admin_id        INT AUTO_INCREMENT PRIMARY KEY,
    full_name       VARCHAR(100) NOT NULL,
    email           VARCHAR(100) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE complaints (
    complaint_id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id           INT NOT NULL,
    category_id       INT NOT NULL,
    description       TEXT NOT NULL,
    photo_url         VARCHAR(255) NOT NULL,
    latitude          DECIMAL(9,6) NOT NULL,
    longitude         DECIMAL(9,6) NOT NULL,
    status            ENUM('pending', 'in_progress', 'resolved', 'closed') NOT NULL DEFAULT 'pending',
    priority          ENUM('low', 'medium', 'high') DEFAULT 'medium',
    assigned_admin_id INT DEFAULT NULL,
    submitted_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    resolved_at       TIMESTAMP NULL DEFAULT NULL,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (assigned_admin_id) REFERENCES admins(admin_id) ON DELETE SET NULL
);


CREATE INDEX idx_complaints_status ON complaints(status);
CREATE INDEX idx_complaints_category ON complaints(category_id);
CREATE INDEX idx_complaints_user ON complaints(user_id);


CREATE TABLE complaint_status_history (
    history_id      INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id    INT NOT NULL,
    old_status      ENUM('pending', 'in_progress', 'resolved', 'closed'),
    new_status      ENUM('pending', 'in_progress', 'resolved', 'closed') NOT NULL,
    changed_by      INT,         
    changed_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES admins(admin_id) ON DELETE SET NULL
);


CREATE TABLE feedback (
    feedback_id     INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    phone           VARCHAR(20) NOT NULL,
    email           VARCHAR(100) NOT NULL,
    message         TEXT NOT NULL,
    submitted_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE VIEW admin_dashboard_summary AS
SELECT
    COUNT(*)                                              AS total_complaints,
    SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) AS in_progress_count,
    SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END)    AS resolved_count,
    SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END)      AS closed_count,
    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END)     AS pending_count
FROM complaints;


CREATE VIEW manager_dashboard AS
SELECT
    u.user_id,
    u.full_name,
    u.email,
    u.account_status,
    c.complaint_id,
    c.submitted_at AS complaint_submitted_at
FROM users u
JOIN complaints c ON u.user_id = c.user_id;




CREATE VIEW user_dashboard AS
SELECT
    c.user_id,
    c.complaint_id,
    cat.category_name AS category,
    c.submitted_at AS complaint_date,
    c.status
FROM complaints c
JOIN categories cat ON c.category_id = cat.category_id;


CREATE VIEW user_complaint_history AS
SELECT
    c.user_id,
    c.complaint_id,
    cat.category_name,
    c.description,
    c.photo_url,
    c.latitude,
    c.longitude,
    c.status,
    c.priority,
    c.submitted_at,
    c.updated_at,
    c.resolved_at
FROM complaints c
JOIN categories cat ON c.category_id = cat.category_id;


CREATE VIEW user_dashboard_summary AS
SELECT
    user_id,
    COUNT(*) AS total_complaints,
    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END)     AS pending_count,
    SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) AS in_progress_count,
    SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END)    AS resolved_count,
    SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END)      AS closed_count
FROM complaints
GROUP BY user_id;

