CREATE DATABASE IF NOT EXISTS `biometrie` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `biometrie`;

CREATE TABLE `sys`(
	`id` int NOT NULL PRIMARY KEY,
	`nom` VARCHAR(255),
	`prenom` VARCHAR(255),
	`email` VARCHAR(255),
	`FacialData` VARCHAR(255),
	`lastAccess` date
);