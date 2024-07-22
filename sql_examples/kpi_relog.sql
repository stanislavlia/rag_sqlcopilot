-- Calculate KPI_relog/efficieny for a specific branch/филиал
-- Пример для подсчета эффективности отдельных филиалов

WITH incoming AS (
    SELECT 
        c.name, 
        COUNT(ap._id) AS incoming_applications
    FROM 
        copilot2.applications ap
    JOIN 
        copilot2.companies c ON ap.companyid = c._id
    WHERE 
        c.name = 'Филиал RG BRANDS в г. Алматы' -- Replace with the specific branch name
        AND ap.statusgroup != 'completed'
        AND ap.statusgroup != 'archived'
    GROUP BY 
        c.name
),
completed AS (
    SELECT 
        c.name, 
        COUNT(ap._id) AS completed_applications
    FROM 
        copilot2.applications ap
    JOIN 
        copilot2.companies c ON ap.companyid = c._id
    WHERE 
        c.name = 'Филиал RG BRANDS в г. Алматы' -- Replace with the specific branch name
        AND ap.statusgroup = 'completed'
    GROUP BY 
        c.name
)
SELECT 
    incoming.name,
    completed.completed_applications,
    incoming.incoming_applications,
    (CAST(completed.completed_applications AS FLOAT) / incoming.incoming_applications) AS KPI_relog
FROM 
    incoming
JOIN 
    completed ON incoming.name = completed.name;
