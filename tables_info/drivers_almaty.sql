 ------------------------------Сколько водителей работает в Алматы ?-----------------
 ------------------------------How many drivers do work in Almaty (RG BRANDS) branch?
select co.name, count(*) from copilot2.couriers cr
JOIN copilot2.companies co ON cr.companyid = co._id 
where cr.companyid='JzgEMNE5K3Br37ZdF'
and cr.status = 'Online'
group by co.name
