## Why

Los contactos de Odoo no capturan la fecha de nacimiento ni exponen la edad de forma visual y rápida. El equipo necesita un addon (`res_partner_extend`) que añada este dato demográfico como campo obligatorio y lo presente en una pestaña dedicada mediante una tarjeta de contacto con identidad visual corporativa (azul, gris, naranja), para consulta rápida sin tener que interpretar la fecha manualmente.

## What Changes

- Se añade el campo `birthdate` (Fecha de nacimiento) en `res.partner`, obligatorio (`required=True`).
- Se añade el campo computado `age` (Edad), de solo lectura, no almacenado, calculado a partir de `birthdate` respecto a la fecha actual.
- Se agrega una nueva pestaña ("Tarjeta de Contacto") en la vista de formulario de `res.partner` (heredada vía XML).
- Dentro de la pestaña se embebe un widget OWL personalizado (`ContactCardWidget`) que muestra: nombre, imagen, edad, fecha de nacimiento y un código QR con la URL del contacto en el backend de Odoo, con estilo de tarjeta.
- El widget se implementa con archivos separados por responsabilidad: componente JS (`contact_card.js`), plantilla QWeb (`contact_card.xml`) y hoja de estilos SCSS (`contact_card.scss`) — sin templates ni estilos inline.
- Estilos corporativos: paleta azul (primario), gris (texto/fondo secundario) y naranja (acento/resaltado) aplicada a la tarjeta.
- Se registran los assets del widget en el bundle `web.assets_backend` del manifest.

## Capabilities

### New Capabilities
- `partner-birthdate`: Campo obligatorio de fecha de nacimiento y campo computado de edad en `res.partner`.
- `contact-card-widget`: Widget OWL de tarjeta de contacto (nombre, imagen, edad, fecha de nacimiento) con estilos corporativos, integrado en una pestaña del formulario de contacto.

### Modified Capabilities
_Ninguna. No existen specs previos en este proyecto (addon nuevo)._

## Impact

- **Módulo nuevo**: `res_partner_extend` (Odoo 19).
- **Modelo afectado**: `res.partner` (herencia `_inherit`).
- **Vistas afectadas**: vista de formulario de contacto (`res.partner.form`), vía vista heredada XML.
- **Assets**: nuevos archivos JS/XML/SCSS registrados en `web.assets_backend`.
- **Dependencias del manifest**: `base`, `web` (mínimas necesarias para el widget OWL).
- **Sin impacto en datos existentes de terceros** más allá de requerir `birthdate` en contactos nuevos/editados (constraint de campo obligatorio en modelo compartido `res.partner`).
