## Context

`res_partner_extend` es un addon nuevo para Odoo 19 sin código previo. No existen specs archivados en `openspec/specs/`. El objetivo es extender `res.partner` con datos demográficos y una visualización enriquecida (widget OWL) sin modificar el comportamiento existente del contacto para usuarios que no interactúan con la nueva pestaña.

Restricciones del entorno:
- Odoo 19 usa el framework de vistas basado en OWL 2 (no legacy Widget/QWeb JS antiguo).
- Los assets de backend se registran en el manifest bajo `web.assets_backend`.
- El campo `birthdate` es obligatorio en un modelo compartido (`res.partner`), por lo que debe evaluarse sin romper flujos de creación existentes (importaciones, XML-RPC, datos demo de otros módulos instalados).

## Goals / Non-Goals

**Goals:**
- Añadir `birthdate` (obligatorio en vista) y `age` (computado, solo lectura, almacenado) a `res.partner`, con recomputo automático diario vía cron.
- Añadir una pestaña "Tarjeta de Contacto" en el formulario de contacto.
- Implementar un widget OWL (`ContactCardWidget`) con archivos separados: JS, XML (template) y SCSS.
- Aplicar paleta corporativa (azul, gris, naranja) mediante variables SCSS dedicadas al widget.
- El widget se registra como campo/widget de tipo `Field` (o componente embebido vía `widget="contact_card"`) reutilizando datos ya cargados en el formulario (sin llamadas RPC adicionales).

**Non-Goals:**
- No se modifica la vista `kanban`/`list` de contactos.
- No se implementa edición de campos desde dentro del widget (es de solo lectura/visualización).
- No se gestiona el recorte/subida de imagen desde el widget (se reutiliza el campo `image_1920`/`avatar_128` existente).
- No se añade validación de edad mínima/máxima ni reglas de negocio sobre la fecha (solo obligatoriedad del campo).

## Decisions

**1. `age` como campo `Integer` computado y almacenado (`store=True`), con `@api.depends('birthdate')` más un cron diario que fuerza el recompute de todos los partners con `birthdate` definido.**
- Decisión explícita del usuario: `age` debe quedar almacenado. Como beneficio derivado, esto habilita filtrar/agrupar por edad en list views y dominios de búsqueda, algo que un campo `store=False` no soporta bien.
- Trade-off identificado y resuelto: un campo `store=True` con `@depends('birthdate')` solo se recalcula cuando `birthdate` cambia o el registro se escribe — el simple paso del tiempo (que hoy sea un día distinto) no dispara recompute por sí solo. Por eso se añade un `ir.cron` diario que ejecuta un método en `res.partner` (`_cron_update_age` o equivalente) que fuerza el recompute de `age` en todos los partners con `birthdate` seteado, evitando que la edad quede "congelada" entre ediciones.
- Alternativa descartada: `store=False` (diseño original) — más simple y siempre exacto sin cron, pero pierde la capacidad de filtrar/agrupar por edad.

**2. `birthdate` obligatorio solo a nivel de vista (`required="1"` en el XML de la vista de formulario de contacto), no a nivel de modelo (`required=True` en Python).**
- Confirmado con el usuario. `res.partner` es un modelo compartido por usuarios, compañías, direcciones de entrega/facturación y proveedores; forzar `required=True` en el modelo bloquearía la creación de esos partners internos en cualquier flujo (UI, importaciones, otros módulos instalados). Al aplicar la obligatoriedad solo en la vista de contacto, el dato se exige cuando un humano edita un contacto desde esa pantalla, sin afectar creaciones programáticas de `res.partner` desde otros módulos.
- Alternativa descartada: `required=True` en el campo del modelo — mayor riesgo de romper flujos existentes de terceros.

**3. Widget OWL como "view widget" genérico (registry `view_widgets`), no como campo de tipo `Field` ni como widget standalone.**
- Resuelto durante implementación: en vez de forzar el componente sobre un `<field widget="contact_card"/>` dummy (que exige atarlo a un nombre de campo real aunque no se edite), se usa el tag genérico `<widget name="contact_card"/>` soportado por las vistas de formulario de Odoo 19, registrado con `registry.category("view_widgets").add("contact_card", {component, fieldDependencies: [...]})`. El array `fieldDependencies` (name, image_1920, birthdate, age) le indica al compilador de la vista qué campos cargar para este widget, sin necesidad de declararlos como `<field>` visibles/invisibles adicionales y sin llamadas RPC propias del componente — recibe `props.record` con esos datos ya cargados en el formulario activo.
- Alternativas descartadas: (a) campo dummy con `<field name="id" widget="contact_card"/>` — funciona pero es semánticamente confuso (el widget no edita "id") y obliga a asegurar por separado que `age`/`birthdate` estén en el arch para que se carguen; (b) widget standalone montado manualmente vía `owl.mount` — mayor complejidad de ciclo de vida e integración con el estado del formulario (dirty/discard/save).

**4. Separación estricta de archivos: `contact_card.js`, `contact_card.xml`, `contact_card.scss`.**
- Cumple el requisito explícito del usuario y la convención de Odoo de mantener template QWeb (`t-name`) y estilos en archivos independientes al componente, referenciados vía `static/src/...` y cargados por el manifest.

**5. Paleta corporativa como variables SCSS locales al widget (`$cc-blue`, `$cc-gray`, `$cc-orange`), sin tocar variables globales de Odoo.**
- Evita colisiones con el tema de Odoo y con otros módulos. Los estilos se ámbito-limitan con una clase raíz `.o_contact_card_widget` para no filtrar estilos a otras partes del formulario.

**6. Código QR generado con el controlador nativo `/report/barcode` de Odoo (`ir.actions.report.barcode()`, vía `reportlab`), no con una librería JS de generación de QR.**
- Añadido tras el desarrollo, a pedido del usuario, como extensión del widget ya implementado. Odoo ya expone `/report/barcode?barcode_type=QR&value=<texto>&width=&height=` (auth `public`, sin necesitar sesión) que devuelve un PNG — el mismo patrón usado en facturas/pagos. Se usa como `<img t-att-src="...">`, igual que `imageUrl` para el avatar: no requiere agregar una dependencia JS de generación de QR ni una llamada RPC propia del componente.
- La URL codificada en el QR se construye 100% en el cliente como `${browser.location.origin}/odoo/res.partner/${record.resId}` (sin RPC: `browser.location.origin` ya está disponible en el navegador), usando la ruta genérica `/odoo/<model>/<id>` de Odoo 17+, que resuelve el formulario de cualquier registro sin depender del slug específico de la app "Contactos".
- Alternativa descartada: librería JS de generación de QR client-side (ej. `qrcode.js`) — añadiría una dependencia nueva sin necesidad, cuando Odoo ya resuelve esto en el servidor.
- Sin QR en contactos nuevos sin guardar (`resId` falsy): no hay una URL de backend válida todavía.

## Risks / Trade-offs

- **[Riesgo] Al ser `required` solo en la vista de contacto, un registro de `res.partner` creado por otro módulo (API, importación, otro flujo de UI) puede quedar sin `birthdate`.**
  → Mitigación: aceptado por diseño — es el comportamiento deseado para no romper flujos de terceros. La obligatoriedad es una guía de captura de datos en la pantalla de contacto, no una integridad referencial estricta a nivel de base de datos.

- **[Riesgo] Cálculo de edad con `birthdate` vacío o futuro.**
  → Mitigación: el compute devuelve `0` o `False` de forma segura cuando `birthdate` no está definido, evitando excepciones en el render del widget.

- **[Riesgo] `age` almacenado puede quedar desactualizado hasta 24h si el cron diario falla o no está activo (por ejemplo, addon recién instalado antes de la primera ejecución programada, o cron desactivado manualmente).**
  → Mitigación: el compute también corre en creación/escritura del registro (comportamiento estándar de campos `store=True` con `@depends`), por lo que cualquier edición del contacto corrige la edad de inmediato; el cron solo cubre el caso de contactos que nadie edita en su cumpleaños.

- **[Trade-off] Un cron diario que recorre todos los partners con `birthdate` añade una tarea programada y carga de escritura adicional (aunque acotada) en bases con muchos contactos.**
  → Aceptable para el alcance de este addon: se recomienda que el método del cron solo escriba (invalidate/recompute) los registros cuya edad realmente cambió respecto al valor almacenado, para minimizar escrituras innecesarias.

## Migration Plan

- Instalación nueva del addon: no hay datos previos que migrar.
- Si se instala sobre una base con contactos existentes: `birthdate` quedará vacío en registros existentes. Como la obligatoriedad es solo de vista, la instalación no falla ni bloquea contactos existentes; el dato se solicitará la próxima vez que alguien edite y guarde ese contacto desde la vista de formulario.
- Rollback: desinstalar el módulo elimina el campo `birthdate` (y su dato) y el campo computado `age`; no hay migración de datos a preservar fuera del módulo.

## Open Questions

- ¿Se requiere mostrar el widget también en modo "nuevo contacto" (sin datos aún) o solo cuando el contacto ya está guardado? Se asume que debe renderizarse siempre, mostrando placeholders (edad "-", imagen por defecto) cuando falten datos.
