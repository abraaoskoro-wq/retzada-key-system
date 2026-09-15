CREATE TABLE `keys` (
	`id` int AUTO_INCREMENT NOT NULL,
	`code` varchar(64) NOT NULL,
	`productId` int NOT NULL,
	`productName` varchar(120) NOT NULL,
	`durationDays` int NOT NULL,
	`status` enum('available','redeemed') NOT NULL DEFAULT 'available',
	`redeemedBy` int,
	`redeemedAt` timestamp,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `keys_id` PRIMARY KEY(`id`),
	CONSTRAINT `keys_code_unique` UNIQUE(`code`)
);
--> statement-breakpoint
CREATE TABLE `products` (
	`id` int AUTO_INCREMENT NOT NULL,
	`name` varchar(120) NOT NULL,
	`category` varchar(80) NOT NULL,
	`durationDays` int NOT NULL,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `products_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `tickets` (
	`id` int AUTO_INCREMENT NOT NULL,
	`userId` int NOT NULL,
	`subject` varchar(160) NOT NULL,
	`message` text NOT NULL,
	`status` enum('open','answered','closed') NOT NULL DEFAULT 'open',
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `tickets_id` PRIMARY KEY(`id`)
);
