-- SCRITTORE SITE — monitoraggio tecnico dei consumi AI
-- Esegui una sola volta nel SQL Editor di Supabase, dopo commercial_setup.sql.
-- Non vengono salvati prompt, risposte o contenuti dei libri.

create table if not exists public.writer_ai_usage_events (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.writer_profiles(id) on delete cascade,
  reference text not null,
  provider text not null,
  model text not null,
  operation text not null,
  input_tokens integer not null default 0 check (input_tokens >= 0),
  output_tokens integer not null default 0 check (output_tokens >= 0),
  cached_input_tokens integer not null default 0 check (cached_input_tokens >= 0),
  reasoning_tokens integer not null default 0 check (reasoning_tokens >= 0),
  credits_requested integer not null default 0 check (credits_requested >= 0),
  credits_charged integer not null default 0 check (credits_charged >= 0),
  deepseek_units integer not null default 0 check (deepseek_units >= 0),
  estimated_cost_usd numeric(14, 8) not null default 0 check (estimated_cost_usd >= 0),
  success boolean not null default true,
  error_code text not null default '',
  created_at timestamptz not null default now(),
  unique (user_id, reference)
);

create index if not exists writer_ai_usage_events_created_at_idx
  on public.writer_ai_usage_events (created_at desc);
create index if not exists writer_ai_usage_events_operation_idx
  on public.writer_ai_usage_events (operation, created_at desc);

alter table public.writer_ai_usage_events enable row level security;

-- Nessun utente può leggere o scrivere il registro: l'app usa la service role
-- lato server e lo mostra esclusivamente agli indirizzi amministratore.
revoke all on table public.writer_ai_usage_events from anon, authenticated;

-- RECUPERO STORICO UNA TANTUM
-- Le prime righe GPT potevano riportare 0 crediti pur essendo state addebitate.
-- Questo aggiornamento legge esclusivamente il ledger esistente e corregge
-- soltanto la telemetria: non modifica saldi, pagamenti, crediti o contenuti.
with addebiti_ai as (
  select
    user_id,
    reference,
    sum(-delta)::integer as crediti_addebitati
  from public.writer_credit_ledger
  where delta < 0
  group by user_id, reference
)
update public.writer_ai_usage_events as utilizzo
set credits_charged = addebiti_ai.crediti_addebitati
from addebiti_ai
where utilizzo.user_id = addebiti_ai.user_id
  and utilizzo.reference = addebiti_ai.reference
  and utilizzo.success is true
  and utilizzo.provider like 'GPT%'
  and utilizzo.deepseek_units = 0
  and utilizzo.credits_charged = 0;
