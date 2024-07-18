--- Сколько водителей работает в филиале Бишкека?
--- How many drivers are there in Bishkek branch?
SELECT COUNT(*) AS driver_count FROM copilot2.couriers
 c JOIN copilot2.companies co ON c.companyid = co._id 
 WHERE co.name = 'Филиал RG BRANDS в г. Бишкек' AND c.status = 'Online';