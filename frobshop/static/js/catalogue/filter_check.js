document.addEventListener("DOMContentLoaded", function() {
    let resultsText = document.querySelector("p.nonefound");
    let filterSection = document.getElementById("filter-section");

    if (resultsText && resultsText.textContent.includes("No products found.")) {
        filterSection.style.display = "none";
    }
});
