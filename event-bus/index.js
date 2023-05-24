const express = require("express");
const axios = require("axios");

const app = express();
app.use(express.json());

const events = [];

app.post("/events", async (req, res) => {
  const event = req.body;
  console.log("Received event:\n", event)
  events.push(event);

  await axios.post("http://generator-srv:5000/events", event).catch((err) => {
    console.log(err);
  });

  await axios.post("http://auth-srv:5001/events", event).catch((err) => {
    console.log(err);
  });

  res.send({ status: "OK" });
});

app.get("/events", (req, res) => {
  res.send(events);
});

app.listen(5005, () => {
  console.log("Listening on 5005");
});
