<template>
  <div class="two-panel">
    <div class="panel-narrow main-options-panel">
      <div class="subpanel main">
        <div class="fieldset">
          <label for="geo-entity">Select a geographic level:</label>
          <select id="geo-entity" v-model="selectedGeoLevel">
            <option>County</option>
            <option>Tract</option>
          </select>
        </div>

        <div class="fieldset" v-if="categoriesByGeometry">
          <label for="category">Select a category of variables:</label>
          <select id="category" v-model="selectedCategory">
            <option :value="null">---</option>
            <option v-for="item, category in categoriesByGeometry" :key="category" :value="category">{{ item.display_name }}</option>
          </select>
        </div>

        <div class="fieldset" v-if="selectedCategory">
          <label for="category">Select a variable to map:</label>
          <select id="category" v-model="selectedMeasure">
            <option :value="null">---</option>
            <option v-for="measure in measuresByCategory" :key="measure.name" :value="measure.name">{{ measure.display_name }}</option>
          </select>
        </div>
      </div>

      <!--
      <div class="fieldset" v-if="measureAnnotations">
        <label for="category">Statistics:</label>
        <p>Minimum: {{ measureAnnotations.min?.toLocaleString() }}</p>
        <p>Maximum: {{ measureAnnotations.max?.toLocaleString() }}</p>
        <p># of Values: {{ Object.keys(measureAnnotations.values).length }}</p>
      </div>
      -->

      <div class="subpanel options">
        <div class="option-fieldset">
          <input id="show-legend" type="checkbox" v-model="showLegend" />
          <label for="show-legend" style="display: inline-block; margin-right: 5px;">Show Legend</label>
        </div>
        <div class="option-fieldset">
          <input id="persist-bounds" type="checkbox" v-model="persistBoundsInURL" />
          <label for="persist-bounds" style="display: inline-block; margin-right: 5px;">Persist Map View in URL</label>
        </div>
      </div>
    </div>

    <div class="panel-wide">
      <LeafletMap
        @created="mapCreated"
        @bounds-changed="boundsChanged"
        :geojson="geometry"
        :color-scale="colorScale"
        :legend-data="legendData"
        :initialBounds="initialBounds"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { scaleSequential, scaleLinear } from 'd3-scale';
import { useRouter, useRoute } from 'vue-router'

import LeafletMap from '@/components/LeafletMap.vue';

const router = useRouter()
const route = useRoute()

// if true, moving the map adds the new bounds to the URL's querystring as '?bounds=[[n, e], [s, w]]'
// (the map will pick up the 'bounds' key on load and use that as its initial bounds)
const persistBoundsInURL = ref(false);

const mapCreated = (map) => {
  // console.log("New map: ", map);
};

// map controls
const selectedGeoLevel = ref('County');
const selectedCategory = ref(null);
const selectedMeasure = ref(null);
const showLegend = ref(true);

// ===========================================================================
// === fixture data collection
// ===========================================================================

// for each geometry table, extracts wkb_geometry
// field, parse it, and attempt to annotate it
const rehydrateGeomWithFIPS = (fips_field) => {
  return (obj) => {
    const geom = JSON.parse(obj.wkb_geometry)
    return {
      "type": "Feature",
      "geometry": geom,
      "properties": {
        "name": obj.full,
        "fips": obj[fips_field]
      }
    }
  }
}

// geojson data
const counties = ref([]);
fetch('http://localhost:8000/counties')
    .then(response => response.json())
    .then(data => data.map(x => rehydrateGeomWithFIPS('us_fips')(x)))
    .then(data => { counties.value = data });

const tracts = ref([]);
fetch('http://localhost:8000/tracts')
    .then(response => response.json())
    .then(data => data.map(x => rehydrateGeomWithFIPS('fips')(x)))
    .then(data => { tracts.value = data });

// stats data
const measures = ref([]);
fetch('http://localhost:8000/stats/measures')
    .then(response => response.json())
    .then(data => { measures.value = data });

// ===========================================================================
// === map bounds: updating querystring, loading from querystring on mount
// === (used for async updates to refs/other actions that don't produce values)
// ===========================================================================

function omit(key, obj) {
  const { [key]: omitted, ...rest } = obj;
  return rest;
}

const boundsChanged = (map, newBounds) => {
  if (persistBoundsInURL.value) {
    router.replace({ path: route.path, query: { ...route.query, bounds: JSON.stringify(newBounds) } })
  }
  else {
    router.replace({ path: route.path, query: omit('bounds', route.query) })
  }
}

const initialBounds = ref(null);
onMounted(() => {
    if (route.query.bounds) {
        initialBounds.value = JSON.parse(route.query.bounds);
    }
});


// ===========================================================================
// === watches
// === (used for async updates to refs/other actions that don't produce values)
// ===========================================================================

// if the geographic entity selection changes, clear our selections
// that'd be a result of it
watch([selectedGeoLevel], (oldValue, newValue) => {
  if (oldValue != newValue) {
    selectedCategory.value = null
    selectedMeasure.value = null
  }
})

// measureAnnotations holds the set of values for geometry regions (identified
// by their FIPS) that ultimately get diplayed as colorings on the map.
// measureAnnotations, if non-null, is merged into the 'geometry' value
// when generating the geojson that gets sent to leaflet.
const measureAnnotations = ref(null);

// we use a watch to populate measureAnnotations, since its value depends on the
// selected geometry type, category, and measure and also includes an async
// fetch (otherwise we'd use a computed property)
watch([selectedCategory, selectedMeasure], (oldValue, newValue) => {
  if (oldValue == newValue) {
    return;
  }

  if (!selectedCategory.value || !selectedMeasure.value) {
    measureAnnotations.value = null;
    return;
  }

  const params = new URLSearchParams({
    measure: selectedMeasure.value
  })

  fetch(`http://localhost:8000/stats/${selectedGeoLevel.value.toLowerCase()}/${selectedCategory.value}/fips-value?` + params)
    .then(response => response.json())
    .then(data => { measureAnnotations.value = data; })
})

// ===========================================================================
// === computed properties
// ===========================================================================

// human labels for our category, measure selections
const selectedCategoryName = computed(() => {
  if (!selectedCategory.value) { return null }
  return categoriesByGeometry.value[selectedCategory.value].display_name
})
const selectedMeasureName = computed(() => {
  if (!selectedMeasure.value) { return null }
  return measuresByCategory.value.find(x => x.name == selectedMeasure.value).display_name
})

// cache geometry for the current selected geo-level
const geometryBySelection = computed(() => {
  switch (selectedGeoLevel.value) {
    case 'County':
      return counties.value
    case 'Tract':
      return tracts.value
    default:
      return null
  }
})

const categoriesByGeometry = computed(() => {
  switch (selectedGeoLevel.value) {
    case 'County':
      return measures.value.county
    case 'Tract':
      return measures.value.tract
    default:
      return null
  }
})

const measuresByCategory = computed(() => {
    return categoriesByGeometry.value[selectedCategory.value].measures
})

// 'geometry' is the geojson that gets sent to leaflet for visualization.
// it can consist of just county/tract boundaries, or if a measure is selected,
// boundaries that are annotated with the values for the selected measure.
const geometry = computed(() => {
  // first, determine what geometry to start with, counties or tracts
  let geom = geometryBySelection.value;
  if (!geom) { return }

  // next, if a measure was selected, merge that data into the geometry
  if (measureAnnotations.value) {
    geom = geom.map((feature) => {
      const valueForFips = feature.properties.fips && measureAnnotations.value.values[feature.properties.fips]

      const measure = valueForFips
      const popupContent = (
        (
          feature.properties.name
            ? `Name: ${feature.properties.name}`
            : `FIPS: ${feature.properties.fips}`
        ) + "<br />\n" +
        `Value: ${valueForFips != null ? valueForFips.toLocaleString() : 'n/a'}`
      )

      return {
        ...feature,
        properties: {
          fips: feature.properties.fips,
          measure, popupContent
        }
      };
    })
  }

  return geom;
})

const colorScale = computed(() => {
  if (!measureAnnotations.value) { return null }

  const {min,max} = measureAnnotations.value;
  
  return scaleSequential(["red", "blue"]).domain([min, max]);
})

const legendData = computed(() => {
  if (!showLegend.value || !measureAnnotations.value || !selectedCategoryName.value || !selectedMeasureName.value) {
    return null
  }

  const {min, max} = measureAnnotations.value;
  const measureScale = scaleLinear().domain([min, max]).nice()

  // produce X elements from the scale
  const steps = measureScale.ticks(5);

  console.log("Steps: ", steps);

  // map those X elements to colored ranges of the domain
  const rows = steps.slice(0, steps.length-1).map((x, i) => ({
    label: `${x.toLocaleString()} - ${steps[i + 1].toLocaleString()}`,
    color: colorScale.value(x)
  }))

  return {
    title: selectedCategoryName.value,
    subtitle: selectedMeasureName.value,
    rows
  }

  // return scaleSequential(["red", "blue"]).domain([min, max]);
})

</script>

<style scoped>
.fieldset {
  margin-bottom: 1em;
}
.fieldset label {
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 0.25em;
}

select {
  border: solid 1px gray;
  padding: 5px;
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  font-size: 1em;
  border-radius: 3px;
}

.two-panel {
  display: flex; margin: 0;
  width: 100%;
}

/* lefthand, narrow side with selections */
.panel-narrow {
  flex: 1 0 350px; background: #eee; padding: 0;
  margin-right: 0; border-right: solid 1px #ccc;
}

.main-options-panel {
  display: flex;
  flex-direction: column;
}

.subpanel { padding: 20px; }

.main { flex: 1 1; }
.options {
  margin-top: 1em; flex: 0 1; background-color: #bbb; padding: 20px;
  border-top: solid 1px #ccc;
}
.options label { color: #333; margin-left: 3px; }
.options .option-fieldset { display: flex; align-items: baseline; }

/* righthand, wide side with map */
.panel-wide { flex: 1 1 100%; }
.full-height { height: 100%; }
</style>
