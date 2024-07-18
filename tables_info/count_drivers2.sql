--- Сколько водителей работает в филиале Шымкента?
SELECT COUNT(*) AS driver_count FROM copilot2.couriers
 c JOIN copilot2.companies co ON c.companyid = co._id 
 WHERE co.name = 'Филиал RG BRANDS в г. Шымкент ' AND c.status = 'Online';