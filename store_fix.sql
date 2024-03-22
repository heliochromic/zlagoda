--Тут ми робимо композитний пк для таблиці store_sale
ALTER TABLE store_sale DROP CONSTRAINT "/*Тут вставте назву constraint в вашій таблиці*/";
ALTER TABLE IF EXISTS public.store_sale
    ADD CONSTRAINT composite PRIMARY KEY ("UPC_id", check_number_id);

--Тут ми міняємо стратегію оновлення для таблиці store_product
--category_number
ALTER TABLE store_product DROP CONSTRAINT "/*Тут вставте назву constraint для category_number в вашій таблиці*/";
ALTER TABLE store_product 
ADD CONSTRAINT store_product_category_id_fk
FOREIGN KEY (category_number_id)
REFERENCES store_category(category_number)
ON UPDATE CASCADE
ON DELETE NO ACTION;

--Тут ми міняємо стратегію оновлення для таблиці store_store_product
--UPC_prom
ALTER TABLE store_store_product DROP CONSTRAINT "/*Тут вставте назву constraint для UPC_prom в вашій таблиці*/";
ALTER TABLE store_store_product 
ADD CONSTRAINT store_store_product_UPC_prom_fk
FOREIGN KEY ("UPC_prom_id")
REFERENCES store_store_product("UPC")
ON UPDATE CASCADE
ON DELETE SET NULL;
--id_product
ALTER TABLE store_store_product DROP CONSTRAINT "/*Тут вставте назву constraint для id_product в вашій таблиці*/";
ALTER TABLE store_store_product 
ADD CONSTRAINT store_store_product_id_product_fk
FOREIGN KEY (id_product_id)
REFERENCES store_product(id_product)
ON UPDATE CASCADE
ON DELETE NO ACTION;

--Тут ми міняємо стратегію оновлення для таблиці store_check
--id_employee
ALTER TABLE store_check DROP CONSTRAINT "/*Тут вставте назву constraint для id_employee в вашій таблиці*/";
ALTER TABLE store_check 
ADD CONSTRAINT store_check_category_id_employee_fk
FOREIGN KEY (id_employee_id)
REFERENCES store_employee(id_employee)
ON UPDATE CASCADE
ON DELETE NO ACTION;
--card_number
ALTER TABLE store_check DROP CONSTRAINT "/*Тут вставте назву constraint для card_number в вашій таблиці*/";
ALTER TABLE store_check 
ADD CONSTRAINT store_check_category_card_number_id_fk
FOREIGN KEY (card_number_id)
REFERENCES store_customer_card(card_number)
ON UPDATE CASCADE
ON DELETE NO ACTION;

--Тут ми міняємо стратегію оновлення для таблиці store_sale
--UPC
ALTER TABLE store_sale DROP CONSTRAINT "/*Тут вставте назву constraint для UPC в вашій таблиці*/";
ALTER TABLE store_sale 
ADD CONSTRAINT store_sale_UPC_fk
FOREIGN KEY ("UPC_id")
REFERENCES store_store_product("UPC")
ON UPDATE CASCADE
ON DELETE NO ACTION;
--check_number
ALTER TABLE store_sale DROP CONSTRAINT "/*Тут вставте назву constraint для check_number в вашій таблиці*/";
ALTER TABLE store_sale 
ADD CONSTRAINT store_sale_check_number_id_fk
FOREIGN KEY (check_number_id)
REFERENCES store_check(check_number)
ON UPDATE CASCADE
ON DELETE CASCADE;