#!/usr/bin/env python3
"""Seed data/ from the payment method data in the paychacha-website repository.

    python3 scripts/import_paychacha.py --source ../paychacha-website
    python3 scripts/import_paychacha.py --source ../paychacha-website --force   # overwrite data/

Python 3.9+, no packages. Run once to create the registry's first data; after that the YAML files
are edited by hand and through pull requests, and running this again with --force would discard
those edits.

It reads <source>/data/payment-methods/: catalog.json (one entry per brand) and the eight
<provider>.json files (each provider's own list). It writes:

  data/methods/<id>.yaml    one per catalog brand
  data/providers/<id>.yaml  one per provider in PROVIDERS; the eight with a list get `coverage`

What is carried over and how:

  id, name, type   the catalog's brand key, name and type.
  aliases          the catalog's local-language name, then every other name the providers list the
                   brand under (other spellings, a bank's name for its payment product, a flow such
                   as "Pix Automático"). A name that is another method's own name is left out.
  countries        the catalog's payer regions; `global: true` where it says GLOBAL.
  currencies       for a method: the national currencies of its countries that at least one
                   provider lists for it (providers also list the currencies they settle in, which
                   say nothing about the payer). For a coverage entry: what the provider lists.
                   Codes are brought to ISO 4217 (RMB -> CNY); codes that are not current ISO 4217
                   codes are dropped and counted in the summary.
  coverage         one entry per provider and method. A provider's several entries for one brand
                   (Pix, Pix Automático, SmartPix) become one, with every country and currency.
  source           the provider's page for that method where there is one, else the page that
                   lists it (see source_for).
  checked          the day paychacha-website fetched the provider's pages.

Left behind: logos, brand colours, the providers' descriptions and per-method attributes
(refunds, chargebacks, settlement), and the countries where a merchant can use a method.
"""
import argparse
import collections
import json
import os
import re
import shutil
import sys
import unicodedata

sys.dont_write_bytecode = True
from codes import COUNTRIES, CURRENCIES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# id, name, website, roles. The first eight have a payment method list in the source data, in the
# order the catalog prefers their names. The rest are the payment services paychacha.com recognises
# on merchant websites (src/payment-providers.ts there); they start with no coverage.
# Roles of the first eight are a first reading. Those of the rest were checked against the providers'
# legal terms and documentation, regulators' registers and Mastercard's payment facilitator list on
# 2026-11-25; a role is listed only where one of those shows it. See GLOSSARY.md.
PROVIDERS = [
    ("stripe", "Stripe", "https://stripe.com", ["psp", "payfac"]),
    ("adyen", "Adyen", "https://www.adyen.com", ["psp", "acquirer", "gateway"]),
    ("airwallex", "Airwallex", "https://www.airwallex.com", ["psp", "acquirer"]),
    ("antom", "Antom", "https://www.antom.com", ["psp", "acquirer"]),
    ("dlocal", "dLocal", "https://www.dlocal.com", ["psp"]),
    ("nuvei", "Nuvei", "https://www.nuvei.com", ["psp", "acquirer", "gateway"]),
    ("payermax", "PayerMax", "https://www.payermax.com", ["psp", "aggregator"]),
    ("kyrenpay", "KyrenPay", "https://kyrenpay.com", ["mor"]),
    # Card acquirers and payment service providers.
    ("paypal", "PayPal", "https://www.paypal.com", ["psp", "gateway", "payfac"]),
    ("braintree", "Braintree", "https://www.braintreepayments.com", ["psp", "gateway", "payfac"]),
    ("checkout-com", "Checkout.com", "https://www.checkout.com", ["psp", "acquirer", "gateway", "payfac"]),
    ("square", "Square", "https://squareup.com", ["psp", "acquirer", "payfac"]),
    ("razorpay", "Razorpay", "https://razorpay.com", ["psp", "gateway", "mor", "aggregator"]),
    ("worldpay", "Worldpay", "https://www.worldpay.com", ["psp", "acquirer", "gateway"]),
    ("rapyd", "Rapyd", "https://www.rapyd.net", ["psp", "acquirer", "aggregator"]),
    ("payu", "PayU", "https://corporate.payu.com", ["psp", "payfac", "aggregator"]),
    ("mollie", "Mollie", "https://www.mollie.com", ["psp", "acquirer", "payfac", "aggregator"]),
    ("xendit", "Xendit", "https://www.xendit.co", ["psp", "gateway", "payfac", "aggregator"]),
    ("2c2p", "2C2P", "https://2c2p.com", ["psp", "payfac", "aggregator"]),
    ("ebanx", "EBANX", "https://www.ebanx.com", ["psp", "payfac", "aggregator"]),
    ("authorize-net", "Authorize.net", "https://www.authorize.net", ["psp", "gateway"]),
    # Merchants of record.
    ("paddle", "Paddle", "https://www.paddle.com", ["mor"]),
    ("lemon-squeezy", "Lemon Squeezy", "https://www.lemonsqueezy.com", ["mor"]),
    ("creem", "Creem", "https://www.creem.io", ["mor"]),
    ("waffo", "Waffo", "https://waffo.com", ["psp", "mor"]),
    ("fastspring", "FastSpring", "https://fastspring.com", ["mor"]),
    ("polar", "Polar", "https://polar.sh", ["mor"]),
    ("dodo-payments", "Dodo Payments", "https://dodopayments.com", ["gateway", "mor"]),
    ("gumroad", "Gumroad", "https://gumroad.com", ["mor"]),
    ("2checkout", "2Checkout", "https://www.2checkout.com", ["psp", "payfac", "mor"]),
    # Cross-border collection for sellers in China.
    ("pingpong", "PingPong", "https://www.pingpongx.com", ["psp", "payfac", "aggregator"]),
    ("oceanpayment", "Oceanpayment", "https://www.oceanpayment.com", ["psp", "acquirer", "aggregator"]),
    ("asiabill", "Asiabill", "https://www.asiabill.com", ["psp", "acquirer", "payfac"]),
    ("useepay", "UseePay", "https://www.useepay.com", ["psp", "acquirer", "aggregator"]),
    # Local payment methods worldwide through one account.
    ("payssion", "Payssion", "https://www.payssion.com", ["psp", "aggregator"]),
    # Cryptocurrency and stablecoin payments.
    ("coinbase-business", "Coinbase Business", "https://www.coinbase.com/business", ["psp"]),
    ("nowpayments", "NOWPayments", "https://nowpayments.io", ["psp"]),
    ("cryptomus", "Cryptomus", "https://cryptomus.com", ["psp"]),
    ("paydify", "Paydify", "https://www.paydify.com", ["psp", "aggregator"]),
    ("infini", "Infini", "https://infini.money", ["psp"]),
    ("binance-pay", "Binance Pay", "https://pay.binance.com", ["psp"]),
    ("okx-pay", "OKX Pay", "https://www.okx.com", ["psp"]),
    ("crypto-com-pay", "Crypto.com Pay", "https://crypto.com/pay", ["psp"]),
    ("bitpay", "BitPay", "https://www.bitpay.com", ["psp"]),
    ("coinpayments", "CoinPayments", "https://www.coinpayments.net", ["psp"]),
    ("coingate", "CoinGate", "https://coingate.com", ["psp"]),
    ("oxapay", "OxaPay", "https://oxapay.com", ["psp"]),
    ("plisio", "Plisio", "https://plisio.net", ["psp"]),
]
WITH_LISTS = [row[0] for row in PROVIDERS[:8]]

# Codes the sources write for a current currency under another name.
CURRENCY_NAMES = {"RMB": "CNY", "YEN": "JPY", "NIS": "ILS"}

# The source for a provider entry that names no page of its own.
ANTOM_ENUMS = "https://docs.antom.com/ac/pm/enumeration_values"
DLOCAL_INDEX = "https://docs.dlocal.com/docs/payment-method"

# ISO 4217's currencies by country, without the funds codes (CLF, MXV, USN, ...). Used only to pick
# a method's own currencies out of the longer lists the providers publish.
NATIONAL = {
    code: currencies.split()
    for currencies, codes in {
        "EUR": "AD AT AX BE BG BL CY DE EE ES FI FR GF GP GR HR IE IT LT LU LV MC ME MF MQ MT NL PM PT RE SI SK SM TF VA XK YT",
        "USD": "AS BQ EC FM GU IO MH MP PR PW TC TL UM US VG VI",
        "XOF": "BF BJ CI GW ML NE SN TG",
        "XAF": "CF CG CM GA GQ TD",
        "XCD": "AG AI DM GD KN LC MS VC",
        "XPF": "NC PF WF",
        "XCG": "CW SX",
        "AUD": "AU CC CX KI NF NR TV",
        "NZD": "CK NU NZ PN TK",
        "GBP": "GB GG IM JE",
        "DKK": "DK FO GL",
        "NOK": "NO SJ",
        "CHF": "CH LI",
        "MAD": "EH MA",
        "BTN INR": "BT",
        "HTG USD": "HT",
        "LSL ZAR": "LS",
        "NAD ZAR": "NA",
        "PAB USD": "PA",
        "SVC USD": "SV",
        "VES VED": "VE",
    }.items()
    for code in codes.split()
}
NATIONAL.update(
    {
        pair[:2]: [pair[3:]]
        for pair in """
        AE:AED AF:AFN AL:ALL AM:AMD AO:AOA AR:ARS AW:AWG AZ:AZN BA:BAM BB:BBD BD:BDT BH:BHD BI:BIF
        BM:BMD BN:BND BO:BOB BR:BRL BS:BSD BW:BWP BY:BYN BZ:BZD CA:CAD CD:CDF CL:CLP CN:CNY CO:COP
        CR:CRC CU:CUP CV:CVE CZ:CZK DJ:DJF DO:DOP DZ:DZD EG:EGP ER:ERN ET:ETB FJ:FJD FK:FKP GE:GEL
        GH:GHS GI:GIP GM:GMD GN:GNF GT:GTQ GY:GYD HK:HKD HN:HNL HU:HUF ID:IDR IL:ILS IN:INR IQ:IQD
        IR:IRR IS:ISK JM:JMD JO:JOD JP:JPY KE:KES KG:KGS KH:KHR KM:KMF KP:KPW KR:KRW KW:KWD KY:KYD
        KZ:KZT LA:LAK LB:LBP LK:LKR LR:LRD LY:LYD MD:MDL MG:MGA MK:MKD MM:MMK MN:MNT MO:MOP MR:MRU
        MU:MUR MV:MVR MW:MWK MX:MXN MY:MYR MZ:MZN NG:NGN NI:NIO NP:NPR OM:OMR PE:PEN PG:PGK PH:PHP
        PK:PKR PL:PLN PY:PYG QA:QAR RO:RON RS:RSD RU:RUB RW:RWF SA:SAR SB:SBD SC:SCR SD:SDG SE:SEK
        SG:SGD SH:SHP SL:SLE SO:SOS SR:SRD SS:SSP ST:STN SY:SYP SZ:SZL TH:THB TJ:TJS TM:TMT TN:TND
        TO:TOP TR:TRY TT:TTD TW:TWD TZ:TZS UA:UAH UG:UGX UY:UYU UZ:UZS VN:VND VU:VUV WS:WST YE:YER
        ZA:ZAR ZM:ZMW ZW:ZWG
        """.split()
    }
)


def slug(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = text.lower().replace("&", " and ").replace("+", " plus ").replace("'", "")
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def tidy(text):
    """One line with plain spaces: Stripe writes "iDEAL | Wero" with narrow no-break spaces."""
    return " ".join(unicodedata.normalize("NFKC", text).split())


def same(text):
    """The key two names share when they differ only in case, accents or punctuation."""
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", plain) or text.lower()


# ---------------------------------------------------------------------------------------- YAML

# Words YAML 1.1 readers take for a boolean or null: Norway's NO, most of all.
RESERVED = {"y", "n", "yes", "no", "on", "off", "true", "false", "null", "~"}


def scalar(text):
    """A string as YAML: bare where every reader takes it for a string, double-quoted otherwise."""
    bare = (
        text
        and text.lower() not in RESERVED
        and any(ch.isalpha() for ch in text)
        and (text[0].isalnum())
        and not text.endswith(":")
        and ": " not in text
        and " #" not in text
        and all(ch.isalnum() or ch in " .-_/()+'&,!:#?=%~@" for ch in text)
    )
    return text if bare else json.dumps(text, ensure_ascii=False)


def flow(codes, indent, first):
    """A list of codes on one line, wrapped at 96 columns; `first` is how much of the first line is used."""
    lines, line = [], "["
    for i, code in enumerate(codes):
        piece = scalar(code) + ("," if i < len(codes) - 1 else "]")
        if len(line) + len(piece) + (first if not lines else indent) > 96 and line not in ("[", ""):
            lines.append(line.rstrip())
            line = ""
        line += piece + " "
    lines.append(line.rstrip())
    return ("\n" + " " * indent).join(lines)


def emit(fields, indent=0):
    """`fields` is a list of (key, value); lists of codes go on one line, lists of names one per line."""
    pad = " " * indent
    out = []
    for key, value in fields:
        if value is None:
            continue
        if key in ("countries", "currencies", "roles", "merchant_countries", "maintainers"):
            out.append(f"{pad}{key}: {flow(value, indent + 2, indent + len(key) + 2)}")
        elif isinstance(value, list):
            out.append(f"{pad}{key}:")
            out.extend(f"{pad}  - {scalar(item)}" for item in value)
        elif value is True:
            out.append(f"{pad}{key}: true")
        elif key == "checked":
            out.append(f"{pad}{key}: {value}")
        else:
            out.append(f"{pad}{key}: {scalar(value)}")
    return out


# ---------------------------------------------------------------------------------- conversion

DROPPED = collections.Counter()  # currency codes that are not current ISO 4217 codes


def currency_codes(entries):
    codes = set()
    for entry in entries:
        listed = entry.get("currencies")
        if not isinstance(listed, list):  # Airwallex writes "All currencies" for cards
            continue
        for code in listed:
            code = CURRENCY_NAMES.get(code, code)
            if code in CURRENCIES:
                codes.add(code)
            else:
                DROPPED[code] += 1
    return sorted(codes)


def place(regions, what):
    """customer_regions -> (`global`, `countries`)."""
    if "GLOBAL" in regions:
        return True, None
    unknown = [code for code in regions if code not in COUNTRIES]
    if unknown:
        sys.exit(f"{what}: {unknown} are not country codes; add them to scripts/codes.py or fix the source")
    return None, sorted(set(regions)) or None


def source_for(provider, lead, countries):
    """The public page that shows the provider supports the method.

    A provider's page for the method itself comes first: its documentation page, then its product
    page. Three providers need more than that:
      Stripe  writes a few documentation addresses in a private form ("docs:/docs/payments/kriya");
              those entries use the product page.
      dLocal  documents methods on one page per country. An entry found in a single country points
              at that page; one found in several points at the index of the country pages. Entries
              that come from dlocal.com's regional pages point there.
      Antom   has one entry (Bettr) that appears only in its list of API values.
    Adyen and PayerMax publish one page with every method, and each entry points at it.
    """
    docs, page = lead.get("docs_url"), lead.get("url")
    https = lambda url: bool(url) and url.startswith("https://")
    if provider == "dlocal":
        if https(docs) and countries and len(countries) == 1:
            return docs
        return page if https(page) else DLOCAL_INDEX
    if https(docs):
        return docs
    if https(page):
        return page
    if provider == "antom":
        return ANTOM_ENUMS
    sys.exit(f"{provider}/{lead['id']} has no public page to cite")


def convert(source):
    folder = os.path.join(source, "data", "payment-methods")
    read = lambda name: json.load(open(os.path.join(folder, name), encoding="utf8"))
    catalog = read("catalog.json")["methods"]
    lists = {provider: read(f"{provider}.json") for provider in WITH_LISTS}
    rows = {(p, m["id"]): m for p, data in lists.items() for m in data["methods"]}

    exact = lambda name: tidy(name).casefold()
    names = {exact(entry["name"]): entry["brand"] for entry in catalog}
    methods, coverage, skipped_aliases = [], collections.defaultdict(list), []
    for entry in sorted(catalog, key=lambda e: e["brand"]):
        brand = entry["brand"]
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", brand):
            sys.exit(f"{brand!r} cannot be an id")
        mine = {p: [rows[(p, i)] for i in ids] for p, ids in entry["providers"].items()}
        every = [m for p in WITH_LISTS for m in mine.get(p, [])]

        aliases, seen = [], {same(entry["name"])}
        candidates = [entry.get("local_name")] + [n for m in every for n in (m["local_name"], m["name"])]
        for name in filter(None, candidates):
            name = tidy(name)
            key = same(name)
            if key in seen:
                continue
            seen.add(key)
            if names.get(exact(name), brand) != brand:
                skipped_aliases.append((brand, name, names[exact(name)]))
                continue
            aliases.append(name)

        is_global, countries = place(entry["customer_regions"], brand)
        national = {c for code in countries or [] for c in NATIONAL.get(code) or sys.exit(f"no currency for {code}")}
        currencies = [c for c in currency_codes(every) if c in national]
        methods.append(
            [
                ("id", brand),
                ("name", tidy(entry["name"])),
                ("aliases", aliases or None),
                ("type", entry["type"]),
                ("global", is_global),
                ("countries", countries),
                ("currencies", currencies or None),
            ]
        )

        for provider, entries in mine.items():
            lead = next((m for m in entries if brand in (m["id"], slug(m["name"]))), entries[0])
            regions = [code for m in entries for code in m["customer_regions"]]
            is_global, countries = place(regions, f"{provider}/{brand}")
            coverage[provider].append(
                [
                    ("method", brand),
                    ("global", is_global),
                    ("countries", countries),
                    ("currencies", currency_codes(entries) or None),
                    ("source", source_for(provider, lead, countries)),
                    ("source_type", "provider_docs"),
                    ("checked", lists[provider]["retrieved_at"]),
                ]
            )

    providers = []
    for id_, name, website, roles in PROVIDERS:
        providers.append((id_, [("id", id_), ("name", name), ("website", website), ("roles", roles)], coverage.get(id_, [])))
    return methods, providers, skipped_aliases, len(rows)


def main():
    parser = argparse.ArgumentParser(description="Seed data/ from paychacha-website's payment method data.")
    parser.add_argument("--source", default=os.path.join(os.path.dirname(ROOT), "paychacha-website"), help="the paychacha-website checkout")
    parser.add_argument("--out", default=os.path.join(ROOT, "data"))
    parser.add_argument("--force", action="store_true", help="replace data/methods and data/providers if they exist")
    args = parser.parse_args()

    targets = [os.path.join(args.out, kind) for kind in ("methods", "providers")]
    if any(os.path.isdir(t) and os.listdir(t) for t in targets) and not args.force:
        sys.exit(f"{args.out} already has data. Edit the YAML files, or pass --force to replace them all.")
    methods, providers, skipped_aliases, entries = convert(args.source)

    for target in targets:
        shutil.rmtree(target, ignore_errors=True)
        os.makedirs(target)
    for fields in methods:
        with open(os.path.join(targets[0], f"{fields[0][1]}.yaml"), "w", encoding="utf8") as f:
            f.write("\n".join(emit(fields)) + "\n")
    for id_, fields, rows in providers:
        lines = emit(fields)
        if rows:
            lines.append("coverage:")
            for row in rows:
                body = emit(row, 4)
                lines.append("  - " + body[0][4:])
                lines.extend(body[1:])
        else:
            lines.append("coverage: []")
        with open(os.path.join(targets[1], f"{id_}.yaml"), "w", encoding="utf8") as f:
            f.write("\n".join(lines) + "\n")

    value = lambda fields, key: dict(fields).get(key)
    covered = sum(len(rows) for _, _, rows in providers)
    print(f"{len(methods)} methods from {entries} provider entries: {sum(1 for m in methods if value(m, 'global'))} worldwide, "
          f"{sum(1 for m in methods if not value(m, 'global') and not value(m, 'countries'))} with no payer country, "
          f"{sum(1 for m in methods if value(m, 'currencies'))} with currencies, {sum(1 for m in methods if value(m, 'aliases'))} with aliases")
    print(f"{len(providers)} providers, {sum(1 for _, _, rows in providers if rows)} with coverage: {covered} entries")
    print("types: " + ", ".join(f"{t} {n}" for t, n in collections.Counter(value(m, "type") for m in methods).most_common()))
    if DROPPED:
        print("currency codes left out (not current ISO 4217): " + ", ".join(f"{c} x{n}" for c, n in sorted(DROPPED.items())))
    if skipped_aliases:
        print("names left out of aliases because another method goes by them: " + "; ".join(f"{b}: {n} (is {o})" for b, n, o in skipped_aliases))
    print("Now run: python3 scripts/validate.py")


if __name__ == "__main__":
    main()
