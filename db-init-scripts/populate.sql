-- ===============================
-- INSERT DEMO DATA
-- ===============================

-- AdminUser
INSERT INTO AdminUser (name, email, password) VALUES
('Alice Admin', 'alice.admin@example.com', 'password123'),
('Bob Admin', 'bob.admin@example.com', 'password456');

-- "User"
INSERT INTO users (name, email) VALUES
('John Doe', 'john.doe@gmail.com'),
('Jane Smith', 'jane.smith@hotmail.com'),
('Mike Johnson', 'mike.johnson@yahoo.com');

-- Tag
INSERT INTO Tag (tagType, tagValue, tagDescription) VALUES
('Diet', 'Vegan', 'Indicates the item is vegan-friendly'),
('Spice', 'Mild', 'Mild spice level'),
('Diet', 'Gluten-Free', 'Indicates the item is gluten-free'),
('Allergy', 'Peanuts', 'Contains peanuts');

-- Restaurant
INSERT INTO Restaurant (name, latitude, longitude, ownerID) VALUES
('Delish Downtown', 40.7128, -74.0060, 1),
('Delish Uptown', 40.7831, -73.9712, 1),
('Quick Bites - Airport', 40.6420, -73.7889, 2);

-- Rating
INSERT INTO Rating (rating, restaurantID, text) VALUES
(5, 1, 'Great ambiance and food!'),
(4, 1, 'Good experience overall.'),
(3, 2, 'Average service, but nice location');

-- Menu
INSERT INTO Menu (restaurantID, description) VALUES
(1, 'Main Menu - Downtown'),
(1, 'Dessert Menu - Downtown'),
(2, 'Uptown Main Menu');

-- MenuSection
INSERT INTO MenuSection (menuID, name) VALUES
(1, 'Appetizers'),
(1, 'Entrees'),
(2, 'Desserts'),
(3, 'Lunch Specials');

-- MenuItem
INSERT INTO MenuItem (sectionID, photoLink, description, name, price, type) VALUES
(1, '', 'A simple green salad', 'Green Salad', 5.99, 'Appetizer'),
(2, '', 'Spicy chicken wings', 'Chicken Wings', 8.99, 'Appetizer'),
(2, '', 'Grilled salmon with lemon sauce', 'Grilled Salmon', 15.99, 'Entree'),
(3, '', 'Chocolate cake with rich frosting', 'Choco Overload', 6.99, 'Dessert');

-- MenuItemHasTag
INSERT INTO MenuItemHasTag (menuItemID, tagID) VALUES
(1, 1), -- Green Salad -> Vegan
(2, 2), -- Chicken Wings -> Mild spice
(3, 3), -- Grilled Salmon -> Gluten-Free
(4, 4); -- Choco Overload -> Contains Peanuts

-- UserLikesTag
INSERT INTO UserLikesTag (userID, tagID) VALUES
(1, 1), -- John Doe likes Vegan
(1, 2), -- John Doe likes Mild spice
(2, 4); -- Jane Smith likes Peanuts (or is at least not allergic)

-- UserLikesMenuItem
INSERT INTO UserLikesMenuItem (userID, menuItemID) VALUES
(1, 1), -- John likes Green Salad
(1, 3), -- John also likes Grilled Salmon
(2, 4); -- Jane likes Choco Overload

-- RestaurantTable
INSERT INTO RestaurantTable (restaurantID, tableNumber, name) VALUES
(1, 1, 'Window Seat'),
(1, 2, 'Bar Seat'),
(2, 5, 'Family Table');
