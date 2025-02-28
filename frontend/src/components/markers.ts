import { max, sum } from "lodash";
import { icon as getHtml } from "@fortawesome/fontawesome-svg-core";
import {
  faCircle,
  faClover,
  faDiamond,
  faFlag,
  faLocationArrow,
  faLocationCrosshairs,
  faLocationPin,
  faMapPin,
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
  faStar,
  faStarOfLife,
  faFlag,
  faClover,
  faLocationArrow,
  faMapPin,
  faThumbTack,
  faLocationCrosshairs,
];

type Icon = (typeof icons)[number];

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
]
  .reverse()
  .map(
    (_, index, array) =>
      /**
       * skip every N colors to space them out visually. don't use N that is
       * factor of number of colors.
       */
      array[(index++ * 3) % array.length]!,
  );

type Color = (typeof colors)[number];

/** line stroke dashes for areas */
const dashes = [
  [10, 10],
  [5, 5],
  [5, 5, 15, 5],
  [0, 0],
];

type Dash = (typeof dashes)[number];

/** total dash length of line symbol in legend */
const dashSymbolLength = String(max(dashes.map((dash) => sum(dash)))!);

type Type = GeoJSON.GeoJsonTypes | "";

/** map enumerated values to markers */
export const getMarkers = <Value extends string>(values: [Value, Type][]) => {
  /** marker sequence */
  let iconIndex = 0;
  let colorIndex = 0;
  let dashIndex = 0;

  const map = {} as Record<Value, ReturnType<typeof getMarker>>;
  for (const [value, type] of values)
    if (value.trim())
      /** add value to map (if not already defined) */
      map[value] ??=
        /** get next marker in sequence */
        getMarker(
          type,
          icons[iconIndex++ % icons.length]!,
          colors[colorIndex++ % colors.length]!,
          type === "Point" ? [] : dashes[dashIndex++ % dashes.length]!,
        );

  return map;
};

function getMarker(
  type: Type,
  icon: Icon,
  color: Color,
  dash: Dash,
  size = 16,
) {
  /** svg of icon */
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("xmlns", ns);
  svg.setAttribute("width", "16");
  svg.setAttribute("height", "16");
  document.body.append(svg);

  /** use font-awesome point marker */
  if (type === "Point") {
    /** get html of next icon */
    svg.innerHTML = getHtml(icon).node[0]!.innerHTML;

    /** get bounds */
    let { x, y, width, height } = svg.getBBox();

    /** scale to size */
    const sizeWidth = size * (width / height);
    const sizeHeight = size;
    const stroke = height / 10;

    /** styles */
    svg.style.color = color;
    svg.style.stroke = "black";
    svg.style.strokeWidth = String(stroke * 2);
    svg.style.strokeLinecap = "round";
    svg.style.strokeLinejoin = "round";
    svg.style.paintOrder = "stroke";
    svg.style.overflow = "visible";

    /** expand view box to include stroke */
    x -= stroke;
    y -= stroke;
    width += 2 * stroke;
    height += 2 * stroke;

    /** fit view box */
    svg.setAttribute("viewBox", [x, y, width, height].join(" "));

    /** set explicit dimensions */
    svg.setAttribute("width", String(sizeWidth));
    svg.setAttribute("height", String(sizeHeight));
  } else {
    const stroke = 20;
    const x = 0;
    const y = -20;
    const width = 100;
    const height = 40;

    /** styles */
    svg.style.fill = "none";
    svg.style.stroke = color;
    svg.style.strokeWidth = String(stroke);
    svg.style.strokeDasharray = dash.join(" ");

    /** create dash */
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    svg.append(line);
    line.setAttribute("x1", "0");
    line.setAttribute("x2", String(width));
    line.setAttribute("pathLength", String(dashSymbolLength));

    /** fit view box */
    svg.setAttribute("viewBox", [x, y, width, height].join(" "));

    /** set explicit dimensions */
    svg.setAttribute("width", String(size));
    svg.setAttribute("height", String(size));
  }

  svg.remove();

  /** html source */
  const html = svg.outerHTML;
  /** encode to data uri */
  const src = `data:image/svg+xml;utf8,${window.encodeURIComponent(html)}`;

  return {
    /** main color */
    color,
    /** dash pattern */
    dash,
    /** icon html */
    html,
    /** icon src url */
    src,
    /** dimensions */
    width: parseFloat(svg.getAttribute("width") ?? ""),
    height: parseFloat(svg.getAttribute("height") ?? ""),
  };
}
