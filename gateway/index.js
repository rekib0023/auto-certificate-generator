const express = require("express");
const cookieParser = require("cookie-parser");

const authRoutes = require("./routes/authRoutes");
const generatorRoutes = require("./routes/generatorRoutes");
const db = require("./models");
const authorizationMiddleware = require("./middlewares");

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use(cookieParser());

app.use("/api/auth", authRoutes);
app.use(authorizationMiddleware);
app.use("/api/generator", generatorRoutes);

db.sequelize.sync().then(() => {
  app.listen(5002, () => {
    console.log("Listening on 5002");
  });
});
