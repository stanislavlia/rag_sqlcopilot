--------------------Назови топ 3 товара филиалу Алматы по вырученной сумме денег за январь 2024 года
------------------- What are top 3 most popular goods in Almaty branch for January 2024?

SELECT 
    ag.name, sum(ag.deliveredquantity * ag.price) as total_revenue
FROM 
    copilot2.applicationgoods ag
LEFT JOIN 
    copilot2.applications ap 
    ON ag.appid = ap._id
WHERE 
    ap.plandeliveryperiodtartdate BETWEEN '2024-01-01' AND '2024-01-31'
    AND ap.companyid = 'JzgEMNE5K3Br37ZdF'
GROUP BY 
    ag.name
ORDER BY total_revenue desc 
LIMIT 3;
