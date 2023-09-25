import * as L from "leaflet";

// modified from:
// https://github.com/DefinitelyTyped/DefinitelyTyped/blob/e4dc6495cdfd9c29449bc91c01bfb9b9ab150f38/types/leaflet-providers/index.d.ts
// installing normally doesn't work

declare module "leaflet" {
  namespace TileLayer {
    class Provider extends TileLayer {
      constructor(
        provider: string,
        options?: TileLayerOptions | { [name: string]: string },
      );

      // modified
      _url: string;
    }

    namespace Provider {
      const providers: ProvidersMap;

      interface ProvidersMap {
        [providerName: string]: ProviderConfig;
      }

      interface ProviderConfig {
        url: string;
        options?: TileLayerOptions | undefined;
        variants?:
          | { [variantName: string]: string | ProviderConfig }
          | undefined;
      }
    }
  }

  namespace tileLayer {
    function provider(
      provider: string,
      options?: TileLayerOptions | { [name: string]: string },
    ): TileLayer.Provider;
  }
}
