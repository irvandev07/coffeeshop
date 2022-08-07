SELECT * FROM "user" ORDER BY id;
SELECT * FROM categories ORDER BY id;
SELECT * FROM products ORDER BY id;
SELECT * FROM "order" ORDER BY id;
SELECT * FROM order_detail ORDER BY id;

select 
	(select count(*) from products) as count_pro,
  	(select count(*) from "user" WHERE is_admin = true) as count_admin, 
	(select count(*) from "user" WHERE is_admin = false) as count_user,
  	(select count(*) from "order") as count_order
	

select TO_CHAR(date, 'Mon') as mon,
	count(*) as sales
from "order"
group by mon order by mon


ALTER SEQUENCE order_id_seq RESTART WITH 1
ALTER SEQUENCE order_detail_id_seq RESTART WITH 1


SELECT product_id, SUM(quantity * subtotal) FROM order_detail GROUP BY product_id ORDER BY SUM DESC LIMIT 5;


select  pr.public_id, o.product_id, SUM(o.quantity) as sold, pr.name_product
from order_detail o
left join products pr on o.product_id = pr.id
group by pr.public_id, o.product_id, pr.name_product
ORDER BY sold DESC LIMIT 5;

select o.product_id, SUM(o.quantity) as sold, pr.name_product, pr.price, pr.image 
from order_detail o 
left join products pr on o.product_id = pr.id 
group by o.product_id, pr.name_product, pr.price, pr.image 
ORDER BY sold DESC LIMIT 5;

select COUNT(o.user_id) as total_order, u.name
from "order" o
left join "user" u on o.user_id = u.id
group by o.user_id, u.name
ORDER BY total_order DESC LIMIT 5;