select *
from blog_post;

insert into blog_post
select  bod_idx         as post_uid
,       bod_title       as post_title
,       bod_slug        as post_slug
,       con_content     as post_content
,       bod_readcnt     as post_views
,       true            as post_isEnabled
,       bod_tag         as post_tag
,       con_regdate     as post_crte_dt
,       con_moddate     as post_mdfy_dt
,       case cat_idx
            when 11 then 32
            when 12 then 33
            when 13 then 26
            when 14 then 24
            when 15 then 29
            when 16 then 17
            when 17 then 18
            when 18 then 15
            when 19 then 27
            when 20 then 23
            when 24 then 41
            when 25 then 14
            when 28 then 20
            when 40 then 31
            when 41 then 34
            when 42 then 40
            when 44 then 26
            when 45 then 16
            when 47 then 10
            when 48 then 10
            when 49 then 13
            when 51 then 21
            when 53 then 22
            when 55 then 37
            when 57 then 10
            when 58 then 30
            when 59 then 38
            when 60 then 11
            when 61 then 28
            when 63 then 19
            when 64 then 12
        end             as menu_uid
,       1               as post_crte_user_id
,       1               as post_mdfy_user_id
from blog_post_mig
where cat_idx not in (2, 5, 23, 26)
order by cat_idx, bod_idx
;
commit;