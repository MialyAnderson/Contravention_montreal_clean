document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('rechercheForm').addEventListener('submit', function(e) {
        e.preventDefault();

        var du = document.getElementById('du').value;
        var au = document.getElementById('au').value;

        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/contrevenants?du=' + du + '&au=' + au, true);

        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                var data = JSON.parse(xhr.responseText);
                var comptage = {};
        
                data.forEach(function(item) {
                    var nom = item.etablissement;
                    comptage[nom] = (comptage[nom] || 0) + 1;
                });
        
                var tbody = document.querySelector('#resultatsTable tbody');
                var thead = document.querySelector('#resultatsTable thead tr');
                tbody.innerHTML = '';
                thead.innerHTML = `
                    <th scope="col">Établissement</th>
                    <th scope="col">Nombre de contraventions</th>
                `;
        
                if (window.utilisateurRole === "admin") {
                    thead.innerHTML += `<th scope="col">Actions</th>`;
                }
        
                for (var etab in comptage) {
                    var tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${etab}</td>
                        <td>${comptage[etab]}</td>
                    `;
        
                    if (window.utilisateurRole === "admin") {
                        tr.innerHTML += `
                            <td>
                                <button class="btn btn-sm btn-warning btn-action" onclick="modifierContrevenant('${etab}')">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-danger btn-action" onclick="supprimerContrevenant('${etab}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </td>
                        `;
                    }
        
                    tbody.appendChild(tr);
                }
        
                document.getElementById('resultatsSection').style.display = 'block';
                document.getElementById('resultatsTable').style.display = 'table';
            }
        };
        

        xhr.onerror = function () {
            alert('Erreur réseau');
        };

        xhr.send();
    });
});

function chargerListeRestaurants() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/contrevenants?du=1900-01-01&au=2100-01-01', true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var data = JSON.parse(xhr.responseText);
            var nomsUniques = new Set();
            data.forEach(function(item) {
                nomsUniques.add(item.etablissement);
            });

            var select = document.getElementById('listeRestaurants');
            nomsUniques.forEach(function(nom) {
                var option = document.createElement('option');
                option.value = nom;
                option.textContent = nom;
                select.appendChild(option);
            });
        }
    };
    xhr.send();
}

function ajouterActionsDansTable(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const rows = table.querySelectorAll("tbody tr");
    rows.forEach(row => {
        const nomEtab = row.children[0].textContent;
        const td = document.createElement("td");

        if (window.utilisateurRole === "admin") {
            td.innerHTML = `
                <button class="btn btn-sm btn-warning btn-action" onclick="modifierContrevenant('${nomEtab}')">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger btn-action" onclick="supprimerContrevenant('${nomEtab}')">
                    <i class="fas fa-trash"></i>
                </button>
            `;
        } else {
            td.innerHTML = `<span class="text-muted">Aucune action</span>`;
        }

        row.appendChild(td);
    });
}


function modifierContrevenant(nom) {
    const nouveauNom = prompt("Modifier le nom de l’établissement :", nom);
    if (!nouveauNom || nouveauNom === nom) return;

    const xhr = new XMLHttpRequest();
    xhr.open("PUT", "/api/contrevenant/" + encodeURIComponent(nom), true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onload = function () {
        if (xhr.status === 200) {
            alert("Contrevenant modifié.");
            location.reload();
        } else {
            alert("Erreur : " + xhr.responseText);
        }
    };
    xhr.send(JSON.stringify({ nouveau_nom: nouveauNom }));
}

function supprimerContrevenant(nom) {
    if (!confirm("Supprimer ce contrevenant et ses contraventions ?")) return;
    const xhr = new XMLHttpRequest();
    xhr.open("DELETE", "/api/contrevenant/" + encodeURIComponent(nom), true);
    xhr.onload = function () {
        if (xhr.status === 200) {
            alert("Contrevenant supprimé.");
            location.reload();
        } else {
            alert("Erreur : " + xhr.responseText);
        }
    };
    xhr.send();
}

document.getElementById('formulaireRestaurant').addEventListener('submit', function(e) {
    e.preventDefault();
    var nom = document.getElementById('listeRestaurants').value;

    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/infractions?nom=' + encodeURIComponent(nom), true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var data = JSON.parse(xhr.responseText);
            var tbody = document.querySelector('#infractionsResultat tbody');
            tbody.innerHTML = '';

            data.forEach(function(item) {
                var tr = document.createElement('tr');

                tr.innerHTML = `
                    <td>${item.date}</td>
                    <td>${item.description}</td>
                    <td>${item.montant}$</td>
                    <td>${item.ville}</td>
                `;
                tbody.appendChild(tr);
            });

            document.getElementById('infractionsResultat').style.display = 'block';
        }
    };
    xhr.send();
});

document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.getElementById('toggleResultats');
    const resultsContent = document.getElementById('resultsContent');
    const toggleIcon = document.getElementById('toggleIcon');

    toggleButton.addEventListener('click', function() {
        resultsContent.classList.toggle('hidden');
        if (resultsContent.classList.contains('hidden')) {
            toggleIcon.classList.replace('fa-chevron-down', 'fa-chevron-right');
        } else {
            toggleIcon.classList.replace('fa-chevron-right', 'fa-chevron-down');
        }
    });

    const toggleButtonInf = document.getElementById('toggleInfractions');
    const resultsContentInf = document.getElementById('infractionsContent');
    const toggleIconInf = document.getElementById('toggleIconInfractions');

    toggleButtonInf.addEventListener('click', function() {
        resultsContentInf.classList.toggle('hidden');
        if (resultsContentInf.classList.contains('hidden')) {
            toggleIconInf.classList.replace('fa-chevron-down', 'fa-chevron-right');
        } else {
            toggleIconInf.classList.replace('fa-chevron-right', 'fa-chevron-down');
        }
    });
    
    const filterPills = document.querySelectorAll('.filter-pill');
    filterPills.forEach(pill => {
        pill.addEventListener('click', function() {
            const filterType = this.textContent.trim();
            alert(`Filtrage par: ${filterType}`);
        });
    });
    
    const today = new Date();
    const lastMonth = new Date();
    lastMonth.setMonth(today.getMonth() - 1);
    
    document.getElementById('au').valueAsDate = today;
    document.getElementById('du').valueAsDate = lastMonth;
});

document.getElementById('rechercheForm').addEventListener('submit', function(e) {
    e.preventDefault();
    document.getElementById('loading').style.display = 'flex';
    setTimeout(function() {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('resultatsSection').style.display = 'block';
    }, 1000);
});

chargerListeRestaurants();

