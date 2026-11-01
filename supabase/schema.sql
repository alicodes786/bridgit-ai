-- Bridgit Phase 1 starter schema.
-- Run on the NEW Bridgit Supabase project. Do not apply to live MA DB.

create extension if not exists pgcrypto;
create extension if not exists vector;

create table if not exists ai_clients (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  created_at timestamptz not null default now()
);

create table if not exists ai_jobs (
  id uuid primary key default gen_random_uuid(),
  client_id uuid references ai_clients (id),
  title text not null,
  status text not null default 'queued'
    check (status in (
      'queued',
      'processing',
      'needs_input',
      'ready_for_review',
      'approved'
    )),
  period text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists ai_job_events (
  id uuid primary key default gen_random_uuid(),
  job_id uuid not null references ai_jobs (id) on delete cascade,
  from_status text,
  to_status text not null,
  reason text,
  created_at timestamptz not null default now()
);

create table if not exists ai_documents (
  id uuid primary key default gen_random_uuid(),
  job_id uuid not null references ai_jobs (id) on delete cascade,
  kind text not null,
  file_name text not null,
  storage_path text,
  created_at timestamptz not null default now()
);

create table if not exists ai_transactions (
  id uuid primary key default gen_random_uuid(),
  job_id uuid not null references ai_jobs (id) on delete cascade,
  txn_date date,
  description text not null,
  reference text,
  amount numeric(14, 2) not null,
  debit_credit text check (debit_credit in ('debit', 'credit')),
  source_row int,
  source_page int,
  created_at timestamptz not null default now()
);

alter table ai_transactions add column if not exists source_page int;

create table if not exists ai_transaction_classifications (
  id uuid primary key default gen_random_uuid(),
  transaction_id uuid not null references ai_transactions (id) on delete cascade,
  account_code text,
  account_name text,
  vat_code text,
  confidence numeric(5, 2),
  source text not null
    check (source in ('mapping', 'firm_rule', 'llm', 'human')),
  reason text,
  needs_review boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists ai_exceptions (
  id uuid primary key default gen_random_uuid(),
  job_id uuid not null references ai_jobs (id) on delete cascade,
  transaction_id uuid references ai_transactions (id) on delete cascade,
  question text not null,
  status text not null default 'open' check (status in ('open', 'resolved')),
  answer text,
  created_at timestamptz not null default now(),
  resolved_at timestamptz
);

create table if not exists ai_mappings (
  id uuid primary key default gen_random_uuid(),
  client_id uuid references ai_clients (id),
  description_pattern text not null,
  account_code text not null,
  account_name text,
  vat_code text,
  status text not null default 'approved' check (status in ('proposed', 'approved')),
  created_at timestamptz not null default now()
);

create table if not exists firm_rules (
  id uuid primary key default gen_random_uuid(),
  rule_key text not null,
  rule_value text not null,
  status text not null default 'approved' check (status in ('proposed', 'approved')),
  created_at timestamptz not null default now()
);

create table if not exists ai_audit_log (
  id uuid primary key default gen_random_uuid(),
  job_id uuid references ai_jobs (id) on delete cascade,
  transaction_id uuid references ai_transactions (id) on delete cascade,
  event_type text not null,
  detail jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists knowledge_chunks (
  id uuid primary key default gen_random_uuid(),
  client_id uuid references ai_clients (id),
  job_id uuid references ai_jobs (id),
  content text not null,
  embedding vector(1536),
  created_at timestamptz not null default now()
);

create index if not exists ai_jobs_status_idx on ai_jobs (status);
create index if not exists ai_transactions_job_idx on ai_transactions (job_id);
create index if not exists ai_exceptions_job_idx on ai_exceptions (job_id);
create index if not exists ai_mappings_client_idx on ai_mappings (client_id);

alter table ai_jobs add column if not exists job_type text;
alter table ai_jobs add column if not exists period_start date;
alter table ai_jobs add column if not exists period_end date;
alter table ai_jobs add column if not exists intake jsonb;
alter table ai_jobs add column if not exists engine jsonb;
alter table ai_jobs add column if not exists chat jsonb;

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

-- Private bucket for bank files. Service role bypasses Storage RLS.
insert into storage.buckets (id, name, public, file_size_limit)
values ('ai-documents', 'ai-documents', false, 52428800)
on conflict (id) do nothing;

