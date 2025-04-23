document.querySelector('.file-upload-input').addEventListener('change', function() {
    const fileName = this.files[0].name;
    const uploadText = document.querySelector('.file-upload-btn p');
    uploadText.textContent = 'Fichier sélectionné: ' + fileName;
});