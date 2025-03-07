document.addEventListener("DOMContentLoaded", function() {
    const petTypeField = document.getElementById("id_pet_type");
    const breedField = document.getElementById("id_breed");

    if (petTypeField && breedField) {
        petTypeField.addEventListener("change", function() {
            const petTypeId = this.value;
            breedField.innerHTML = '<option value="">---------</option>'; // Reset breed dropdown

            if (petTypeId) {
                fetch(`/get_breeds/?pet_type_id=${petTypeId}`)
                .then(response => response.json())
                .then(data => {
                    data.forEach(breed => {
                        const option = document.createElement("option");
                        option.value = breed.id;
                        option.textContent = breed.name;
                        breedField.appendChild(option);
                    });
                })
                .catch(error => console.error("Error fetching breeds:", error));
            }
        });
    }
});
