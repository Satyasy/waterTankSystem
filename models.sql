-- Schema for IoT sensor readings (LDR, water sensor, buzzer)
CREATE DATABASE IF NOT EXISTS water_sensors;
USE iot_sensors;

CREATE TABLE IF NOT EXISTS sensor_readings (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  device_id VARCHAR(64) NOT NULL,
  ldr INT NULL,
  water TINYINT(1) NULL,
  buzzer TINYINT(1) NULL,
  ts DATETIME NOT NULL,
  INDEX idx_device_ts (device_id, ts)
);
