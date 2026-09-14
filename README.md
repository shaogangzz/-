# 猪周期领先指标监控

这是一个纯静态网页 + GitHub Actions 数据更新的猪周期研究看板。

## 你只需要做的事情

1. 把整个项目上传到 GitHub 仓库根目录。
2. GitHub → Settings → Pages。
3. Build and deployment 选择 **Deploy from a branch**。
4. Branch 选择 `main`，目录选择 `/ (root)`。
5. 保存。
6. 等待 GitHub Pages 发布，之后直接打开网页地址。

## 自动更新

`.github/workflows/update-pig-cycle-data.yml` 会在工作日定时运行，也可以在 GitHub → Actions → update-pig-cycle-data → Run workflow 手动运行。

网页点击“刷新数据”只负责重新读取云端 `data/data.json`，不会在浏览器里直接抓取数据。

## 重要说明

首次版本已经把网页、自动化框架和 AKShare 接口接入位置准备好。由于公开数据接口的函数名/字段可能随 AKShare 版本调整，脚本不会猜测缺失字段，以免产生“看起来有数据但实际上错误”的结果。运行 Actions 后可以根据日志补齐仔猪、能繁母猪、均重和利润的稳定数据源。

## 6项指标

- 能繁母猪/产能
- 仔猪价格
- 商品猪价格
- 生猪出栏均重
- 生猪期货
- 自繁自养利润

综合判断采用历史分位数 + 趋势，能繁母猪权重最高，避免单看猪价判断周期反转。
