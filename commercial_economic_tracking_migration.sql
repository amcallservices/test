-- SCRITTORE SITE — cartelline economiche per operazioni AI
-- Esegui una sola volta nel SQL Editor di Supabase, dopo le migrazioni
-- commercial_ai_usage_migration.sql e commercial_ai_usage_pricing_migration.sql.
-- Non modifica saldi, pagamenti, crediti, manoscritti, prompt o utenti.

alter table public.writer_ai_usage_events
  add column if not exists macro_operation_id text not null default '',
  add column if not exists parent_reference text not null default '',
  add column if not exists user_category text not null default 'legacy_unknown',
  add column if not exists billing_status text not null default 'legacy_unknown',
  add column if not exists event_kind text not null default 'api_call',
  add column if not exists session_fingerprint text not null default '',
  add column if not exists project_fingerprint text not null default '',
  add column if not exists deepseek_units_estimated integer not null default 0 check (deepseek_units_estimated >= 0),
  add column if not exists charged_value_eur numeric(14, 6) not null default 0 check (charged_value_eur >= 0),
  add column if not exists input_cost_usd numeric(14, 8) not null default 0 check (input_cost_usd >= 0),
  add column if not exists cached_input_cost_usd numeric(14, 8) not null default 0 check (cached_input_cost_usd >= 0),
  add column if not exists output_cost_usd numeric(14, 8) not null default 0 check (output_cost_usd >= 0),
  add column if not exists web_cost_usd numeric(14, 8) not null default 0 check (web_cost_usd >= 0),
  add column if not exists cost_currency text not null default 'USD',
  add column if not exists duration_ms integer not null default 0 check (duration_ms >= 0),
  add column if not exists retry_of text not null default '';

create index if not exists writer_ai_usage_events_macro_operation_idx
  on public.writer_ai_usage_events (macro_operation_id, created_at desc)
  where macro_operation_id <> '';

create index if not exists writer_ai_usage_events_economic_status_idx
  on public.writer_ai_usage_events (user_category, billing_status, created_at desc);

create index if not exists writer_ai_usage_events_project_fingerprint_idx
  on public.writer_ai_usage_events (project_fingerprint, created_at desc)
  where project_fingerprint <> '';

-- Le righe già esistenti non possono essere attribuite con certezza a una
-- sessione, a un progetto o a un tipo di utente: restano quindi dichiarate
-- esplicitamente come storico non classificato invece di essere indovinate.
update public.writer_ai_usage_events
set
  user_category = case
    when user_category = '' then 'legacy_unknown'
    else user_category
  end,
  billing_status = case
    when billing_status = '' then 'legacy_unknown'
    else billing_status
  end,
  event_kind = case
    when event_kind = '' then 'api_call'
    else event_kind
  end,
  cost_currency = case
    when cost_currency = '' then 'USD'
    else cost_currency
  end
where user_category = ''
   or billing_status = ''
   or event_kind = ''
   or cost_currency = '';

-- La service role dell'app continua a scrivere il registro; anon e
-- authenticated non ricevono alcun nuovo permesso di lettura o scrittura.
revoke all on table public.writer_ai_usage_events from anon, authenticated;
