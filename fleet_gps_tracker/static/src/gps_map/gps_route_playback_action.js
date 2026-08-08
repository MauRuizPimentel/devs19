/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, onWillUnmount, useRef, useState } from "@odoo/owl";
import { loadGoogleMapsApi, vehicleMarkerIcon } from "./gps_map_utils";

const ANIMATION_STEP_MS = 300;
const START_ICON_URL = "/fleet_gps_tracker/static/src/img/flag_start.svg";
const END_ICON_URL = "/fleet_gps_tracker/static/src/img/flag_end.svg";

export class GpsRoutePlaybackAction extends Component {
    static template = "fleet_gps_tracker.GpsRoutePlaybackAction";

    setup() {
        this.orm = useService("orm");
        this.mapContainerRef = useRef("mapContainer");
        this.state = useState({ status: "loading" });
        this.params = this.props.action.params || {};
        onMounted(() => this.initMap());
        onWillUnmount(() => this.stopAnimation());
    }

    stopAnimation() {
        if (this.animationInterval) {
            clearInterval(this.animationInterval);
            this.animationInterval = null;
        }
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
        const points = this.params.points || [];
        if (!points.length) {
            this.state.status = "empty";
            return;
        }
        this.map = new maps.Map(this.mapContainerRef.el, { center: points[0], zoom: 15 });
        new maps.Polyline({
            path: points,
            map: this.map,
            strokeColor: "#2c5f8a",
            strokeWeight: 3,
        });
        new maps.Marker({
            position: points[0],
            map: this.map,
            title: "Inicio",
            icon: { url: START_ICON_URL, scaledSize: new maps.Size(24, 32) },
            zIndex: 5,
        });
        new maps.Marker({
            position: points[points.length - 1],
            map: this.map,
            title: "Fin",
            icon: { url: END_ICON_URL, scaledSize: new maps.Size(24, 32) },
            zIndex: 5,
        });
        const marker = new maps.Marker({
            position: points[0],
            map: this.map,
            icon: vehicleMarkerIcon(maps, this.params.vehicle_icon),
            zIndex: 10,
        });
        const bounds = new maps.LatLngBounds();
        points.forEach((point) => bounds.extend(point));
        this.map.fitBounds(bounds);

        let index = 0;
        this.animationInterval = setInterval(() => {
            index += 1;
            if (index >= points.length) {
                this.stopAnimation();
                return;
            }
            marker.setPosition(points[index]);
        }, ANIMATION_STEP_MS);

        this.state.status = "ready";
    }
}

registry.category("actions").add("fleet_gps_tracker.route_playback", GpsRoutePlaybackAction);
