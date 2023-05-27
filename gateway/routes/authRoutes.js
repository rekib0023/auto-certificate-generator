const express = require("express");
const router = express.Router();
const axios = require("axios");

const constants = require("../constants");

router.post("/signup", async (req, res) => {
  try {
    const response = await axios.post(
      `${constants.AUTH_SRV}/api/signup`,
      req.body
    );

    const { access_token, refresh_token } = response.data;

    delete response.data.access_token;
    delete response.data.refresh_token;

    res.cookie("access_token", access_token, {
      httpOnly: true,
    });

    res.cookie("refresh_token", refresh_token, {
      httpOnly: true,
    });

    const event = {
      type: "USER_CREATED",
      data: response.data,
    };

    await axios
      .post(`${constants.EVENT_BUS_SRV}/events`, event)
      .catch((err) => {
        console.log(err);
      });

    return res.status(201).send(response.data);
  } catch (error) {
    console.log(error);
    if (error.response) {
      return res.status(error.response.status).send(error.response.data);
    } else {
      return res.status(500).send({ error: "Internal server error" });
    }
  }
});

router.post("/login", async (req, res) => {
  try {
    const response = await axios.post(
      `${constants.AUTH_SRV}/api/login`,
      req.body
    );
    const { access_token, refresh_token } = response.data;

    delete response.data.access_token;
    delete response.data.refresh_token;

    res.cookie("access_token", access_token, {
      httpOnly: true,
    });

    res.cookie("refresh_token", refresh_token, {
      httpOnly: true,
    });

    return res.status(201).send(response.data);
  } catch (error) {
    console.log(error);
    if (error.response) {
      return res.status(error.response.status).send(error.response.data);
    } else {
      return res.status(500).send({ error: "Internal server error" });
    }
  }
});

router.post("/logout", (req, res) => {
  res.clearCookie("access_token");
  res.clearCookie("refresh_token");
  res.send("Logged out");
});

router.post("/refresh-token", async (req, res) => {
  try {
    const { access_token } = req.cookies;
    const response = await axios
      .post(`${constants.AUTH_SRV}/api/refresh-token`, null, {
        headers: {
          Cookie: `access_token=${access_token}; HttpOnly`,
        },
      })
      .catch((error) => {
        return res.status(error.response.status).send(error.response.data);
      });
    res.cookie("access_token", response.data.access_token, {
      httpOnly: true,
    });
    console.log(response.data);
    return res.status(response.status);
  } catch (error) {
    console.log(error);
    return res.status(500).send({ error: "Internal server error" });
  }
});

module.exports = router;
