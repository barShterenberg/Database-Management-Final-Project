
--q1

Create VIEW return_by_1_family_without_children_at_least_and_genre_start_with_A_longest_by_genre
as
select  p.title, p.genre,p.duration
from RecordReturns rr inner join Households H on H.hID = rr.hID
inner join Programs p on p.title=rr.title
where (p.genre LIKE 'A%') and h.ChildrenNum=0;

create VIEW Max_duration
as
select distinct temp.genre, MAX(temp.duration) as duration
from return_by_1_family_without_children_at_least_and_genre_start_with_A_longest_by_genre temp
group by temp.genre;

create VIEW Max_duration_by_genre
as
select distinct temp.genre, MIN(temp.title) as title
from Max_duration md, return_by_1_family_without_children_at_least_and_genre_start_with_A_longest_by_genre temp
where md.duration=temp.duration
group by temp.genre;

--q2

CREATE view kosherPrograms
AS
select pr.title, pr.hID, pr.rank
from ProgramRanks pr, RecordOrders ro
where pr.title = ro.title and pr.hID = ro.hID
union
select pr.title, pr.hID, pr.rank
from ProgramRanks pr, RecordReturns rr
where pr.title = rr.title and pr.hID = rr.hID;

create view more_than_3_rates
AS
select kp.title, count(kp.rank) as count_of_ranks
from kosherPrograms kp
group by kp.title
having count(distinct kp.hID) >= 3
;


--q3
create VIEW count_of_distinct_family_that_return_programs
as
select rr.title, count(distinct rr.hID) as count_returns_by_distinct_family
from RecordReturns rr
group by rr.title;

create VIEW count_of_distinct_family_that_return_programs_10Plus
as
select rr.title, count(distinct rr.hID) count_returns_by_distinct_family
from RecordReturns rr
group by rr.title
having count(distinct rr.hID)>=10;

create view return_by_8_plus_family
as
select plus10_reurn.title, count(distinct h.hID) as count_distinct_8_plus_net_worth
from count_of_distinct_family_that_return_programs_10Plus plus10_reurn
inner join RecordReturns rr on plus10_reurn.title=rr.title
inner join Households H on rr.hID = H.hID
where h.netWorth>=8
group by plus10_reurn.title;

create view join_by_title
as
select plus10.title, plus10.count_returns_by_distinct_family, plus8.count_distinct_8_plus_net_worth
from return_by_8_plus_family plus8, count_of_distinct_family_that_return_programs_10Plus plus10
where plus8.title=plus10.title and (2*plus8.count_distinct_8_plus_net_worth)>plus10.count_returns_by_distinct_family
;