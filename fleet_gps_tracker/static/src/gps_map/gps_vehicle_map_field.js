/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, onWillUnmount, useRef, useState } from "@odoo/owl";
import { buildVehicleInfoWindowContent, loadGoogleMapsApi, vehicleMarkerIcon } from "./gps_map_utils";

export class GpsVehicleMapField extends Component {
    static template = "fleet_gps_tracker.GpsVehicleMapField";
    static props = { ...standardFieldProps };

    setup() {
        this.orm = useService("orm");
        this.mapContainerRef = useRef("mapContainer");
        this.state = useState({ status: "loading" });
        onMounted(() => this.initMap());
        onWillUnmount(() => {
            this.map = null;
        });
    }

    async initMap() {
        const apiKey = await this.orm.call("res.config.settings", "get_google_maps_api_key", []);
        if (!apiKey) {
            this.state.status = "missing_key";
            return;
        }
        let maps;
        try {
            maps = await loadGoogleMapsApi(apiKey);
        } catch {
            this.state.status = "error";
            return;
        }
        if (!this.props.record.data.last_recorded_at) {
            this.state.status = "no_position";
            return;
        }
        const position = {
            lat: this.props.record.data.latitude,
            lng: this.props.record.data.longitude,
        };
        this.map = new maps.Map(this.mapContainerRef.el, { center: position, zoom: 15 });
        const marker = new maps.Marker({
            position,
            map: this.map,
            icon: vehicleMarkerIcon(maps, this.props.record.data.icon),
        });
        const infoWindow = new maps.InfoWindow();
        marker.addListener("click", () => {
            infoWindow.setContent(
                buildVehicleInfoWindowContent({
                    name: this.props.record.data.name,
                    latitude: this.props.record.data.latitude,
                    longitude: this.props.record.data.longitude,
                    last_recorded_at: this.props.record.data.last_recorded_at,
                })
            );
            infoWindow.open({ map: this.map, anchor: marker });
        });
        this.state.status = "ready";
    }
}

registry.category("fields").add("gps_vehicle_map", { component: GpsVehicleMapField });
