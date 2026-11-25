# Contributing

[中文](CONTRIBUTING.zh-CN.md)

Changes come in as pull requests. Each one is checked automatically, then reviewed by a person.

## What the registry accepts

- **Facts with a public source.** Every coverage entry needs `source`: an https page anyone can open that shows the provider supports the method. A page behind a login, a PDF sent by email or "we know this internally" cannot be checked by a reader, so it is not a source.
- **Online payments only.** A method belongs here if a merchant can offer it at an online checkout, on a bill, or through a payment link. Methods that only work in person, and products that only pay money out, do not.
- **No marketing copy, rankings, prices, fees or logos.** Pull requests that add them are declined.

## If you work for a provider

You are the best source for your own entry, and you are welcome to keep it up to date.

**To correct or extend your entry**, edit `data/providers/<your-id>.yaml`:

1. Fix `name`, `website` or `roles`. Roles are defined in the [glossary](GLOSSARY.md#provider-roles); list every one that applies.
2. Add or correct coverage entries. For each one give the method's `id`, the payer `countries` (or `global: true`), optionally the `currencies`, a `source`, and today's date as `checked`.
3. Set `source_type: self_reported` on the entries you write. The `source` is still required: link the page on your site or documentation that lists the method.
4. Add your GitHub username under `maintainers` if you will keep the file current.

Say in the pull request that you work for the provider. We may ask you to confirm it, for example from an address on the company's domain.

**To register a provider that is not listed**, add `data/providers/<id>.yaml` with `id`, `name`, `website`, `roles` and `coverage`. An empty `coverage: []` is fine to start with.

**To add `merchant_countries`**, also give `merchant_countries_source`: the public page that lists where a business must be registered to sign up.

## Adding or correcting a payment method

Add `data/methods/<id>.yaml`, or edit the existing file.

- The `id` is a lowercase slug of the name: `touch-n-go`, `mb-way`.
- A method is what the payer holds. One wallet reached through several flows is one method; two wallets that share a name are two (`line-pay` in Japan, `rabbit-line-pay` in Thailand).
- Name the payment product, not the institution behind it, where the two differ: K PLUS, not Kasikorn Bank. Put the other name in `aliases`.
- `countries` are where the payers are, not where merchants can accept it.
- Say in the pull request which public page shows the method exists and where it is used.

## Writing the files

- Country codes are ISO 3166-1 alpha-2 and currency codes are ISO 4217, in capitals: `GB`, not `UK`; `CNY`, not `RMB`. List member countries one by one instead of `EU`.
- **Write Norway as `"NO"`, in quotes.** A bare `NO` means "false" in YAML.
- Keep coverage entries in order of `method`, one entry per method.
- `checked` is the day you last opened the source, as `YYYY-MM-DD`.

Run the check before you open the pull request:

```bash
pip install -r requirements.txt
python3 scripts/validate.py
```

It prints one line per problem and says what to change.

## Disagreements

If you think an entry is wrong and have no public page to prove it, open an issue and say what you know. An entry whose source no longer shows what it claims will be corrected or removed.
