## 1. Estructura del módulo

- [x] 1.1 Crear estructura de carpetas del addon `res_partner_extend` (`models/`, `views/`, `data/`, `static/src/js/`, `static/src/xml/`, `static/src/scss/`, `security/`).
- [x] 1.2 Crear `__manifest__.py` con `name`, `version` (19.0.x.x.x), `depends: ['base', 'web', 'mail']` (mail si la vista base de contacto lo requiere), `data` (vistas) y `assets` (`web.assets_backend`).
- [x] 1.3 Crear `__init__.py` raíz importando `models`.
- [x] 1.4 Crear `models/__init__.py` importando `res_partner`.

## 2. Modelo: fecha de nacimiento y edad

- [x] 2.1 Crear `models/res_partner.py` con `_inherit = 'res.partner'`.
- [x] 2.2 Añadir campo `birthdate = fields.Date(string="Fecha de nacimiento")` (sin `required=True` a nivel de modelo, según decisión de diseño).
- [x] 2.3 Añadir campo computado `age = fields.Integer(string="Edad", compute="_compute_age", store=True)`.
- [x] 2.4 Implementar `_compute_age` con `@api.depends('birthdate')`, calculando años completos entre `birthdate` y `fields.Date.context_today(self)`, devolviendo `0` cuando `birthdate` no está definido.
- [x] 2.5 Verificar manualmente en Odoo shell o UI que `age` se recalcula correctamente al cambiar `birthdate` y guardar (campo `store=True` requiere escritura del registro para persistir el recompute). **Verificado real** vía `odoo shell` en `res_partner_extend_test`: `birthdate=1990-01-01` → `age=36`; reescribir `birthdate=2000-06-15` → `age=26` (recompute inmediato al guardar).

## 3. Cron: recompute periódico de la edad

- [x] 3.1 Implementar en `models/res_partner.py` un método `_cron_update_age(self)` que busque partners con `birthdate` definido y fuerce el recompute de `age` (por ejemplo, invalidando el campo o re-triggereando el compute), escribiendo solo los registros cuyo valor de `age` efectivamente cambió.
- [x] 3.2 Crear `data/ir_cron_data.xml` con un `<record>` de `ir.cron` que ejecute `_cron_update_age` diariamente (`interval_number=1`, `interval_type='days'`).
- [x] 3.3 Registrar `data/ir_cron_data.xml` en `data` del manifest.
- [x] 3.4 Verificar manualmente (ejecutando el cron desde Ajustes > Técnico > Automatización > Acciones Planificadas) que `age` se actualiza para contactos cuyo cumpleaños ya pasó sin haber sido editados. **Confirmado manualmente por el usuario en el navegador** sobre `res_partner_extend_test`.

## 4. Vista: pestaña de Tarjeta de Contacto

- [x] 4.1 Crear `views/res_partner_views.xml` con una vista heredada de `res.partner.form` (`inherit_id="base.view_partner_form"`).
- [x] 4.2 Añadir el campo `birthdate` en la posición adecuada del formulario existente, con `required="1"` definido en el atributo de la vista (no en el modelo). **Corregido**: se insertó inicialmente junto a `email` (dentro de un `<div class="d-flex...">` de header sin `<label>`, por lo que el label no se veía); se movió al `<group>` de información personal, justo después de `function`, con `invisible="is_company"` (consistente con el resto del grupo), donde Odoo genera el `<label>` automáticamente.
- [x] 4.3 Añadir una nueva `<page string="Tarjeta de Contacto">` dentro del `<notebook>` del formulario.
- [x] 4.4 Dentro de la nueva página, usar el tag genérico `<widget name="contact_card"/>` (registry `view_widgets`) en lugar de un campo dummy — el widget declara sus propias `fieldDependencies` (name, image_1920, birthdate, age) para que el formulario las cargue automáticamente, sin necesitar un `<field>` extra ni RPC propio.
- [x] 4.5 Registrar `views/res_partner_views.xml` en `data` del manifest.

## 5. Widget OWL: componente JavaScript

- [x] 5.1 Crear `static/src/js/contact_card.js` definiendo `class ContactCardWidget extends Component`.
- [x] 5.2 Declarar `static template = "res_partner_extend.ContactCard"` referenciando el archivo de plantilla separado (sin markup inline).
- [x] 5.3 Declarar `static props = { ...standardWidgetProps }` (patrón de view widget de Odoo 19, ver decisión de diseño actualizada).
- [x] 5.4 Implementar getters para exponer al template: nombre (`record.data.name`), URL de imagen (`imageUrl` de `@web/core/utils/urls`), edad (`record.data.age`) y fecha de nacimiento formateada (`formatDate` de `@web/core/l10n/dates`, respeta idioma del usuario).
- [x] 5.5 Manejar el caso de `birthdate`/`age` vacíos devolviendo un placeholder ("-") en el getter correspondiente.
- [x] 5.6 Registrar el componente en `registry.category("view_widgets").add("contact_card", {component: ContactCardWidget, fieldDependencies: [...]})`.
- [x] 5.7 Añadir getter `contactUrl` que construya `${browser.location.origin}/odoo/res.partner/${record.resId}` (cadena vacía si `resId` es falsy) usando `browser` de `@web/core/browser/browser`.
- [x] 5.8 Añadir getter `qrCodeUrl` que arme `/report/barcode?barcode_type=QR&value=<contactUrl codificado>&width=120&height=120&quiet=1` vía `URLSearchParams` (reusando el controlador nativo `/report/barcode` de Odoo, sin librerías JS de QR).

## 6. Widget OWL: plantilla QWeb

- [x] 6.1 Crear `static/src/xml/contact_card.xml` con `<templates>` y `t-name="res_partner_extend.ContactCard"`.
- [x] 6.2 Estructurar el markup de la tarjeta: contenedor raíz con clase `o_contact_card_widget`, sección de imagen, nombre, edad y fecha de nacimiento.
- [x] 6.3 Usar bindings reactivos (`t-esc`, `t-att-src`) para los getters expuestos por el componente JS, evitando lógica compleja en el template.
- [x] 6.4 Añadir sección QR (`t-if="contactUrl"`) con `<img t-att-src="qrCodeUrl"/>`, oculta cuando el contacto no tiene `resId` (aún no guardado).

## 7. Widget OWL: estilos corporativos

- [x] 7.1 Crear `static/src/scss/contact_card.scss` con variables locales: `$cc-blue`, `$cc-gray`, `$cc-orange` (y sus tonos claros/oscuros necesarios).
- [x] 7.2 Aplicar los estilos dentro del scope `.o_contact_card_widget` (fondo/borde en azul, texto secundario en gris, acentos/badges en naranja), sin modificar variables SCSS globales de Odoo.
- [x] 7.3 Asegurar diseño responsive básico de la tarjeta (imagen circular, disposición en `flex-wrap` que colapsa a columna en anchos reducidos).
- [x] 7.4 Estilar la sección del QR (`.o_contact_card_widget_qr`) dentro del mismo scope, consistente con la paleta corporativa.

## 8. Registro de assets

- [x] 8.1 Añadir `contact_card.js`, `contact_card.xml` y `contact_card.scss` al bundle `web.assets_backend` en `__manifest__.py`, respetando el orden de carga (template XML y JS pueden coexistir sin orden estricto; SCSS al final del bloque de estilos).

## 9. Verificación funcional

- [x] 9.1 Instalar el addon en una base de Odoo 19 local y confirmar que no hay errores en el log de instalación. **Verificado real**: instalado en base de prueba descartable `res_partner_extend_test` (docker compose `/Users/mauricio/docker/odoo19`, contenedor `odoo19`). Log de instalación limpio: 15 módulos cargados, `res_partner_extend` (10/15) sin errores, incluyendo carga de `data/ir_cron_data.xml` y `views/res_partner_views.xml`.
- [x] 9.2 Abrir un contacto nuevo: confirmar que aparece la pestaña "Tarjeta de Contacto" con el widget renderizado y placeholders donde falten datos. **Confirmado manualmente por el usuario en el navegador** sobre `res_partner_extend_test`.
- [x] 9.3 Completar `birthdate` en un contacto y guardar: confirmar que `age` se calcula y almacena correctamente y el widget lo refleja. **Confirmado manualmente por el usuario en el navegador** sobre `res_partner_extend_test`.
- [x] 9.4 Intentar guardar un contacto desde la vista de formulario sin `birthdate`: confirmar que la UI bloquea el guardado por el campo requerido en vista. **Confirmado manualmente por el usuario en el navegador** sobre `res_partner_extend_test`.
- [x] 9.5 Confirmar (vía código o consola del navegador) que no hay errores de carga de assets (JS/XML/SCSS) ni estilos filtrados fuera de `.o_contact_card_widget`. **Verificado real**: login exitoso en `res_partner_extend_test`, bundle `web.assets_web.min.js`/`.min.css` descargado con HTTP 200, contiene `ContactCardWidget`/`res_partner_extend.ContactCard` y la clase `o_contact_card_widget`; logs del contenedor sin errores para esta base (los únicos errores en logs corresponden a la base `cfdi`, no relacionada). Aislamiento de estilos fuera del contenedor raíz no verificado visualmente (requiere navegador).
- [x] 9.6 Confirmar que un flujo interno de creación de `res.partner` sin `birthdate` (por ejemplo, crear un usuario nuevo desde Ajustes) no se ve bloqueado por este cambio. **Verificado real** vía `odoo shell`: `env['res.partner'].create({'name': ...})` sin `birthdate` se crea sin error (`birthdate=False`), confirmando que la obligatoriedad es solo de vista.
- [x] 9.7 Ejecutar manualmente el cron `_cron_update_age` y confirmar que actualiza `age` en contactos cuyo cumpleaños ya pasó desde el último guardado, y que no reescribe innecesariamente los que no cambiaron. **Confirmado manualmente por el usuario en el navegador** sobre `res_partner_extend_test`.
