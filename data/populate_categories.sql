-- Main Categories
INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
VALUES 
('Electronics', 'ELECTRONICS', 'Electronic devices and accessories', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Home & Kitchen', 'HOME_KITCHEN', 'Home and kitchen products', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Clothing', 'CLOTHING', 'Clothing and apparel', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Sports & Outdoors', 'SPORTS_OUTDOORS', 'Sports and outdoor equipment', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Beauty & Personal Care', 'BEAUTY_PERSONAL', 'Beauty and personal care products', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Office Products', 'OFFICE', 'Office supplies and equipment', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Toys & Games', 'TOYS_GAMES', 'Toys and games', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Video Games', 'VIDEO_GAMES', 'Video games and gaming equipment', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Health & Household', 'HEALTH_HOUSEHOLD', 'Health and household products', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Pet Supplies', 'PET_SUPPLIES', 'Pet supplies and accessories', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Tools & Home Improvement', 'TOOLS_HOME', 'Tools and home improvement products', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Subcategories (using parent_id references)
INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Smart Speakers', 'SMART_SPEAKERS', 'Smart speakers and voice assistants', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'ELECTRONICS';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Headphones & Earbuds', 'HEADPHONES_EARBUDS', 'Headphones and earbuds', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'ELECTRONICS';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Streaming Media Players', 'STREAMING_PLAYERS', 'Streaming devices and media players', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'ELECTRONICS';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Cell Phone Accessories', 'PHONE_ACCESSORIES', 'Mobile phone accessories', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'ELECTRONICS';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Computer Components', 'COMPUTER_COMPONENTS', 'Computer parts and components', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'ELECTRONICS';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Networking Products', 'NETWORKING', 'Networking equipment and accessories', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'ELECTRONICS';

-- Home & Kitchen subcategories
INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Small Appliances', 'SMALL_APPLIANCES', 'Kitchen appliances and electronics', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'HOME_KITCHEN';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Cookware', 'COOKWARE', 'Pots, pans, and cooking equipment', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'HOME_KITCHEN';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Cleaning Supplies', 'CLEANING_SUPPLIES', 'Cleaning materials and supplies', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'HOME_KITCHEN';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Bedding', 'BEDDING', 'Bed sheets, pillows, and bedding accessories', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'HOME_KITCHEN';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Food Storage', 'FOOD_STORAGE', 'Food storage containers and supplies', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'HOME_KITCHEN';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Travel Mugs', 'TRAVEL_MUGS', 'Travel mugs and thermoses', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'HOME_KITCHEN';

-- Add other subcategories for remaining main categories...
-- Beauty & Personal Care
INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Skin Care', 'SKIN_CARE', 'Skin care products', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'BEAUTY_PERSONAL';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Hair Care Appliances', 'HAIR_APPLIANCES', 'Hair dryers and styling tools', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'BEAUTY_PERSONAL';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Lip Care', 'LIP_CARE', 'Lip balms and treatments', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'BEAUTY_PERSONAL';

-- Office Products
INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Writing Supplies', 'WRITING_SUPPLIES', 'Pens, pencils, and writing materials', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'OFFICE';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Art Supplies', 'ART_SUPPLIES', 'Art and craft supplies', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'OFFICE';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Scissors & Cutting Tools', 'SCISSORS_CUTTING', 'Scissors and cutting implements', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'OFFICE';

-- Health & Household
INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Vitamins & Supplements', 'VITAMINS', 'Vitamins and dietary supplements', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'HEALTH_HOUSEHOLD';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Household Cleaners', 'HOUSEHOLD_CLEANERS', 'Cleaning products', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'HEALTH_HOUSEHOLD';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Bathroom Cleaners', 'BATHROOM_CLEANERS', 'Bathroom cleaning products', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'HEALTH_HOUSEHOLD';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Laundry Care', 'LAUNDRY_CARE', 'Laundry products and supplies', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'HEALTH_HOUSEHOLD';

-- Other categories
INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Men''s Clothing', 'MENS_CLOTHING', 'Men''s apparel', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'CLOTHING';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Water Bottles', 'WATER_BOTTLES', 'Water bottles and hydration', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'SPORTS_OUTDOORS';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Building Toys', 'BUILDING_TOYS', 'Construction and building toys', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'TOYS_GAMES';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Gaming Consoles', 'GAMING_CONSOLES', 'Video game consoles', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'VIDEO_GAMES';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Games', 'GAMES', 'Video games', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'VIDEO_GAMES';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Dog Food', 'DOG_FOOD', 'Dog food and nutrition', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'PET_SUPPLIES';

INSERT INTO categories (name, code, description, parent_id, created_at, updated_at)
SELECT 'Lubricants', 'LUBRICANTS', 'Lubricants and maintenance products', id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
FROM categories WHERE code = 'TOOLS_HOME';
