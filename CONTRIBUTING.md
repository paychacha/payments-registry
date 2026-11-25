# Contributing

[中文](CONTRIBUTING.zh-CN.md)

Changes come in as pull requests. Each one is checked automatically, then reviewed by a person. [Opening a pull request](#opening-a-pull-request) takes a few minutes in the browser and needs no tools.

If you would rather not open one, [fill in a form](https://github.com/paychacha/payments-registry/issues/new/choose) and a maintainer will make the change.

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

## Opening a pull request

### In the browser

You need a GitHub account and nothing else.

1. **Open the file.** For a provider that is `data/providers/<id>.yaml`, for a payment method `data/methods/<id>.yaml`. To add a new one, open the folder and choose **Add file → Create new file**, then name it `<id>.yaml`.
2. **Click the pencil icon** ("Edit this file"). GitHub asks to fork the repository: click **Fork this repository**. A fork is your own copy, where your change waits until it is accepted.
3. **Make the change**, then click **Commit changes…**, describe it in one line and click **Propose changes**.
4. **Click Create pull request.** Fill in the three questions (what changed, the public source, whether you work for the provider) and click **Create pull request** again.
5. **Wait for the check.** A green tick means the files are valid. A red cross means something needs fixing: click **Details** to read which line and why, then edit the file again from the pull request's **Files changed** tab. The pull request updates itself.
6. **A maintainer reviews it**, merges it or asks a question in the pull request. GitHub emails you either way.

On your first pull request the check waits for a maintainer to start it, so the tick may take a day to appear.

To change several files in one pull request, make the first edit as above, then stay on the branch GitHub created in your fork (it is named like `patch-1`), edit the other files there, and open the pull request at the end.

### With git

```bash
gh repo fork paychacha/payments-registry --clone
cd payments-registry
git checkout -b update-my-provider

# edit the files, then check them
pip install -r requirements.txt
python3 scripts/validate.py

git commit -am "Stripe: add coverage for Pix"
git push -u origin update-my-provider
gh pr create
```

`validate.py` prints one line per problem and says what to change. It is the same check the pull request runs.

### Without a pull request

[Open an issue](https://github.com/paychacha/payments-registry/issues/new/choose) with one of the forms: **Report an error** or **List a provider**. Give the public page that backs it up, and a maintainer will make the change.

## Disagreements

If you think an entry is wrong and have no public page to prove it, open an issue and say what you know. An entry whose source no longer shows what it claims will be corrected or removed.
