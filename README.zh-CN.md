# Payments Registry 支付方式登记册

[English](README.md)

一份公开的记录：各国的人用什么支付方式付款，哪些支付服务商支持这些方式。由 [paychacha.com](https://paychacha.com) 和服务商自己通过 pull request 共同维护。

按国家浏览：**[paychacha.com/zh/payment-methods](https://paychacha.com/zh/payment-methods)**。

截至 2026-11-25，这里有：

- **715 个支付方式**，付款人分布在 153 个国家和地区：支付宝、iDEAL、Pix、Visa，以及大量本地钱包、银行和现金缴费网络。
- **48 家服务商**：支付服务商、收单机构、支付网关、支付促成商、登记商户和聚合服务商。
- **1231 条覆盖关系**，来自已读过公开支付方式清单的 8 家服务商。每一条说明某家服务商支持某个支付方式、在哪些国家支持，并附上能证明这一点的公开页面链接。

## 里面有什么

```
data/methods/<id>.yaml     每个支付方式一个文件
data/providers/<id>.yaml   每家服务商一个文件，含它支持的支付方式
schema/                    两类文件的 JSON Schema
GLOSSARY.zh-CN.md          PSP、收单机构、网关、PayFac、MoR、聚合服务商、APM、ISV
```

支付方式是付款人用来付款的品牌：

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

服务商是商户签约的公司，`coverage` 列出它支持的支付方式：

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

### 支付方式的字段

| 字段 | 含义 |
| --- | --- |
| `id` | 小写短横线 slug，全库唯一，与文件名相同。 |
| `name` | 品牌在国际上通用的名称。 |
| `aliases` | 当地语言的名称、其他写法，以及各家服务商清单里对它的叫法。 |
| `type` | 11 类之一：`card`、`wallet`、`real_time_payment`、`bank_redirect`、`bank_transfer`、`cash_voucher`、`bnpl`、`prepaid_voucher`、`bank_debit`、`carrier_billing`、`stablecoin`。定义见[术语表](GLOSSARY.zh-CN.md#支付方式类型)。 |
| `countries` | 付款人主要在哪些国家，ISO 3166-1 两位代码。`XK` 表示科索沃。 |
| `global` | 全球通用的品牌（如 Visa、PayPal）写 `true`，代替 `countries`。 |
| `currencies` | 付款人用什么币种付款，ISO 4217 代码。 |
| `website` | 品牌官网。 |

### 服务商的字段

| 字段 | 含义 |
| --- | --- |
| `id`、`name`、`website` | 同上。 |
| `roles` | 这家公司担任的所有角色：`psp`、`acquirer`、`gateway`、`payfac`、`mor`、`aggregator`。定义见[术语表](GLOSSARY.zh-CN.md#服务商角色)。 |
| `merchant_countries` | 商户主体注册在哪些国家可以签约。须同时填 `merchant_countries_source`，即列出这些国家的公开页面。 |
| `maintainers` | 服务商自己负责维护这个文件的员工的 GitHub 用户名。 |
| `coverage` | 每个支持的支付方式一条。 |

每条覆盖关系包括：

| 字段 | 含义 |
| --- | --- |
| `method` | `data/methods/` 下某个文件的 `id`。 |
| `countries` 或 `global` | 服务商在哪些付款人国家支持这个方式，照来源的说法。 |
| `currencies` | 服务商用哪些币种处理这个方式。 |
| `source` | 能证明这一条的公开 https 页面。必填。 |
| `source_type` | `provider_docs`：读自服务商的公开页面。`self_reported`：服务商在 pull request 里自报。`third_party`：其他公开来源。 |
| `checked` | 最近一次核对来源的日期。 |

## 怎样正确理解这些数据

- **没填表示不知道，不表示没有。** 支付方式没有 `countries`，是因为来源没写。服务商名下没有某个支付方式，它仍可能支持，只是还没人登记。
- **覆盖关系是服务商的公开页面在 `checked` 那天的说法。** 服务商会不打招呼地调整清单。依赖某一条之前，请打开 `source` 确认。
- **`countries` 指付款人所在国家。** Adyen 公布的是商户可以使用某个方式的国家，不是付款人在哪，所以它的条目没有 `countries`。
- **支付方式的 `currencies` 只含它所在国家的本币。** 服务商的覆盖关系里常常更多，因为服务商还会列出自己的结算币种。
- **角色是初步判断**，依据常识填写，尚未经各服务商确认。欢迎更正。
- **48 家服务商里有 40 家还没有覆盖关系。** 先列出来，便于它们自己补充。

## 不收什么

登记册只记录事实：没有宣传语，不做排名，不放价格和费率，不收 logo。

只收能用于线上收银台、账单支付、支付链接的支付方式。只能当面使用的方式和只用于出款的产品不收。

## 使用与引用

数据按 [CC BY 4.0](LICENSE) 开放，可以自由使用，包括商用。引用时请附链接：

> 来源：[Payments Registry](https://paychacha.com/zh/payment-methods)，paychacha.com

paychacha.com 上有 37 个国家各自的页面，例如 [paychacha.com/zh/payment-methods/japan](https://paychacha.com/zh/payment-methods/japan)，以及 100 多个支持较广的支付方式各自的页面，例如 [paychacha.com/zh/payment-methods/pix](https://paychacha.com/zh/payment-methods/pix)。

`scripts/` 下的脚本按 [MIT 许可](scripts/LICENSE)开放。品牌和公司名称归各自权利人所有，这里只为指明它们而使用。

## 参与维护

欢迎服务商自己登记、更正自己的信息。任何人都可以补充支付方式或修正错误，只要有公开页面为证。见 [CONTRIBUTING.zh-CN.md](CONTRIBUTING.zh-CN.md)。

每个 pull request 都会跑这项检查：

```bash
pip install -r requirements.txt
python3 scripts/validate.py
```

## 初始数据从哪来

paychacha.com 在 2026-11-24 读取了八家服务商（Stripe、Adyen、Airwallex、Antom、dLocal、Nuvei、PayerMax、KyrenPay）公开的支付方式清单，把 1314 条按品牌合并成每个品牌一条，并去掉了不能用于线上收款的条目。`scripts/import_paychacha.py` 把那份数据转成了这里的文件，各字段怎么得出的写在脚本开头的说明里。
