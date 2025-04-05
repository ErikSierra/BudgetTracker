CREATE TABLE dbo.DuplicateTransactions (
    TransactionDate DATE NOT NULL,
    ClearingDate DATE NULL,
    Description VARCHAR(255) NOT NULL,
    Category VARCHAR(100) NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    Source VARCHAR(50) NULL,
    DuplicateLoggedAt DATETIME DEFAULT GETDATE()
);
