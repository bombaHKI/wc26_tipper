const root = document.documentElement;
const styleEl = document.createElement("style");
document.head.appendChild(styleEl);
const styleSheet = styleEl.sheet;

function createPointColorIndicatorRules() {
    function toRGBString(r,g,b) {
        return "rgb(" + r + "," + g + "," + b + ")";
    }
    var r1,r2,g1,g2,b1,b2;
    var r1_h,r2_h,g1_h,g2_h,b1_h,b2_h;
    r1 = 220;
    g1 = 220;
    b1 = 255;
    r2 = 255;
    g2 = 140;
    b2 = 140;

    r1_h = 50;
    g1_h = 50;
    b1_h = 255;
    r2_h = 255;
    g2_h = 10;
    b2_h = 30;
    root.style.setProperty("--color0", toRGBString(240,240,250));
    root.style.setProperty("--point0", toRGBString(240,240,250));
    root.style.setProperty("--point_h0", toRGBString(50,50,150));
    for (i = 1; i<=17; ++i) {
        var r = r1 + (r2-r1)/17*i;
        var g = g1 + (g2-g1)/17*i;
        var b = b1 + (b2-b1)/17*i;
        var r_h = r1_h + (r2_h-r1_h)/17*i;
        var g_h = g1_h + (g2_h-g1_h)/17*i;
        var b_h = b1_h + (b2_h-b1_h)/17*i;
        root.style.setProperty("--color"+i, toRGBString(r,g,b));
        root.style.setProperty("--point"+i, toRGBString(r,g,b));
        root.style.setProperty("--point_h"+i, toRGBString(r_h,g_h,b_h));
    }
    for (i = 0; i<=17; ++i) {
        styleSheet.insertRule(
        "td[data-points='"+i+"'], \
         div[data-points='"+i+"'] {\
            background-color: \
                var(--color"+i+"); \
            );\
        }");
    }
}
createPointColorIndicatorRules();

function highlightPoints(e) {
    e.stopPropagation();
    const target = e.target;
    const i = target.dataset.points;

    target.toggleAttribute("data-highlighted");
    if (target.hasAttribute("data-highlighted")) 
        root.style.setProperty("--color"+i, "var(--point_h"+i+")");
    else
        root.style.setProperty("--color"+i, "var(--point"+i+")");
}