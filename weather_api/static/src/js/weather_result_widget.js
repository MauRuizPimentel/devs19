/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

// fa-cloud-rain and fa-smog don't exist in the FontAwesome 4.7 bundled with Odoo; use FA4-available fallbacks.
const CONDITION_ICONS = {
    Clear: "fa-sun-o",
    Clouds: "fa-cloud",
    Rain: "fa-tint",
    Drizzle: "fa-tint",
    Thunderstorm: "fa-bolt",
    Snow: "fa-snowflake-o",
    Mist: "fa-cloud",
    Fog: "fa-cloud",
    Haze: "fa-cloud",
    Smoke: "fa-cloud",
};
const DEFAULT_CONDITION_ICON = "fa-question-circle-o";

export class WeatherResultWidget extends Component {
    static template = "weather_api.WeatherResultWidget";
    static props = { ...standardFieldProps };

    get result() {
        const value = this.props.record.data[this.props.name];
        if (!value) {
            return null;
        }
        try {
            return JSON.parse(value);
        } catch {
            return null;
        }
    }

    get flagEmoji() {
        const countryCode = this.result?.country_code;
        if (!countryCode || countryCode.length !== 2) {
            return "";
        }
        const codePoints = [...countryCode.toUpperCase()].map((char) => 127397 + char.charCodeAt(0));
        return String.fromCodePoint(...codePoints);
    }

    get conditionIconClass() {
        return CONDITION_ICONS[this.result?.condition_main] || DEFAULT_CONDITION_ICON;
    }

    get roundedTemperature() {
        const temperature = this.result?.temperature;
        return typeof temperature === "number" ? Math.round(temperature) : null;
    }
}

registry.category("fields").add("weather_result", {
    component: WeatherResultWidget,
});
