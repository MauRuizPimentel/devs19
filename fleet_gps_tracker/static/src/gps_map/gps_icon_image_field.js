/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

export class IconImageField extends Component {
    static template = "fleet_gps_tracker.IconImageField";
    static props = { ...standardFieldProps };

    get iconUrl() {
        return this.props.record.data[this.props.name];
    }
}

registry.category("fields").add("icon_image", { component: IconImageField });
