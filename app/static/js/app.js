function copiarLista() {
    let ingredientes = obtenerIngredientes();
    if (ingredientes.length == 0) {
        alert("No hay ingredientes para copiar");
        return;
    }

    navigator.clipboard.writeText(ingredientes)
        .then(() => alert("Lista copiada 📋"))
        .catch(err => console.error(err));
}
function obtenerIngredientes(){
    let ingredientes = [];

    document.querySelectorAll(".ingrediente-texto").forEach(label => {
        // Buscamos el checkbox asociado a este label
        // (En el nuevo diseño, el checkbox está justo antes del label)
        let container = label.parentElement;
        let checkbox = container.querySelector("input[type='checkbox']");
        
        let texto = label.textContent.trim();
        
        // Solo agregamos si NO está tildado
        if (checkbox && !checkbox.checked) {
            ingredientes.push("- " + texto);
        }
    });
    if (ingredientes.length == 0) {
        return ingredientes
    }
    return "🛒 Lista de compras:\n\n" + ingredientes.join("\n");
}
function enviarWhatsApp() {
    let ingredientes = obtenerIngredientes();
    if (ingredientes.length === 0) {
        alert("No hay ingredientes para enviar");
        return;
    }

    let url = "https://wa.me/?text=" + encodeURIComponent(ingredientes);

    window.open(url, "_blank");
}

function exportarPDF() {
// 1. Creamos un contenedor "fantasma" en memoria
    const contenedorTemporal = document.createElement("div");
    
    // Le damos un estilo para que la tabla se vea bien (ancho de escritorio)
    contenedorTemporal.style.width = "1100px";
    contenedorTemporal.style.padding = "30px";
    contenedorTemporal.style.background = "white";

    // 2. Buscamos TODOS los elementos que tengan tu ID (o clase)
    const elementos = document.querySelectorAll("#contenido-menu-completo");
    const ingredientes = document.querySelectorAll(".ingre")
    if (elementos.length === 0) {
        alert("No se encontraron elementos para exportar");
        return;
    }

    // 3. Iteramos y clonamos cada parte dentro de nuestro contenedor temporal
    elementos.forEach((el) => {
        const clon = el.cloneNode(true); // 'true' clona también los hijos (tablas, texto, etc.)
        clon.style.display = "block";    // Nos aseguramos de que sea visible en el PDF
        clon.style.marginBottom = "30px"; // Separación entre secciones
        clon.style.width = "900px";
        contenedorTemporal.appendChild(clon);
    });
    // Creamos el contenedor padre para los ingredientes
    const contenedorIngredientes = document.createElement("div");
    contenedorIngredientes.style.display = "flex";
    contenedorIngredientes.style.flexWrap = "wrap"; // CLAVE: Esto permite el salto de línea
    contenedorIngredientes.style.width = "100%";
    contenedorIngredientes.style.gap = "10px"; // Espacio entre items
    contenedorIngredientes.style.marginTop = "20px";

    // Agregamos un título antes de los ingredientes
    const titulo = document.createElement("h3");
    titulo.innerText = "🛒 Lista de Compras";
    contenedorTemporal.appendChild(titulo);
    ingredientes.forEach((ingre) => {
        // Creamos un clon o un elemento nuevo para cada ingrediente
        const clon = document.createElement("div");
        
        // Estilos para que se vea como un "item" de lista
        clon.style.width = "30%"; // Esto pone 3 ingredientes por fila aproximadamente
        clon.style.fontSize = "12px";
        clon.style.padding = "5px 10px";
        clon.style.borderBottom = "1px solid #eee"; // Una línea sutil divisoria
        clon.style.boxSizing = "border-box"; // Para que el padding no rompa el width
        clon.style.breakInside = "avoid";     // Versión moderna
        clon.style.display = "inline-block";
        // El texto del ingrediente
        clon.innerText = "- " + ingre.innerText.trim(); 

        // Lo metemos en el contenedor que hace wrap
        contenedorIngredientes.appendChild(clon);
    });
    contenedorTemporal.appendChild(contenedorIngredientes);
    // 4. Configuramos el PDF
    const opciones = {
        margin:       0.5,
        filename:     'Mi_Menu_Completo.pdf',
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, scrollX: 0, scrollY: 0 },
        jsPDF:        { unit: 'in', format: 'a4', orientation: 'landscape' },
        pagebreak: { 
            mode: ['avoid-all', 'css', 'legacy'], 
            before: '.salto-pagina' // Opcional: podés forzar un salto antes de la lista de compras
        }
    };

    // 5. Generamos el PDF desde el contenedor temporal
    // Importante: No hace falta agregarlo al body, html2pdf puede leerlo desde la memoria
    html2pdf().set(opciones).from(contenedorTemporal).save();
}