const express = require("express");
const router = express.Router();
const os = require("os");
const multer = require("multer");
const fs = require("fs");

const uploadtoS3 = require("../utils");
const upload = multer({ dest: os.tmpdir() });

router.post("/upload-to-s3", upload.single("file"), async (req, res) => {
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

module.exports = router;
