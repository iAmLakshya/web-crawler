-- Sources: what to crawl and when
create table crawl_sources (
    id uuid primary key default gen_random_uuid(),
    domain text not null,
    entry_url text not null,
    type text not null,
    frequency text not null default 'once',
    max_pages int,
    status text not null default 'active',
    created_at timestamptz not null default now(),
    next_run_at timestamptz,

    constraint valid_type check (type in ('single_page', 'full_domain')),
    constraint valid_status check (status in ('active', 'paused')),
    constraint valid_max_pages check (max_pages is null or max_pages > 0)
);

-- Runs: individual crawl executions
create table crawl_runs (
    id uuid primary key default gen_random_uuid(),
    source_id uuid not null references crawl_sources(id) on delete cascade,
    status text not null default 'pending',
    started_at timestamptz,
    completed_at timestamptz,
    pages_found int not null default 0,
    pages_crawled int not null default 0,
    pages_failed int not null default 0,
    error text,
    created_at timestamptz not null default now(),

    constraint valid_run_status check (status in ('pending', 'running', 'completed', 'failed'))
);

-- Indexes for common queries
create index crawl_sources_domain_idx on crawl_sources(domain);
create index crawl_sources_status_idx on crawl_sources(status);
create index crawl_sources_next_run_idx on crawl_sources(next_run_at) where status = 'active';

create index crawl_runs_source_idx on crawl_runs(source_id);
create index crawl_runs_status_idx on crawl_runs(status);
create index crawl_runs_created_idx on crawl_runs(created_at desc);

-- Pages: crawled content with version history
create table crawled_pages (
    id uuid primary key default gen_random_uuid(),
    run_id uuid not null references crawl_runs(id) on delete cascade,
    source_id uuid not null references crawl_sources(id) on delete cascade,
    url text not null,
    url_hash text not null,
    content_hash text,
    content text,
    status_code int,
    error text,
    crawled_at timestamptz not null default now()
);

create index crawled_pages_url_hash_idx on crawled_pages(url_hash);
create index crawled_pages_source_idx on crawled_pages(source_id);
create index crawled_pages_run_idx on crawled_pages(run_id);
create index crawled_pages_crawled_at_idx on crawled_pages(crawled_at desc);
create index crawled_pages_url_latest_idx on crawled_pages(url_hash, crawled_at desc);

-- Parsed pages: processed content from raw HTML
create table parsed_pages (
    id uuid primary key default gen_random_uuid(),
    page_id uuid not null unique references crawled_pages(id) on delete cascade,
    title text,
    description text,
    markdown text,
    metadata jsonb,
    word_count int,
    parsed_at timestamptz not null default now(),
    parser_version text not null default '1.0'
);

create index parsed_pages_page_idx on parsed_pages(page_id);
create index parsed_pages_parsed_at_idx on parsed_pages(parsed_at desc);

-- Queue: distributed crawl queue for multiple workers
create table crawl_queue (
    id uuid primary key default gen_random_uuid(),
    run_id uuid not null references crawl_runs(id) on delete cascade,
    url text not null,
    url_hash text not null,
    priority int not null default 0,
    depth int not null default 0,
    status text not null default 'pending',
    worker_id text,
    claimed_at timestamptz,
    attempts int not null default 0,
    max_attempts int not null default 3,
    created_at timestamptz not null default now(),

    constraint valid_queue_status check (status in ('pending', 'processing', 'completed', 'failed'))
);

create unique index crawl_queue_run_url_idx on crawl_queue(run_id, url_hash);

create index crawl_queue_pending_idx on crawl_queue(run_id, priority desc, created_at)
    where status = 'pending';

create index crawl_queue_stale_idx on crawl_queue(claimed_at)
    where status = 'processing';

-- Enable RLS on all tables
alter table crawl_sources enable row level security;
alter table crawl_runs enable row level security;
alter table crawled_pages enable row level security;
alter table parsed_pages enable row level security;
alter table crawl_queue enable row level security;

-- RPC: Atomically claim queue items using FOR UPDATE SKIP LOCKED
create or replace function claim_queue_items(
    p_run_id uuid,
    p_worker_id text,
    p_limit int default 10
)
returns setof crawl_queue
language plpgsql
as $$
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
$$;

-- RPC: Reset stale queue items that have been processing too long
create or replace function reset_stale_queue_items(
    p_timeout_minutes int default 5
)
returns int
language plpgsql
as $$
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
$$;

-- RPC: Get crawled pages that haven't been parsed yet
create or replace function get_unparsed_pages(
    p_limit int default 100
)
returns setof crawled_pages
language sql
as $$
    select cp.*
    from crawled_pages cp
    left join parsed_pages pp on pp.page_id = cp.id
    where pp.id is null and cp.content is not null
    order by cp.crawled_at desc
    limit p_limit;
$$;
