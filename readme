# Pagina para venta y cotizacion de productos de la tienda Abarrotes Yamessi

El diseño de esta pagina se explica en este documento, y se llevará a cao en varias fases:

## Fase 1: El Producto Mínimo Viable (Implementación Fácil) 🚀

Estos son los elementos básicos para que tu página sea funcional y útil desde el primer día.

    1. Estructura y Diseño Visual (HTML + CSS)

        Qué es: El esqueleto y la apariencia de tu página. Define el logo, los colores de tu marca, la tipografía, un encabezado y un pie de página.

        Requisitos Técnicos (Cliente): Archivos index.html para la estructura y style.css para los estilos. Idealmente, un diseño responsive que se vea bien en celulares.

    2. Catálogo de Productos Visual

        Qué es: Una página que muestra tus productos con foto, nombre y precio. Al principio, puede ser una lista estática.

        Requisitos Técnicos (Cliente): Crear un archivo productos.json con la lista de productos y usar un poco de JavaScript para leerlo y generar el HTML dinámicamente en la página del cliente.

        Preparación para el Futuro (Servidor): Este archivo productos.json podría ser generado automáticamente por un sistema de inventario en el futuro.

    3. Carrusel de Ofertas en Portada

        Qué es: Un slider o carrusel interactivo en la página principal que muestra las promociones más importantes.

        Requisitos Técnicos (Cliente): JavaScript. Puedes usar una librería ligera como Swiper.js para implementarlo fácilmente.

## Fase 2: Mejorando la Experiencia Interactiva (Implementación Intermedia) ✨

Con la base lista, estas funciones harán que la página se sienta moderna y mucho más fácil de usar.

    1. Búsqueda y Filtros en Tiempo Real

        Qué es: Una barra de búsqueda y botones de filtro (por categoría, marca, etc.) que actualizan la lista de productos sin recargar la página.

        Requisitos Técnicos (Cliente): JavaScript. El script leerá el archivo productos.json una vez y luego filtrará los resultados en el navegador del cliente basándose en su entrada.

    2. Carrito de Compras Visual (Sin Pedido)

        Qué es: Un carrito que se actualiza en tiempo real. El cliente puede agregar productos, ver cómo el subtotal cambia al instante y la lista de artículos se guarda aunque cambie de página.

        Requisitos Técnicos (Cliente): JavaScript. Se usa localStorage del navegador para guardar los productos del carrito y que no se pierdan. En esta fase, el carrito aún no envía el pedido.

    3. Galerías de Imágenes por Producto

        Qué es: Permitir que cada producto tenga varias fotos y que el cliente pueda hacer clic en miniaturas para cambiar la imagen principal o hacer zoom.

        Requisitos Técnicos (Cliente): JavaScript para manejar los eventos de clic y cambio de imagen. Las imagenes se subiran a un CDN y los enlaces se almacenaran en el .json de los produtos

## Fase 3: Funciones Avanzadas y Conectividad Futura (Implementación Compleja) 🧠

Estas son funciones de alto impacto que fidelizan al cliente y preparan tu página para procesar ventas reales.

    1. Creador de Listas de Supermercado

        Qué es: Una herramienta para que los usuarios creen y guarden sus propias listas de compras personalizadas en tu página.

        Requisitos Técnicos (Cliente): JavaScript y un uso más avanzado de localStorage para guardar, editar y borrar las listas del usuario.

    2. Barra de Progreso para Envío Gratis

        Qué es: Una barra visual que le dice al cliente: "¡Solo te faltan $XX para el envío gratis!".

        Requisitos Técnicos (Cliente): JavaScript que se conecta con el estado del carrito de compras y calcula la diferencia contra un monto predefinido.

    3. Formulario de Pedido (El Puente al Servidor)

        Qué es: El paso final. Un formulario donde el cliente ingresa sus datos (nombre, dirección, teléfono) y ve un resumen final de su carrito antes de "enviar" el pedido.

        Por qué es importante: Es el objetivo final: capturar la intención de compra del cliente.

        Requisitos Técnicos (Cliente): Un formulario HTML y JavaScript para validar los campos y recopilar toda la información del carrito y del cliente en un solo objeto (JSON).

        Preparación para el Futuro (Servidor): El botón "Realizar Pedido" es el que necesitará conectividad. Inicialmente, podría usar un servicio como Formspree para enviar el pedido a tu correo sin un servidor. Más adelante, este botón haría una llamada a una función sin servidor (como Cloudflare Workers) que procese el pago y registre el pedido en una base de datos. La lógica de pago y guardado de datos NUNCA debe estar en el lado del cliente por seguridad.
