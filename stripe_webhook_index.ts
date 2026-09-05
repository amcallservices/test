import Stripe from "npm:stripe@^22";
import { createClient } from "npm:@supabase/supabase-js@2";

const stripe = new Stripe(Deno.env.get("STRIPE_API_KEY")!);
const cryptoProvider = Stripe.createSubtleCryptoProvider();

const PACKAGES: Record<string, { credits: number; amountCents: number }> = {
  prova_15: { credits: 15, amountCents: 100 },
  base_150: { credits: 150, amountCents: 1000 },
  creator_375: { credits: 375, amountCents: 2500 },
  studio_750: { credits: 750, amountCents: 5000 },
  professionale_1500: { credits: 1500, amountCents: 10000 },
};

// Checkout creati prima dell'aggiornamento: non sono più acquistabili,
// ma possono essere completati senza perdere l'accredito.
const LEGACY_PACKAGES: Record<string, { credits: number; amountCents: number }> = {
  prova_7: { credits: 7, amountCents: 100 },
  base_100: { credits: 100, amountCents: 1000 },
  creator_260: { credits: 260, amountCents: 2500 },
  studio_530: { credits: 530, amountCents: 5000 },
  professionale_1050: { credits: 1050, amountCents: 10000 },
};

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
);

const json = (body: Record<string, unknown>, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });

Deno.serve(async (request) => {
  if (request.method !== "POST") {
    return json({ error: "Metodo non consentito" }, 405);
  }

  const signature = request.headers.get("stripe-signature");
  if (!signature) {
    return json({ error: "Firma Stripe mancante" }, 400);
  }

  const payload = await request.text();
  let event: Stripe.Event;

  try {
    event = await stripe.webhooks.constructEventAsync(
      payload,
      signature,
      Deno.env.get("STRIPE_WEBHOOK_SIGNING_SECRET")!,
      undefined,
      cryptoProvider,
    );
  } catch {
    return json({ error: "Firma Stripe non valida" }, 400);
  }

  if (
    event.type !== "checkout.session.completed" &&
    event.type !== "checkout.session.async_payment_succeeded"
  ) {
    return json({ received: true });
  }

  const session = event.data.object as Stripe.Checkout.Session;
  if (session.payment_status !== "paid") {
    return json({ received: true, status: "pagamento_non_confermato" });
  }

  const packageKey = session.metadata?.package_key ?? "";
  const userId = session.metadata?.user_id ?? "";
  const packageInfo = PACKAGES[packageKey] ?? LEGACY_PACKAGES[packageKey];

  if (
    !userId ||
    !packageInfo ||
    session.amount_total !== packageInfo.amountCents ||
    session.currency !== "eur"
  ) {
    console.warn("Checkout ignorato: pacchetto o metadati non riconosciuti", {
      sessionId: session.id,
      packageKey,
    });
    return json({ received: true, ignored: "pacchetto_non_riconosciuto" });
  }

  const { data, error } = await supabase.rpc("grant_checkout_credits", {
    p_session_id: session.id,
    p_user_id: userId,
    p_package_key: packageKey,
    p_credits: packageInfo.credits,
  });

  if (error) {
    console.error("Errore accredito crediti", error);
    return json({ error: "Accredito non riuscito" }, 500);
  }

  // Il referral viene valutato sempre dopo l'accredito normale. Se Stripe
  // ritenta lo stesso evento, entrambe le RPC restano idempotenti: i crediti
  // non possono essere attribuiti due volte.
  const { data: referralData, error: referralError } = await supabase.rpc(
    "grant_writer_referral_rewards",
    {
      p_session_id: session.id,
      p_referred_user_id: userId,
    },
  );

  if (referralError) {
    // Rispondiamo 500 affinché Stripe ritenti: il pagamento è già custodito
    // nella tabella idempotente, quindi il retry potrà completare solo il
    // premio eventualmente rimasto in sospeso senza duplicare il saldo.
    console.error("Errore premio referral", referralError);
    return json({ error: "Premio referral non ancora elaborato" }, 500);
  }

  return json({
    received: true,
    credited: data === true,
    referral: referralData?.status ?? "not_available",
    sessionId: session.id,
  });
});
