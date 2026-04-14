import { useEffect, useRef, useState } from "react";
import PropTypes from "prop-types";

export default function ChartContainer({
  className = "h-80 w-full min-w-0",
  children,
}) {
  const ref = useRef(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node) return undefined;

    const updateReadyState = () => {
      const width = node.clientWidth;
      const height = node.clientHeight;
      setIsReady(width > 0 && height > 0);
    };

    updateReadyState();

    if (typeof ResizeObserver === "undefined") {
      window.addEventListener("resize", updateReadyState);
      return () => {
        window.removeEventListener("resize", updateReadyState);
      };
    }

    const observer = new ResizeObserver(updateReadyState);
    observer.observe(node);

    return () => {
      observer.disconnect();
    };
  }, []);

  return (
    <div
      ref={ref}
      className={className}
      style={{
        backgroundColor: "var(--color-bg-card)",
        border: "1px solid var(--color-border)",
        boxShadow: "var(--color-card-shadow)",
        borderRadius: "12px",
      }}
    >
      {isReady ? children : null}
    </div>
  );
}

ChartContainer.propTypes = {
  className: PropTypes.string,
  children: PropTypes.node,
};
