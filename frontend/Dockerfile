# ⚠️ 修改点：将 node:18 改为 node:22
FROM node:22 AS build-stage

WORKDIR /app

# 复制 package.json 并安装依赖
COPY package.json package-lock.json* ./

# 为了防止网络超时，建议换成淘宝源 (可选，但推荐)
RUN npm config set registry https://registry.npmmirror.com
RUN npm install

# 复制源代码并构建
COPY . .
RUN npm run build

# --- 第二阶段：运行 ---
FROM nginx:stable-alpine as production-stage

COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]