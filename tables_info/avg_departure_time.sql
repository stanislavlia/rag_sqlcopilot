
-- Average courier departure time.
-- To find out average first departure time for drivers,
-- you can stick to this particular SQL query:

SELECT 
    couriers.fullname,
    metrics.average_went_time
	FROM (
		SELECT 
			courier_id,
			TIME '00:00' + (SUM(EXTRACT(EPOCH FROM courierwentdate::timestamp)) / COUNT(*)) * INTERVAL '1 second' AS average_went_time
		FROM 
			applications 
		GROUP BY 
			courier_id
	) AS metrics
	JOIN copilot2.couriers ON metrics.courier_id = couriers._id
	ORDER BY metrics.average_went_time;