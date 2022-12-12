CREATE TABLE Product(
   stock_code VARCHAR(50),
   Description VARCHAR(80),
   PRIMARY KEY(stock_code)
);

CREATE TABLE Country(
   country_id SERIAL PRIMARY KEY,
   country_name VARCHAR(50) NOT NULL,
   zone_name VARCHAR(50)
);

CREATE TABLE Invoice(
   invoice_no VARCHAR(6),
   invoice_date VARCHAR(20),
   country_id int NOT NULL,
   customer_id VARCHAR(5), 
   PRIMARY KEY(invoice_no),
   FOREIGN KEY(country_id) REFERENCES Country(country_id)
);

CREATE TABLE DetailFacture(
   stock_code VARCHAR(50),
   invoice_no VARCHAR(6),
   unit_price NUMERIC(6,2),
   quantity INT,
   detailfacture_id SERIAL PRIMARY KEY,
   FOREIGN KEY(stock_code) REFERENCES Product(stock_code),
   FOREIGN KEY(invoice_no) REFERENCES Invoice(invoice_no)
);