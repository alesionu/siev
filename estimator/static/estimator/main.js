

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

document.addEventListener('DOMContentLoaded', () => {

    
    const btnEstimar = document.getElementById('btn-estimar');
    const inputProjectName = document.getElementById('input-project-name');
    const inputM2Terreno = document.getElementById('input-m2-terreno');
    const inputPersonas = document.getElementById('input-personas');
    const selectOrientacion = document.getElementById('select-orientacion');
    const selectFormaTerreno = document.getElementById('select-forma-terreno');
    const loadingSpinner = document.getElementById('loading-spinner');

    const displayCosto = document.getElementById('display-costo');
    const displayTiempo = document.getElementById('display-tiempo');
    const displayDormitorios = document.getElementById('display-dormitorios');
    const displayBanos = document.getElementById('display-banos');
    const displayM2Cocina = document.getElementById('display-m2-cocina');
    const displayM2EstarComedor = document.getElementById('display-m2-estar-comedor');
    const displayM2DormitoriosTotal = document.getElementById('display-m2-dormitorios-total');
    const displayM2BanosTotal = document.getElementById('display-m2-banos-total');
    const displayPlanoImg = document.getElementById('display-plano-img');

    if (btnEstimar) {
        btnEstimar.addEventListener('click', handleEstimateClick);
    }

    async function handleEstimateClick() {
        
        const projectName = inputProjectName.value.trim();
        const m2Terreno = inputM2Terreno.value;
        const personas = inputPersonas.value;

        if (projectName === "") {
            alert("Por favor, introduce un nombre para tu proyecto.");
            inputProjectName.focus();
            return;
        }
        if (m2Terreno <= 0) {
            alert("Por favor, introduce un valor válido para M² del Terreno.");
            inputM2Terreno.focus();
            return;
        }
        if (personas <= 0) {
            alert("Por favor, introduce un número válido de personas.");
            inputPersonas.focus();
            return;
        }

        loadingSpinner.style.display = 'block';
        btnEstimar.style.display = 'none';

        const data = {
            project_name: projectName,
            m2_terreno: parseInt(m2Terreno, 10),
            cantidad_personas: parseInt(personas, 10),
            orientacion: parseInt(selectOrientacion.value, 10),
            forma_terreno: selectFormaTerreno.value
        };

        console.log("Enviando estos datos a la API:", data);

        try {
            const response = await fetch('/api/estimate/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken 
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error del servidor');
            }

            const resultados = await response.json();
            console.log("Resultados recibidos:", resultados);

            displayCosto.innerText = `USD ${resultados.costo_estimado.toLocaleString('es-AR')}`; 
            displayTiempo.innerText = `~ ${resultados.tiempo_meses} Meses`;
            displayDormitorios.innerText = resultados.cantidad_dormitorio;
            displayBanos.innerText = resultados.cantidad_bano;
            displayM2Cocina.innerText = resultados.m2_cocina;
            displayM2EstarComedor.innerText = resultados.m2_estar_comedor;
            displayM2DormitoriosTotal.innerText = resultados.m2_dormitorios_total;
            displayM2BanosTotal.innerText = resultados.m2_banos_total;

            
            const finalImageUrl = `/static/${resultados.url_plano_sugerido}`;
            displayPlanoImg.src = finalImageUrl;

            // --- F. Éxito y Redirección! ---
            alert("¡Estimación guardada con éxito! Serás redirigido al Dashboard.");
            window.location.href = '/'; 
        } catch (error) {
            console.error("Error al estimar:", error);
            alert(`Hubo un error al guardar la estimación:\n${error.message}`);
            loadingSpinner.style.display = 'none';
            btnEstimar.style.display = 'block';
        }
    }
});