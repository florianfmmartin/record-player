var rp = require('request-promise-native');

const projectUrl = 'https://' + process.env.PROJECT_DOMAIN + '.glitch.me';
const googleVision = require('./googleVision');
const spotify = require('./spotify');
const censoredWords = require('./censoredWords');


// data is a variable that gets passed through the whole chain
// imagePath is the url of the image on the server
function askGoogleVision(data, imagePath) {
  return new Promise(async function(resolve, reject) {
    console.log("\nImage: " + projectUrl + imagePath);
    let gcpVisionOptions = googleVision.getGcpOptions(projectUrl + imagePath);
    let gvGuess = await rp(gcpVisionOptions);
    if (gvGuess) {
      data.gvGuess = gvGuess;
      resolve(data);
    } else {
      reject(Error("No response from Google Vision"));
    }
  });
}

// Gets the "best guess" from the Google Vision response object
// Splits the string into an array to check for words we want to remove
// censoredWords.js has a list of words that should be removed (like 'cd')
function checkGoogleVisionGuess(data) {
  const gvGuess = data.gvGuess;
  console.log(JSON.stringify(gvGuess));
  let guess = gvGuess.responses[0].webDetection.bestGuessLabels[0].label;
  data.gvBestGuess = guess;
  console.log("guess: " + guess);
  let guessArray = guess.split(" ");
  let safeArray = []
  console.log("guessArray: ");
  console.log(guessArray);
  for (var i in guessArray) {
    let safe = true;
    if (censoredWords.censoredWords.indexOf(guessArray[i]) > -1) {
      safe = false; 
    }
    if (safe) {
      safeArray.push(guessArray[i]); 
    }
  }
  data.safeArray = safeArray;
  return data;   
}


// Before asking spotify remove anything in the Google Vision
// guess before a hyphen (-) character. The Google Vision API was
// was putting record label info in, which was confusing the
// Spotify API.

async function askSpotifyApi(spotifyToken, data) {
  const safeGuessArray = data.safeArray;
  let albumId = false;
  let spotifyData = {};
  let splitSafeGuessArray = splitGuessAtHyphen(safeGuessArray);
  for (var i = splitSafeGuessArray.length; i > 0; i--) {
    spotifyData = await spotifyApiRequest(spotifyToken, splitSafeGuessArray.slice(0, i));
    if (spotifyData.albums && spotifyData.albums.items && spotifyData.albums.items[0]) {
      albumId = spotifyData.albums.items[0].id;
    }
    if (albumId) {
      break;
    }
  }
  
  if (!albumId) {
    console.log('Spotify Error -- Out of words to guess');
    throw('No items: ' + splitSafeGuessArray + '(' + safeGuessArray + ')');
  }
  data.albumId = albumId;
  return data;
}

/
async function spotifyApiRequest(spotifyToken, splitSafeGuessArray) {
  let safeGuess = splitSafeGuessArray.join(" ");
  let spotifyQueryOptions = spotify.queryOptions(spotifyToken, safeGuess);
  let spotifyData = await rp(spotifyQueryOptions);
  if (spotifyData.albums.items.length === 0) {
    console.log("No Items");
    return false;
  } else {
    return spotifyData;
  }
}

// This function throws away everything before a hyphen (-) character
// from the Google Vision guess. This is because on a few example
// queries it was adding things like the record label name along with the
// artist which was confusing the spotify API.
function splitGuessAtHyphen(safeGuessArray) {
  let splitArray = safeGuessArray;
  if (safeGuessArray.length > 0) {
    let hyphenIndex = safeGuessArray.indexOf('-');  
    if (hyphenIndex > -1) {
      splitArray = safeGuessArray.slice(hyphenIndex + 1, safeGuessArray.length);
    }
    console.log("Split Array:");
    console.log(splitArray);
  }
  return splitArray;
}


function apiChain(imagePath, req, res) {
  console.log("Image Path: " + imagePath);
  let data = {};
  
  return askGoogleVision(data, imagePath)
  .then(checkGoogleVisionGuess)
  .then(askSpotifyApi.bind(null, req.cookies.spotifyAccessToken))
  .then((data) => {
    data.error = false;
    return data;
  })
  .catch(function (err) {
    console.log(err);
    data.error = true;
    data.errorMessage = err;
    return data;
  });
}

module.exports = apiChain;