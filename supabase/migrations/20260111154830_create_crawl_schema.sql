
  create table "public"."crawl_queue" (
    "id" uuid not null default gen_random_uuid(),
    "run_id" uuid not null,
    "url" text not null,
    "url_hash" text not null,
    "priority" integer not null default 0,
    "depth" integer not null default 0,
    "status" text not null default 'pending'::text,
    "worker_id" text,
    "claimed_at" timestamp with time zone,
    "attempts" integer not null default 0,
    "max_attempts" integer not null default 3,
    "created_at" timestamp with time zone not null default now()
      );



  create table "public"."crawl_runs" (
    "id" uuid not null default gen_random_uuid(),
    "source_id" uuid not null,
    "status" text not null default 'pending'::text,
    "started_at" timestamp with time zone,
    "completed_at" timestamp with time zone,
    "pages_found" integer not null default 0,
    "pages_crawled" integer not null default 0,
    "pages_failed" integer not null default 0,
    "error" text,
    "created_at" timestamp with time zone not null default now()
      );



  create table "public"."crawl_sources" (
    "id" uuid not null default gen_random_uuid(),
    "domain" text not null,
    "entry_url" text not null,
    "type" text not null,
    "frequency" text not null default 'once'::text,
    "max_pages" integer,
    "status" text not null default 'active'::text,
    "created_at" timestamp with time zone not null default now(),
    "next_run_at" timestamp with time zone
      );



  create table "public"."crawled_pages" (
    "id" uuid not null default gen_random_uuid(),
    "run_id" uuid not null,
    "source_id" uuid not null,
    "url" text not null,
    "url_hash" text not null,
    "content_hash" text,
    "content" text,
    "status_code" integer,
    "error" text,
    "crawled_at" timestamp with time zone not null default now()
      );



  create table "public"."parsed_pages" (
    "id" uuid not null default gen_random_uuid(),
    "page_id" uuid not null,
    "title" text,
    "description" text,
    "markdown" text,
    "metadata" jsonb,
    "word_count" integer,
    "parsed_at" timestamp with time zone not null default now(),
    "parser_version" text not null default '1.0'::text
      );


CREATE INDEX crawl_queue_pending_idx ON public.crawl_queue USING btree (run_id, priority DESC, created_at) WHERE (status = 'pending'::text);

CREATE UNIQUE INDEX crawl_queue_pkey ON public.crawl_queue USING btree (id);

CREATE UNIQUE INDEX crawl_queue_run_url_idx ON public.crawl_queue USING btree (run_id, url_hash);

CREATE INDEX crawl_queue_stale_idx ON public.crawl_queue USING btree (claimed_at) WHERE (status = 'processing'::text);

CREATE INDEX crawl_runs_created_idx ON public.crawl_runs USING btree (created_at DESC);

CREATE UNIQUE INDEX crawl_runs_pkey ON public.crawl_runs USING btree (id);

CREATE INDEX crawl_runs_source_idx ON public.crawl_runs USING btree (source_id);

CREATE INDEX crawl_runs_status_idx ON public.crawl_runs USING btree (status);

CREATE INDEX crawl_sources_domain_idx ON public.crawl_sources USING btree (domain);

CREATE INDEX crawl_sources_next_run_idx ON public.crawl_sources USING btree (next_run_at) WHERE (status = 'active'::text);

CREATE UNIQUE INDEX crawl_sources_pkey ON public.crawl_sources USING btree (id);

CREATE INDEX crawl_sources_status_idx ON public.crawl_sources USING btree (status);

CREATE INDEX crawled_pages_crawled_at_idx ON public.crawled_pages USING btree (crawled_at DESC);

CREATE UNIQUE INDEX crawled_pages_pkey ON public.crawled_pages USING btree (id);

CREATE INDEX crawled_pages_run_idx ON public.crawled_pages USING btree (run_id);

CREATE INDEX crawled_pages_source_idx ON public.crawled_pages USING btree (source_id);

CREATE INDEX crawled_pages_url_hash_idx ON public.crawled_pages USING btree (url_hash);

CREATE INDEX crawled_pages_url_latest_idx ON public.crawled_pages USING btree (url_hash, crawled_at DESC);

CREATE UNIQUE INDEX parsed_pages_page_id_key ON public.parsed_pages USING btree (page_id);

CREATE INDEX parsed_pages_page_idx ON public.parsed_pages USING btree (page_id);

CREATE INDEX parsed_pages_parsed_at_idx ON public.parsed_pages USING btree (parsed_at DESC);

CREATE UNIQUE INDEX parsed_pages_pkey ON public.parsed_pages USING btree (id);

alter table "public"."crawl_queue" add constraint "crawl_queue_pkey" PRIMARY KEY using index "crawl_queue_pkey";

alter table "public"."crawl_runs" add constraint "crawl_runs_pkey" PRIMARY KEY using index "crawl_runs_pkey";

alter table "public"."crawl_sources" add constraint "crawl_sources_pkey" PRIMARY KEY using index "crawl_sources_pkey";

alter table "public"."crawled_pages" add constraint "crawled_pages_pkey" PRIMARY KEY using index "crawled_pages_pkey";

alter table "public"."parsed_pages" add constraint "parsed_pages_pkey" PRIMARY KEY using index "parsed_pages_pkey";

alter table "public"."crawl_queue" add constraint "crawl_queue_run_id_fkey" FOREIGN KEY (run_id) REFERENCES public.crawl_runs(id) ON DELETE CASCADE not valid;

alter table "public"."crawl_queue" validate constraint "crawl_queue_run_id_fkey";

alter table "public"."crawl_queue" add constraint "valid_queue_status" CHECK ((status = ANY (ARRAY['pending'::text, 'processing'::text, 'completed'::text, 'failed'::text]))) not valid;

alter table "public"."crawl_queue" validate constraint "valid_queue_status";

alter table "public"."crawl_runs" add constraint "crawl_runs_source_id_fkey" FOREIGN KEY (source_id) REFERENCES public.crawl_sources(id) ON DELETE CASCADE not valid;

alter table "public"."crawl_runs" validate constraint "crawl_runs_source_id_fkey";

alter table "public"."crawl_runs" add constraint "valid_run_status" CHECK ((status = ANY (ARRAY['pending'::text, 'running'::text, 'completed'::text, 'failed'::text]))) not valid;

alter table "public"."crawl_runs" validate constraint "valid_run_status";

alter table "public"."crawl_sources" add constraint "valid_max_pages" CHECK (((max_pages IS NULL) OR (max_pages > 0))) not valid;

alter table "public"."crawl_sources" validate constraint "valid_max_pages";

alter table "public"."crawl_sources" add constraint "valid_status" CHECK ((status = ANY (ARRAY['active'::text, 'paused'::text]))) not valid;

alter table "public"."crawl_sources" validate constraint "valid_status";

alter table "public"."crawl_sources" add constraint "valid_type" CHECK ((type = ANY (ARRAY['single_page'::text, 'full_domain'::text]))) not valid;

alter table "public"."crawl_sources" validate constraint "valid_type";

alter table "public"."crawled_pages" add constraint "crawled_pages_run_id_fkey" FOREIGN KEY (run_id) REFERENCES public.crawl_runs(id) ON DELETE CASCADE not valid;

alter table "public"."crawled_pages" validate constraint "crawled_pages_run_id_fkey";

alter table "public"."crawled_pages" add constraint "crawled_pages_source_id_fkey" FOREIGN KEY (source_id) REFERENCES public.crawl_sources(id) ON DELETE CASCADE not valid;

alter table "public"."crawled_pages" validate constraint "crawled_pages_source_id_fkey";

alter table "public"."parsed_pages" add constraint "parsed_pages_page_id_fkey" FOREIGN KEY (page_id) REFERENCES public.crawled_pages(id) ON DELETE CASCADE not valid;

alter table "public"."parsed_pages" validate constraint "parsed_pages_page_id_fkey";

alter table "public"."parsed_pages" add constraint "parsed_pages_page_id_key" UNIQUE using index "parsed_pages_page_id_key";

grant delete on table "public"."crawl_queue" to "anon";

grant insert on table "public"."crawl_queue" to "anon";

grant references on table "public"."crawl_queue" to "anon";

grant select on table "public"."crawl_queue" to "anon";

grant trigger on table "public"."crawl_queue" to "anon";

grant truncate on table "public"."crawl_queue" to "anon";

grant update on table "public"."crawl_queue" to "anon";

grant delete on table "public"."crawl_queue" to "authenticated";

grant insert on table "public"."crawl_queue" to "authenticated";

grant references on table "public"."crawl_queue" to "authenticated";

grant select on table "public"."crawl_queue" to "authenticated";

grant trigger on table "public"."crawl_queue" to "authenticated";

grant truncate on table "public"."crawl_queue" to "authenticated";

grant update on table "public"."crawl_queue" to "authenticated";

grant delete on table "public"."crawl_queue" to "service_role";

grant insert on table "public"."crawl_queue" to "service_role";

grant references on table "public"."crawl_queue" to "service_role";

grant select on table "public"."crawl_queue" to "service_role";

grant trigger on table "public"."crawl_queue" to "service_role";

grant truncate on table "public"."crawl_queue" to "service_role";

grant update on table "public"."crawl_queue" to "service_role";

grant delete on table "public"."crawl_runs" to "anon";

grant insert on table "public"."crawl_runs" to "anon";

grant references on table "public"."crawl_runs" to "anon";

grant select on table "public"."crawl_runs" to "anon";

grant trigger on table "public"."crawl_runs" to "anon";

grant truncate on table "public"."crawl_runs" to "anon";

grant update on table "public"."crawl_runs" to "anon";

grant delete on table "public"."crawl_runs" to "authenticated";

grant insert on table "public"."crawl_runs" to "authenticated";

grant references on table "public"."crawl_runs" to "authenticated";

grant select on table "public"."crawl_runs" to "authenticated";

grant trigger on table "public"."crawl_runs" to "authenticated";

grant truncate on table "public"."crawl_runs" to "authenticated";

grant update on table "public"."crawl_runs" to "authenticated";

grant delete on table "public"."crawl_runs" to "service_role";

grant insert on table "public"."crawl_runs" to "service_role";

grant references on table "public"."crawl_runs" to "service_role";

grant select on table "public"."crawl_runs" to "service_role";

grant trigger on table "public"."crawl_runs" to "service_role";

grant truncate on table "public"."crawl_runs" to "service_role";

grant update on table "public"."crawl_runs" to "service_role";

grant delete on table "public"."crawl_sources" to "anon";

grant insert on table "public"."crawl_sources" to "anon";

grant references on table "public"."crawl_sources" to "anon";

grant select on table "public"."crawl_sources" to "anon";

grant trigger on table "public"."crawl_sources" to "anon";

grant truncate on table "public"."crawl_sources" to "anon";

grant update on table "public"."crawl_sources" to "anon";

grant delete on table "public"."crawl_sources" to "authenticated";

grant insert on table "public"."crawl_sources" to "authenticated";

grant references on table "public"."crawl_sources" to "authenticated";

grant select on table "public"."crawl_sources" to "authenticated";

grant trigger on table "public"."crawl_sources" to "authenticated";

grant truncate on table "public"."crawl_sources" to "authenticated";

grant update on table "public"."crawl_sources" to "authenticated";

grant delete on table "public"."crawl_sources" to "service_role";

grant insert on table "public"."crawl_sources" to "service_role";

grant references on table "public"."crawl_sources" to "service_role";

grant select on table "public"."crawl_sources" to "service_role";

grant trigger on table "public"."crawl_sources" to "service_role";

grant truncate on table "public"."crawl_sources" to "service_role";

grant update on table "public"."crawl_sources" to "service_role";

grant delete on table "public"."crawled_pages" to "anon";

grant insert on table "public"."crawled_pages" to "anon";

grant references on table "public"."crawled_pages" to "anon";

grant select on table "public"."crawled_pages" to "anon";

grant trigger on table "public"."crawled_pages" to "anon";

grant truncate on table "public"."crawled_pages" to "anon";

grant update on table "public"."crawled_pages" to "anon";

grant delete on table "public"."crawled_pages" to "authenticated";

grant insert on table "public"."crawled_pages" to "authenticated";

grant references on table "public"."crawled_pages" to "authenticated";

grant select on table "public"."crawled_pages" to "authenticated";

grant trigger on table "public"."crawled_pages" to "authenticated";

grant truncate on table "public"."crawled_pages" to "authenticated";

grant update on table "public"."crawled_pages" to "authenticated";

grant delete on table "public"."crawled_pages" to "service_role";

grant insert on table "public"."crawled_pages" to "service_role";

grant references on table "public"."crawled_pages" to "service_role";

grant select on table "public"."crawled_pages" to "service_role";

grant trigger on table "public"."crawled_pages" to "service_role";

grant truncate on table "public"."crawled_pages" to "service_role";

grant update on table "public"."crawled_pages" to "service_role";

grant delete on table "public"."parsed_pages" to "anon";

grant insert on table "public"."parsed_pages" to "anon";

grant references on table "public"."parsed_pages" to "anon";

grant select on table "public"."parsed_pages" to "anon";

grant trigger on table "public"."parsed_pages" to "anon";

grant truncate on table "public"."parsed_pages" to "anon";

grant update on table "public"."parsed_pages" to "anon";

grant delete on table "public"."parsed_pages" to "authenticated";

grant insert on table "public"."parsed_pages" to "authenticated";

grant references on table "public"."parsed_pages" to "authenticated";

grant select on table "public"."parsed_pages" to "authenticated";

grant trigger on table "public"."parsed_pages" to "authenticated";

grant truncate on table "public"."parsed_pages" to "authenticated";

grant update on table "public"."parsed_pages" to "authenticated";

grant delete on table "public"."parsed_pages" to "service_role";

grant insert on table "public"."parsed_pages" to "service_role";

grant references on table "public"."parsed_pages" to "service_role";

grant select on table "public"."parsed_pages" to "service_role";

grant trigger on table "public"."parsed_pages" to "service_role";

grant truncate on table "public"."parsed_pages" to "service_role";

grant update on table "public"."parsed_pages" to "service_role";

alter table "public"."crawl_sources" enable row level security;
alter table "public"."crawl_runs" enable row level security;
alter table "public"."crawled_pages" enable row level security;
alter table "public"."parsed_pages" enable row level security;
alter table "public"."crawl_queue" enable row level security;


