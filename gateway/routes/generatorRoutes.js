const express = require("express");
const router = express.Router();
const axios = require("axios");
const os = require("os");
const multer = require("multer");
const fs = require("fs");

const uploadtoS3 = require("../utils");
const upload = multer({ dest: os.tmpdir() });
const constants = require("../constants");
const { Campaign } = require("../models");

router.post("/create-campaign", upload.single("file"), async (req, res) => {
  const user = req.user;
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

  const {
    template_key = "template.html",
    campaign_name = "default",
    company_name,
  } = req.body;

  try {
    const campaign = await Campaign.create({
      campaign_name,
      company_name,
      created_by: user.id,
    });

    const event = {
      type: "CAMPAIGN_CREATED",
      data: {
        template_key,
        campaign_name,
        file_url,
        campaign_id: campaign.id,
        company_name,
      },
    };

    await axios.post(constants.EVENT_BUS_SRV, event).catch((err) => {
      console.log(err);
      res.status(err.response.status).send(err.response.data);
    });

    res.status(201).send(campaign);
  } catch (error) {
    console.log(error.errors);
    res.status(400).send(error.errors);
  }
});

module.exports = router;
