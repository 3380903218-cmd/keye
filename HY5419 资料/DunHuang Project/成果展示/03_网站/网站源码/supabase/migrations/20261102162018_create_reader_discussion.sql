-- Public pseudonymous discussion, reached only through the Edge Function.
-- The private schema and RPCs are not accessible with browser API keys.
create schema discussion_private;
revoke all on schema discussion_private from public, anon, authenticated;
grant usage on schema discussion_private to service_role;

create table discussion_private.messages (
  id uuid primary key default gen_random_uuid(),
  client_id uuid not null unique,
  parent_id uuid references discussion_private.messages(id) on delete cascade,
  display_name text not null check (char_length(btrim(display_name)) between 1 and 32),
  body text not null check (char_length(btrim(body)) between 1 and 2000),
  category text not null default 'general'
    check (category in ('general','map','network','collections','sources')),
  created_at timestamptz not null default clock_timestamp(),
  hidden boolean not null default false
);
create index discussion_roots on discussion_private.messages(created_at desc, id desc)
  where parent_id is null and not hidden;
create index discussion_replies on discussion_private.messages(parent_id, created_at, id);
alter table discussion_private.messages enable row level security;
revoke all on discussion_private.messages from public, anon, authenticated;
grant select, insert, update on discussion_private.messages to service_role;

create table discussion_private.rate_buckets (
  key text primary key,
  window_start timestamptz not null,
  last_post timestamptz not null,
  posts integer not null
);
alter table discussion_private.rate_buckets enable row level security;
revoke all on discussion_private.rate_buckets from public, anon, authenticated;
grant select, insert, update, delete on discussion_private.rate_buckets to service_role;

create function discussion_private.take_slot(p_key text, p_max integer, p_gap interval)
returns void language plpgsql set search_path = '' as $$
declare b discussion_private.rate_buckets; t timestamptz := clock_timestamp();
begin
  select * into b from discussion_private.rate_buckets where key = p_key for update;
  if found and b.window_start > t - interval '10 minutes' then
    if b.posts >= p_max or b.last_post > t - p_gap then
      raise exception using message = 'rate_limit', errcode = 'P0001';
    end if;
    update discussion_private.rate_buckets set posts = posts + 1, last_post = t where key = p_key;
  else
    insert into discussion_private.rate_buckets values (p_key,t,t,1)
    on conflict (key) do update set window_start=t,last_post=t,posts=1;
  end if;
end $$;
revoke all on function discussion_private.take_slot(text,integer,interval) from public, anon, authenticated;
grant execute on function discussion_private.take_slot(text,integer,interval) to service_role;

create function discussion_private.render_thread(
  p_id uuid, p_reply_before timestamptz default null, p_reply_before_id uuid default null
) returns jsonb language sql stable set search_path = '' as $$
  with root as (
    select * from discussion_private.messages where id=p_id and parent_id is null and not hidden
  ), replies as (
    select r.* from discussion_private.messages r, root
    where r.parent_id=root.id and not r.hidden
      and (p_reply_before is null or (r.created_at,r.id) < (p_reply_before,p_reply_before_id))
    order by r.created_at desc,r.id desc limit 26
  ), visible as (select * from replies order by created_at desc,id desc limit 25)
  select jsonb_build_object(
    'id',m.id,'name',m.display_name,'body',m.body,'category',m.category,'createdAt',m.created_at,
    'replies',coalesce((select jsonb_agg(jsonb_build_object(
       'id',v.id,'name',v.display_name,'body',v.body,'createdAt',v.created_at
     ) order by v.created_at,v.id) from visible v),'[]'::jsonb),
    'replyCount',(select count(*) from discussion_private.messages r where r.parent_id=m.id and not r.hidden),
    'replyNext',case when (select count(*) from replies)>25 then
      (select jsonb_build_object('at',v.created_at,'id',v.id) from visible v order by v.created_at,v.id limit 1)
      else null end
  ) from root m;
$$;
revoke all on function discussion_private.render_thread(uuid,timestamptz,uuid) from public, anon, authenticated;
grant execute on function discussion_private.render_thread(uuid,timestamptz,uuid) to service_role;

create function public.dunhuang_discussion_list(
  p_before timestamptz default null, p_before_id uuid default null,
  p_thread_id uuid default null,
  p_reply_before timestamptz default null, p_reply_before_id uuid default null
) returns jsonb language plpgsql stable security invoker set search_path = '' as $$
declare result jsonb;
begin
  if p_thread_id is not null then
    result := discussion_private.render_thread(p_thread_id,p_reply_before,p_reply_before_id);
    return jsonb_build_object('threads',case when result is null then '[]'::jsonb else jsonb_build_array(result) end,'next',null);
  end if;
  if (p_before is null) <> (p_before_id is null) then raise exception 'invalid_cursor'; end if;
  with candidates as (
    select m.id,m.created_at from discussion_private.messages m
    where m.parent_id is null and not m.hidden
      and (p_before is null or (m.created_at,m.id) < (p_before,p_before_id))
    order by m.created_at desc,m.id desc limit 11
  ), visible as (select * from candidates order by created_at desc,id desc limit 10)
  select jsonb_build_object(
    'threads',coalesce((select jsonb_agg(discussion_private.render_thread(v.id) order by v.created_at desc,v.id desc) from visible v),'[]'::jsonb),
    'next',case when (select count(*) from candidates)>10 then
      (select jsonb_build_object('at',v.created_at,'id',v.id) from visible v order by v.created_at,v.id limit 1)
      else null end
  ) into result;
  return result;
end $$;
revoke all on function public.dunhuang_discussion_list(timestamptz,uuid,uuid,timestamptz,uuid) from public, anon, authenticated;
grant execute on function public.dunhuang_discussion_list(timestamptz,uuid,uuid,timestamptz,uuid) to service_role;

create function public.dunhuang_discussion_post(
  p_client_id uuid, p_thread_id uuid, p_name text, p_body text,
  p_category text, p_fingerprint text, p_network_hash text
) returns jsonb language plpgsql security invoker set search_path = '' as $$
declare existing discussion_private.messages; parent discussion_private.messages;
  new_id uuid; name_text text := btrim(p_name); body_text text := btrim(p_body);
begin
  if p_client_id is null or name_text is null or body_text is null
    or char_length(name_text) not between 1 and 32 or char_length(body_text) not between 1 and 2000
    or p_category is null or p_category not in ('general','map','network','collections','sources')
    or p_fingerprint is null or p_fingerprint !~ '^[0-9a-f]{64}$'
    or p_network_hash is null or p_network_hash !~ '^[0-9a-f]{64}$'
  then raise exception 'invalid_input'; end if;

  -- Serialise retries of one submission, then the looser network and visitor limits.
  perform pg_advisory_xact_lock(hashtextextended('dunhuang-client:'||p_client_id::text,0));
  select * into existing from discussion_private.messages where client_id=p_client_id;
  if found then
    if existing.hidden or existing.display_name<>name_text or existing.body<>body_text
      or existing.parent_id is distinct from p_thread_id then raise exception 'request_conflict'; end if;
    return jsonb_build_object('id',existing.id,'threadId',coalesce(existing.parent_id,existing.id),'duplicate',true);
  end if;
  if p_thread_id is not null then
    select * into parent from discussion_private.messages where id=p_thread_id and parent_id is null and not hidden for share;
    if not found then raise exception 'thread_unavailable'; end if;
    p_category:=parent.category;
  end if;
  perform pg_advisory_xact_lock(hashtextextended('dunhuang-network:'||p_network_hash,0));
  perform pg_advisory_xact_lock(hashtextextended('dunhuang-visitor:'||p_fingerprint,0));
  perform discussion_private.take_slot('network:'||p_network_hash,90,interval '0 seconds');
  perform discussion_private.take_slot('visitor:'||p_fingerprint,8,interval '5 seconds');
  delete from discussion_private.rate_buckets where window_start < clock_timestamp()-interval '48 hours';
  insert into discussion_private.messages(client_id,parent_id,display_name,body,category)
    values(p_client_id,p_thread_id,name_text,body_text,p_category) returning id into new_id;
  return jsonb_build_object('id',new_id,'threadId',coalesce(p_thread_id,new_id),'duplicate',false);
end $$;
revoke all on function public.dunhuang_discussion_post(uuid,uuid,text,text,text,text,text) from public, anon, authenticated;
grant execute on function public.dunhuang_discussion_post(uuid,uuid,text,text,text,text,text) to service_role;

comment on table discussion_private.messages is 'Public, unverified reader messages. Set hidden=true to moderate; hidden roots also hide their replies in the public API.';
comment on table discussion_private.rate_buckets is 'Non-public daily salted network/visitor hashes; expired windows are cleaned during subsequent writes. No plaintext IP addresses.';
