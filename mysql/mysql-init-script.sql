-- Initialize database and table for node metrics
CREATE DATABASE IF NOT EXISTS nodes;

USE nodes;

CREATE TABLE IF NOT EXISTS node_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    node_name VARCHAR(255) NOT NULL,
    cpu_millicores DECIMAL(10, 2) NOT NULL,
    memory_mb DECIMAL(10, 2) NOT NULL,
    collected_at DATETIME NOT NULL,
    INDEX idx_node_name (node_name),
    INDEX idx_collected_at (collected_at),
    UNIQUE KEY unique_node_timestamp (node_name, collected_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Enable event scheduler
SET GLOBAL event_scheduler = ON;

-- Create TTL event to automatically delete metrics older than 30 minutes
-- This event runs every 5 minutes
DROP EVENT IF EXISTS cleanup_old_node_metrics;

CREATE EVENT cleanup_old_node_metrics
ON SCHEDULE EVERY 5 MINUTE
DO
  DELETE FROM nodes.node_metrics 
  WHERE collected_at < DATE_SUB(NOW(), INTERVAL 30 MINUTE);

