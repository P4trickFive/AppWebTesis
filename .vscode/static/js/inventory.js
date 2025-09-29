let cart = {};
let totalPrice = 0;

function searchProducts() {
    const searchText = document.getElementById('search-bar').value.toLowerCase();
    const products = document.querySelectorAll('.product-card');
    let foundProducts = false;

    // Ocultamos todos los productos al principio
    products.forEach(product => {
        const name = product.dataset.name.toLowerCase();
        const category = product.dataset.category.toLowerCase();

        // Comprobamos si el nombre o la categoría del producto coinciden con el texto de búsqueda
        if (name.includes(searchText) || category.includes(searchText)) {
            product.style.display = "block";  // Mostrar producto
            foundProducts = true;
        } else {
            product.style.display = "none";  // Ocultar producto
        }
    });

    // Si se encuentran productos, mostramos el contenedor de productos
    if (foundProducts) {
        document.getElementById('products-list').style.display = "grid"; // Usamos "grid" para el diseño de cuadrícula
    } else {
        document.getElementById('products-list').style.display = "none"; // Si no hay productos, ocultamos el contenedor
    }
}


// Función para agregar productos al carrito
document.querySelectorAll('.add-to-cart').forEach(button => {
    button.addEventListener('click', (e) => {
        const productId = e.target.dataset.id;
        const productName = e.target.dataset.name;
        const productPrice = parseFloat(e.target.dataset.price);

        // Agregar al carrito o aumentar cantidad si ya existe
        if (cart[productId]) {
            cart[productId].qty += 1;
        } else {
            cart[productId] = { name: productName, price: productPrice, qty: 1 };
        }

        // Actualizar carrito
        updateCart();
    });
});

// Función para actualizar cantidad carrito
function updateQty(productId, value) {
    const newQty = Math.max(1, value);  // no menor a 1
    cart[productId].qty = newQty;
    updateCart();
}

function removeProduct(productId) {
    const productPrice = cart[productId].price * cart[productId].qty;
    delete cart[productId];
    totalPrice -= productPrice;  // Actualizar el total cuando se elimina un producto
    updateCart();
}

// Función Actualizar el carrito
function updateCart() {
    const cartSummary = document.getElementById('cart-summary');
    cartSummary.innerHTML = "";  // Limpiar carrito
    totalPrice = 0;

    Object.keys(cart).forEach(productId => {
        const product = cart[productId];
        totalPrice += product.price * product.qty;

        cartSummary.innerHTML += `
            <div class="border-b pb-4">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="font-medium">${product.name}</p>
                        <div class="text-sm text-gray-600">Cantidad:
                            <input type="number" value="${product.qty}" min="1" onchange="updateQty('${productId}', this.value)" class="w-12 text-center border">
                        </div>
                    </div>
                    <button class="border border-input px-3 bg-primary1 text-primary-foreground rounded-md" onclick="removeProduct('${productId}')">Eliminar</button>
                </div>
            </div>
        `;
    });

    // Actualizar precio total
    document.getElementById('total-price').textContent = totalPrice.toFixed(2);
}

// Actualizar historial de ventas
function updateSalesHistory() {
    const salesHistoryList = document.getElementById('sales-history');
    salesHistoryList.innerHTML = "";  // Limpiar historial de ventas

    salesHistory.forEach(sale => {
        salesHistoryList.innerHTML += `
            <li>
                <strong>Fecha:</strong> ${sale.date} | 
                <strong>Cliente:</strong> ${sale.customer} | 
                <strong>Total:</strong> S/.${sale.total}
            </li>
        `;
    });
}

// Confirmación de venta y envío de datos
$('#confirmarVentaBtn').click(function(event) {
    event.preventDefault();  // Evitar formulario automáticamento

    if (Object.keys(cart).length > 0) {
        const saleData = {
            productos: Object.keys(cart).map(productId => {
                const producto = cart[productId];
                return {
                    id: productId,  // Envio del ID del producto
                    codigo: producto.codigo,  //Código del producto
                    nombre: producto.name,  //Nombre
                    precio: producto.price,  //Precio
                    cantidad: producto.qty  //Cantidad
                };
            })
        };

        console.log("Datos de la venta a enviar:", saleData);  // Verificar los datos

        $.ajax({
            url: '/realizar_venta',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(saleData),  // Enviar carrito
            success: function(response) {
                console.log("Respuesta del backend:", response);
                alert("Venta confirmada con éxito. Total: S/." + response.total);
                cart = {};  // Vaciar el carrito después de la venta
                updateCart();  // Actualizar carrito
            },
            error: function(error) {
                console.error("Error en la solicitud:", error);
                alert("Hubo un error: " + error.responseJSON.error);
            }
        });
    } else {
        alert("Por favor, añade productos al carrito.");
    }
});