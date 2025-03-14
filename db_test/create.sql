-- Enable foreign key checks in SQLite
PRAGMA foreign_keys = ON;

-- 1) AdminUser
CREATE TABLE AdminUser (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL
);

-- 2) "User"
CREATE TABLE "User" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL
);

-- 3) Tag
CREATE TABLE Tag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tagType TEXT NOT NULL,
    tagValue TEXT NOT NULL,
    tagDescription TEXT
);

-- 4) RestaurantChain
-- Assuming ownerID references AdminUser (owner is an admin)
CREATE TABLE RestaurantChain (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    ownerID INTEGER NOT NULL,
    FOREIGN KEY (ownerID) REFERENCES AdminUser(id)
);

-- 5) Restaurant
CREATE TABLE Restaurant (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    chainID INTEGER NOT NULL,
    latitude REAL,
    longitude REAL,
    FOREIGN KEY (chainID) REFERENCES RestaurantChain(id)
);

-- 6) Rating
CREATE TABLE Rating (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rating INTEGER NOT NULL,       -- Could add CHECK(rating BETWEEN 1 AND 5) if desired
    restaurantID INTEGER NOT NULL,
    text TEXT,
    FOREIGN KEY (restaurantID) REFERENCES Restaurant(id)
);

-- 7) Menu
CREATE TABLE Menu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurantID INTEGER NOT NULL,
    description TEXT,
    FOREIGN KEY (restaurantID) REFERENCES Restaurant(id)
);

-- 8) MenuSection
-- Note: The logical model duplicated "int menuID"; we keep only one here.
CREATE TABLE MenuSection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menuID INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (menuID) REFERENCES Menu(id)
);

-- 9) MenuItem
CREATE TABLE MenuItem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menuItemID INTEGER NOT NULL,
    tagID INTEGER NOT NULL,
    FOREIGN KEY (menuItemID) REFERENCES MenuItem(id),
    FOREIGN KEY (tagID) REFERENCES Tag(id)
);

-- 11) UserLikesTag
CREATE TABLE UserLikesTag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userID INTEGER NOT NULL,
    tagID INTEGER NOT NULL,
    FOREIGN KEY (userID) REFERENCES "User"(id),
    FOREIGN KEY (tagID) REFERENCES Tag(id)
);

-- 12) UserLikesMenuItem
CREATE TABLE UserLikesMenuItem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userID INTEGER NOT NULL,
    menuItemID INTEGER NOT NULL,
    FOREIGN KEY (userID) REFERENCES "User"(id),
    FOREIGN KEY (menuItemID) REFERENCES MenuItem(id)
);

-- 13) RestaurantTable
CREATE TABLE RestaurantTable (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurantID INTEGER NOT NULL,
    tableNumber INTEGER NOT NULL,
    name TEXT,
    FOREIGN KEY (restaurantID) REFERENCES Restaurant(id)
);
