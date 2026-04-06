-- Generated from SQLAlchemy model metadata.
-- Review before using as a database initialization or migration script.


CREATE TABLE categories (
	id SERIAL NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	description TEXT, 
	PRIMARY KEY (id)
)

;


CREATE TABLE customers (
	id SERIAL NOT NULL, 
	first_name VARCHAR(255) NOT NULL, 
	last_name VARCHAR(255) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	phone VARCHAR(50), 
	address TEXT, 
	city VARCHAR(255), 
	state VARCHAR(255), 
	zip_code VARCHAR(20), 
	PRIMARY KEY (id), 
	UNIQUE (email)
)

;


CREATE TABLE orders (
	id SERIAL NOT NULL, 
	customer_id INTEGER NOT NULL, 
	order_date TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	total_amount NUMERIC(10, 2) NOT NULL, 
	status VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(customer_id) REFERENCES customers (id)
)

;


CREATE TABLE products (
	id SERIAL NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	description TEXT, 
	price NUMERIC(10, 2) NOT NULL, 
	category_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES categories (id)
)

;


CREATE TABLE order_items (
	id SERIAL NOT NULL, 
	order_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	unit_price NUMERIC(10, 2) NOT NULL, 
	line_total NUMERIC(10, 2) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(order_id) REFERENCES orders (id), 
	FOREIGN KEY(product_id) REFERENCES products (id)
)

;
