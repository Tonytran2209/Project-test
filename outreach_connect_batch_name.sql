-- Run once in Supabase SQL Editor before deploying Connect batch naming.
-- Preserve the existing campaign name in display_name and technical ID in job_code.
alter table public.outreach_jobs
  add column if not exists batch_name text;

-- Backfill every previous Connect batch with its local run date.
update public.outreach_jobs
set batch_name = to_char(created_at at time zone 'Asia/Ho_Chi_Minh', 'DD/MM/YYYY')
where job_type = 'connect'
  and created_at is not null
  and nullif(btrim(batch_name), '') is null;

comment on column public.outreach_jobs.batch_name is
  'Human-readable Connect batch name; display_name remains the campaign name.';
