-- Apply once in Supabase before starting the updated Acceptance worker.
-- No messages are queued or sent by these functions.
begin;
alter table public.outreach_job_targets
  add column if not exists ready_first_name text,
  add column if not exists auto_message_dismissed boolean not null default false;
alter table public.outreach_message_targets add column if not exists first_name text;

create table if not exists public.outreach_ready_notifications (
  batch_id uuid primary key references public.outreach_message_batches(id) on delete cascade,
  source_connect_batch_id uuid not null references public.outreach_jobs(id),
  label text not null,
  recipient_count integer not null check (recipient_count > 0),
  created_at timestamptz not null default now(),
  seen_at timestamptz
);
alter table public.outreach_ready_notifications enable row level security;
revoke all on public.outreach_ready_notifications from anon, authenticated;
grant all on public.outreach_ready_notifications to service_role;

-- Serialize preparations of the same prospect, including manual Prepare.
-- Existing duplicates are not modified by this migration.
create or replace function public.guard_outreach_ready_recipient() returns trigger
language plpgsql set search_path = public as $$
begin
  if new.status = 'prepared' and new.prospect_id is not null then
    perform pg_advisory_xact_lock(hashtextextended(new.prospect_id::text, 731));
    if exists (select 1 from public.outreach_message_targets t
               where t.prospect_id = new.prospect_id and t.id <> new.id
               and t.status in ('prepared', 'queued', 'processing', 'sent')) then
      raise exception 'Recipient already prepared, queued, processing or sent';
    end if;
  end if;
  return new;
end $$;
drop trigger if exists guard_outreach_ready_recipient on public.outreach_message_targets;
create trigger guard_outreach_ready_recipient before insert on public.outreach_message_targets
for each row execute function public.guard_outreach_ready_recipient();

create or replace function public.prepare_outreach_ready_batch(
  p_source_id uuid, p_campaign_id text, p_template text, p_targets jsonb
) returns jsonb language plpgsql security definer set search_path = public as $$
declare
  v_id uuid := gen_random_uuid();
  v_items jsonb := '[]'::jsonb;
  v_item jsonb;
  v_count integer;
  v_label text;
begin
  if nullif(trim(p_template), '') is null or jsonb_typeof(p_targets) <> 'array'
     or jsonb_array_length(p_targets) > 200 then
    raise exception 'Invalid Ready batch payload';
  end if;
  perform pg_advisory_xact_lock(hashtextextended('outreach-auto-ready', 731));
  select coalesce(nullif(j.batch_name, ''), to_char(j.created_at at time zone 'Asia/Ho_Chi_Minh','DD/MM/YYYY'))
         || ' - ' || coalesce(j.display_name, '') into v_label
  from public.outreach_jobs j where j.id = p_source_id;
  if v_label is null then raise exception 'Source Connect batch not found'; end if;
  for v_item in select value from jsonb_array_elements(p_targets) order by value->>'prospect_id' loop
    perform pg_advisory_xact_lock(hashtextextended(v_item->>'prospect_id', 731));
    if exists (select 1 from public.outreach_job_targets t
               join public.outreach_prospects p on p.id = t.prospect_id
               where t.id = (v_item->>'source_target_id')::uuid and t.job_id = p_source_id
                 and t.prospect_id = (v_item->>'prospect_id')::uuid
                 and t.assigned_account_id = v_item->>'assigned_account_id'
                 and p.linkedin_url = v_item->>'linkedin_url'
                 and t.status = 'completed' and p.connect_status = 'invitation_sent'
                 and t.acceptance_status = 'accepted' and not t.auto_message_dismissed
                 and nullif(trim(t.ready_first_name), '') is not null
                 and t.ready_first_name = v_item->>'first_name')
       and nullif(trim(v_item->>'message_text'), '') is not null
       and not exists (select 1 from public.outreach_job_targets d
                       where d.prospect_id = (v_item->>'prospect_id')::uuid and d.auto_message_dismissed)
       and not exists (select 1 from public.outreach_message_targets m
                       where m.prospect_id = (v_item->>'prospect_id')::uuid) then
      v_items := v_items || jsonb_build_array(v_item);
    end if;
  end loop;
  v_count := jsonb_array_length(v_items);
  if v_count = 0 then return jsonb_build_object('created', false); end if;
  insert into public.outreach_message_batches(id, batch_code, status, message_template, target_count, created_at, updated_at)
  values(v_id, 'MSG-AUTO-' || v_id::text, 'prepared', p_template, v_count, now(), now());
  insert into public.outreach_message_targets(batch_id, prospect_id, source_target_id, assigned_account_id,
                                             linkedin_url, normalized_url, first_name, message_text, status, created_at, updated_at)
  select v_id, (x->>'prospect_id')::uuid, (x->>'source_target_id')::uuid, x->>'assigned_account_id',
         x->>'linkedin_url', nullif(x->>'normalized_url',''), x->>'first_name', x->>'message_text', 'prepared', now(), now()
  from jsonb_array_elements(v_items) x;
  insert into public.outreach_ready_notifications(batch_id, source_connect_batch_id, label, recipient_count)
  values(v_id, p_source_id, v_label, v_count);
  return jsonb_build_object('created', true, 'batch_id', v_id, 'target_count', v_count);
end $$;

create or replace function public.delete_outreach_ready_batches(p_batch_ids uuid[])
returns jsonb language plpgsql security definer set search_path = public as $$
declare v_count integer;
begin
  if coalesce(cardinality(p_batch_ids), 0) not between 1 and 200 then
    raise exception 'Select between 1 and 200 Ready batches';
  end if;
  perform pg_advisory_xact_lock(hashtextextended('outreach-auto-ready', 731));
  perform 1 from public.outreach_message_batches where id = any(p_batch_ids) order by id for update;
  select count(*) into v_count from public.outreach_message_batches b
  join public.outreach_ready_notifications n on n.batch_id = b.id
  where b.id = any(p_batch_ids) and b.status = 'prepared';
  if v_count <> cardinality(p_batch_ids) or exists (
    select 1 from public.outreach_message_targets t where t.batch_id = any(p_batch_ids) and t.status <> 'prepared'
  ) then raise exception 'Only existing Ready batches with unsent drafts can be deleted'; end if;
  update public.outreach_job_targets set auto_message_dismissed = true
  where id in (select source_target_id from public.outreach_message_targets where batch_id = any(p_batch_ids));
  delete from public.outreach_message_targets where batch_id = any(p_batch_ids);
  delete from public.outreach_message_batches where id = any(p_batch_ids);
  return jsonb_build_object('deleted_count', v_count);
end $$;

revoke all on function public.prepare_outreach_ready_batch(uuid,text,text,jsonb) from public, anon, authenticated;
revoke all on function public.delete_outreach_ready_batches(uuid[]) from public, anon, authenticated;
grant execute on function public.prepare_outreach_ready_batch(uuid,text,text,jsonb) to service_role;
grant execute on function public.delete_outreach_ready_batches(uuid[]) to service_role;
notify pgrst, 'reload schema';
commit;
