# Mappa · ChatGPT Ads, da zero alla prima campagna

**Per chi:** una persona italiana che non ha mai fatto pubblicità a pagamento.
**Arrivo:** campagna completa in Ads Manager, **in pausa e mai attivata** (0 € di spesa pubblicitaria).
**Durata:** 6 tappe, circa **160 min** di video. **Fonti:** 37 pagine del centro assistenza OpenAI scaricate il 6/11/2026
(95 concetti, ognuno con la pagina e la frase copiata: `mappa.json`).

## Le tappe

| # | Tappa | Alla fine sai… | Min | Video validi dal |
|---|---|---|---|---|
| 1 | Cos'è ChatGPT Ads e come appare un annuncio | dove compare, chi lo vede, da cosa è fatto, come viene scelto | 20 | 9/2/2026 |
| 2 | Aprire l'account Ads Manager dall'Italia senza far partire nulla | account italiano con nomi, logo, fatturazione e verifica avviata | 25 | 31/8/2026* |
| 3 | La struttura: campagna, gruppo di annunci e context hints | obiettivo, paese, piattaforme; context hints scritti come frasi | 30 | 5/5/2026* |
| 4 | Scrivere l'annuncio: titolo, testo, immagine e pagina di arrivo | 2-3 annunci validi; decidi sui creative enhancements | 25 | 30/10/2026 |
| 5 | Budget e offerte: quanto puoi spendere davvero | budget in euro, spesa massima giorno/settimana, strategia d'offerta | 30 | 9/11/2026 |
| 6 | Misurazione e lista di controllo: campagna pronta, ma in pausa | UTM e Pixel, dove leggi i risultati, campagna chiusa in pausa | 30 | 30/9/2026* |

\* data da `chatgpt_ads.md`, **non ufficiale** (le pagine OpenAI non la scrivono).

**Perché quest'ordine:** prima si capisce cosa si compra; poi si apre l'account, che è il passo più lento (verifica fino a 7 giorni
lavorativi, conviene avviarla presto); poi si costruisce dall'alto in basso come chiede Ads Manager (campagna → gruppo → annuncio);
poi i soldi, quando si sa cosa si finanzia; per ultima la misurazione con la lista di controllo, che chiude senza attivare.

## Avvisi per chi sta in Italia

- **Disponibile in self-service** («Italy | Available»): chi fa pubblicità e paga deve avere sede in un paese della lista.
- **Minimo 15 € al giorno** con fatturazione in euro. Minimo del budget totale e soglie di pagamento in euro: non scritti.
- **Paese, valuta e fuso orario non si cambiano** dopo la creazione dell'account; carta e fatturazione dello stesso paese; partita IVA in Billing → Settings.
- **Niente personalizzazione in SEE e Svizzera**: niente pubblici personalizzati (liste clienti) per campagne verso SEE e Svizzera.
- **Account nuovo = solo Italia** all'inizio; il paese va incluso, escludere gli altri non basta.
- **La verifica non è un freno**: alcuni account spendono prima che sia finita. Per non spendere si mette **in pausa**.
- **Settori**: salute, finanza e legale fuori dagli USA sono in gran parte vietati o riservati.
- **Lingua**: dal 30/10 i creative enhancements possono tradurre e riscrivere l'annuncio.
- **Strumenti**: Shopify solo USA; GA4 in beta; nessun tetto di spesa giornaliero per account self-service pagati con carta.

## Cambi che rendono vecchi i video

- **9/2/2026** inizio del test USA · **5/5** Ads Manager beta e CPC* · **31/8** self-service in Europa e Italia*
- **25/9** nomi di account, brand e ragione sociale separati · **30/9** finestre di attribuzione flessibili*
- **26/10** formato a più immagini (4-6, un link, solo «Learn more») · **30/10** creative enhancements attivi di base
- **senza data** budget giornaliero = media su 7 giorni (fino a 2 volte in un giorno, al massimo 7 volte nella settimana)
- **9/11** Target CPC e Target CPA nelle campagne nuove, «Intelligent bidding» al posto di Maximize Results · **1/1/2027** fine di Max Bid e Max CPC

**Fuori percorso:** feed prodotti, Shopify, HubSpot, Sponsored Agents, partner di misurazione e MMP, GA4, pubblici personalizzati,
caricamento in blocco, Conversions API ed Event Quality Score, SSO e SCIM, plugin di Ads Manager, API, Negative Phrases (motivi in `mappa.json`).

## Dubbi

1. **L'Italia è davvero self-service?** La tabella dice «Italy | Available», ma la stessa pagina (20001245) dice che nei «new European
   markets» per ora si parte tramite il team OpenAI o i partner. Non è chiaro se l'Italia sia fra questi.
2. **Nomi delle offerte in transizione.** Strategia automatica: «Maximize results» (20001425, 20001268) e «Intelligent bidding, formerly
   Maximize Results» (20001634). Offerta manuale: «Manual: Max bid», «Max CPC», «Bid Cap» (20001412), «maximum bid». La pagina di base
   (20001207, aggiornata oggi) consiglia ancora un Max CPC di 3-5 $. **Non è scritto se dopo il 9/11 una campagna Clicks nuova potrà
   ancora usare Max CPC**: per le conversioni Target CPA «replaces» Max Bid, per i clic Target CPC «is available».
3. **Come si paga l'asta?** 20001207: «relevance-weighted, second-price auction». 20001634: «The final winning auction bid sets the price
   you pay». Le due frasi non dicono chiaramente la stessa cosa.
4. **Nome dell'obiettivo.** «Views» (20001210, 20001216) contro «Reach campaigns» (20001207, 20001209). Nel caricamento CSV:
   «Views or Clicks» (20001209) contro «Views, Clicks, or Conversions» (20001218).
5. **Limiti di caratteri.** 20001209 al passo 5 chiama «character limits» i valori consigliati (16-24 e 32-48); i massimi veri sono 50 e 100.
6. **Crawler.** 20001212 sembra chiedere sia OAI-AdsBot sia OAI-SearchBot; 20001243 dice che solo AdsBot è obbligatorio, SearchBot consigliato.
7. **Data dei creative enhancements.** `chatgpt_ads.md` dice 29/10, la pagina ufficiale venerdì 30/10: vale il 30/10.
8. **Budget giornaliero come media.** 20001413 lo presenta come un cambio («What is changing») ma non scrive da quando vale.
9. **«Pronta ma non lanciata» non è descritta bene.** Le pagine parlano di «Saving a draft» e di pausa, ma non spiegano come salvare senza
   pubblicare, né se la revisione degli annunci avviene con la campagna in pausa. La prima campagna può non mostrare le date prima della
   pubblicazione. Strada più sicura: all'iscrizione **saltare** la creazione dal sito, salvare tutto, **controllare lo stato in pausa**,
   e non contare su verifica o fatturazione mancanti come freno.

**Limiti di questa mappa:** i minuti sono una stima, da controllare quando si cercano i video. La tappa 5 oggi non può avere un video
valido (il cambio è il 9/11): o la si accetta con avviso o si cerca di nuovo dopo il 9/11. I video in italiano saranno probabilmente
pochi. Molte pagine sono state aggiornate nelle ultime ore: prima di pubblicare il percorso va rifatto il controllo dei cambi.
