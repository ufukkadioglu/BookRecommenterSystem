FROM node:18.16.0-alpine

WORKDIR /user_interface

COPY . .

RUN npm ci

RUN npm run build

EXPOSE 3000

CMD [ "npx", "serve", "build" ]
