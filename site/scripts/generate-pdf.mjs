import fs from "fs";
import path from "path";
import React from "react";
import {
  Document,
  Page,
  Text,
  View,
  StyleSheet,
  renderToFile,
} from "@react-pdf/renderer";

const resume = JSON.parse(
  fs.readFileSync(
    path.join(process.cwd(), "content/resume/resume.json"),
    "utf-8",
  ),
);

const styles = StyleSheet.create({
  page: { padding: 40, fontSize: 11, fontFamily: "Helvetica" },
  title: { fontSize: 22, marginBottom: 4 },
  subtitle: { fontSize: 12, color: "#555", marginBottom: 16 },
  section: { marginTop: 14, marginBottom: 6, fontSize: 13, fontWeight: "bold" },
  text: { marginBottom: 4 },
  bullet: { marginLeft: 12, marginBottom: 2 },
});

function ResumeDoc() {
  return React.createElement(
    Document,
    null,
    React.createElement(
      Page,
      { size: "A4", style: styles.page },
      React.createElement(Text, { style: styles.title }, resume.name),
      React.createElement(
        Text,
        { style: styles.subtitle },
        `${resume.title} · ${resume.email} · ${resume.location}`,
      ),
      React.createElement(Text, { style: styles.section }, "Summary"),
      React.createElement(Text, { style: styles.text }, resume.summary),
      React.createElement(Text, { style: styles.section }, "Skills"),
      React.createElement(Text, { style: styles.text }, resume.skills.join(", ")),
      React.createElement(Text, { style: styles.section }, "Experience"),
      ...resume.experience.map((job) =>
        React.createElement(
          View,
          { key: job.company },
          React.createElement(
            Text,
            { style: styles.text },
            `${job.role} — ${job.company} (${job.period})`,
          ),
          ...job.highlights.map((h) =>
            React.createElement(Text, { key: h, style: styles.bullet }, `• ${h}`),
          ),
        ),
      ),
      React.createElement(Text, { style: styles.section }, "Education"),
      ...resume.education.map((edu) =>
        React.createElement(
          Text,
          { key: edu.institution, style: styles.text },
          `${edu.degree}, ${edu.institution} (${edu.period})`,
        ),
      ),
    ),
  );
}

const outDir = path.join(process.cwd(), "public");
fs.mkdirSync(outDir, { recursive: true });
const outPath = path.join(outDir, "resume.pdf");

await renderToFile(React.createElement(ResumeDoc), outPath);
console.log("Generated:", outPath);
