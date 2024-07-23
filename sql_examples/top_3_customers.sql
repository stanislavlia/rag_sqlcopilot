-----------------------------Назови топ-3 клиента по алматы за Июль 2024 года
-----------------------------Top 3 most profitable priority clients for July 2024
SELECT 
    cr.name, sum(app.generalprice)
FROM 
    copilot2.applications app
LEFT JOIN 
    copilot2.clients cr 
    ON app.client_id = cr._id
WHERE 
    app.plandeliveryperiodtartdate BETWEEN '2024-07-01' AND '2024-08-01'
    AND app.companyid = (SELECT _id FROM copilot2.companies WHERE name = 'RG BRANDS')
GROUP BY 
    cr.name
ORDER BY sum(app.generalprice) desc limit 3