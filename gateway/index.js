const express = require("express");
const axios = require("axios");
const os = require("os");
const multer = require("multer");
const fs = require("fs");

const uploadtoS3 = require("./utils");

const app = express();
const upload = multer({ dest: os.tmpdir() });

app.use(express.json());

app.post("/api/create-campaign", upload.single("file"), async (req, res) => {
  if (!req.file) {
    return res.status(400).send("No file uploaded.");
  }

  const { originalname: fileName, path } = req.file;

  const fileExtension = fileName.split(".").pop();

  if (!["xls", "xlsx"].includes(fileExtension)) {
    return res.status(400).send("Invalid file format.");
  }

  const fileContent = fs.readFileSync(path);

  fs.unlinkSync(path);

  const file_url = await uploadtoS3(fileContent, `sheets/${fileName}`);

  if (file_url === null) {
    return res.status(500).send("internal server error");
  }

  const { template_key = "template.html", campaign_name = "default" } =
    req.body;

  // create campaign
  const campaign_id = 11;

  const event = {
    type: "CAMPAIGN_CREATED",
    template_key,
    campaign_name,
    file_url,
    campaign_id,
  };

  await axios.post("http://event-bus-srv:5005/events", event).catch((err) => {
    console.log(err);
  });

  res.status(201).send({ campaign_id, campaign_name });
});

app.post("/api/upload-to-s3", upload.single("file"), async (req, res) => {
  if (!req.file) {
    return res.status(400).send("No file uploaded.");
  }

  const { originalname: fileName, path } = req.file;

  const fileContent = fs.readFileSync(path);
  fs.unlinkSync(path);

  const { type } = req.body;

  const prefix = type === "templates" ? "templates" : "static";

  const file_url = await uploadtoS3(fileContent, `${prefix}/${fileName}`);

  if (file_url === null) {
    return res.status(500).send("internal server error");
  }

  return res.send({ status: "OK" });
});

app.listen(5002, () => {
  console.log("Listening on 5002");
});
