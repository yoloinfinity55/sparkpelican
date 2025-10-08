---
layout: post.njk
title: "将 Eleventy 网站部署到 GitHub Pages 的常见问题解析"
date: 2025-10-06
description: 解决将 Eleventy 网站部署到 GitHub Pages 时遇到的常见问题，包括分支设置、令牌配置和文章链接 404 错误。
author: "Infinity Spark"
readingTime: "3 min read"
---

当你按照教程将 Eleventy (11ty) 网站部署到 GitHub Pages 时，通常会遵循一系列步骤，包括创建部署分支和设置 GitHub Actions 自动化工作流。然而，在这个过程中，有几个关键点常常引起混淆，甚至导致部署失败。

本文将总结两个在部署过程中遇到的真实问题，帮助你避开这些常见的“坑”。

## 问题一：`gh-pages` 分支真的是“可选”的吗？

许多教程（包括我参考的指南）在创建部署分支时会提到“（可选）”字样。

```bash
# 指南中的步骤
git checkout --orphan gh-pages
git reset --hard
git commit --allow-empty -m "Initial commit for gh-pages"
git push origin gh-pages
```

**结论是：对于本指南描述的自动化部署流程，这一步实际上是必需的，而不是可选的。**

### 为什么必需？

GitHub Actions 的工作流程是：在 `main` 分支有更新时，自动构建你的网站（生成 `_site` 文件夹），然后将这个文件夹的内容推送到一个指定的分支（通常是 `gh-pages`），GitHub Pages 再从这个分支读取文件并展示你的网站。

如果 `gh-pages` 分支在 GitHub 远程仓库上不存在，那么当 GitHub Actions 第一次运行时，`push` 操作会因为找不到目标分支而失败。

因此，**提前手动创建并推送一个空的 `gh-pages` 分支，是为自动化部署提供一个可以推送的目标，这是确保工作流首次运行成功的关键准备步骤。**

## 问题二：修复 GitHub Actions 配置文件中的 `github_token`

在设置 `.github/workflows/deploy.yml` 文件时，一个微小但致命的错误是 `github_token` 的配置。

**错误的配置：**
```yaml
- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: $ # 这是一个无效的占位符
    publish_dir: ./_site
```

这个 `$` 符号只是一个占位符，如果直接使用，工作流会因为没有权限推送到你的仓库而失败。

**正确的配置：**
必须使用 GitHub Actions 提供的特殊语法来访问它为每次运行自动生成的令牌。

```yaml
- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }} # 正确的语法
    publish_dir: ./_site
```

### 优化后的完整工作流

这是一个经过修正和优化的 `deploy.yml` 文件，它使用了更新的 Actions 版本、更合适的 Node.js 版本，并开启了依赖缓存以加快构建速度。

```yaml
# .github/workflows/deploy.yml

name: Deploy 11ty Blog to GitHub Pages

on:
  push:
    branches:
      - main

jobs:
  build-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18' # 使用一个较新的 LTS 版本
          cache: 'npm' # 缓存 npm 依赖

      - name: Install dependencies
        run: npm ci # 在 CI/CD 环境中比 npm install 更快、更安全

      - name: Build the site
        run: npm run build

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./_site
```

## 问题三：部署成功但文章链接 404 Not Found

有时你会发现，网站主页 `yoursite.com` 访问正常，但某一篇具体的文章链接 `yoursite.com/posts/xxxx/` 却返回 404 错误。

这通常不是部署流程的问题，而是 Eleventy 本身的一个特性导致的。

**最可能的原因是：文章的发布日期被设置为了未来。**

例如，如果你的文章元数据（Front Matter）中这样写：

```markdown
---
title: "我的未来文章"
date: 2099-01-01 # 这是一个未来的日期
layout: post.njk
---
```

Eleventy 在执行 `npm run build` 时，会默认**忽略**所有日期在未来的文章。因此，这篇“未来文章”的 HTML 文件根本不会被生成并放到 `_site` 目录中。既然文件不存在，访问它的链接自然就会返回 404。

### 如何解决？

1.  **修改文章日期**：将文章 `.md` 文件中的 `date` 修改为今天或过去的日期。
2.  **强制构建未来文章**：如果你确实需要在本地预览未来的文章，可以在构建命令中加入 `--future` 参数。
    ```json
    // package.json
    "scripts": {
      "build": "eleventy",
      "build-future": "eleventy --future", // 添加一个新命令
      "start": "eleventy --serve"
    },
    ```
    但请注意，用于线上部署的 `build` 命令通常不应包含此参数，以防意外发布未到期的内容。

希望这些总结能帮助你顺利完成 Eleventy 网站的部署！
```
