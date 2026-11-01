-- Persist process_job summary (bank rec, coded counts, last_error) on the job.
-- Run on the Bridgit Supabase project (not live MA).

alter table ai_jobs add column if not exists engine jsonb;
