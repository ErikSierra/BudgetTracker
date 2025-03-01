CREATE PROCEDURE dbo.UpdateCategories
AS
BEGIN
    SET NOCOUNT ON;

    ----------------------------------------------------------------------------
    -- 1) Payment Category
    ----------------------------------------------------------------------------
    UPDATE dbo.BudgetTracker
    SET Category = 'Payment'
    WHERE UPPER(Description) LIKE '%OPENAI%'
       OR UPPER(Description) LIKE '%CHATGPT%'
       OR UPPER(Description) LIKE '%TAYLOR KIA%'
       OR UPPER(Description) LIKE '%SCHOOL PAYMENT%'
       OR UPPER(Description) LIKE '%SCOTT%';

    ----------------------------------------------------------------------------
    -- 2) School Category for SNHU
    ----------------------------------------------------------------------------
    UPDATE dbo.BudgetTracker
    SET Category = 'School'
    WHERE UPPER(Description) LIKE '%SNHU%';

    ----------------------------------------------------------------------------
    -- 3) Restaurants Category
    ----------------------------------------------------------------------------
    UPDATE dbo.BudgetTracker
    SET Category = 'Restaurants'
    WHERE UPPER(Description) LIKE '%BLACK SWAN GRILL%'
       OR UPPER(Description) LIKE '%FIRST SOLAR%';

    ----------------------------------------------------------------------------
    -- 4) Shopping Category
    ----------------------------------------------------------------------------
    UPDATE dbo.BudgetTracker
    SET Category = 'Shopping'
    WHERE 
          UPPER(Description) LIKE '%WALMART%'
       OR UPPER(Description) LIKE '%TARGET%'
       OR UPPER(Description) LIKE '%DICKS%'
       OR UPPER(Description) LIKE '%BNC%'
       OR UPPER(Description) LIKE '%APPLE.COM%'
       OR UPPER(Description) LIKE '%VILROS%'
       OR UPPER(Description) LIKE '%LEGO%'
       OR UPPER(Description) LIKE '%FYE%'
       OR UPPER(Description) LIKE '%TAS%'
       OR UPPER(Description) LIKE '%CORSRA%'
       OR UPPER(Description) LIKE '%SWANTON SPORTS%'
       OR UPPER(Description) LIKE '%BATH & BODY WORKS%'
       OR UPPER(Description) LIKE '%VITAMINSHOPPE%'
       OR UPPER(Description) LIKE '%SPIRIT HALLOWEEN%'   
       OR UPPER(Description) LIKE '%MENARDS%'
       OR UPPER(Description) LIKE '%CABELAS%'
       OR UPPER(Description) LIKE '%AMZN%'
       OR UPPER(Description) LIKE '%AMAZON%'
       OR UPPER(Description) LIKE '%MICRO CENTER%'
       OR UPPER(Description) LIKE '%COSTCO%'
       OR UPPER(Description) LIKE '%SAM''S CLUB%'
       OR UPPER(Description) LIKE '%BJ''S%'
       OR UPPER(Description) LIKE '%BEST BUY%'
       OR UPPER(Description) LIKE '%HOME DEPOT%'
       OR UPPER(Description) LIKE '%LOWE''S%'
       OR UPPER(Description) LIKE '%KOHLS%'
       OR UPPER(Description) LIKE '%MACYS%'
       OR UPPER(Description) LIKE '%JCPENNEY%'
       OR UPPER(Description) LIKE '%SEARS%'
       OR UPPER(Description) LIKE '%BED BATH%'
       OR UPPER(Description) LIKE '%KROGER%'
       OR UPPER(Description) LIKE '%GIANT EAGLE%'
       OR UPPER(Description) LIKE '%ALDI%'
       OR UPPER(Description) LIKE '%DOLLAR TREE%'
       OR UPPER(Description) LIKE '%DOLLAR GENERAL%'
       OR UPPER(Description) LIKE '%BIG LOTS%'
       OR UPPER(Description) LIKE '%OFFICE DEPOT%'
       OR UPPER(Description) LIKE '%OFFICEMAX%'
       OR UPPER(Description) LIKE '%STAPLES%'
       OR UPPER(Description) LIKE '%ROSS STORES%'
       OR UPPER(Description) LIKE '%MARSHALLS%'
       OR UPPER(Description) LIKE '%TJ MAXX%'
       OR UPPER(Description) LIKE '%OLD NAVY%'
       OR UPPER(Description) LIKE '%GAP%'
       OR UPPER(Description) LIKE '%FOREVER 21%'
       OR UPPER(Description) LIKE '%AMERICAN EAGLE%'
       OR UPPER(Description) LIKE '%URBAN OUTFITTERS%'
       OR UPPER(Description) LIKE '%NORDSTROM%'
       OR UPPER(Description) LIKE '%SHOPRITE%'
       OR UPPER(Description) LIKE '%BURLINGTON%'
       OR UPPER(Description) LIKE '%WINCO%'
       OR UPPER(Description) LIKE '%MEIJER%'
       OR UPPER(Description) LIKE '%CVS%'
       OR UPPER(Description) LIKE '%WALGREENS%'
       OR UPPER(Description) LIKE '%RITE AID%'
       OR UPPER(Description) LIKE '%GAMESTOP%'
       OR UPPER(Description) LIKE '%DSW%'
       OR UPPER(Description) LIKE '%FOOT LOCKER%'
       OR UPPER(Description) LIKE '%DICK''S SPORTING GOODS%'
       OR UPPER(Description) LIKE '%BASS PRO%'
       OR UPPER(Description) LIKE '%APPLE STORE%'
       OR UPPER(Description) LIKE '%SAMS CLUB%'   
       OR UPPER(Description) LIKE '%BJ''S WHOLESALE CLUB%'
       OR UPPER(Description) LIKE '%SHOPPING%'
       OR UPPER(Description) LIKE '%REI%'
       OR UPPER(Description) LIKE '%CABELAS%'
       OR UPPER(Description) LIKE '%PUBLIX%'
       OR UPPER(Description) LIKE '%SAFEWAY%'
       OR UPPER(Description) LIKE '%ALBERTSONS%'
       OR UPPER(Description) LIKE '%VONS%'
       OR UPPER(Description) LIKE '%WHOLE FOODS%'
       OR UPPER(Description) LIKE '%TRADER JOE%'
       OR UPPER(Description) LIKE '%COLES CATERING%'
       OR UPPER(Description) LIKE '%SCHWANS%'
       OR UPPER(Description) LIKE '%GERMAN MARKET%'
       OR UPPER(Description) LIKE '%SWAN CREEK CANDLE%'
       OR UPPER(Description) LIKE '%CALI CLEANERS%'
       OR UPPER(Description) LIKE '%GOLF GALAXY%'
       OR UPPER(Description) LIKE '%IQCALENDARS%'
       OR UPPER(Description) LIKE '%SIE ROK%';

    ----------------------------------------------------------------------------
    -- 5) Default Update: Change "Other" to "Shopping"
    ----------------------------------------------------------------------------
    UPDATE dbo.BudgetTracker
    SET Category = 'Shopping'
    WHERE Category = 'Other';
END;
GO
