/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { formatDate } from "@web/core/l10n/dates";
import { imageUrl } from "@web/core/utils/urls";
import { browser } from "@web/core/browser/browser";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";

export class ContactCardWidget extends Component {
    static template = "res_partner_extend.ContactCard";
    static props = { ...standardWidgetProps };

    get partnerName() {
        return this.props.record.data.name || "-";
    }

    get age() {
        const age = this.props.record.data.age;
        return age ? String(age) : "-";
    }

    get birthdateLabel() {
        const birthdate = this.props.record.data.birthdate;
        return birthdate ? formatDate(birthdate) : "-";
    }

    get avatarUrl() {
        const record = this.props.record;
        if (!record.resId) {
            return "/web/static/img/placeholder.png";
        }
        return imageUrl("res.partner", record.resId, "image_1920");
    }

    get contactUrl() {
        const record = this.props.record;
        if (!record.resId) {
            return "";
        }
        return `${browser.location.origin}/odoo/res.partner/${record.resId}`;
    }

    get qrCodeUrl() {
        const params = new URLSearchParams({
            barcode_type: "QR",
            value: this.contactUrl,
            width: 120,
            height: 120,
            quiet: 1,
        });
        return `/report/barcode?${params.toString()}`;
    }
}

registry.category("view_widgets").add("contact_card", {
    component: ContactCardWidget,
    fieldDependencies: [
        { name: "name", type: "char" },
        { name: "image_1920", type: "binary" },
        { name: "birthdate", type: "date" },
        { name: "age", type: "integer" },
    ],
});
