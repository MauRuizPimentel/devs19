# partner-birthdate Specification

## Purpose
TBD - created by syncing change add-contact-card-widget. Update Purpose once the change is archived.

## Requirements

### Requirement: Fecha de nacimiento en el contacto
El sistema SHALL añadir el campo `birthdate` (Fecha de nacimiento, tipo `Date`) al modelo `res.partner`. El campo SHALL ser obligatorio en la vista de formulario de contacto, pero NO SHALL ser obligatorio a nivel del modelo (otros flujos que crean `res.partner` internamente, como usuarios, compañías o direcciones, no deben verse bloqueados).

#### Scenario: Guardar un contacto sin fecha de nacimiento desde el formulario
- **WHEN** un usuario crea o edita un contacto desde la vista de formulario de contacto y deja `birthdate` vacío
- **THEN** el sistema impide guardar y marca el campo `birthdate` como requerido en la interfaz

#### Scenario: Guardar un contacto con fecha de nacimiento válida
- **WHEN** un usuario completa `birthdate` con una fecha válida y guarda el contacto
- **THEN** el sistema persiste el valor en el registro de `res.partner` sin errores

#### Scenario: Creación programática de un partner sin `birthdate`
- **WHEN** otro módulo o flujo interno crea un registro de `res.partner` (por ejemplo, al crear un usuario, una compañía o una dirección de entrega) sin especificar `birthdate`
- **THEN** el sistema permite la creación sin error, ya que la obligatoriedad solo aplica en la vista de formulario de contacto

### Requirement: Edad calculada del contacto
El sistema SHALL exponer un campo computado `age` (Edad, tipo `Integer`) en `res.partner`, de solo lectura y almacenado (`store=True`), calculado como la diferencia en años completos entre `birthdate` y la fecha actual del contexto de usuario. El campo SHALL recomputarse automáticamente cuando `birthdate` cambia (`@depends`) y SHALL soportar filtrado y agrupación en vistas de lista y búsquedas, al estar almacenado.

#### Scenario: Cálculo de edad con fecha de nacimiento definida
- **WHEN** un contacto tiene `birthdate` establecido a una fecha pasada válida
- **THEN** el campo `age` muestra el número de años completos transcurridos hasta la fecha actual

#### Scenario: Cálculo de edad sin fecha de nacimiento
- **WHEN** un contacto no tiene `birthdate` definido (por ejemplo, un partner creado por otro módulo sin este dato)
- **THEN** el campo `age` devuelve `0` sin lanzar una excepción

#### Scenario: Edad no editable directamente
- **WHEN** un usuario visualiza el formulario de contacto
- **THEN** el campo `age` se muestra como solo lectura y no puede editarse manualmente

#### Scenario: Recompute inmediato al cambiar la fecha de nacimiento
- **WHEN** un usuario edita `birthdate` en un contacto existente y guarda
- **THEN** el campo `age` almacenado se recalcula y refleja el nuevo valor sin esperar al cron diario

#### Scenario: Filtrado y agrupación por edad
- **WHEN** un usuario aplica un filtro o agrupación por `age` en la vista de lista de contactos
- **THEN** el sistema devuelve resultados correctos, ya que `age` es un campo almacenado consultable por el ORM

### Requirement: Recompute periódico de la edad
El sistema SHALL ejecutar un `ir.cron` diario que recorra los contactos con `birthdate` definido y fuerce el recompute del campo `age`, de forma que la edad almacenada no quede desactualizada en contactos que no son editados en la fecha de su cumpleaños.

#### Scenario: Ejecución diaria del cron
- **WHEN** transcurre un día y el contacto no fue editado
- **THEN** el cron diario recalcula `age` para todos los partners con `birthdate` definido, actualizando el valor almacenado si corresponde

#### Scenario: Cumpleaños sin edición manual del contacto
- **WHEN** la fecha actual alcanza el aniversario de `birthdate` de un contacto y nadie edita el registro ese día
- **THEN** la siguiente ejecución del cron actualiza `age` en +1 sin intervención manual

