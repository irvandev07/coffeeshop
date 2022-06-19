SELECT * FROM "order" ORDER BY id;
SELECT * FROM "user" ORDER BY id;
SELECT * FROM order_detail ORDER BY id;
SELECT * FROM products ORDER BY id;
SELECT * FROM categories ORDER BY id;


SELECT product_id, SUM(quantity * subtotal) FROM order_detail GROUP BY product_id ORDER BY SUM DESC LIMIT 5;


select o.product_id, SUM(o.quantity) as sold, pr.name_product
from order_detail o
left join products pr on o.product_id = pr.id
group by o.product_id, pr.name_product
ORDER BY sold DESC LIMIT 5;

select COUNT(o.user_id) as total_order, u.name
from "order" o
left join "user" u on o.user_id = u.id
group by o.user_id, u.name
ORDER BY total_order DESC LIMIT 5;