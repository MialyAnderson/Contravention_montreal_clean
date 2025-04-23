document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/plaintes')
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById('tablePlaintes');
            data.forEach(plainte => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${plainte.id}</td>
                    <td>${plainte.nom_etablissement}</td>
                    <td>${plainte.adresse}</td>
                    <td>${plainte.ville}</td>
                    <td>${plainte.date_visite}</td>
                    <td>${plainte.nom_prenom_client}</td>
                    <td>${plainte.description_probleme}</td>
                    <td><button class="btn btn-danger btn-sm" onclick="supprimerPlainte(${plainte.id})">Supprimer</button></td>
                `;
                table.appendChild(tr);
            });
        });
});

function supprimerPlainte(id) {
    if (!confirm("Confirmez-vous la suppression de cette plainte ?")) return;

    const xhr = new XMLHttpRequest();
    xhr.open("DELETE", `/supprime-inspection/${id}`, true);
    xhr.onload = function () {
        if (xhr.status === 200) {
            alert("Plainte supprimée avec succès.");
            location.reload();
        } else {
            alert("Erreur lors de la suppression : " + xhr.responseText);
        }
    };
    xhr.onerror = function () {
        alert("Erreur réseau lors de la suppression.");
    };
    xhr.send();
}