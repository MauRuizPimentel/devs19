## ADDED Requirements

### Requirement: Recipe record storage
The system SHALL provide a `recipe.recipe` model that stores a recipe's name, preparation instructions, preparation time, and difficulty level.

#### Scenario: Recipe created with required fields
- **WHEN** a recipe record is created with name, instructions, preparation time, and difficulty
- **THEN** the record SHALL be saved and retrievable with all four fields populated

### Requirement: Recipe list view
The system SHALL provide a list view of `recipe.recipe` records displaying the name, preparation time, and difficulty level.

#### Scenario: Viewing the recipe list
- **WHEN** a user opens the Recipes list view
- **THEN** the list SHALL show each recipe's name, preparation time, and difficulty level as columns

### Requirement: Default recipe image
The system SHALL populate a recipe's image with a bundled default image when no image is provided at creation time.

#### Scenario: Recipe created without an image
- **WHEN** a recipe record is created without an explicit `image` value
- **THEN** the record SHALL be saved with the bundled default image rather than a blank image

### Requirement: Field constraints
The system SHALL restrict difficulty level to a fixed set of values (easy, medium, hard) and SHALL require preparation time to be a non-negative number of minutes.

#### Scenario: Invalid preparation time rejected
- **WHEN** a user attempts to save a recipe with a negative preparation time
- **THEN** the system SHALL raise a validation error and prevent saving
