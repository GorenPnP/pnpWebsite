/***** RANDOMIZERS ******/

function randomOf(array) {
    return array[Math.floor(Math.random() * array.length)]
}


/**
 * @returns float >= Math.ceil(min) & <= Math.floor(max)
 */
 function randomFloat(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.random() * (max - min) + min;
}


function round(number, decimalPlaces = 0) {

    // use standard round of Math module
    if (decimalPlaces === 0) { return Math.round(number); }

    // 10 to the power of 'decimalPlaces'
    var x = 1;
    for (; decimalPlaces; decimalPlaces--) { x *= 10; }

    // round
    return Math.round((number + Number.EPSILON) * x) / x;
}

// function luminance(r, g, b) {
//   const color = [r, g, b].map(colorFactor => {
//       colorFactor /= 255;
//       if (colorFactor <= 0.03928) {
//           return colorFactor / 12.92;
//       }
//       return Math.pow(((colorFactor + 0.055) / 1.055), 2.4);
//   });
//   return (color[0] * 0.2126 + color[1] * 0.7152 + color[2] * 0.0722) + 0.05;
// }

// function splitRGB(rgbString) {
//   const partLength = (rgbString.length - 1) / 3;  // 1 or 2
//   const rgbPartRegex = new RegExp(`[\\da-fA-F]{${partLength}}`, 'g');

//   // convert:
//   // '#555' -> [['5'], ['5'], ['5']] -> ['5', '5', '5'] -> ['55', '55', '55'] -> [85, 85, 85]
//   const parts = [...rgbString.matchAll(rgbPartRegex)]
//     .map(part => part[0])
//     .map(part => part.length === 1 ? part + part : part)
//     .map(part => parseInt(part, 16));

//   return parts
// }


/****** UPDATE & DISPLAY VALUES ********/

function updateMaterial(newMaterial) {

  // update material
  currentMaterial = newMaterial;
  document.querySelector(`#current-material`).innerHTML = newMaterial.name;

  // update button bg
  const miningWindowStyle = document.querySelector(`#mining-window`).style;
  miningWindowStyle.setProperty('--bg-color', newMaterial.bgColor);
  miningWindowStyle.backgroundImage = newMaterial.texture ? `url(${newMaterial.texture})` : '';

//  // update button color
//   const lightness = luminance(...splitRGB(newMaterial.bgColor));
//   miningWindowStyle.color = lightness < 0.5 ? "#fff" : "#000";
}

const allBrokenClasses = Array.from(Array(10).keys()).map((_, i) => `broken-${i+1}`);
function updateRigidity(newRigidity) {
  currentRigidity = newRigidity;
  document.querySelector(`#current-rigidity`).innerHTML = newRigidity;

  const ratioBroken = round((currentMaterial.rigidity - currentRigidity) / currentMaterial.rigidity * 10, 0);

  document.querySelector(`#mining-window`).classList.remove(...allBrokenClasses);
  document.querySelector(`#mining-window`).classList.add(`broken-${ratioBroken}`)
}

function hideText() {
  document.querySelector(`#mining-window b`).style.opacity = 0;
}

function updateAmountMined(drops) {
  hideText();

  const table_tag = document.querySelector(`#amount-mined`);

  // init table (add rows for each material)
  for (const drop of drops) {
    const [amount, item] = drop;
    const persistentTag = document.querySelector(`#material-${item}`);

    // update existing row
    if (persistentTag) {
      persistentTag.innerHTML = parseInt(persistentTag.innerHTML) + amount;
      continue;
    }

    // construct new row of material
    const row = document.createElement("DIV");
    row.innerHTML = 
      `<b>${item}: </b>` +
      `<span id="material-${item}">${amount}</span>`;

    table_tag.appendChild(row);
  }
}


/***** EVENT LISTENERS / HOOKS *******/
// function nope() {
//   alert("Nope 😑");
// }


function addEventListeners() {

  document.querySelector(`#mining-window`).addEventListener('click', () => mining())

  document.querySelector("body").addEventListener("keydown", e => {
    if (e.keyCode === 32 && !keyLocked) mining();
  
    // if ([16, 17, 73, 123].includes(e.keyCode)) {
    //   console.log("gotten", e.keyCode)
    //   e.preventDefault();
    //   nope();
    // }
  });
  
  // window.oncontextmenu = () =>
  // {
  //   nope();
  //   return false;     // cancel default menu
  // }
}


window.addEventListener("DOMContentLoaded", () => {
  addEventListeners();

  setInterval(() => {
    const event = new Event('click');
    document.querySelector(`#mining-window`).dispatchEvent(event);
  }, 100);
});

