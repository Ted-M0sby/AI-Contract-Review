# AI 合同审查 Demo 前端

面向房屋租赁合同的 AI 审查演示前端，包含注册、登录、合同列表、合同上传、合同详情与审查结果页面。

## 技术栈

- Vue 3
- Vite
- Vue Router
- jQuery
- Lucide Icons

## 本地启动

```bash
npm install
npm run dev
```

默认开发地址为 `http://localhost:5173`。

## 后端地址

默认后端地址为 `http://192.168.31.37:8888`。需要连接其他后端时，在项目根目录创建 `.env.local`：

```env
VITE_API_BASE_URL=http://your-api-host:8888
```

## 构建

```bash
npm run build
```

构建产物生成在 `dist` 目录中。`node_modules`、`dist` 和本地环境变量文件已加入 `.gitignore`，不需要提交到 GitHub。

