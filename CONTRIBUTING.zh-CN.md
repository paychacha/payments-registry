# 参与维护

[English](CONTRIBUTING.md)

修改通过 pull request 提交。每个 pull request 先自动检查，再由人审核。[提交 pull request](#提交-pull-request) 在浏览器里几分钟就能完成，不需要安装任何工具。

不想提 pull request 的话，可以[填一张表单](https://github.com/paychacha/payments-registry/issues/new/choose)，由维护者代为修改。

## 登记册收什么

- **有公开来源的事实。** 每条覆盖关系都要有 `source`：一个任何人都能打开、能看出服务商支持该支付方式的 https 页面。需要登录才能看的页面、邮件发来的 PDF、“我们内部知道”，读者都无法核对，不算来源。
- **只收线上收款。** 商户能放在线上收银台、账单或支付链接里的支付方式才收。只能当面使用的方式和只用于出款的产品不收。
- **不收宣传语、排名、价格、费率和 logo。** 加这些内容的 pull request 不会合并。

## 如果你在服务商工作

你自己的条目，你最清楚，欢迎由你来维护。

**更正或补充你们的条目**，编辑 `data/providers/<你们的 id>.yaml`：

1. 改 `name`、`website` 或 `roles`。角色的定义见[术语表](GLOSSARY.zh-CN.md#服务商角色)，符合的都列上。
2. 新增或更正覆盖关系。每条填支付方式的 `id`、付款人所在的 `countries`（或 `global: true`）、`source`，以及当天日期作为 `checked`；`currencies` 可选。
3. 你写的条目标 `source_type: self_reported`。`source` 仍然必填：链接到你们官网或文档里列出这个支付方式的页面。
4. 如果你会持续维护这个文件，把你的 GitHub 用户名加到 `maintainers`。

请在 pull request 里说明你在这家服务商工作。我们可能请你确认，比如用公司域名的邮箱发一封邮件。

**登记一家还没有列出的服务商**，新建 `data/providers/<id>.yaml`，填 `id`、`name`、`website`、`roles` 和 `coverage`。一开始可以写空的 `coverage: []`。

**填 `merchant_countries`** 时要同时填 `merchant_countries_source`：列出商户主体须注册在哪些国家才能签约的公开页面。

## 新增或更正支付方式

新建 `data/methods/<id>.yaml`，或编辑已有文件。

- `id` 是名称的小写短横线写法：`touch-n-go`、`mb-way`。
- 支付方式是付款人手里的那个东西。同一个钱包的几种接入方式算一个；同名的两个钱包算两个（日本的 `line-pay`、泰国的 `rabbit-line-pay`）。
- 产品名和机构名不同时，用支付产品的名称，不用机构名：K PLUS，而不是 Kasikorn Bank。另一个名字放进 `aliases`。
- `countries` 是付款人所在的国家，不是商户可以受理的国家。
- 请在 pull request 里说明哪个公开页面能证明这个支付方式存在、在哪里使用。

## 文件怎么写

- 国家用 ISO 3166-1 两位代码，币种用 ISO 4217 代码，都大写：`GB` 而不是 `UK`，`CNY` 而不是 `RMB`。不写 `EU`，把成员国逐个列出。
- **挪威要写成带引号的 `"NO"`。** 不带引号的 `NO` 在 YAML 里表示“否”。
- 覆盖关系按 `method` 排序，每个支付方式一条。
- `checked` 是你最近一次打开来源的日期，格式 `YYYY-MM-DD`。

## 提交 pull request

### 在浏览器里

只需要一个 GitHub 账号。GitHub 的界面是英文的，下面的按钮名称照原样写。

1. **打开文件。** 服务商是 `data/providers/<id>.yaml`，支付方式是 `data/methods/<id>.yaml`。要新增一个，打开所在文件夹，点 **Add file → Create new file**，文件名写 `<id>.yaml`。
2. **点铅笔图标**（“Edit this file”）。GitHub 会提示先 fork 仓库：点 **Fork this repository**。fork 是你自己名下的一份副本，修改被接受之前先存在那里。
3. **改好内容**，点 **Commit changes…**，用一句话说明改了什么，再点 **Propose changes**。
4. **点 Create pull request。** 回答三个问题（改了什么、公开来源、你是否在这家服务商工作），再点一次 **Create pull request**。
5. **等自动检查。** 绿色对勾表示文件格式正确。红色叉表示有地方要改：点 **Details** 看是哪一行、什么原因，然后在 pull request 的 **Files changed** 页里再次编辑文件，pull request 会自动更新。
6. **维护者审核**后合并，或在 pull request 里向你提问。两种情况 GitHub 都会发邮件通知你。

第一次提 pull request 时，自动检查要等维护者手动放行，所以对勾可能要过一天才出现。

一个 pull request 里要改多个文件：先按上面的步骤改第一个，然后留在 GitHub 在你的 fork 里建的那个分支（名字类似 `patch-1`）上继续改其他文件，最后再创建 pull request。

### 用 git

```bash
gh repo fork paychacha/payments-registry --clone
cd payments-registry
git checkout -b update-my-provider

# 修改文件，然后检查
pip install -r requirements.txt
python3 scripts/validate.py

git commit -am "Stripe: add coverage for Pix"
git push -u origin update-my-provider
gh pr create
```

`validate.py` 每个问题输出一行，并说明该怎么改。pull request 跑的是同一项检查。

### 不提 pull request

[开一个 issue](https://github.com/paychacha/payments-registry/issues/new/choose)，选 **Report an error** 或 **List a provider** 表单，附上能佐证的公开页面，由维护者代为修改。

## 有不同意见时

如果你认为某一条有误，但没有公开页面可以证明，请开一个 issue 说明你了解的情况。来源页面已不再支持其说法的条目，会被更正或删除。
