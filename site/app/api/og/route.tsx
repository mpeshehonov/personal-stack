import { ImageResponse } from "next/og";

export const runtime = "edge";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const title = searchParams.get("title")?.slice(0, 120) ?? "Максим Пешехонов";
  const subtitle =
    searchParams.get("subtitle")?.slice(0, 80) ?? "Senior Frontend Developer";

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "64px 72px",
          background: "linear-gradient(135deg, #f8fafc 0%, #eff6ff 55%, #dbeafe 100%)",
          fontFamily: "system-ui, sans-serif",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
          }}
        >
          <div
            style={{
              width: "12px",
              height: "12px",
              borderRadius: "999px",
              background: "#2563eb",
            }}
          />
          <span
            style={{
              fontSize: "22px",
              fontWeight: 600,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              color: "#2563eb",
            }}
          >
            mpeshekhonov.ru
          </span>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          <div
            style={{
              fontSize: title.length > 60 ? "48px" : "56px",
              fontWeight: 700,
              lineHeight: 1.15,
              color: "#0f172a",
              letterSpacing: "-0.02em",
            }}
          >
            {title}
          </div>
          <div
            style={{
              fontSize: "28px",
              fontWeight: 500,
              color: "#475569",
              lineHeight: 1.35,
            }}
          >
            {subtitle}
          </div>
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div
            style={{
              height: "4px",
              width: "120px",
              borderRadius: "999px",
              background: "#2563eb",
            }}
          />
          <span style={{ fontSize: "20px", color: "#64748b" }}>
            Portfolio · Blog · Resume
          </span>
        </div>
      </div>
    ),
    { width: 1200, height: 630 },
  );
}
