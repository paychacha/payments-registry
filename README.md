<p align="center">
  <a href="https://paychacha.com"><img src=".github/assets/paychacha.svg" width="64" height="64" alt="paychacha"></a>
</p>
<h1 align="center">Payments Registry</h1>
<p align="center">
  Which payment methods people use in each country, and which payment providers support them.
</p>
<p align="center">
  <a href="https://paychacha.com/payment-methods"><b>Browse by country</b></a> ·
  <a href="GLOSSARY.md">Glossary</a> ·
  <a href="CONTRIBUTING.md">Contribute</a> ·
  <a href="README.zh-CN.md">中文</a>
</p>
<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/data-CC%20BY%204.0-2f7d3a" alt="Data licence: CC BY 4.0"></a>
  <a href="scripts/LICENSE"><img src="https://img.shields.io/badge/scripts-MIT-2f7d3a" alt="Scripts licence: MIT"></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/pull%20requests-welcome-4a9a2e" alt="Pull requests welcome"></a>
</p>

An open record of which payment methods people use in each country, and which payment providers support them. It is maintained by [paychacha.com](https://paychacha.com) and by the providers themselves, through pull requests.

Browse it by country at **[paychacha.com/payment-methods](https://paychacha.com/payment-methods)**.

As of 2026-11-25 it holds:

- **715 payment methods** used by payers in 153 countries and territories: Alipay, iDEAL, Pix, Visa and the long tail of local wallets, banks and cash networks.
- **48 providers**: payment service providers, acquirers, gateways, payment facilitators, merchants of record and aggregators.
- **1,231 coverage entries** for the 8 providers whose public method lists have been read so far. Each says that a provider supports a method, where, and links to the public page that shows it.

## What is in it

```
data/methods/<id>.yaml     one payment method per file
data/providers/<id>.yaml   one provider per file, with the methods it supports
schema/                    JSON Schemas for both
GLOSSARY.md                PSP, acquirer, gateway, PayFac, MoR, aggregator, APM, ISV
```

A payment method is a brand a payer pays with:

```yaml
# data/methods/alipay.yaml
id: alipay
name: Alipay
aliases:
  - 支付宝
type: wallet
countries: [CN]
currencies: [CNY]
```

A provider is a company a merchant signs with. Its `coverage` lists the methods it supports:

```yaml
# data/providers/stripe.yaml
id: stripe
name: Stripe
website: https://stripe.com
roles: [psp, payfac]
coverage:
  - method: alipay
    countries: [CN]
    currencies: [AUD, CAD, CNY, EUR, GBP, HKD, JPY, MYR, NZD, SGD, USD]
    source: https://docs.stripe.com/payments/alipay
    source_type: provider_docs
    checked: 2026-11-24
```

### Method fields

| Field | Meaning |
| --- | --- |
| `id` | Lowercase slug, unique, same as the file name. |
| `name` | The name the brand goes by internationally. |
| `aliases` | Local-language names, other spellings, and the names providers list the method under. |
| `type` | One of 11 kinds: `card`, `wallet`, `real_time_payment`, `bank_redirect`, `bank_transfer`, `cash_voucher`, `bnpl`, `prepaid_voucher`, `bank_debit`, `carrier_billing`, `stablecoin`. Each is defined in the [glossary](GLOSSARY.md#payment-method-types). |
| `countries` | Where the brand's payers mainly are, as ISO 3166-1 alpha-2 codes. `XK` stands for Kosovo. |
| `global` | `true` in place of `countries` for a brand used worldwide, such as Visa or PayPal. |
| `currencies` | The currencies payers pay in, as ISO 4217 codes. |
| `website` | The brand's own site. |

### Provider fields

| Field | Meaning |
| --- | --- |
| `id`, `name`, `website` | As above. |
| `roles` | Every role the company plays: `psp`, `acquirer`, `gateway`, `payfac`, `mor`, `aggregator`. Each is defined in the [glossary](GLOSSARY.md#provider-roles). |
| `merchant_countries` | Where a merchant's business can be registered to sign up, with `merchant_countries_source`, the public page that lists them. |
| `maintainers` | GitHub usernames of the provider's own staff who keep the file up to date. |
| `coverage` | One entry per supported method. |

Each coverage entry has:

| Field | Meaning |
| --- | --- |
| `method` | The `id` of a file in `data/methods/`. |
| `countries` or `global` | The payer countries the provider supports the method in, as its source states them. |
| `currencies` | The currencies the provider processes the method in. |
| `source` | A public https page that shows this. Required. |
| `source_type` | `provider_docs`: read from the provider's public pages. `self_reported`: stated by the provider in a pull request. `third_party`: any other public source. |
| `checked` | The day the source was last read. |

## Reading the data correctly

- **A missing field means unknown, not no.** A method with no `countries` is one whose sources name none. A provider with no entry for a method may still support it: the entry has not been added yet.
- **Coverage is what a provider's public pages said on the `checked` date.** Providers change their lists without notice. Follow `source` before relying on an entry.
- **`countries` means payer countries.** Adyen publishes the countries where merchants can use a method, not where its payers are, so its entries have no `countries`.
- **A method's `currencies` are only the national currencies of its countries.** A provider's coverage entry often lists more, because providers also publish the currencies they settle in.
- **Roles are a first reading**, made from general knowledge and not yet confirmed by the providers. Corrections are welcome.
- **40 of the 48 providers have no coverage yet.** They are listed so that they can add their own.

## What is not in it

The registry records facts only. It has no marketing copy, no rankings, no prices or fees, and no logos.

It covers payment methods that work for online checkout, bill payment or payment links. Methods that only work in person, and products that only pay money out, are left out.

## Using and citing

The data is free to use, including commercially, under [CC BY 4.0](LICENSE). Credit it with a link:

> Source: [Payments Registry](https://paychacha.com/payment-methods), paychacha.com

paychacha.com has a page for each of 37 countries, for example [paychacha.com/payment-methods/japan](https://paychacha.com/payment-methods/japan), and for more than 100 widely supported methods, for example [paychacha.com/payment-methods/pix](https://paychacha.com/payment-methods/pix).

The scripts in `scripts/` are under the [MIT licence](scripts/LICENSE). Brand and company names belong to their owners and appear here only to identify them.

## Contributing

Providers are invited to register themselves and correct their own entries. Anyone can add a method or fix a mistake, as long as a public page backs it up. See [CONTRIBUTING.md](CONTRIBUTING.md).

Every pull request is checked by:

```bash
pip install -r requirements.txt
python3 scripts/validate.py
```

## Where the first data came from

paychacha.com read the public payment method lists of eight providers on 2026-11-24 (Stripe, Adyen, Airwallex, Antom, dLocal, Nuvei, PayerMax and KyrenPay), merged the 1,314 entries into one record per brand, and left out what cannot serve online payments. `scripts/import_paychacha.py` turned that data into the files here; its opening comment says how each field was derived.
