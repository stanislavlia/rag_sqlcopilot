
--- Сколько водителей работает в филиале Караганды?
--- How many drivers are there in Karaganda branch?
SELECT COUNT(*) AS driver_count FROM copilot2.couriers
 c JOIN copilot2.companies co ON c.companyid = co._id 
 WHERE co.name = 'Филиал RG BRANDS в г. Караганда' AND c.status = 'Online';