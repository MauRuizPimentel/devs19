/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, useRef, useState } from "@odoo/owl";
import { buildVehicleInfoWindowContent, loadGoogleMapsApi, vehicleMarkerIcon } from "./gps_map_utils";

const DEFAULT_CENTER = { lat: 19.432608, lng: -99.133209 };

export class GpsMapOverviewAction extends Component {
    static template = "fleet_gps_tracker.GpsMapOverviewAction";

    setup() {
        this.orm = useService("orm");
        this.mapContainerRef = useRef("mapContainer");
        this.state = useState({ status: "loading" });
        onMounted(() => this.initMap());
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
        const vehicles = await this.orm.searchRead(
            "gps.vehicle",
            [["has_position", "=", true]],
            ["name", "icon", "latitude", "longitude", "last_recorded_at"]
        );
        this.map = new maps.Map(this.mapContainerRef.el, { center: DEFAULT_CENTER, zoom: 12 });
        if (!vehicles.length) {
            this.state.status = "empty";
            return;
        }
        const infoWindow = new maps.InfoWindow();
        const bounds = new maps.LatLngBounds();
        for (const vehicle of vehicles) {
            const position = { lat: vehicle.latitude, lng: vehicle.longitude };
            const marker = new maps.Marker({
                position,
                map: this.map,
                title: vehicle.name,
                icon: vehicleMarkerIcon(maps, vehicle.icon),
            });
            marker.addListener("click", () => {
                infoWindow.setContent(buildVehicleInfoWindowContent(vehicle));
                infoWindow.open({ map: this.map, anchor: marker });
            });
            bounds.extend(position);
        }
        this.map.fitBounds(bounds);
        this.state.status = "ready";
    }
}

registry.category("actions").add("fleet_gps_tracker.overview_map", GpsMapOverviewAction);
