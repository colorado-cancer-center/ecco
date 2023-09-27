import * as L from "leaflet";
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

// https://tailwindcss.com/docs/customizing-colors
const colors = [
  "#ec4899",
  "#d946ef",
  "#a855f7",
  "#8b5cf6",
  "#6366f1",
  "#3b82f6",
  "#0ea5e9",
  "#06b6d4",
  "#14b8a6",
  "#10b981",
  "#22c55e",
  "#84cc16",
  "#eab308",
  "#f59e0b",
  "#f97316",
  "#ef4444",
];

export const markerOptions = icons.map((def, index) => {
  // get html node of icon
  const svg = icon(def).node[0] as SVGSVGElement;

  // skip every N colors to space them out visually
  // don't use N that is factor of number of colors or else you'll get repeats
  const color = colors[(index * 3) % colors.length] || "black";

  // expand viewbox to account for stroke
  const padding = 40;
  const [x = 0, y = 0, w = 512, h = 512] =
    svg.getAttribute("viewBox")?.split(" ").map(Number) || [];
  svg.setAttribute(
    "viewBox",
    [x - padding, y - padding, w + padding * 2, h + padding * 2].join(" "),
  );

  // hard-code styles
  svg.style.color = color;
  svg.style.stroke = "black";
  svg.style.strokeWidth = String(padding * 2);

  // encode url
  const url = "data:image/svg+xml;base64," + window.btoa(svg.outerHTML);

  return L.icon({
    iconUrl: url,
    iconSize: [12, 12],
  });
});
