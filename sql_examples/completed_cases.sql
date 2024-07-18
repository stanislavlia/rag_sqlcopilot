---------- Какой % завершения заказов за любой период (как все филиалы, так и по отдельности).
-----------What is the application completion rate for all branches?

WITH orders_by_date AS (
  	SELECT
      	ap.companyid,
      	ap.statusgroup,
		COUNT(*) AS order_count
  	FROM
      	copilot2.applications ap
  	WHERE
      	ap.plandeliveryperiodtartdate::date = '2024-07-10'
  	GROUP BY
      	ap.companyid, ap.statusgroup
  ),
  branch_completion AS (
  	SELECT
      	companies.name AS branch_name,
      	SUM(CASE WHEN ob.statusgroup = 'finished' THEN ob.order_count ELSE 0 END) AS finished_orders,
	 	SUM(CASE WHEN ob.statusgroup != 'archived' THEN ob.order_count ELSE 0 END) AS total_orders,
      	ROUND(
          	COALESCE(
              	100.0 * SUM(CASE WHEN ob.statusgroup = 'finished' THEN ob.order_count ELSE 0 END) / SUM(CASE WHEN ob.statusgroup != 'archived' THEN ob.order_count ELSE 0 END),
              	0
          	), 2
      	) AS completion_rate
  	FROM
      	orders_by_date ob
  	JOIN
      	copilot2.companies companies ON ob.companyid = companies._id
  	GROUP BY
      	companies.name
  )
  SELECT
  	branch_name,
  	finished_orders,
  	total_orders,
  	completion_rate
  FROM
  	branch_completion
  ORDER BY
  	completion_rate DESC
  LIMIT 20;