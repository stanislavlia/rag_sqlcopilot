-- Count the number of incoming applications for a specific branch
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
    c.name;