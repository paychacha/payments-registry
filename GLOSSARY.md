# Glossary

[中文](GLOSSARY.zh-CN.md)

The words people use for payment companies overlap, and one company is often several of them at once. This page says what each word means in this registry, and how to tell one from another.

## Who is in a payment

- **Payer**: the person or business paying. In card payments, the cardholder.
- **Merchant**: the business being paid for its goods or services.
- **Payment method**: what the payer pays with: a card brand, a wallet, a bank transfer scheme. Each one is a file in [`data/methods/`](data/methods/).
- **Provider**: the company the merchant signs a contract with in order to accept payments. Each one is a file in [`data/providers/`](data/providers/), tagged with one or more of the roles below.

## Provider roles

These are the values of `roles` in a provider file. A provider lists every role it plays, in any of its products or markets.

### `psp`: payment service provider

A company that lets a merchant accept payments under one contract. It supplies the connection to the merchant's checkout and arranges for the payments to be processed and the money to be paid out.

This is the broad term. Most providers are a PSP and something narrower as well: a PSP may do its own acquiring, act as a payment facilitator, or pass payments to other companies.

**How to tell:** the merchant signs a payment services agreement with the company and is paid out by it, or through it.

### `acquirer`

A bank or licensed financial institution that is a member of the card networks, or holds the equivalent position in another payment system, and accepts payments on a merchant's behalf. It receives the money from the payers' banks through the network, pays the merchant, and answers to the network for the merchant's transactions, including chargebacks and fines.

**How to tell:** the company is itself a member or licensed acquirer of a card network or payment scheme, and is not relying on another institution's membership. A payments regulator's licence to sign up merchants, such as a "merchant acquisition" licence, is not enough by itself: payment facilitators hold those too.

### `gateway`

The technical service that carries payment details from the merchant's checkout to an acquirer or processor and brings back the result: approved or declined. A gateway on its own does not hold or pay out the merchant's money; the merchant needs an acquiring contract with someone as well.

**How to tell:** a merchant can use the service with an acquiring contract held at a different company.

### `payfac`: payment facilitator

A company registered with the card networks through a sponsoring acquirer. It holds one master merchant account and signs merchants beneath it as sub-merchants. It checks and approves those merchants itself, pays them out, and is responsible to the acquirer for what they do.

The merchant is still the seller: its name is on the cardholder's statement, often after the facilitator's prefix. Above a volume threshold set by the networks, a sub-merchant has to sign with the acquirer directly as well.

**How to tell:** the merchant can start accepting cards without a merchant account of its own at an acquirer.

### `mor`: merchant of record

The company that is, in law, the seller in the transaction. It sells to the buyer in its own name, its name is on the buyer's statement and receipt, and it carries the seller's duties: charging and remitting sales tax or VAT, refunds, chargebacks, and keeping to the card networks' rules. The business that makes the product supplies it through the merchant of record, which pays over the proceeds less its fee.

**How to tell:** the receipt names this company as the seller, and this company remits the tax.

### `aggregator`

A company that has contracts with many payment method operators, acquirers or local processors, and offers them all to a merchant through one contract and one integration. It collects from those partners and pays the merchant.

The word is used in other ways elsewhere. Card networks once used "aggregator" for what they now call a payment facilitator, and in India "payment aggregator" is a licensed category. Here it means only this: for most of the methods it offers, another institution does the acquiring.

**How to tell:** the methods on offer reach the merchant through the company's partners, not through its own licences.

### The roles side by side

| Role | Who is the seller | Who the merchant's payment contract is with | Who answers to the card network |
| --- | --- | --- | --- |
| `psp` | the merchant | the PSP | depends on the PSP's other roles |
| `acquirer` | the merchant | the acquirer | the acquirer |
| `gateway` | the merchant | the gateway for the connection, an acquirer for the money | the merchant's acquirer |
| `payfac` | the merchant | the payment facilitator | the facilitator's sponsoring acquirer, which holds the facilitator responsible |
| `mor` | the merchant of record | the merchant of record, as its supplier | whoever the merchant of record uses |
| `aggregator` | the merchant | the aggregator | the aggregator's partners |

## Words that are not provider roles

### APM: alternative payment method

Any payment method that is not one of the international card brands; some people mean anything that is not a card at all. Wallets, bank transfers, real-time payments, cash vouchers, pay-later plans and carrier billing are all APMs. "Local payment method" (LPM) means much the same, with the stress on methods used in one country.

APM describes a payment method, not a company, so it is not a role. It is not a method `type` here either, because it says only what a method is not. A method is filed under what it is: see the types below.

### ISV: independent software vendor

A software company whose product has payments built in: a shop platform, booking or invoicing software, a point-of-sale system. The ISV integrates one or more providers, and its customers accept payments through that provider from inside the software.

An ISV is a way payment services reach merchants. It is not the company processing the payment, so it is not a role here. A software company that goes on to become a payment facilitator or a merchant of record is listed as a provider under those roles.

## Payment method types

The values of `type` in a method file.

| `type` | What it is |
| --- | --- |
| `card` | A card brand. The payer enters a card number or uses a saved card, and can dispute a payment through the card issuer. |
| `wallet` | A digital wallet. The payer confirms the payment in the wallet's app or by scanning a QR code. |
| `real_time_payment` | A national instant payment system that moves money between bank accounts in seconds, usually by QR code or approval in a banking app. |
| `bank_redirect` | Online banking. The payer is sent to their own bank's site or app, signs in and approves the payment. |
| `bank_transfer` | The payer sends the money themselves to an account or reference given at checkout. |
| `cash_voucher` | The payer gets a voucher or barcode and pays in cash at a shop, bank or payment point before it expires. |
| `bnpl` | Buy now, pay later. The payer pays in instalments or at a later date; the pay-later company pays the merchant. |
| `prepaid_voucher` | The payer buys a prepaid card or code in advance and enters it at checkout. |
| `bank_debit` | The payer authorises the merchant to collect from their bank account. |
| `carrier_billing` | The charge is added to the payer's mobile phone bill. |
| `stablecoin` | The payer pays with a stablecoin from a crypto wallet. |

## Other terms

- **Issuer**: the bank or institution that gave the payer their card or account.
- **Card network** (card scheme): the organisation whose rules and systems connect issuers and acquirers, such as Visa or Mastercard.
- **Processor**: the company that operates the systems an acquirer uses to authorise and settle payments. It may be the acquirer itself or a contractor.
- **Merchant account**: the account an acquirer opens for a merchant to accept card payments, identified by a merchant ID (MID).
- **Sub-merchant**: a merchant accepting payments under a payment facilitator's master merchant account.
- **Settlement**: paying the merchant the money collected from payers, less fees.
- **Chargeback**: a payment reversed by the issuer after the cardholder disputes it.
- **Local acquiring**: processing a card payment through an acquirer in the cardholder's own country, which issuers approve more readily than a payment from abroad.
