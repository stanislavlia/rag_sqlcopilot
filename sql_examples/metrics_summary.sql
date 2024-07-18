
-- Here's a SQL query to conduct an analysis and compute many important metrcics at once.
--     Use this as example, when you try to answer questons about active applications, KPI of drivers,
--     incoming/new applications and cancelled applications.
--     (Note: Филиалы - this is a Russian word corresponding to department or branch of a company.
--      You can acess name of the department by looking at companies.name)


WITH metrics AS (
    SELECT
        ap.companyid,
        SUM(CASE WHEN ap.statusgroup IN ('finished', 'inprocess') THEN 1 ELSE 0 END) AS finished_or_inprocess,
        SUM(CASE WHEN ap.factdeliverydate <= ap.plandeliveryperiod_enddate AND ap.statusgroup = 'finished' THEN 1 ELSE 0 END) AS finished_on_time,
        SUM(CASE WHEN ap.rejectcount = 0 AND ap.statusgroup = 'finished' THEN 1 ELSE 0 END) AS rejected_and_finished,
        SUM(CASE WHEN ap.finishedinarea = TRUE AND ap.statusgroup = 'finished' THEN 1 ELSE 0 END) AS finished_in_area,
        SUM(CASE WHEN ap.statusgroup = 'finished' THEN 1 ELSE 0 END) AS finished,
        SUM(CASE WHEN ap.rejectcount > 0 THEN 1 ELSE 0 END) AS reject_count,
        SUM(CASE WHEN ap.statusgroup = 'inprocess' THEN 1 ELSE 0 END) AS inprocess_count,
        SUM(CASE WHEN ap.statusgroup = 'new' THEN 1 ELSE 0 END) AS new_count,
    SUM(CASE WHEN ap.statusgroup != 'archived' THEN 1 ELSE 0 END) AS all_orders
    FROM
        copilot2.applications ap
    GROUP BY
        ap.companyid
)
SELECT
    companies.name AS Филиалы,
  COALESCE(metrics.all_orders, 0) AS Все_заказы,
  COALESCE(metrics.new_count, 0) AS Входящие,
  COALESCE(metrics.inprocess_count, 0) AS Активные_заказы,
  COALESCE(metrics.finished, 0) AS Завершенные_заказы,
  COALESCE(metrics.reject_count, 0) AS Возвраты,
    ROUND(COALESCE(
        0.5 * (CASE WHEN metrics.finished_or_inprocess > 0 THEN metrics.finished_on_time::numeric / metrics.finished_or_inprocess ELSE 0 END) +
        0.3 * (CASE WHEN metrics.finished > 0 THEN metrics.rejected_and_finished::numeric / metrics.finished ELSE 0 END) +
        0.2 * (CASE WHEN metrics.finished > 0 THEN metrics.finished_in_area::numeric / metrics.finished ELSE 0 END), 
        0
    )*100, 1
    )AS KPI_Relog
FROM
    metrics
JOIN
    copilot2.companies AS companies ON metrics.companyid = companies._id
ORDER BY
    all_orders DESC