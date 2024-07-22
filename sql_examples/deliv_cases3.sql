-------------------Количество фактически доставленных кейсов за август в Нур-Султан?-------------------
-------------------How many delivered cases/applications do we have for August in Nur-Sultan (RG BRANDS) branch?
SELECT
    c.name, ap.plandeliveryperiodtartdate::date, 
    SUM(ag.deliveredquantity * ag.casecoefficient) AS fact_cases,
    SUM(ag.quantity * ag.casecoefficient) as plan_cases
FROM
    copilot2.applicationgoods ag
JOIN
    copilot2.applications ap ON ag.appid = ap._id
JOIN
    copilot2.companies c ON ap.companyid = c._id
WHERE ap.plandeliveryperiodtartdate between '2024-08-01' and '2024-09-01'
    AND ap.statusgroup != 'archived'
    AND ag.pg_deleted_at is null
    AND c.name = 'Филиал RG BRANDS в г. Нур-Султан'
GROUP BY c.name, ap.plandeliveryperiodtartdate::date;
