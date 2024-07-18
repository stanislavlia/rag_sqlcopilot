--------------------Назови топ 3 товара филиалу Алматы по вырученной сумме денег за этот товар
------------------- What are top 3 most popular goods in Almaty branch?

SELECT 
    ag.name, sum(ag.deliveredquantity * ag.price)
FROM 
    copilot2.applicationgoods ag
LEFT JOIN 
    copilot2.applications ap 
    ON ag.appid = ap._id
WHERE 
    ap.plandeliveryperiodtartdate BETWEEN '2024-07-01' AND '2024-07-16'
    AND ap.companyid = 'JzgEMNE5K3Br37ZdF'
GROUP BY 
    ag.name
ORDER BY sum(ag.deliveredquantity * ag.price) desc limit 3
