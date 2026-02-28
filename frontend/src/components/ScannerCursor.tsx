import { useEffect, useRef, useCallback, useState } from "react";
import { useIsMobile } from "@/hooks/use-mobile";

type CursorState = "default" | "clickable" | "button" | "danger" | "success" | "warning" | "text" | "heading";

const ScannerCursor = () => {
  const isMobile = useIsMobile();
  const coreRef = useRef<HTMLDivElement>(null);
  const outerRef = useRef<HTMLDivElement>(null);
  const dotRef = useRef<HTMLDivElement>(null);
  const rippleRef = useRef<HTMLDivElement>(null);
  const labelRef = useRef<HTMLSpanElement>(null);

  const pos = useRef({ x: -100, y: -100 });
  const target = useRef({ x: -100, y: -100 });
  const outerPos = useRef({ x: -100, y: -100 });
  const rafId = useRef<number>(0);
  const [hoverState, setHoverState] = useState<CursorState>("default");

  const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

  const animate = useCallback(() => {
    // Core follows with 0.08s-feel lag
    pos.current.x = lerp(pos.current.x, target.current.x, 0.14);
    pos.current.y = lerp(pos.current.y, target.current.y, 0.14);

    // Outer ring even slower
    outerPos.current.x = lerp(outerPos.current.x, target.current.x, 0.09);
    outerPos.current.y = lerp(outerPos.current.y, target.current.y, 0.09);

    if (coreRef.current) {
      coreRef.current.style.transform = `translate(${pos.current.x}px, ${pos.current.y}px) translate(-50%, -50%)`;
    }
    if (outerRef.current) {
      // We need to set a CSS variable for the base transform so the rotation animation composes
      outerRef.current.style.setProperty('--base-transform', `translate(${outerPos.current.x}px, ${outerPos.current.y}px) translate(-50%, -50%)`);
    }

    rafId.current = requestAnimationFrame(animate);
  }, []);

  useEffect(() => {
    if (isMobile) return;

    document.body.style.cursor = "none";

    const style = document.createElement("style");
    style.id = "scanner-cursor-global";
    style.textContent = `*, *::before, *::after { cursor: none !important; }`;
    document.head.appendChild(style);

    const onMove = (e: MouseEvent) => {
      target.current.x = e.clientX;
      target.current.y = e.clientY;
    };

    const onDown = () => {
      if (coreRef.current) coreRef.current.classList.add("cursor-click");
      if (rippleRef.current) {
        rippleRef.current.classList.remove("cursor-ripple-active");
        void rippleRef.current.offsetWidth;
        rippleRef.current.classList.add("cursor-ripple-active");
      }
    };

    const onUp = () => {
      if (coreRef.current) coreRef.current.classList.remove("cursor-click");
    };

    const detectState = (el: HTMLElement | null): CursorState => {
      if (!el) return "default";
      const tag = el.tagName.toLowerCase();

      // Verdict states
      if (el.closest("[data-verdict='false']") || el.closest("[data-danger]") || el.closest(".badge-pulse-red")) return "danger";
      if (el.closest("[data-verdict='true']") || el.closest("[data-success]") || el.closest(".badge-pulse-green")) return "success";
      if (el.closest("[data-verdict='review']") || el.closest("[data-warning]") || el.closest(".badge-pulse-amber")) return "warning";

      // Headings
      if (/^h[1-6]$/.test(tag) || el.closest("h1, h2, h3, h4, h5, h6")) return "heading";

      // Buttons
      if (tag === "button" || el.closest("button") || el.getAttribute("role") === "button") return "button";

      // Links / clickable
      if (tag === "a" || el.closest("a") || getComputedStyle(el).cursor === "pointer") return "clickable";

      // Text blocks
      if (tag === "p" || tag === "span" || tag === "li" || tag === "blockquote") return "text";

      return "default";
    };

    const onOver = (e: MouseEvent) => {
      setHoverState(detectState(e.target as HTMLElement));
    };

    window.addEventListener("mousemove", onMove, { passive: true });
    window.addEventListener("mousedown", onDown);
    window.addEventListener("mouseup", onUp);
    window.addEventListener("mouseover", onOver, { passive: true });

    rafId.current = requestAnimationFrame(animate);

    return () => {
      document.body.style.cursor = "";
      document.getElementById("scanner-cursor-global")?.remove();
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mousedown", onDown);
      window.removeEventListener("mouseup", onUp);
      window.removeEventListener("mouseover", onOver);
      cancelAnimationFrame(rafId.current);
    };
  }, [isMobile, animate]);

  if (isMobile) return null;

  const glowColor = {
    default: "var(--cursor-indigo)",
    clickable: "var(--cursor-cyan)",
    button: "var(--cursor-cyan)",
    danger: "var(--cursor-red)",
    success: "var(--cursor-green)",
    warning: "var(--cursor-amber)",
    text: "var(--cursor-indigo)",
    heading: "var(--cursor-indigo)",
  }[hoverState];

  const isExpanded = ["clickable", "button", "text", "heading", "danger", "success", "warning"].includes(hoverState);
  const showLabel = hoverState === "clickable";
  const outerFast = ["clickable", "button", "heading"].includes(hoverState);

  const outerSize = isExpanded ? 40 : 34;

  return (
    <>
      {/* Outer reactive ring */}
      <div
        ref={outerRef}
        className={`scanner-cursor-outer ${outerFast ? "outer-fast" : ""}`}
        style={{
          "--glow": glowColor,
          width: outerSize,
          height: outerSize,
        } as React.CSSProperties}
      />

      {/* Main lens ring */}
      <div
        ref={coreRef}
        className={`scanner-cursor-core ${isExpanded ? "scanner-expanded" : ""} scanner-state-${hoverState}`}
        style={{ "--glow": glowColor } as React.CSSProperties}
      >
        {/* Glass */}
        <div className="scanner-cursor-glass" />

        {/* Core dot */}
        <div
          ref={dotRef}
          className="scanner-cursor-dot"
          style={{ "--glow": glowColor } as React.CSSProperties}
        />

        {/* SCAN label */}
        <span
          ref={labelRef}
          className="scanner-cursor-label"
          style={{ opacity: showLabel ? 1 : 0, "--glow": glowColor } as React.CSSProperties}
        >
          SCAN
        </span>

        {/* Click ripple */}
        <div ref={rippleRef} className="scanner-cursor-ripple" style={{ borderColor: glowColor } as React.CSSProperties} />
      </div>
    </>
  );
};

export default ScannerCursor;
