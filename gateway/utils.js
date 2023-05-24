require("dotenv").config();

const AWS = require("aws-sdk");

AWS.config.update({
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  region: "us-east-1",
});

const useLocalStack = process.env.USE_LOCALSTACK || 0;

if (useLocalStack) {
  const endpoint = process.env.LOCALSTACK_ENDPOINT;

  AWS.config.update({
    endpoint: endpoint,
    s3ForcePathStyle: true,
  });
}

const s3 = new AWS.S3();

const bucketName = "certificate-templates";

const uploadtoS3 = (file, object_key) => {
  return new Promise((resolve, reject) => {
    const uploadParams = {
      Bucket: bucketName,
      Key: object_key,
      Body: file,
    };

    s3.upload(uploadParams, (err, data) => {
      if (err) {
        console.error(err);
        reject(err);
      } else {
        console.log("File uploaded successfully");
        resolve(data.Location);
      }
    });
  });
};

module.exports = uploadtoS3;
