## ADDED Requirements

### Requirement: Preview button on recipe records
The system SHALL provide a "Preview" button on each recipe record that opens a popup showing a styled recipe card.

#### Scenario: Opening the preview
- **WHEN** the user clicks "Preview" on a recipe
- **THEN** a popup SHALL open displaying an OWL widget with the recipe's image, name, preparation time, difficulty level, and preparation instructions

### Requirement: Recipe card visual styling
The preview popup SHALL render the recipe information inside a custom-styled card component, distinct from standard Odoo form fields, optimized for readability and visual appeal.

#### Scenario: Popup styling applied
- **WHEN** the preview popup opens
- **THEN** the recipe image, name, preparation time, and difficulty SHALL be rendered inside the custom-styled card, not as plain form fields

### Requirement: Missing image fallback
The system SHALL show a placeholder image in the popup when a recipe has no associated image.

#### Scenario: Recipe without image
- **WHEN** the user previews a recipe that has no image set
- **THEN** the popup SHALL display a placeholder image instead of a broken image
