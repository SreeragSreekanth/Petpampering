// static/pet_owner/js/pet_form.js
function initializePetForm(breedData, initialBreedId) {
    console.log("Breed Data Received:", breedData);
    const petTypeSelect = document.getElementById('pet-type-select');
    const breedSelect = document.getElementById('breed-select');

    if (petTypeSelect && breedSelect) {
        console.log("Selects found:", petTypeSelect, breedSelect);
        function updateBreeds() {
            const petTypeId = petTypeSelect.value;
            const breeds = breedData[petTypeId] || [];
            console.log("Updating breeds for petTypeId:", petTypeId, "Breeds:", breeds);

            breedSelect.innerHTML = '<option value="">---------</option>';
            breeds.forEach(breed => {
                const option = document.createElement('option');
                option.value = breed.id;
                option.text = breed.name;
                breedSelect.appendChild(option);
            });

            if (initialBreedId && breeds.some(b => b.id === initialBreedId)) {
                breedSelect.value = initialBreedId;
            }
        }

        updateBreeds();
        petTypeSelect.addEventListener('change', updateBreeds);
    } else {
        console.error('Pet type or breed select element not found');
    }
}