function previewImage(input) {
    var preview = document.getElementById('preview');
    var file = input.files[0];

    if (file) {
        var reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
}

document.querySelector('input[name="profile_picture"]').addEventListener('change', function() {
    previewImage(this);
});