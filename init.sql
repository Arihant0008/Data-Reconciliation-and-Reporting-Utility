USE reconciliation_db;

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    symbol VARCHAR(10),
    trade_type VARCHAR(10),
    amount DECIMAL(10, 2)
);

INSERT INTO transactions (transaction_id, symbol, trade_type, amount) VALUES
('TXN-1001', 'AAPL', 'BUY', 5000.00),
('TXN-1002', 'TSLA', 'SELL', 1200.50),
('TXN-1004', 'AMZN', 'SELL', 9000.00),
('TXN-1005', 'MSFT', 'BUY', 150.00),
('TXN-1006', 'NVDA', 'BUY', 400.00);