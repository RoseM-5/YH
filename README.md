# YH 产品资料展示站

这是基于上一版 Astro 网站框架制作的独立副本。页面使用用户提供的 YH Logo、三份产品画册、案例文案、配图和 `展示视频.mp4`；三套画册产品统一按 YH 品牌呈现，原始画册名称与页码留在数据中供核对。本站只做展示，不接收询盘，也不使用业务数据库。

## 页面与组件

| 页面 | 路径 | 内容 |
| --- | --- | --- |
| 首页 | `/` | 展示视频与两行宣传标语、紧凑产品主推、全宽解决方案轮播与可翻页动态卡片 |
| 产品中心 | `/products/` | 50 个型号、7 类筛选与站内搜索 |
| 产品详情 | `/products/{id}/` | 画册图片、产品描述、原始参数、同类产品 |
| 解决方案 | `/solutions/`、`/solutions/{slug}/` | 6 个任务场景；横幅使用资料配图 |
| 新闻与活动 | `/news/`、`/news/{slug}/` | 7 篇行业观察与活动状态说明；横幅使用资料配图 |
| 关于与联系 | `/about/`、`/contact/` | 资料范围与联系说明，不展示虚构联系方式 |

共生成 69 个静态页面。公共布局在 `src/layouts/SiteLayout.astro`；`SiteHeader`、`SiteFooter`、首页 `HomeHero` / `HomeProducts` / `HomeApplications` / `HomeInsights`、产品 `Catalog*`、内容 `Editorial*` 组件分别处理导航、页面结构和交互。`src/scripts/site.ts` 管理导航、搜索和滚动入场；首页脚本只管理首屏和首页动画。

## 数据与素材

- `src/data/products.json` 是产品列表、搜索和详情页的唯一运行时产品数据源。它由 `scripts/prepare_catalog.py` 从三份 `catalog.json` 生成，不在组件中手写型号或参数。
- `image_manifest.json` 记录 205 张画册源图的归属、尺寸、用途与未用原因；172 张产品图片经保持内容的 WebP 转换放在 `public/media/products/`。
- `src/data/editorial.ts` 保存解决方案与行业观察内容，配图映射与案例边界见 `source/content/EDITORIAL_MAPPING.md`。
- 首页视频由文件夹中的 `展示视频.mp4` 转为适合网页加载的 1280 像素宽静音 MP4，放在 `public/media/hero/hero.mp4`；加载前显示同视频画面的 `poster.webp`。其他页面暂不使用视频。
- YH 原始 Logo 位于 `public/media/brand/`。目录中的源数据副本放在 `source/catalogs/` 和 `source/content/`，不依赖运行时连接桌面文件夹。

## 运行与更新

### GitHub Pages 部署

本公开仓库内的 `.github/workflows/deploy.yml` 会在推送到 `main` 后构建并部署网站。首次使用时，在仓库 **Settings → Pages → Build and deployment** 中将来源设为 **GitHub Actions**。部署网址为 `https://rosem-5.github.io/YH/`。构建使用 `GITHUB_PAGES=1` 和 `/YH/` 前缀，不影响本地根路径预览。

### Cloudflare Pages 部署

连接此 GitHub 仓库到 Cloudflare Pages，生产分支选 `main`，构建命令填 `npm run build`，输出目录填 `dist`。站点建好后，可在构建环境变量中设置 `PUBLIC_SITE_URL` 为实际网站域名。连接完成后，推送到 `main` 会自动重新部署。

### 本地运行

```powershell
npm ci
npm run dev
npm run check
npm run build
python scripts/verify_site.py
```

重新从桌面资料生成产品数据与图片：

```powershell
python scripts/prepare_catalog.py --source-dir '..\建站资料'
```

视频转换脚本：`python scripts/prepare_hero.py '..\建站资料\展示视频.mp4'`，需要 `ffmpeg` 或 `imageio-ffmpeg`。运行前将示例路径改为本机资料目录。新增型号时先更新对应画册结构化数据，再运行生成脚本与构建，不需要复制详情页代码。

资料中未提供正式企业联系方式。公开机构案例只用于说明行业任务，页面提供原始链接，不把案例写作 YH 客户项目。参数保留画册原文和单位；具体配置以正式资料为准。
