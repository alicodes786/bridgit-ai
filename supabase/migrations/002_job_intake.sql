-- Week 1b intake: job type, period dates, client rules.
-- Run on the Bridgit Supabase project (not live MA).

alter table ai_jobs add column if not exists job_type text;
alter table ai_jobs add column if not exists period_start date;
alter table ai_jobs add column if not exists period_end date;
alter table ai_jobs add column if not exists intake jsonb;

create table if not exists client_rules (
  id uuid primary key default gen_random_uuid(),
  client_id uuid references ai_clients (id),
  job_type text,
  rule_key text not null,
  rule_value text not null,
  status text not null default 'approved' check (status in ('proposed', 'approved')),
  created_at timestamptz not null default now()
);

create index if not exists client_rules_client_idx on client_rules (client_id);
