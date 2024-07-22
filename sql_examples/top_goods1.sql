--------------------Назови топ 5 товара филиалу Алматы по вырученной сумме денег за второй квартал 2024 года
------------------- What are top 5 most popular goods in Almaty branch for Q2 2024?

SELECT 
    ag.name, sum(ag.deliveredquantity * ag.price) as total_revenue
FROM 
    copilot2.applicationgoods ag
LEFT JOIN 
    copilot2.applications ap 
    ON ag.appid = ap._id
WHERE 
    ap.plandeliveryperiodtartdate BETWEEN '2024-04-01' AND '2024-06-30'
    AND ap.companyid = 'JzgEMNE5K3Br37ZdF'
GROUP BY 
    ag.name
ORDER BY total_revenue desc 
LIMIT 5;
