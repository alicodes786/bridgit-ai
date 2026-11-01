-- Run this in the Bridgit Supabase SQL editor if schema.sql was applied
-- before the storage bucket existed.

insert into storage.buckets (id, name, public, file_size_limit)
values ('ai-documents', 'ai-documents', false, 52428800)
on conflict (id) do nothing;
