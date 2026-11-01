-- Chat transcript on a job (Cards vs Chat toggle in /app).
-- Run on the Bridgit Supabase project.

alter table ai_jobs add column if not exists chat jsonb;
