const axios = require("axios");
const apiChain = require("./apiChain")

let access_token = "";
let expiration = 0;

const auth = async () => {
  console.log("Getting new token...");
  const authReq = await axios("https://accounts.spotify.com/api/token", {
    method: "POST",
    params: {
      grant_type: "client_credentials",
    },
    auth: {
      username: process.env.SPOTIFY_CLIENT_ID,
      password: process.env.SPOTIFY_CLIENT_SECRET,
    },
    headers: {
      Accept: "application/json",
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });

  if (authReq.data.access_token) {
    access_token = authReq.data.access_token;
    expiration = Date.now() / 1000 + authReq.data.expires_in - 10;
  } else {
    throw Error("Could not auth to spotify");
  }
};

const start = async () => {
  try {
    if (Date.now() / 1000 > expiration) {
      await auth();
    }

    const cameraReq = await apiChain("/photo/photo_transformed.jpg", access_token);
    const albumId = cameraReq.albumId;
    console.log(albumId);

  } catch (err) {
    console.log("oups", err);
  }
};

module.exports = { start, access_token };
