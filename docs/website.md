# 下载网站维护

站点地址：https://ningzixi.github.io/CubeMX-CN/

页面是 `docs/` 下的静态 HTML、CSS、JavaScript，无前端构建依赖、外部字体或分析脚本。GitHub Pages 使用 `main` 分支的 `/docs` 目录，`.nojekyll` 跳过 Jekyll 处理。Gitee 保存同样源码并托管正式发行版与便携 ZIP；仓库目前没有可用的 Gitee Pages 入口。

本地预览：

```powershell
python -m http.server 8765 --bind 127.0.0.1 --directory docs
```

然后访问 http://127.0.0.1:8765/ 。

发布新版本时：

1. 验证程序并生成 Windows 便携 ZIP 和 SHA-256 文件。
2. 在 Gitee 和 GitHub 对应标签的发行版上传同一份附件，并从公开链接下载校验。
3. 同步修改 `docs/index.html` 中的版本、文件大小、下载地址和校验值，以及 README 的当前下载地址。保持校验值对应实际附件。
4. 更新兼容性与验证范围，勿把未完成的业务回归写成通过。
5. 检查桌面和手机布局、锚点、图片、下载链接与复制功能，提交并同步两个仓库。

`docs/images/home.png` 为仓库现有真实截图；首页顶部另有明确标注的显示示意。不要将示意当作软件实际界面。

## 配色与国内访问

网站使用原版截图取样的深蓝 `#03234B`、浅蓝 `#D9E9F6`、亮蓝 `#39A9DC`；正文和按钮文字按网页可读性调整对比度。

2026-11-04 复核：仓库 `/pages` 返回 404；Gitee 官方服务集成目录未列出 Pages，V5 OpenAPI 也没有 `/pages` 端点，因此当前没有已确认可用的 Gitee Pages 部署入口。源码托管在 Gitee 不等于可以在 Gitee 域名下运行 HTML 页面。官方下载入口仍优先使用 Gitee 发行版，国内用户可直接打开该发行版而无需经过网站。

若要进一步加速网站本身，需要另选可用的国内静态托管或已有服务器，并根据实际域名和服务条件部署；本次没有新购服务或修改 DNS。
