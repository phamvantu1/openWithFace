FROM node:16
WORKDIR /app
COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD ["npx", "nodemon", "--inspect", "src/iot.js"]
