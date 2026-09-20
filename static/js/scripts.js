```javascript
/* =========================================================
   SISTEMA DE OBJETOS PERDIDOS
   JavaScript general
   ========================================================= */


/* =========================================================
   1. CONFIRMACIÓN DE ELIMINACIÓN
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const botonesEliminar =
        document.querySelectorAll(".eliminar");


    botonesEliminar.forEach(function (boton) {

        boton.addEventListener("click", function (evento) {

            const confirmar = confirm(
                "¿Estás seguro de que deseas eliminar este objeto?"
            );


            if (!confirmar) {
                evento.preventDefault();
            }

        });

    });

});


/* =========================================================
   2. PREVISUALIZACIÓN DE FOTOGRAFÍAS
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const camposImagen =
        document.querySelectorAll('input[type="file"]');


    camposImagen.forEach(function (campo) {

        campo.addEventListener("change", function () {

            const archivo = campo.files[0];


            if (!archivo) {
                return;
            }


            if (!archivo.type.startsWith("image/")) {

                alert(
                    "Por favor, selecciona un archivo de imagen."
                );

                campo.value = "";

                return;
            }


            const lector = new FileReader();


            lector.onload = function (evento) {

                let contenedor =
                    campo.closest(".seccion-formulario");


                if (!contenedor) {
                    return;
                }


                let imagenPrevia =
                    contenedor.querySelector(".vista-previa");


                if (!imagenPrevia) {

                    imagenPrevia =
                        document.createElement("img");

                    imagenPrevia.className =
                        "vista-previa";


                    imagenPrevia.style.width = "220px";
                    imagenPrevia.style.height = "160px";
                    imagenPrevia.style.objectFit = "cover";
                    imagenPrevia.style.borderRadius = "8px";
                    imagenPrevia.style.marginTop = "15px";
                    imagenPrevia.style.border =
                        "1px solid var(--borde)";


                    campo.parentElement.appendChild(
                        imagenPrevia
                    );

                }


                imagenPrevia.src =
                    evento.target.result;

            };


            lector.readAsDataURL(archivo);

        });

    });

});


/* =========================================================
   3. EVITAR ENVÍOS DOBLES
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const formularios =
        document.querySelectorAll("form");


    formularios.forEach(function (formulario) {

        formulario.addEventListener("submit", function () {

            const boton =
                formulario.querySelector(
                    'button[type="submit"]'
                );


            if (!boton) {
                return;
            }


            boton.disabled = true;

            boton.style.opacity = "0.7";

            boton.style.cursor = "not-allowed";


            setTimeout(function () {

                boton.disabled = false;

                boton.style.opacity = "";

                boton.style.cursor = "";

            }, 5000);

        });

    });

});
```
