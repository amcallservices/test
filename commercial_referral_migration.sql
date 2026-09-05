-- SCRITTORE SITE — PROGRAMMA REFERRAL
-- Esegui UNA SOLA VOLTA nel SQL Editor di Supabase, dopo commercial_setup.sql.
-- Questa migrazione aggiunge soltanto le strutture del referral: non altera
-- saldi esistenti, pagamenti passati o funzioni della scrittura.

-- Un codice personale, non riconducibile all'email, per ogni account.
create table if not exists public.writer_referral_codes (
  user_id uuid primary key references public.writer_profiles(id) on delete cascade,
  code text not null unique check (code ~ '^SS[A-Z0-9]{10}$'),
  created_at timestamptz not null default now()
);

-- Un invito può essere associato una sola volta all'account invitato.
-- Il pagamento qualificante e i premi restano registrati per audit e idempotenza.
create table if not exists public.writer_referrals (
  referred_user_id uuid primary key references public.writer_profiles(id) on delete cascade,
  referrer_user_id uuid not null references public.writer_profiles(id) on delete cascade,
  referral_code text not null,
  status text not null default 'pending'
    check (status in ('pending', 'rewarded', 'not_eligible')),
  qualified_session_id text unique references public.writer_payments(stripe_checkout_session_id) on delete set null,
  qualified_package_key text,
  referrer_credits integer not null default 0 check (referrer_credits >= 0),
  referred_credits integer not null default 0 check (referred_credits >= 0),
  created_at timestamptz not null default now(),
  rewarded_at timestamptz,
  check (referrer_user_id <> referred_user_id)
);

create index if not exists writer_referrals_referrer_idx
  on public.writer_referrals (referrer_user_id, created_at desc);

alter table public.writer_referral_codes enable row level security;
alter table public.writer_referrals enable row level security;

drop policy if exists "referral_code_owner_read" on public.writer_referral_codes;
create policy "referral_code_owner_read" on public.writer_referral_codes
  for select using (auth.uid() = user_id);

drop policy if exists "referral_owner_read" on public.writer_referrals;
create policy "referral_owner_read" on public.writer_referrals
  for select using (auth.uid() = referred_user_id or auth.uid() = referrer_user_id);

-- Genera un codice breve, casuale e condivisibile. La verifica di unicità
-- impedisce collisioni anche nel caso estremamente raro di due codici uguali.
create or replace function public.writer_new_referral_code()
returns text language plpgsql security definer set search_path = public as $$
declare
  v_code text;
begin
  loop
    v_code := 'SS' || upper(substring(replace(gen_random_uuid()::text, '-', '') from 1 for 10));
    exit when not exists (
      select 1 from public.writer_referral_codes where code = v_code
    );
  end loop;
  return v_code;
end;
$$;

create or replace function public.ensure_writer_referral_code(p_user_id uuid)
returns text language plpgsql security definer set search_path = public as $$
declare
  v_code text;
begin
  select code into v_code
  from public.writer_referral_codes
  where user_id = p_user_id;

  if v_code is not null then
    return v_code;
  end if;

  loop
    v_code := public.writer_new_referral_code();
    begin
      insert into public.writer_referral_codes (user_id, code)
      values (p_user_id, v_code);
      return v_code;
    exception when unique_violation then
      -- Se la collisione riguarda l'utente, rileggiamo il codice già creato;
      -- se riguarda il codice casuale, il ciclo ne genera un altro.
      select code into v_code
      from public.writer_referral_codes
      where user_id = p_user_id;
      if v_code is not null then
        return v_code;
      end if;
    end;
  end loop;
end;
$$;

-- Crea il codice anche per gli account registrati prima dell'introduzione
-- del referral. Non assegna alcun premio.
do $$
declare
  v_user_id uuid;
begin
  for v_user_id in
    select id from public.writer_profiles order by created_at
  loop
    perform public.ensure_writer_referral_code(v_user_id);
  end loop;
end;
$$;

-- Ogni nuovo profilo riceverà automaticamente il proprio codice personale.
create or replace function public.create_writer_referral_code()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  perform public.ensure_writer_referral_code(new.id);
  return new;
end;
$$;

do $$
begin
  if not exists (
    select 1 from pg_trigger
    where tgname = 'writer_profiles_referral_code'
      and tgrelid = 'public.writer_profiles'::regclass
      and not tgisinternal
  ) then
    create trigger writer_profiles_referral_code
      after insert on public.writer_profiles
      for each row execute function public.create_writer_referral_code();
  end if;
end;
$$;

-- Collega il codice ricevuto all'account appena creato. Il legame è una sola
-- volta, non può essere auto-riferito e non può essere aggiunto dopo un
-- acquisto qualificante già eseguito.
create or replace function public.claim_writer_referral(
  p_referred_user_id uuid,
  p_code text
)
returns jsonb language plpgsql security definer set search_path = public as $$
declare
  v_code text;
  v_referrer_user_id uuid;
begin
  v_code := upper(regexp_replace(coalesce(p_code, ''), '[^A-Za-z0-9]', '', 'g'));
  if v_code !~ '^SS[A-Z0-9]{10}$' then
    return jsonb_build_object('ok', false, 'status', 'invalid_code');
  end if;

  select user_id into v_referrer_user_id
  from public.writer_referral_codes
  where code = v_code;
  if v_referrer_user_id is null then
    return jsonb_build_object('ok', false, 'status', 'invalid_code');
  end if;
  if v_referrer_user_id = p_referred_user_id then
    return jsonb_build_object('ok', false, 'status', 'self_referral');
  end if;
  if not exists (select 1 from public.writer_profiles where id = p_referred_user_id) then
    return jsonb_build_object('ok', false, 'status', 'profile_missing');
  end if;
  if exists (
    select 1 from public.writer_payments where user_id = p_referred_user_id
  ) then
    return jsonb_build_object('ok', false, 'status', 'purchase_already_exists');
  end if;

  insert into public.writer_referrals (
    referred_user_id, referrer_user_id, referral_code
  ) values (
    p_referred_user_id, v_referrer_user_id, v_code
  ) on conflict (referred_user_id) do nothing;

  if found then
    return jsonb_build_object('ok', true, 'status', 'claimed');
  end if;
  return jsonb_build_object('ok', false, 'status', 'already_claimed');
end;
$$;

-- Accredita i premi solo dopo che il webhook Stripe ha registrato il
-- pagamento. I valori sono fissati qui, quindi non possono essere alterati
-- dalla pagina web: Prova non dà premi; Base/Creator/Studio/Professionale sì.
create or replace function public.grant_writer_referral_rewards(
  p_session_id text,
  p_referred_user_id uuid
)
returns jsonb language plpgsql security definer set search_path = public as $$
declare
  v_package_key text;
  v_referrer_user_id uuid;
  v_status text;
  v_referral_code text;
  v_referrer_credits integer;
  v_referred_credits integer;
begin
  select package_key into v_package_key
  from public.writer_payments
  where stripe_checkout_session_id = p_session_id
    and user_id = p_referred_user_id
  for update;
  if not found then
    return jsonb_build_object('ok', false, 'status', 'payment_missing');
  end if;

  select referrer_user_id, status, referral_code
  into v_referrer_user_id, v_status, v_referral_code
  from public.writer_referrals
  where referred_user_id = p_referred_user_id
  for update;
  if not found then
    return jsonb_build_object('ok', false, 'status', 'no_referral');
  end if;
  if v_status <> 'pending' then
    return jsonb_build_object('ok', false, 'status', v_status);
  end if;
  if not exists (
    select 1 from public.writer_referral_codes
    where user_id = v_referrer_user_id and code = v_referral_code
  ) then
    update public.writer_referrals
    set status = 'not_eligible'
    where referred_user_id = p_referred_user_id;
    return jsonb_build_object('ok', false, 'status', 'invalid_referrer');
  end if;

  case v_package_key
    when 'base_150' then
      v_referrer_credits := 15;
      v_referred_credits := 10;
    when 'creator_375' then
      v_referrer_credits := 38;
      v_referred_credits := 15;
    when 'studio_750' then
      v_referrer_credits := 75;
      v_referred_credits := 30;
    when 'professionale_1500' then
      v_referrer_credits := 150;
      v_referred_credits := 50;
    else
      -- Il pacchetto Prova e i pacchetti storici non consumano il referral:
      -- l'invito resta pendente per un eventuale primo pacchetto ammesso.
      return jsonb_build_object('ok', false, 'status', 'package_not_eligible');
  end case;

  -- Il premio vale sul primo pacchetto ammesso: una Prova precedente non lo
  -- annulla, un precedente Base/Creator/Studio/Professionale sì.
  if exists (
    select 1 from public.writer_payments
    where user_id = p_referred_user_id
      and stripe_checkout_session_id <> p_session_id
      and package_key in ('base_150', 'creator_375', 'studio_750', 'professionale_1500')
  ) then
    update public.writer_referrals
    set status = 'not_eligible'
    where referred_user_id = p_referred_user_id;
    return jsonb_build_object('ok', false, 'status', 'not_first_eligible_purchase');
  end if;

  -- Blocca entrambi i saldi in ordine stabile prima di aggiornarli.
  perform 1 from public.writer_profiles
  where id in (v_referrer_user_id, p_referred_user_id)
  order by id for update;

  update public.writer_profiles
  set credits = credits + v_referrer_credits, updated_at = now()
  where id = v_referrer_user_id;
  update public.writer_profiles
  set credits = credits + v_referred_credits, updated_at = now()
  where id = p_referred_user_id;

  insert into public.writer_credit_ledger (user_id, delta, reason, reference)
  values (
    v_referrer_user_id,
    v_referrer_credits,
    'referral_reward_referrer',
    'referral:' || p_session_id
  ) on conflict (user_id, reference, reason) do nothing;

  insert into public.writer_credit_ledger (user_id, delta, reason, reference)
  values (
    p_referred_user_id,
    v_referred_credits,
    'referral_welcome_bonus',
    'referral:' || p_session_id
  ) on conflict (user_id, reference, reason) do nothing;

  update public.writer_referrals
  set status = 'rewarded',
      qualified_session_id = p_session_id,
      qualified_package_key = v_package_key,
      referrer_credits = v_referrer_credits,
      referred_credits = v_referred_credits,
      rewarded_at = now()
  where referred_user_id = p_referred_user_id;

  return jsonb_build_object(
    'ok', true,
    'status', 'rewarded',
    'referrer_credits', v_referrer_credits,
    'referred_credits', v_referred_credits
  );
end;
$$;

revoke all on function public.writer_new_referral_code() from public;
revoke all on function public.ensure_writer_referral_code(uuid) from public;
revoke all on function public.claim_writer_referral(uuid, text) from public;
revoke all on function public.grant_writer_referral_rewards(text, uuid) from public;
grant execute on function public.ensure_writer_referral_code(uuid) to service_role;
grant execute on function public.claim_writer_referral(uuid, text) to service_role;
grant execute on function public.grant_writer_referral_rewards(text, uuid) to service_role;
