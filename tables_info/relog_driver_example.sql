 -----------------------Какой водитель использует приложение не нажимая кнопку «выехал» в Relog Driver?
 --------Which driver uses application Relog Driver without pressing "Depart" button.
 
select cr.fullname, app.courierwentdate from copilot2.applications app
left join copilot2.couriers cr on app.courier_id = cr._id
where app.plandeliveryperiodtartdate between '2024-07-10' and '2024-07-11'
and app.companyid='JzgEMNE5K3Br37ZdF' 
and app.courierwentdate is null
