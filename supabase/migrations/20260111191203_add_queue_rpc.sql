set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.claim_queue_items(p_run_id uuid, p_worker_id text, p_limit integer DEFAULT 10)
 RETURNS SETOF public.crawl_queue
 LANGUAGE plpgsql
AS $function$
begin
    return query
    with claimed as (
        select id from crawl_queue
        where run_id = p_run_id and status = 'pending'
        order by priority desc, created_at
        limit p_limit
        for update skip locked
    )
    update crawl_queue q
    set
        status = 'processing',
        worker_id = p_worker_id,
        claimed_at = now(),
        attempts = attempts + 1
    from claimed c
    where q.id = c.id
    returning q.*;
end;
$function$
;

CREATE OR REPLACE FUNCTION public.get_unparsed_pages(p_limit integer DEFAULT 100)
 RETURNS SETOF public.crawled_pages
 LANGUAGE sql
AS $function$
    select cp.*
    from crawled_pages cp
    left join parsed_pages pp on pp.page_id = cp.id
    where pp.id is null and cp.content is not null
    order by cp.crawled_at desc
    limit p_limit;
$function$
;

CREATE OR REPLACE FUNCTION public.reset_stale_queue_items(p_timeout_minutes integer DEFAULT 5)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
declare
    affected int;
begin
    update crawl_queue
    set
        status = 'pending',
        worker_id = null,
        claimed_at = null
    where status = 'processing'
        and claimed_at < now() - (p_timeout_minutes || ' minutes')::interval
        and attempts < max_attempts;

    get diagnostics affected = row_count;
    return affected;
end;
$function$
;


