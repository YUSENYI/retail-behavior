CREATE DATABASE IF NOT EXISTS retail_behavior
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'retail'@'localhost' IDENTIFIED BY '2112';
CREATE USER IF NOT EXISTS 'retail'@'127.0.0.1' IDENTIFIED BY '2112';
CREATE USER IF NOT EXISTS 'retail'@'%' IDENTIFIED BY '2112';

ALTER USER 'retail'@'localhost' IDENTIFIED BY '2112';
ALTER USER 'retail'@'127.0.0.1' IDENTIFIED BY '2112';
ALTER USER 'retail'@'%' IDENTIFIED BY '2112';

GRANT ALL PRIVILEGES ON retail_behavior.* TO 'retail'@'localhost';
GRANT ALL PRIVILEGES ON retail_behavior.* TO 'retail'@'127.0.0.1';
GRANT ALL PRIVILEGES ON retail_behavior.* TO 'retail'@'%';

FLUSH PRIVILEGES;
