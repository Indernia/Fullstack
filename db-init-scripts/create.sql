-- 1) AdminUser
CREATE TABLE AdminUser (
    id SERIAL PRIMARY KEY,    -- Use SERIAL instead of AUTOINCREMENT
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL
);

-- 2) "User"
CREATE TABLE users (
    id SERIAL PRIMARY KEY,    -- Use SERIAL instead of AUTOINCREMENT
    name TEXT NOT NULL,
    email TEXT NOT NULL
);

-- 3) Tag
CREATE TABLE Tag (
    id SERIAL PRIMARY KEY,    -- Use SERIAL instead of AUTOINCREMENT
    tagType TEXT NOT NULL,
    tagValue TEXT NOT NULL,
    tagDescription TEXT
);

-- 4) RestaurantChain
CREATE TABLE RestaurantChain (
    id SERIAL PRIMARY KEY,    -- Use SERIAL instead of AUTOINCREMENT
    name TEXT NOT NULL,
    ownerID INTEGER NOT NULL,
    FOREIGN KEY (ownerID) REFERENCES AdminUser(id)
);

-- 5) Restaurant
CREATE TABLE Restaurant (
    id SERIAL PRIMARY KEY,    -- Use SERIAL instead of AUTOINCREMENT
    name TEXT NOT NULL,
    chainID INTEGER NOT NULL,
    latitude REAL,
    longitude REAL,
    FOREIGN KEY (chainID) REFERENCES RestaurantChain(id)
);

-- 6) Rating
CREATE TABLE Rating (
    id SERIAL PRIMARY KEY,    -- Use SERIAL instead of AUTOINCREMENT
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5), 
    restaurantID INTEGER NOT NULL,
    text TEXT,
    FOREIGN KEY (restaurantID) REFERENCES Restaurant(id)
);

-- 7) Menu
CREATE TABLE Menu (
    id SERIAL PRIMARY KEY,    -- Use SERIAL instead of AUTOINCREMENT
    restaurantID INTEGER NOT NULL,
    description TEXT,
    FOREIGN KEY (restaurantID) REFERENCES Restaurant(id)
);

-- 8) MenuSection
CREATE TABLE MenuSection (
    id SERIAL PRIMARY KEY,    -- Use SERIAL instead of AUTOINCREMENT
    menuID INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (menuID) REFERENCES Menu(id)
);

-- 9) MenuItem
CREATE TABLE MenuItem (
    id SERIAL PRIMARY KEY,    -- Use SERIAL instead of AUTOINCREMENT
    sectionID INTEGER NOT NULL,
    photoLink TEXT,
    description TEXT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    type TEXT,
    FOREIGN KEY (sectionID) REFERENCES MenuSection(id)
);

-- 10) MenuItemHasTag
CREATE TABLE MenuItemHasTag (
    id SERIAL PRIMARY KEY,    -- Use SERIAL instead of AUTOINCREMENT
    menuItemID INTEGER NOT NULL,
    tagID INTEGER NOT NULL,
    FOREIGN KEY (menuItemID) REFERENCES MenuItem(id),
    FOREIGN KEY (tagID) REFERENCES Tag(id)
);

-- 11) UserLikesTag
CREATE TABLE UserLikesTag (
    id SERIAL PRIMARY KEY,    -- Use SERIAL instead of AUTOINCREMENT
    userID INTEGER NOT NULL,
    tagID INTEGER NOT NULL,
    FOREIGN KEY (userID) REFERENCES users(id),
    FOREIGN KEY (tagID) REFERENCES Tag(id)
);

-- 12) UserLikesMenuItem
CREATE TABLE UserLikesMenuItem (
    id SERIAL PRIMARY KEY,    -- Use SERIAL instead of AUTOINCREMENT
    userID INTEGER NOT NULL,
    menuItemID INTEGER NOT NULL,
    FOREIGN KEY (userID) REFERENCES users(id),
    FOREIGN KEY (menuItemID) REFERENCES MenuItem(id)
);

-- 13) RestaurantTable
CREATE TABLE RestaurantTable (
    id SERIAL PRIMARY KEY,    -- Use SERIAL instead of AUTOINCREMENT
    restaurantID INTEGER NOT NULL,
    tableNumber INTEGER NOT NULL,
    name TEXT,
    FOREIGN KEY (restaurantID) REFERENCES Restaurant(id)
);


-- 14) Order
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,    -- Use SERIAL instead of AUTOINCREMENT
    restaurantID INTEGER NOT NULL,
    userID INTEGER NOT NULL,
    tableID INTEGER NOT NULL,
    orderTime TIMESTAMP NOT NULL,
    orderCost REAL NOT NULL,
    orderComplete BOOLEAN NOT NULL,
    FOREIGN KEY (userID) REFERENCES users(id),
    FOREIGN KEY (tableID) REFERENCES RestaurantTable(id),
    FOREIGN KEY (restaurantID) REFERENCES Restaurant(id)
);


-- 15) OrderIncludesMenuItem
CREATE TABLE OrderIncludesMenuItem (
    id SERIAL PRIMARY KEY,    -- Use SERIAL instead of AUTOINCREMENT
    orderID INTEGER NOT NULL,
    menuItemID INTEGER NOT NULL,
    FOREIGN KEY (orderID) REFERENCES orders(id),
    FOREIGN KEY (menuItemID) REFERENCES MenuItem(id)
);
