const axios = require("axios");

const constants = require("./constants");

const authorizationMiddleware = async (req, res, next) => {
  try {
    const { access_token } = req.cookies;

    if (access_token === null) {
      res.status(401).json({ message: "Unauthorized" });
    }

    var user = await axios
      .post(`${constants.AUTH_SRV}/api/verify`, null, {
        headers: {
          Cookie: `access_token=${access_token}; HttpOnly`,
        },
      })
      .catch((error) => {
        const response = error.response;
        return res.status(response.status).send(response.data);
      });
    user = user.data;
    delete user.access_token;
    delete user.refresh_token;
    req.user = user;

    next();
  } catch (error) {
    console.log(error);
    res.status(403).json({ message: "Forbidden" });
  }
};

module.exports = authorizationMiddleware;
