/** @odoo-module **/

// Vehicle icons are pin-shaped (viewBox 0 0 40 48) with the tip at the bottom
// center, so the marker must be anchored there instead of at its center.
const VEHICLE_ICON_SIZE = [30, 36];
const VEHICLE_ICON_ANCHOR = [15, 36];

export function vehicleMarkerIcon(maps, iconUrl) {
    return {
        url: iconUrl,
        scaledSize: new maps.Size(...VEHICLE_ICON_SIZE),
        anchor: new maps.Point(...VEHICLE_ICON_ANCHOR),
    };
}

export function formatVehicleDate(value) {
    if (!value) {
        return "Sin fecha";
    }
    return typeof value.toFormat === "function" ? value.toFormat("dd/MM/yyyy HH:mm") : String(value);
}

export function buildVehicleInfoWindowContent(vehicle) {
    const container = document.createElement("div");
    container.classList.add("o_gps_map_info_window");

    const title = document.createElement("strong");
    title.textContent = vehicle.name;
    container.appendChild(title);

    const coords = document.createElement("div");
    coords.textContent = `Lat: ${vehicle.latitude.toFixed(6)}, Lng: ${vehicle.longitude.toFixed(6)}`;
    container.appendChild(coords);

    const date = document.createElement("div");
    date.textContent = formatVehicleDate(vehicle.last_recorded_at);
    container.appendChild(date);

    return container;
}

let mapsApiPromise = null;

export function loadGoogleMapsApi(apiKey) {
    if (mapsApiPromise) {
        return mapsApiPromise;
    }
    mapsApiPromise = new Promise((resolve, reject) => {
        if (window.google && window.google.maps) {
            resolve(window.google.maps);
            return;
        }
        const callbackName = "__fleetGpsTrackerGoogleMapsLoaded";
        window[callbackName] = () => {
            delete window[callbackName];
            resolve(window.google.maps);
        };
        const script = document.createElement("script");
        script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(apiKey)}&callback=${callbackName}`;
        script.async = true;
        script.onerror = () => {
            mapsApiPromise = null;
            reject(new Error("Failed to load the Google Maps JavaScript API"));
        };
        document.head.appendChild(script);
    });
    return mapsApiPromise;
}
