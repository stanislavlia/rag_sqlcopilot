-----------------------------Назови топ 5 клиентов по филиалу Алматы за  2023 год

SELECT 
    cr.name, sum(app.generalprice)
FROM 
    copilot2.applications app
LEFT JOIN 
    copilot2.clients cr 
    ON app.client_id = cr._id
WHERE 
    app.plandeliveryperiodtartdate BETWEEN '2023-01-01' AND '2024-01-01'
    AND app.companyid = (SELECT _id FROM copilot2.companies WHERE name = 'RG BRANDS')
GROUP BY 
    cr.name
ORDER BY sum(app.generalprice) desc limit 5