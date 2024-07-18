 ------------------------------Сколько водителей работает по всем филиалам? -----------------
 ------------How many drivers/couriers do we have among all branches?
 -------Make sure to always check whether driver status is 'Online'
 -------'Online' - means this driver currently works and is an active employee.
 select co.name, count(*) from copilot2.couriers cr
JOIN copilot2.companies co ON cr.companyid = co._id 
where cr.status = 'Online' --always add this to correspond to drivers that work with us.
group by co.name
