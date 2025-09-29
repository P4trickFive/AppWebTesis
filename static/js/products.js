function searchProducts() {
        const query = document.getElementById('search').value.toLowerCase();
        const rows = document.querySelectorAll('.product-row');
        rows.forEach(row => {
            const name = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
            const category = row.querySelector('td:nth-child(3)').textContent.toLowerCase();
            if (name.includes(query) || category.includes(query)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
    });
}

//fetch(`/buscar_producto?nombre=${encodeURIComponent(nombre)}`)



document.addEventListener("DOMContentLoaded", function () {
    const nombreInput = document.getElementById("nombre");
    const cantidadInput = document.getElementById("cantidad");
    const precioInput = document.getElementById("precio");
    const categoriaInput = document.getElementById("categoria");
    const datalist = document.getElementById("productosList");

    // Obtener el botón de cancelar desde el HTML
    const cancelarBtn = document.getElementById("cancelar_seleccion");
    cancelarBtn.style.display = "none"; // Ocultar el botón inicialmente

    // Función para realizar la búsqueda
    const realizarBusqueda = (nombre) => {
        fetch(`/buscar_producto?nombre=${encodeURIComponent(nombre)}`)
            .then(response => response.json())
            .then(data => {
                datalist.innerHTML = "";

                data.forEach(producto => {
                    const option = document.createElement("option");
                    option.value = producto.nombre;
                    option.dataset.precio = producto.precio;
                    option.dataset.categoria = producto.categoria;
                    option.dataset.cantidad = producto.cantidad;
                    datalist.appendChild(option);
                });
            })
            .catch(error => console.error("Error al obtener productos:", error));
    };

    nombreInput.addEventListener("input", function () {
        const nombre = nombreInput.value.trim();
        if (nombre.length < 2) {
            datalist.innerHTML = "";
            return;
        }

        // Llamamos a la función de búsqueda solo si hay 2 o más caracteres
        realizarBusqueda(nombre);
    });

    nombreInput.addEventListener("change", function () {
        const selectedOption = [...datalist.options].find(option => option.value === nombreInput.value);
        if (selectedOption) {
            // Rellenamos los campos de información
            cantidadInput.value = selectedOption.dataset.cantidad;
            precioInput.value = selectedOption.dataset.precio;
            categoriaInput.value = selectedOption.dataset.categoria;

            // Bloqueamos el campo 'nombre' para evitar más ediciones (solo lectura)
            nombreInput.readOnly = true;

            // Mostrar el botón de cancelar
            cancelarBtn.style.display = "inline-block";
        }
    });

    // Botón para limpiar el formulario y desbloquear el nombre
    cancelarBtn.addEventListener("click", function () {
        nombreInput.value = "";  // Limpiar el campo de nombre
        nombreInput.readOnly = false;  // Hacer editable el campo de nombre
        cancelarBtn.style.display = "none";  // Ocultar el botón de cancelar

        // Limpiar los otros campos
        cantidadInput.value = "";
        precioInput.value = "";
        categoriaInput.value = "";

        // Limpiar las sugerencias del datalist
        datalist.innerHTML = '';
    });
});
