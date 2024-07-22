--------------------Назови топ 10 товара филиалу Алматы по вырученной сумме денег за 2023 год
------------------- What are top 10 most popular goods in Almaty branch for the year 2023?

SELECT 
    ag.name, sum(ag.deliveredquantity * ag.price) as total_revenue
FROM 
    copilot2.applicationgoods ag
LEFT JOIN 
    copilot2.applications ap 
    ON ag.appid = ap._id
WHERE 
    ap.plandeliveryperiodtartdate BETWEEN '2023-01-01' AND '2023-12-31'
    AND ap.companyid = 'JzgEMNE5K3Br37ZdF'
GROUP BY 
    ag.name
ORDER BY total_revenue desc 
LIMIT 10;
