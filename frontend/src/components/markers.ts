import * as L from "leaflet";
import { chunk } from "lodash";
import { icon } from "@fortawesome/fontawesome-svg-core";
import {
  faBurst,
  faCertificate,
  faCircle,
  faCircleHalfStroke,
  faClover,
  faCube,
  faDiamond,
  faLocationArrow,
  faLocationCrosshairs,
  faLocationPin,
  faMapPin,
  faMound,
  faSplotch,
  faSquare,
  faStar,
  faStarOfLife,
  faThumbTack,
} from "@fortawesome/free-solid-svg-icons";

/** neutral-looking shapes from font-awesome */
const icons = [
  faCircle,
  faSquare,
  faDiamond,
  faCertificate,
  faSplotch,
  faMound,
  faBurst,
  faClover,
  faCircleHalfStroke,
  faCube,
  faStar,
  faStarOfLife,
  faLocationPin,
  faLocationArrow,
  faLocationCrosshairs,
  faMapPin,
  faThumbTack,
];

/** https://tailwindcss.com/docs/customizing-colors */
const colors = [
  "#ef4444",
  "#f97316",
  "#f59e0b",
  "#eab308",
  "#84cc16",
  "#22c55e",
  "#10b981",
  "#14b8a6",
  "#06b6d4",
  "#0ea5e9",
  "#3b82f6",
  "#6366f1",
  "#8b5cf6",
  "#a855f7",
  "#d946ef",
  "#ec4899",
  "#f43f5e",
].reverse();

export const markerOptions = icons.map((def, index) => {
  /** lookup icon definition */
  const { node } = icon(def);

  /** get html of icon */
  const svg = node[0] as SVGSVGElement;

  /** skip every N colors to space them out visually */
  /** don't use N that is factor of number of colors or else you'll get repeats */
  const color = colors[(index * 3) % colors.length] || "black";

  /** outline thickness */
  const stroke = 150;

  /** expand viewbox to account for stroke */
  const padding = stroke / 2;
  const [x = 0, y = 0, w = 512, h = 512] =
    svg.getAttribute("viewBox")?.split(" ").map(Number) || [];
  svg.setAttribute(
    "viewBox",
    [x - padding, y - padding, w + padding * 2, h + padding * 2].join(" "),
  );

  /** hard-code styles (<img>'s can't be styled from "outside", e.g. in css) */
  svg.style.color = color;
  svg.style.stroke = "black";
  svg.style.strokeWidth = String(stroke);
  svg.style.paintOrder = "stroke";

  /** encode url */
  const url = "data:image/svg+xml;base64," + window.btoa(svg.outerHTML);

  return L.icon({
    iconUrl: url,
    iconSize: [15, 15],
  });
});
