USE property_db;

CREATE TABLE IF NOT EXISTS properties (
    property_id INT AUTO_INCREMENT PRIMARY KEY,
    address VARCHAR(255) NOT NULL,
    street_address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(10),
    zip_code VARCHAR(10),
    property_type VARCHAR(50),
    year_built INT,
    sqft_mu INT,
    sqft_total INT,
    beds INT,
    baths INT,
    UNIQUE(address)
);

CREATE TABLE IF NOT EXISTS valuations (
    valuation_id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT NOT NULL,
    list_price DECIMAL(12, 2),
    zestimate DECIMAL(12, 2),
    rent_zestimate DECIMAL(12, 2),
    redfin_value DECIMAL(12, 2),
    expected_rent DECIMAL(12, 2),
    previous_rent DECIMAL(12, 2),
    arv DECIMAL(12, 2),
    low_fmr DECIMAL(12, 2),
    high_fmr DECIMAL(12, 2),
    FOREIGN KEY (property_id) REFERENCES properties(property_id)
        ON DELETE CASCADE
);

-- 3. Create Child Table: 'hoa'
CREATE TABLE IF NOT EXISTS hoa (
    hoa_id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT NOT NULL,
    hoa_fee DECIMAL(10, 2),
    hoa_flag VARCHAR(10),
    FOREIGN KEY (property_id) REFERENCES properties(property_id)
        ON DELETE CASCADE
);

-- 4. Create Child Table: 'rehab'
CREATE TABLE IF NOT EXISTS rehab (
    rehab_id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT NOT NULL,
    underwriting_rehab DECIMAL(12, 2),
    rehab_calculation DECIMAL(12, 2),
    paint VARCHAR(10),
    flooring_flag VARCHAR(10),
    foundation_flag VARCHAR(10),
    roof_flag VARCHAR(10),
    hvac_flag VARCHAR(10),
    kitchen_flag VARCHAR(10),
    bathroom_flag VARCHAR(10),
    appliances_flag VARCHAR(10),
    windows_flag VARCHAR(10),
    landscaping_flag VARCHAR(10),
    trashout_flag VARCHAR(10),
    FOREIGN KEY (property_id) REFERENCES properties(property_id)
        ON DELETE CASCADE
);

