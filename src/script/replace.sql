Select df.stock_code, df.quantity, invd.invoice_date, invd.country_name
From detailfacture as df, (
	Select invoice_no, REGEXP_REPLACE(REGEXP_REPLACE(invoice_date, '(?<=[\/])\d{1,2}\/', ''), '\d{1,2}:\d{1,2}', '') as invoice_date, country_name
	From invoice
) as invd
Where df.invoice_no = invd.invoice_no

