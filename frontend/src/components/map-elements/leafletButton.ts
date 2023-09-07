// adapted from https://stackoverflow.com/a/31929242/22216869

import '@/components/map-elements/styles/leafletButton.scss'
import L from 'leaflet';

export default L.Control.extend({
    options: {
        position: 'topleft',
        title: 'No title',
        body: "X",
        click: null
    },
    
    onAdd: function () {
        const options = this.options;
        const container = L.DomUtil.create('a');

        container.className = "leaflet-map-button";

        container.title = options.title;
        container.innerHTML = options.body;

        container.onclick = function() {
            console.log('buttonClicked');
            if (options.click) {
                options.click();
            }
        }
        
        return container;
    }
});
