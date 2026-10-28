CREATE DATABASE business_listings;
USE business_listings;

CREATE TABLE listing_master (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    business_name VARCHAR(255) NOT NULL,
    category VARCHAR(120) NOT NULL,
    city VARCHAR(120) NOT NULL,
    address VARCHAR(500) NULL,
    phone VARCHAR(50) NULL,
    source VARCHAR(120) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_listing_city (city),
    INDEX idx_listing_category (category),
    INDEX idx_listing_source (source),
    INDEX idx_listing_name_city (business_name, city)
);

SELECT COUNT(*) AS total_listings
FROM listing_master;

SELECT city, COUNT(*) AS total
FROM listing_master
GROUP BY city
ORDER BY total DESC;

SELECT category, COUNT(*) AS total
FROM listing_master
GROUP BY category
ORDER BY total DESC;

