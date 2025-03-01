SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BudgetTracker](
	[TransactionDate] [date] NOT NULL,
	[ClearingDate] [date] NULL,
	[Description] [varchar](255) NOT NULL,
	[Category] [varchar](100) NOT NULL,
	[Amount] [decimal](10, 2) NOT NULL,
	[Source] [varchar](50) NULL
) ON [PRIMARY]
GO
