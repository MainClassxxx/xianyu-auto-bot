# 前端开发文档

## 🚀 快速开始

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:3000

### 生产构建

```bash
npm run build
```

### Docker 部署

```bash
docker-compose up -d frontend
```

## 📁 目录结构

```
frontend/
├── src/
│   ├── components/
│   │   └── Layout.vue          # 主布局组件
│   ├── views/
│   │   ├── Dashboard.vue       # 仪表盘
│   │   ├── Accounts.vue        # 账号管理
│   │   ├── Items.vue           # 商品管理
│   │   ├── Orders.vue          # 订单管理
│   │   ├── Conversations.vue   # 对话消息
│   │   ├── AutoReply.vue       # 自动回复
│   │   ├── AutoDelivery.vue    # 自动发货
│   │   ├── Notifications.vue   # 通知管理
│   │   ├── Stats.vue           # 数据统计
│   │   └── Settings.vue        # 系统设置
│   ├── router/
│   │   └── index.js            # 路由配置
│   ├── api/                    # API 接口（待实现）
│   ├── store/                  # 状态管理（待实现）
│   ├── assets/                 # 静态资源
│   ├── App.vue                 # 根组件
│   └── main.js                 # 入口文件
├── index.html
├── package.json
├── vite.config.js
└── Dockerfile
```

## 🎨 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Element Plus** - Vue 3 组件库
- **Vue Router** - 官方路由管理器
- **Pinia** - Vue 状态管理
- **Vite** - 下一代前端构建工具
- **Axios** - HTTP 客户端

## 📊 功能模块

### 已完成

- ✅ 项目脚手架
- ✅ 路由配置
- ✅ 主布局组件
- ✅ 仪表盘页面
- ✅ 账号管理页面
- ✅ 商品管理页面
- ✅ 订单管理页面
- ✅ 自动回复页面
- ✅ 自动发货页面
- ✅ 系统设置页面
- ✅ Docker 配置

### 待实现

- [ ] API 接口调用封装
- [ ] 状态管理（Pinia）
- [ ] 对话消息页面
- [ ] 通知管理页面
- [ ] 数据统计图表（ECharts）
- [ ] 权限管理
- [ ] 主题切换
- [ ] 移动端适配

## 🔧 开发指南

### 添加新页面

1. 在 `src/views/` 创建新组件
2. 在 `src/router/index.js` 添加路由
3. 在 `src/components/Layout.vue` 添加菜单项

### 调用 API

```javascript
// src/api/index.js
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 5000
})

export const getAccounts = () => api.get('/accounts')
export const addAccount = (data) => api.post('/accounts', data)
```

### 状态管理

```javascript
// src/store/account.js
import { defineStore } from 'pinia'

export const useAccountStore = defineStore('account', {
  state: () => ({
    accounts: []
  }),
  actions: {
    async fetchAccounts() {
      const res = await getAccounts()
      this.accounts = res.data
    }
  }
})
```

## 📖 相关文档

- [Vue 3 文档](https://vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)
- [Vite 文档](https://vitejs.dev/)
- [Pinia 文档](https://pinia.vuejs.org/)

---

**Created**: 2024-03-10  
**Version**: 2.0.0
