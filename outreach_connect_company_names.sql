-- Run in Supabase SQL Editor before using the Connect company-name column.
alter table public.outreach_prospects
  add column if not exists company_name text;

comment on column public.outreach_prospects.company_name is
  'Company supplied at Connect import, paired with the profile URL by input row.';

notify pgrst, 'reload schema';
