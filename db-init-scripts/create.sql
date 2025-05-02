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

-- Theme
CREATE TABLE themes (
    name TEXT PRIMARY KEY,
    primarycolor VARCHAR(7) NOT NULL, -- Hex color code hence´limiting to 7 characters eg. #FFFFFF
    background VARCHAR(7) NOT NULL,
    secondary VARCHAR(7) NOT NULL,
    text VARCHAR(7) NOT NULL,
    text2 VARCHAR(7) NOT NULL,
    accent1 VARCHAR(7) NOT NULL,
    accent2 VARCHAR(7) NOT NULL
);

-- 4) Restaurant
CREATE TABLE restaurant (
    id SERIAL PRIMARY KEY,    -- Use SERIAL instead of AUTOINCREMENT
    ownerID INTEGER NOT NULL,
    name TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    theme TEXT NOT NULL DEFAULT 'Standard',
    stripekey TEXT,
    openingtime TEXT,
    closingtime TEXT,
    description TEXT,
    averageRating REAL DEFAULT 0,
    totaltables INT DEFAULT 1,
    FOREIGN KEY (ownerID) REFERENCES AdminUser(id) ON DELETE CASCADE,
    FOREIGN KEY (theme) REFERENCES themes(name) ON DELETE SET DEFAULT
);

-- 5) AdminKey
CREATE TABLE apikeys (
    apikey TEXT NOT NULL PRIMARY KEY,
    restaurantID INT NOT NULL,
    FOREIGN KEY (restaurantID) REFERENCES restaurant(id) ON DELETE CASCADE
);

-- 6) Rating
CREATE TABLE Rating (
    id SERIAL PRIMARY KEY,    -- Use SERIAL instead of AUTOINCREMENT
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5), 
    restaurantid INTEGER NOT NULL,
    text TEXT,
    FOREIGN KEY (restaurantID) REFERENCES Restaurant(id) ON DELETE CASCADE
);

-- 7) Menu
CREATE TABLE Menu (
    id SERIAL PRIMARY KEY,    -- Use SERIAL instead of AUTOINCREMENT
    restaurantID INTEGER NOT NULL,
    description TEXT,
    FOREIGN KEY (restaurantID) REFERENCES Restaurant(id) ON DELETE CASCADE
);

-- 8) MenuSection
CREATE TABLE MenuSection (
    id SERIAL PRIMARY KEY,    -- Use SERIAL instead of AUTOINCREMENT
    menuID INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (menuID) REFERENCES Menu(id) ON DELETE CASCADE
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
    FOREIGN KEY (sectionID) REFERENCES MenuSection(id) ON DELETE CASCADE
);

-- 10) MenuItemHasTag
CREATE TABLE MenuItemHasTag (
    id SERIAL PRIMARY KEY,    -- Use SERIAL instead of AUTOINCREMENT
    menuItemID INTEGER NOT NULL,
    tagID INTEGER NOT NULL,
    UNIQUE (menuItemID, tagID),
    FOREIGN KEY (menuItemID) REFERENCES MenuItem(id) ON DELETE CASCADE,
    FOREIGN KEY (tagID) REFERENCES Tag(id) ON DELETE CASCADE
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
    comments TEXT,
    ispaid BOOLEAN NOT NULL DEFAULT FALSE,
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

CREATE OR REPLACE FUNCTION set_average_rating()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE restaurant
    SET averagerating = (
        SELECT AVG(rating)
        FROM Rating
    r   WHERE restaurantid = NEW.restaurantid 
    )
    WHERE id = NEW.restaurantid;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;



CREATE TRIGGER update_average_rating
AFTER INSERT OR UPDATE OR DELETE ON rating
FOR EACH ROW
EXECUTE FUNCTION set_average_rating();




