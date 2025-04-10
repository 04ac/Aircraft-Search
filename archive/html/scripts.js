const ERROR_IMAGE_URL = "";

function init() {
  // mode selector
  document
    .querySelector(".mode-selector")
    .addEventListener("click", function (event) {
      modeSelect(event.target);
    });

  // query input
  document
    .querySelector("#queryForm")
    .addEventListener("submit", function (event) {
      event.preventDefault();
      query();
    });
}

///////////////////////////////////////////////////////////////////////////

function modeSelect(cell) {
  const modeSelectorCells = document.querySelectorAll(".mode-selector-cell");
  const queryInstructionBox = document.querySelector(".query-instruction");
  const inputBox = document.querySelector("#number-input");

  if (cell.className != "mode-selector-cell mode-selector-cell-selected") {
    for (let i = 0; i < modeSelectorCells.length; i++) {
      modeSelectorCells[i].className = "mode-selector-cell";
    }
    cell.className = "mode-selector-cell mode-selector-cell-selected";
  }

  mode = cell.getAttribute("data-mode");
  if (mode == "regNo") {
    queryInstructionBox.textContent = "Enter aircraft's registration number:";
    inputBox.placeholder = "N145DQ for example";
  } else if (mode == "flightNo") {
    queryInstructionBox.textContent = "Enter flight number:";
    inputBox.placeholder = "AI441 for example";
  }
}

///////////////////////////////////////////////////////////////////////////

function webRequest(type, url, callback) {
  const loader = document.querySelector(".loader-container");
  loader.style.display = "block";
  fetch(url, {
    method: type,
  })
    .then((response) => response.json())
    .then((response) => callback(response))
    .catch((error) => console.log(error));
}

function query() {
  const mode = document
    .querySelector(".mode-selector-cell-selected")
    .getAttribute("data-mode");
  const inputBox = document.querySelector("#number-input");
  const loader = document.querySelector(".loader-container");
  const results = document.querySelector(".results");
  const resultsImageContainer = document.querySelector(
    ".aircraft-image-container"
  );
  const resultsImage = document.querySelector("#aircraft-image");

  if (mode == "regNo") {
    url = `/query?regno=${inputBox.value}`;
    let response;

    webRequest("POST", url, (response) => {
      console.log(response["success"]);
      if (response["success"]) {
        resultsImageContainer.style.display = "block";
        resultsImage.src = response["aircraft_image_link"];
        resultsImage.alt = "Aircraft image";

        results.textContent = "";
        // results.textContent = JSON.stringify(response, undefined, 4);
        // output(JSON.stringify(response, undefined, 4));
        output(syntaxHighlight(JSON.stringify(response, undefined, 4)));
      } else {
        results.style.color = "#FF0000";
        results.textContent = response["message"];
        resultsImage.alt = "";
        resultsImage.src = ERROR_IMAGE_URL;
        resultsImageContainer.style.display = "block";
      }
      loader.style.display = "none";
    });
  } else if (mode == "flightNo") {
    queryInstructionBox.textContent = "This feature will be available shortly";
    // TODO
  }
}

// https://jsfiddle.net/KJQ9K/554/
function output(inp) {
  const results = document.querySelector(".results");
  results.appendChild(document.createElement("pre")).innerHTML = inp;
}

function syntaxHighlight(json) {
  json = json
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  return json.replace(
    /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
    function (match) {
      var cls = "number";
      if (/^"/.test(match)) {
        if (/:$/.test(match)) {
          cls = "key";
        } else {
          cls = "string";
        }
      } else if (/true|false/.test(match)) {
        cls = "boolean";
      } else if (/null/.test(match)) {
        cls = "null";
      }
      return '<span class="' + cls + '">' + match + "</span>";
    }
  );
}
