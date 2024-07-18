-------------------Среднее время выезда за июнь по алмате (филиалу Алматы)?
------------------What are the average departure time for all drivers in Almaty RG BRANDS branch?
SELECT 
    cr.fullname, 
    TO_CHAR(TO_TIMESTAMP(AVG(EXTRACT(EPOCH FROM app.courierwentdate))), 'YYYY-MM-DD HH24:MI:SS') AS avg_courierwentdate
FROM 
    copilot2.applications app
LEFT JOIN 
    copilot2.couriers cr 
    ON app.courier_id = cr._id
WHERE 
    app.plandeliveryperiodtartdate BETWEEN '2024-07-01' AND '2024-07-16'
    AND app.companyid = 'JzgEMNE5K3Br37ZdF'
GROUP BY 
    cr.fullname;