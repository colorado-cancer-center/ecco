<!--
credit to stormester for this leaflet wrapper:
https://www.reddit.com/r/vuejs/comments/z80ik8/using_leaflet_with_vue3/iya3iod/
-->

<script lang="ts">
import {
    defineComponent, onMounted, onUpdated, PropType, ref
} from 'vue';
import "leaflet/dist/leaflet.css";
import L, {Map} from 'leaflet';

import Legend from '@/components/map-elements/leafletLegend';
import CustomButton from '@/components/map-elements/leafletButton';


function initMap(element: HTMLElement, props, emit): [Map, L.GeoJSON, L.Control] {
    const map = L.map(element, { /* options */})
        .setView([38.939949, -105.617083], 7);

    // ====================
    // base tile layer
    // ====================

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    // ====================
    // geojson layer for showing county, tract + coloration
    // ====================

    const geojsonLayer = L.geoJSON(props.geojson, {
        style: function(feature) {
            if (props.colorScale) {
                return {
                    "color": feature?.properties?.measure != null && props.colorScale(feature?.properties?.measure) || "gray",
                    "weight": 1,
                    "opacity": 0.65
                }
            }

            return {
                "color": "gray",
                "weight": 1,
                "opacity": 0.65
            }
        },
        onEachFeature: (feature, layer) => {
            // if there's popup content for this element, bind it to the popup
            if (feature?.properties?.popupContent) {
                layer.bindPopup(feature.properties.popupContent);
            }
        }
    }).addTo(map);

    // ====================
    // extra map controls: legend, fit bounds button
    // ====================

    const legendControl = new Legend({
        legendData: props.legend
    }).addTo(map);

    map.addControl(new CustomButton({
        title: 'Fit View to Geometry',
        // text: '<i class="fa-solid fa-expand"></i>',
        body: '&#x26F6;',
        click: () => {
            map.fitBounds(geojsonLayer.getBounds());
        }
    }));

    // ====================
    // layer bounds handling: setting initial bounds, updating bounds watchers
    // ====================

    // set us to the initial bounds, if specified
    if (props.initialBounds) {
        map.fitBounds(props.initialBounds);
    }

    // whenever the map is changed, emit the new bounds
    // (this is used, e.g., for our parent StatsMap control to update the URL)
    map.on('moveend', function(e) {
        const bounds = map.getBounds();
        const boundsArray = [
            [bounds.getNorth(), bounds.getEast()],
            [bounds.getSouth(), bounds.getWest()]
        ];
        emit('bounds-changed', map, boundsArray);
    });

    return [map, geojsonLayer, legendControl];
};

export default defineComponent({
    emits: ['created', 'removed', 'bounds-changed'],
    props: {
        geojson: {
            type: Object as PropType<any>,
            required: false,
            default: []
        },
        colorScale: {
            type: Function,
            required: false,
            default: null
        },
        legendData: {
            type: Object as PropType<any>,
            required: false,
            default: {}
        },
        initialBounds: {
            type: Object as PropType<any>,
            required: false,
            default: null
        }
    },

    setup(props, { emit, slots }) {
        const mapElement = ref<HTMLElement>();
        let map: Map | undefined;
        let geojsonLayer: L.GeoJSON | undefined;
        let legendControl: L.Control | undefined;

        function removeMap() {
            if (map) {
                map.remove();
                map = undefined;
                emit('removed');
            }
        }

        // see https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API
        // for details about the IntersectionObserver.
        const observer = new IntersectionObserver(function(entries) {
            if(entries[0].isIntersecting === true && mapElement.value) {
                // Element shown - insert map
                removeMap();
                [map, geojsonLayer, legendControl] = initMap(mapElement.value, props, emit);
                emit('created', map);
            } else {
                removeMap();
            }
        }, { threshold: [0] });

        onMounted(() => {
            if (mapElement.value) {
                // Observe visibility of map container
                observer.observe(mapElement.value);
            } else {
                console.error('when attempting to observe mapElement.value, it was undefined');
            }
        });

        onUpdated(() => {
            if (map && geojsonLayer) {
                geojsonLayer.clearLayers();
                geojsonLayer.addData(props.geojson);
                // map.fitBounds(geojsonLayer.getBounds());
            }

            if (map && legendControl) {
                // remove and recreate the legend
                map.removeControl(legendControl);
                legendControl = new Legend({
                    legendData: props.legendData
                }).addTo(map);
            }
        });

        return { mapElement };
    }
});
</script>

<template>
    <!-- Using v-once to make sure Vue will not update -->
    <div class="full-height" ref="mapElement" v-once></div>
</template>
