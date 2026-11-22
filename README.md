# YH 企业官网

基于 Astro 的静态展示站。中文页面位于 `/`，英文页面位于 `/en/`；顶部语言入口会打开当前页面的对应版本。网站展示产品、解决方案、新闻与活动、关于我们及联系方式，不使用询盘表单或数据库。

## 内容来源

- `src/data/products.json` 是 38 个型号、7 个类别和详情参数的站内数据源。原资料不明确的字段保留提示，详见 `PRODUCT_DATA_AUDIT.md`。
- `src/data/mission-content.json` 保存方案和新闻文章。页面使用项目内的产品图片与场景配图。
- 公司邮箱为 `info@yunhetech.net`；WhatsApp 联系二维码位于 `public/media/contact/`。
- `src/data/en-strings.json` 保存英文文案。构建时从同一套中文 Astro 页面生成对应英文页面，保持型号、数值、图片与路由一致。

## 本地验证

```powershell
npm ci
npm run check
npm run build
npm run preview
```

`npm run build` 先生成 87 个中文静态页面，再生成 87 个英文静态页面。通过 `npm run preview` 查看双语站。`npm run dev` 用于编辑中文 Astro 页面；英文静态页面在构建后预览。

新增或修改中文页面文案时，先运行 `npm run build:zh`，再运行 `python scripts/update_en_strings.py` 收集并翻译新增文本。逐条核对 `src/data/en-strings.json` 中的产品术语、数值与资料疑点，然后运行 `npm run build`。正常构建只读取本地词库，不访问翻译服务；缺少英文词条时会报错。

## 部署

`.github/workflows/deploy.yml` 在 `main` 推送后运行检查和构建。站点基址为 `/`，目标域名为 `https://yunhetech.net`；本地修改不会自动推送。

GitHub Pages 使用 Actions 发布，必须在仓库 **Settings → Pages → Custom domain** 中设置 `yunhetech.net`。此发布模式不会从 `CNAME` 文件读取域名设置。随后在阿里云 DNS 中为主机记录 `@` 添加四条 A 记录，分别指向 `185.199.108.153`、`185.199.109.153`、`185.199.110.153` 和 `185.199.111.153`；为 `www` 添加 CNAME，指向 `rosem-5.github.io`。保留现有邮件的 MX、TXT 等记录。待解析和证书就绪后，在 Pages 设置中启用 **Enforce HTTPS**。
