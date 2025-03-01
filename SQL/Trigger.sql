CREATE TRIGGER dbo.trg_BudgetTracker_AfterInsertUpdate
ON dbo.BudgetTracker
AFTER INSERT, UPDATE
AS
BEGIN
    -- Prevent recursive triggering if this trigger causes further updates
    IF (TRIGGER_NESTLEVEL() > 1)
        RETURN;

    EXEC dbo.UpdateCategories;
END;
GO
