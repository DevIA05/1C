select a from temp
except
select a from temp2;

SELECT temp.a FROM temp 
LEFT JOIN temp2 
ON temp.a = temp2.a
WHERE temp2.a IS NULL;

SELECT T1.name1,T2.name2
FROM `table1` T1 
INNER JOIN `table2` T2 ON t2.name1=t1.PrimaryKey;

INSERT INTO tempcountry(country_name)
VALUES ('Japon');

INSERT INTO tempinvoice(invoice_no, invoice_date, customer_id, country_name)
VALUES ('123456', '0/0/1000 00:01', NULL, 'Papaye');

INSERT INTO tempdetailfacture(unit_price, quantity, invoice_no, stock_code)
VALUES (99.99, 99, '987456', '012345');