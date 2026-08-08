/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";
import { Component, markup, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

const DIFFICULTY_LABELS = {
    easy: "Easy",
    medium: "Medium",
    hard: "Hard",
};

const PLACEHOLDER_IMAGE_URL = "/ia_recipe_generator/static/src/img/recipe_placeholder.svg";

export class RecipePreviewDialog extends Component {
    static template = "ia_recipe_generator.RecipePreviewDialog";
    static components = { Dialog };
    static props = {
        name: String,
        preparationTime: Number,
        difficulty: String,
        instructions: { type: [String, Object], optional: true },
        imageUrl: { type: String, optional: true },
        close: { type: Function, optional: true },
    };

    setup() {
        this.state = useState({ imageFailed: false });
    }

    get difficultyLabel() {
        return DIFFICULTY_LABELS[this.props.difficulty] || this.props.difficulty;
    }

    get imageSrc() {
        if (this.state.imageFailed || !this.props.imageUrl) {
            return PLACEHOLDER_IMAGE_URL;
        }
        return this.props.imageUrl;
    }

    onImageError() {
        this.state.imageFailed = true;
    }
}

export class RecipePreviewButtonField extends Component {
    static template = "ia_recipe_generator.RecipePreviewButton";
    static props = { ...standardFieldProps };

    setup() {
        this.dialog = useService("dialog");
    }

    openPreview() {
        const record = this.props.record;
        const hasImage = !!record.data.image;
        this.dialog.add(RecipePreviewDialog, {
            name: record.data.name,
            preparationTime: record.data.preparation_time,
            difficulty: record.data.difficulty,
            instructions: record.data.instructions ? markup(record.data.instructions) : undefined,
            imageUrl: hasImage ? `/web/image/${record.resModel}/${record.resId}/image` : undefined,
        });
    }
}

registry.category("fields").add("recipe_preview_button", {
    component: RecipePreviewButtonField,
});
