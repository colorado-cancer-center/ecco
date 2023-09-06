<!--
credit to stormester for this leaflet wrapper:
https://www.reddit.com/r/vuejs/comments/z80ik8/using_leaflet_with_vue3/iya3iod/
-->

<script lang="ts">
import {
    defineComponent, defineEmits, inject,
    onMounted, onUpdated, PropType, reactive, ref, toRef, toRefs
} from 'vue';
import "leaflet/dist/leaflet.css";
import L, {Map} from 'leaflet';
import legend from '@/utils/leafletLegend';

function initMap(element: HTMLElement, props): [Map, L.GeoJSON, L.Control] {
    const map = L.map(element, { /* options */})
        .setView([38.939949, -105.617083], 7);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    // add geojson layer
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
            // does this feature have a property named popupContent?
            if (feature?.properties?.popupContent) {
                layer.bindPopup(feature.properties.popupContent);
            }
        }
    }).addTo(map);

    // add legend layer
    const legendControl = legend({
        legendData: props.legend
    }).addTo(map);

    // L.easyButton('fa-globe', function(btn, map){
    //     map.fitBounds(geojsonLayer.getBounds());
    // }).addTo(map);

    return [map, geojsonLayer, legendControl];
};

export default defineComponent({
    emits: ['created', 'removed'],
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
                [map, geojsonLayer, legendControl] = initMap(mapElement.value, props);
                emit('created', map);
                // console.log("loaded map")
            } else {
                // Not shown - remove map
                removeMap();
                // console.log("removed map")
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
                map.fitBounds(geojsonLayer.getBounds());
            }

            if (map && legendControl) {
                // remove and recreate the legend
                map.removeControl(legendControl);
                legendControl = legend({
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
