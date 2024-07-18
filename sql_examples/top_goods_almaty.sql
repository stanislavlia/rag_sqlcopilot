-----------------------------Назови топ-3 самых крупных (прибыльных) клиента по Алматы 
-------What are top 3 most profitable clients in Almaty branch?

SELECT 
    cr.name, sum(app.generalprice)
FROM 
    copilot2.applications app
LEFT JOIN 
    copilot2.clients cr 
    ON app.client_id = cr._id
WHERE 
    app.plandeliveryperiodtartdate BETWEEN '2024-07-01' AND '2024-07-16'
    AND app.companyid = 'JzgEMNE5K3Br37ZdF'
GROUP BY 
    cr.name
ORDER BY sum(app.generalprice) desc limit 3