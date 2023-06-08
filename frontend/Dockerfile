# Stage 1: Build the Angular app
FROM node:18 as build
WORKDIR /frontend

COPY . .

ADD . /frontend

RUN npm install

RUN npm run build --target=production

# Stage 2: Serve app with nginx server
FROM nginx:1.19.0-alpine as prod-stage

COPY --from=build /frontend/dist /usr/share/nginx/html
COPY ./nginx-custom.conf /etc/nginx/conf.d/default.conf

EXPOSE 4200
CMD ["nginx", "-g", "daemon off;"]