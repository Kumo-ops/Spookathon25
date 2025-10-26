// helper.js

document.addEventListener("DOMContentLoaded", () => {
  console.log("helper.js loaded ");

  // Get form elements
  const price = document.getElementById("price");
  const age = document.getElementById("age");
  const idea = document.querySelector(".idea-input");
  const submitBtn = document.querySelector(".submit-btn");

  // --- Prevent scientific notation characters ---
  document.addEventListener("DOMContentLoaded", () => {
    const price = document.getElementById("price");

  // Block invalid keys (scientific notation and math signs)
  price.addEventListener("keydown", (e) => {
    if (["e", "E", "+", "-"].includes(e.key)) e.preventDefault();
  });

  // Also filter out pasted input or other invalid text
  price.addEventListener("input", () => {
    price.value = price.value.replace(/[^\d.]/g, "");
  });
})

  // --- Only allow numbers and dot for price ---
  price.addEventListener("input", () => {
    price.value = price.value.replace(/[^\d.]/g, "");
  });

  // --- Handle submit button click ---
  submitBtn.addEventListener("click", () => {
    const ideaText = idea.value.trim();
    if (ideaText === "") {
      alert("Please enter your costume idea first!");
      return;
    }

    console.log("Submitted idea:", ideaText);
    idea.value = ""; // clear text area
  });
    if (genderInput && personImage) {
    genderInput.addEventListener("input", () => {
      const value = genderInput.value.toLowerCase();

      if (value === "male") {
        personImage.src = "Body.png";
      } 
      else if (value === "female") {
        personImage.src = "femaleIcon.jpg";
      } 
      else {
        personImage.src = "Body.png"; // default
      }
    });
  }
});

