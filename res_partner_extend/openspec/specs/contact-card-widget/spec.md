# contact-card-widget Specification

## Purpose
TBD - created by syncing change add-contact-card-widget. Update Purpose once the change is archived.

## Requirements

### Requirement: Pestaña de Tarjeta de Contacto en el formulario
El sistema SHALL añadir una nueva pestaña ("Tarjeta de Contacto") a la vista de formulario de `res.partner`, mediante una vista heredada, que contenga el widget de tarjeta de contacto.

#### Scenario: Visualización de la pestaña en un contacto existente
- **WHEN** un usuario abre el formulario de un contacto existente
- **THEN** el sistema muestra la pestaña "Tarjeta de Contacto" junto a las demás pestañas del formulario de contacto

#### Scenario: Visualización de la pestaña en un contacto nuevo
- **WHEN** un usuario crea un nuevo contacto (formulario aún no guardado)
- **THEN** el sistema muestra la pestaña "Tarjeta de Contacto" con el widget renderizado, mostrando valores por defecto (placeholder) para los campos aún no completados

### Requirement: Widget de tarjeta de contacto
El sistema SHALL proporcionar un componente OWL (`ContactCardWidget`) registrado en el registry de campos de Odoo, que muestre en una tarjeta visual: el nombre del contacto, su imagen, su edad calculada (`age`) y su fecha de nacimiento (`birthdate`), leyendo los valores directamente del registro del formulario activo sin realizar llamadas RPC adicionales.

#### Scenario: Renderizado con datos completos
- **WHEN** el contacto tiene `name`, imagen, `birthdate` y `age` definidos
- **THEN** el widget muestra los cuatro datos en la tarjeta: nombre, imagen, edad y fecha de nacimiento formateada según el idioma/localización del usuario

#### Scenario: Renderizado sin imagen
- **WHEN** el contacto no tiene imagen cargada
- **THEN** el widget muestra una imagen por defecto (placeholder) en lugar de un espacio vacío o un error

#### Scenario: Renderizado sin fecha de nacimiento
- **WHEN** el contacto no tiene `birthdate` definido
- **THEN** el widget muestra un valor placeholder (por ejemplo "-") en los campos de edad y fecha de nacimiento, sin lanzar errores en la consola

#### Scenario: Actualización reactiva al editar el nombre
- **WHEN** un usuario modifica el campo `name` del contacto en otra pestaña del formulario, sin guardar aún
- **THEN** el widget de tarjeta de contacto refleja el nuevo nombre inmediatamente, sin recargar la página

### Requirement: Código QR de acceso al contacto
El sistema SHALL mostrar en la tarjeta de contacto un código QR que codifica la URL absoluta del formulario de ese contacto en el backend de Odoo, generado sin llamadas RPC adicionales ni dependencias JavaScript nuevas, reutilizando el mecanismo estándar de generación de códigos de barra/QR del servidor.

#### Scenario: Renderizado del QR en un contacto guardado
- **WHEN** un usuario abre la tarjeta de contacto de un contacto ya guardado (con `id` real)
- **THEN** el widget muestra un código QR que, al escanearse, apunta a la URL absoluta del formulario de ese contacto en el backend de Odoo

#### Scenario: Sin QR en un contacto nuevo sin guardar
- **WHEN** un usuario abre la tarjeta de contacto de un contacto nuevo aún no guardado (sin `id`)
- **THEN** el widget no muestra un código QR (no existe una URL válida a la cual apuntar), sin lanzar errores

### Requirement: Implementación en archivos separados
El sistema SHALL implementar el widget de tarjeta de contacto con tres archivos independientes: un componente JavaScript (lógica OWL), una plantilla QWeb en XML (estructura visual) y una hoja de estilos SCSS (presentación). El componente JavaScript NO SHALL contener el template inline ni estilos inline.

#### Scenario: Separación de responsabilidades verificable en el código fuente
- **WHEN** se inspecciona el código fuente del widget en `static/src/`
- **THEN** existen archivos distintos para el componente JS, la plantilla XML (`t-name` QWeb) y los estilos SCSS, y el componente JS referencia la plantilla mediante `static template` sin definir markup inline

### Requirement: Estilos corporativos de la tarjeta de contacto
El sistema SHALL aplicar una paleta de colores corporativa a la tarjeta de contacto compuesta por azul, gris y naranja, definida mediante variables SCSS propias del widget, sin modificar variables globales del tema de Odoo.

#### Scenario: Colores aplicados a la tarjeta
- **WHEN** se renderiza el widget de tarjeta de contacto
- **THEN** el contenedor principal, los textos secundarios y el elemento de acento/resaltado usan respectivamente los tonos azul, gris y naranja definidos en las variables SCSS del widget

#### Scenario: Estilos aislados del resto del formulario
- **WHEN** el widget se renderiza dentro del formulario de contacto junto a otros campos y pestañas
- **THEN** los estilos del widget se aplican únicamente dentro de su contenedor raíz (clase CSS dedicada) y no alteran la apariencia de otros elementos del formulario

