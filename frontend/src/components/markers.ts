import * as L from "leaflet";
import { icon } from "@fortawesome/fontawesome-svg-core";
import {
  faBolt,
  faBurst,
  faCertificate,
  faCircle,
  faCloud,
  faClover,
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

/**
 * choose shapes from font-awesome that look neutral (don't imply any good/bad
 * connotation). put simpler shapes first. also be careful that similar looking
 * shapes don't get assigned similar looking colors.
 */
const icons = [
  faCircle,
  faSquare,
  faDiamond,
  faLocationPin,
  faStarOfLife,
  faSplotch,
  faMound,
  faBurst,
  faClover,
  faCertificate,
  faStar,
  faCloud,
  faBolt,
  faLocationArrow,
  faMapPin,
  faThumbTack,
  faLocationCrosshairs,
];

let iconIndex = 0;
/** get next icon in sequence */
function getIcon() {
  return icons[++iconIndex % icons.length]!;
}

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

let colorIndex = 0;
/** get next color in sequence */
function getColor() {
  /**
   * skip every N colors to space them out visually. don't use N that is factor
   * of number of colors.
   */
  return colors[(++colorIndex * 3) % colors.length]!;
}

/** line stroke dashes for areas */
const dashes = ["10 10 10 10 10", "5 10 15 10 5"];

let dashIndex = 0;
/** get next dash in sequence */
function getDash() {
  return dashes[++dashIndex % dashes.length]!;
}

/** reset marker sequence */
export function resetMarkers() {
  iconIndex = 0;
  colorIndex = 0;
  dashIndex = 0;
}

/** get next marker in sequence */
export function getMarker(type: "point" | "area") {
  /** get next color */
  const color = getColor();
  /** get next dash pattern */
  const dash = getDash();

  /** svg of icon */
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("xmlns", "http://www.w3.org/2000/svg");
  document.body.append(svg);

  /** use font-awesome point marker */
  if (type === "point") {
    const stroke = 50;

    /** get html of next icon */
    svg.innerHTML = icon(getIcon()).node[0]!.innerHTML;

    /** styles */
    svg.style.color = color;
    svg.style.stroke = "black";
    svg.style.strokeWidth = String(stroke * 2);
    svg.style.paintOrder = "stroke";

    /** expand viewbox to include stroke */
    const { x, y, width, height } = svg.getBBox();
    svg.setAttribute(
      "viewBox",
      [x - stroke, y - stroke, width + 2 * stroke, height + 2 * stroke].join(
        " ",
      ),
    );
  } else {
    const width = 100;
    const stroke = 10;

    /** create dash */
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    svg.append(line);
    line.setAttribute("x1", "0");
    line.setAttribute("x2", String(width));
    line.setAttribute("pathLength", "50");

    /** styles */
    svg.style.fill = "none";
    svg.style.stroke = color;
    svg.style.strokeWidth = String(stroke);
    svg.style.strokeDasharray = dash;

    /** fit viewbox to contents */
    svg.setAttribute("viewBox", `0 ${-stroke * 4} ${width} ${stroke * 2 * 4}`);
  }

  /** encode url */
  const url = URL.createObjectURL(
    new Blob([svg.outerHTML], { type: "image/svg+xml" }),
  );

  svg.remove();

  return {
    /** main color */
    color,
    /** dash pattern */
    dash,
    /** icon object url */
    url,
    /** leaflet icon object */
    icon: L.icon({ iconUrl: url, iconSize: [15, 15] }),
  };
}
