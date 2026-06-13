FROM node:22-alpine AS base
WORKDIR /app
RUN corepack enable

FROM base AS deps
COPY package.json .yarnrc.yml ./
RUN yarn install

FROM deps AS development
COPY . .
EXPOSE 3000
CMD ["yarn", "dev"]

FROM deps AS build
COPY . .
RUN yarn build

FROM base AS production
ENV NODE_ENV=production
COPY --from=deps /app/node_modules /app/node_modules
COPY --from=build /app/.next /app/.next
COPY --from=build /app/public /app/public
COPY --from=build /app/package.json /app/package.json
EXPOSE 3000
CMD ["yarn", "start"]
