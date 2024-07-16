-- To answer which driver is most efficient, you need to use our sophisticated formula for driver's KPI.
--     Here's the explanation of formula:
    
--     On-time Rate (50%): Places the highest importance on timely deliveries.
--     Rejection Rate (20%): Emphasizes the importance of reducing rejected deliveries by considering it inversely.
--     Finished-in-Area Rate (20%): Highlights the importance of completing deliveries within the designated area.
--     Within Planned Distance Rate (10%): Encourages adherence to planned routes and distance efficiency.

-- The KPI formula combines these components to give a weighted score that reflects a driver's overall performance, 
-- taking into account timeliness, reliability, effectiveness in specific areas, and route efficiency.
--  This comprehensive approach ensures that drivers are evaluated on multiple critical aspects of their job performance
SELECT 
    couriers.fullname,
    COALESCE(
        0.5 * (CASE WHEN metrics.finished_or_inprocess > 0 THEN metrics.finished_on_time::numeric / metrics.finished_or_inprocess ELSE 0 END) +
        0.3 * (CASE WHEN metrics.finished > 0 THEN metrics.rejected_and_finished::numeric / metrics.finished ELSE 0 END) +
        0.2 * (CASE WHEN metrics.finished > 0 THEN metrics.finished_in_area::numeric / metrics.finished ELSE 0 END), 
        0
    ) AS weighted_score
	FROM (
		SELECT
			courier_id,
			SUM(CASE WHEN statusgroup IN ('finished', 'inprocess') THEN 1 ELSE 0 END) AS finished_or_inprocess,
			SUM(CASE WHEN factdeliverydate <= plandeliveryperiod_enddate AND statusgroup = 'finished' THEN 1 ELSE 0 END) AS finished_on_time,
			SUM(CASE WHEN rejectcount = 0 AND statusgroup = 'finished' THEN 1 ELSE 0 END) AS rejected_and_finished,
			SUM(CASE WHEN finishedinarea = TRUE AND statusgroup = 'finished' THEN 1 ELSE 0 END) AS finished_in_area,
			SUM(CASE WHEN statusgroup = 'finished' THEN 1 ELSE 0 END) AS finished
		FROM
			copilot.applications
		GROUP BY
			courier_id
	) AS metrics
	JOIN copilot2.couriers ON metrics.courier_id = couriers._id
	ORDER BY weighted_score DESC;