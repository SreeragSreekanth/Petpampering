document.addEventListener("DOMContentLoaded", function () {
    let petTypeSelect = document.getElementById("id_pet_type");
    let breedSelect = document.getElementById("id_breed");

    if (petTypeSelect) {
        petTypeSelect.addEventListener("change", function () {
            let petTypeId = this.value;
            if (petTypeId) {
                fetch(`/load-breeds/?pet_type=${petTypeId}`)
                    .then(response => response.json())
                    .then(data => {
                        breedSelect.innerHTML = '<option value="">---------</option>';
                        data.forEach(breed => {
                            let option = document.createElement("option");
                            option.value = breed.id;
                            option.textContent = breed.name;
                            breedSelect.appendChild(option);
                        });
                    })
                    .catch(error => console.error("Error fetching breeds:", error));
            } else {
                breedSelect.innerHTML = '<option value="">---------</option>';
            }
        });
    }
});
