CREATE TABLE IF NOT EXISTS items (
    id       SERIAL PRIMARY KEY,
    name     TEXT    NOT NULL,
    quantity INTEGER NOT NULL
);

INSERT INTO items (name, quantity) VALUES
    ('tomato', 40),
    ('cherry tomato', 25),
    ('onion', 60),
    ('garlic', 15),
    ('rice (kg)', 30);
