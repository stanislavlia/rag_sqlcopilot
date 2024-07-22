-- Count the number of completed applications for ALL branches for a specific period of time
SELECT 
    COUNT(ap._id) AS completed_applications
FROM 
    copilot2.applications ap
WHERE 
    ap.statusgroup = 'completed'
    AND ap.plandeliveryperiodtartdate BETWEEN '2024-01-01' AND '2024-01-31'; -- Replace with the specific time period
