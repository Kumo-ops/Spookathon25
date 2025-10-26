// helper.js
document.addEventListener("DOMContentLoaded", () => {
  console.log("helper.js loaded ✅");

  // ----- Grab elements -----
  const price       = document.getElementById("price");            // <input type="number">
  const idea        = document.querySelector(".idea-input");       // textarea
  const submitBtn   = document.querySelector(".submit-btn");       // button
  const gender      = document.getElementById("gender");           // <select>
  const personImage = document.getElementById("person-image");     // <img>

  // ===== PRICE: block scientific notation & sanitize =====
  if (price) {
    // block typing e/E/+/- in number inputs
    price.addEventListener("keydown", (e) => {
      if (["e", "E", "+", "-"].includes(e.key)) e.preventDefault();
    });
    // strip any pasted/typed non-digits/dot
    price.addEventListener("input", () => {
      price.value = price.value.replace(/[^\d.]/g, "");
    });
  }

  // ===== SUBMIT IDEA =====
  if (submitBtn && idea) {
    submitBtn.addEventListener("click", () => {
      const txt = idea.value.trim();
      if (!txt) {
        alert("Please enter your costume idea first!");
        return;
      }
      console.log("Submitted idea:", txt);
      idea.value = "";

      //reveal hidden text boxes next to body
      const headBox = document.getElementById("head-textbox").style.display = "block";
      const bodyBox = document.getElementById("body-textbox").style.display = "block";
      const legsBox = document.getElementById("legs-textbox").style.display = "block";

      // reveal hidden arrows
      ["arrow-head", "arrow-body", "arrow-legs"].forEach(id => {
        document.getElementById(id).style.display = "block";
      });
    });
  }


  // ===== GENDER -> swap image =====
  if (gender && personImage) {
    const SRC = {
      male:   "transparentMale.png",
      female: "transparentFemale.png",
      "":     "transparentMale.png", // default
    };

    const updateImage = () => {
      const v = (gender.value || "").toLowerCase();
      personImage.src = SRC[v] ?? SRC[""];
      personImage.alt =
        v === "female" ? "Female Person Icon" :
        v === "male"   ? "Male Person Icon"   :
                         "Person Icon";
    };

    gender.addEventListener("change", updateImage);
    gender.addEventListener("input",  updateImage); // some browsers fire input
    updateImage(); // set initial image
  }
});
