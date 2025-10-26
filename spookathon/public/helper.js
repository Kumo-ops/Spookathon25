// helper.js
document.addEventListener("DOMContentLoaded", () => {
  console.log("helper.js loaded");

  // ----- Grab elements -----
  const category    = document.getElementById("category");
  const age         = document.getElementById("age");
  const price       = document.getElementById("price");
  const idea        = document.querySelector(".idea-input");
  const submitBtn   = document.querySelector(".submit-btn");
  const gender      = document.getElementById("gender");
  const personImage = document.getElementById("person-image");

  // ===== PRICE: blocks scientific notations =====
  if (price) {
    price.addEventListener("keydown", (e) => {
      if (["e", "E", "+", "-"].includes(e.key)) e.preventDefault();
    });
    price.addEventListener("input", () => {
      price.value = price.value.replace(/[^\d.]/g, "");
    });
  }

  // ===== Log when filters change, shown in DevTools =====
  [category, age, gender, price].forEach(el => {
    if (!el) return;
    el.addEventListener("change", () => {
      console.log("Filter changed:", {
        category: category?.value,
        age: age?.value,
        gender: gender?.value,
        price: price?.value
      });
    });
  });

  // ===== FETCH RECOMMENDATIONS FROM BACKEND =====
  const fetchRecommendations = async () => {
    const payload = {
      category: category?.value || "all",
      price: parseFloat(price?.value) || 0,
      age: age?.value || "Adult",
      gender: gender?.value || "",
    };
    console.log("Sending payload:", payload);

    try {
      const res = await fetch("http://127.0.0.1:8000/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error("Backend request failed");
      const data = await res.json();

      const fill = (id, part) => {
        const box = document.getElementById(id);
        if (!box) return;
        const link = box.querySelector("a");
        if (!link) return;

        if (part) {
          link.textContent = part.title || "View";
          link.href = part.url || "#";
        } else {
          link.textContent = "No match";
          link.href = "#";
        }
      };

      fill("head-textbox", data.head);
      fill("body-textbox", data.body);
      fill("legs-textbox", data.legs);

      console.log("Received recommendations:", data);
    } catch (error) {
      console.error("Failed to fetch recommendations:", error);
    }
  };

  // ===== SUBMIT IDEA =====
  if (submitBtn) {
    submitBtn.addEventListener("click", async (e) => {
      // in case the button is inside a <form>
      e.preventDefault();

      console.log("Submit clicked with filters:", {
        category: category?.value,
        age: age?.value,
        gender: gender?.value,
        price: price?.value,
        idea: idea?.value?.trim()
      });

      const txt = idea?.value?.trim() || "";
      if (!txt) {
        // keep the alert if you want, but don't block fetch/logging
        console.warn("Idea is empty — continuing anyway to fetch recommendations.");
      } else {
        console.log("Submitted idea:", txt);
        idea.value = "";
      }

      // show the three link boxes
      ["head-textbox", "body-textbox", "legs-textbox"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = "block";
      });

      // show the arrows
      ["arrow-head", "arrow-body", "arrow-legs"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = "block";
      });

      // now actually call the backend
      await fetchRecommendations();
    });
  }

  // ===== GENDER -> swap image =====
  if (gender && personImage) {
    const SRC = {
      male:   "transparentMale.png",
      female: "transparentFemale.png",
      "":     "transparentMale.png",
    };

    const updateImage = () => {
      const v = (gender.value || "").toLowerCase();
      personImage.src = SRC[v] ?? SRC[""];
      personImage.alt = v === "female" ? "Female Person Icon"
                        : v === "male" ? "Male Person Icon"
                        : "Person Icon";
    };

    gender.addEventListener("change", updateImage);
    gender.addEventListener("input",  updateImage);
    updateImage();
  }
});
