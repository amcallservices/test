-- SCRITTORE SITE — costi API calcolati con il listino ufficiale
-- Esegui una sola volta nel SQL Editor di Supabase.
-- Non modifica saldi, crediti, pagamenti, utenti o contenuti dei libri.

alter table public.writer_ai_usage_events
  add column if not exists web_search_calls integer not null default 0 check (web_search_calls >= 0),
  add column if not exists pricing_band text not null default '',
  add column if not exists pricing_version text not null default '';

-- Aggiorna soltanto le righe DeepSeek già archiviate. Il calcolo usa le
-- fasce ufficiali V4 Pro del momento registrato in UTC; le vecchie chiamate
-- GPT non possono includere ricerche web retroattive, perché quel numero non
-- veniva ancora salvato.
with tariffe_deepseek as (
  select
    id,
    case
      when extract(isodow from created_at at time zone 'UTC') between 1 and 5
       and (
         extract(hour from created_at at time zone 'UTC') between 1 and 3
         or extract(hour from created_at at time zone 'UTC') between 6 and 9
       ) then 'DeepSeek V4 Pro · punta UTC'
      else 'DeepSeek V4 Pro · ridotta UTC'
    end as fascia,
    case
      when extract(isodow from created_at at time zone 'UTC') between 1 and 5
       and (
         extract(hour from created_at at time zone 'UTC') between 1 and 3
         or extract(hour from created_at at time zone 'UTC') between 6 and 9
       ) then 1.32::numeric
      else 0.66::numeric
    end as prezzo_input,
    case
      when extract(isodow from created_at at time zone 'UTC') between 1 and 5
       and (
         extract(hour from created_at at time zone 'UTC') between 1 and 3
         or extract(hour from created_at at time zone 'UTC') between 6 and 9
       ) then 0.044::numeric
      else 0.022::numeric
    end as prezzo_cache,
    case
      when extract(isodow from created_at at time zone 'UTC') between 1 and 5
       and (
         extract(hour from created_at at time zone 'UTC') between 1 and 3
         or extract(hour from created_at at time zone 'UTC') between 6 and 9
       ) then 3.96::numeric
      else 1.98::numeric
    end as prezzo_output
  from public.writer_ai_usage_events
  where provider ilike 'DeepSeek%'
)
update public.writer_ai_usage_events as evento
set
  estimated_cost_usd = round(
    (
      greatest(0, evento.input_tokens - least(evento.input_tokens, evento.cached_input_tokens)) * tariffe.prezzo_input
      + least(evento.input_tokens, evento.cached_input_tokens) * tariffe.prezzo_cache
      + evento.output_tokens * tariffe.prezzo_output
    ) / 1000000,
    8
  ),
  pricing_band = tariffe.fascia,
  pricing_version = 'deepseek-v4-pro-2026-09-07'
from tariffe_deepseek as tariffe
where evento.id = tariffe.id;

update public.writer_ai_usage_events
set
  pricing_band = case
    when model ilike '%mini%' then 'GPT-5.4 mini · storico token'
    else 'GPT-5.4 · storico token'
  end,
  pricing_version = 'openai-token-storico-senza-ricerche'
where provider like 'GPT%'
  and pricing_version = '';
