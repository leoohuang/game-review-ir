import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const pptxgen = require("pptxgenjs");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Game Review IR Team";
pptx.subject = "Member C Evaluation Metrics";
pptx.title = "Member C - Retrieval Evaluation";
pptx.company = "Game Review IR";
pptx.lang = "en-US";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "en-US",
};

const C = {
  ink: "14213D",
  muted: "52677A",
  light: "EEF4F8",
  panel: "F8FBFD",
  line: "D6E3EC",
  blue: "2563EB",
  cyan: "0E7490",
  green: "0F766E",
  amber: "D97706",
  red: "BE123C",
  white: "FFFFFF",
};

const W = 13.333;
const H = 7.5;

function addTitle(slide, title, subtitle) {
  slide.addText(title, {
    x: 0.55, y: 0.38, w: 8.8, h: 0.44,
    fontFace: "Aptos Display", fontSize: 24, bold: true, color: C.ink,
    margin: 0,
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.58, y: 0.87, w: 8.2, h: 0.24,
      fontSize: 8.5, color: C.muted, margin: 0,
      breakLine: false,
    });
  }
  slide.addShape(pptx.ShapeType.line, {
    x: 0.55, y: 1.18, w: 12.2, h: 0,
    line: { color: C.line, width: 1 },
  });
}

function foot(slide, idx) {
  slide.addText(`Member C Evaluation | ${idx}`, {
    x: 10.75, y: 7.08, w: 1.95, h: 0.18,
    fontSize: 6.8, color: "71899A", align: "right", margin: 0,
  });
}

function chip(slide, label, x, y, color = C.blue) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w: 1.78, h: 0.38,
    rectRadius: 0.08,
    fill: { color, transparency: 88 },
    line: { color, transparency: 70, width: 0.8 },
  });
  slide.addText(label, {
    x: x + 0.08, y: y + 0.1, w: 1.62, h: 0.16,
    fontSize: 8.5, bold: true, color, align: "center", margin: 0,
  });
}

function metricCard(slide, label, value, detail, x, y, w, color) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h: 1.32,
    rectRadius: 0.06,
    fill: { color: C.panel },
    line: { color: C.line, width: 0.9 },
  });
  slide.addText(label, {
    x: x + 0.18, y: y + 0.17, w: w - 0.36, h: 0.2,
    fontSize: 8.5, bold: true, color: C.muted, margin: 0,
  });
  slide.addText(value, {
    x: x + 0.18, y: y + 0.45, w: w - 0.36, h: 0.48,
    fontFace: "Aptos Display", fontSize: 25, bold: true, color, margin: 0,
  });
  slide.addText(detail, {
    x: x + 0.18, y: y + 0.98, w: w - 0.36, h: 0.18,
    fontSize: 7.5, color: C.muted, margin: 0,
  });
}

function addBullets(slide, bullets, x, y, w, h) {
  slide.addText(bullets.map(text => ({ text, options: { bullet: { type: "ul" } } })), {
    x, y, w, h,
    fontSize: 13,
    color: C.ink,
    breakLine: false,
    fit: "shrink",
    paraSpaceAfterPt: 7,
    margin: 0,
  });
}

function addFlowNode(slide, label, detail, x, y, w, color) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h: 0.92,
    rectRadius: 0.06,
    fill: { color, transparency: 90 },
    line: { color, transparency: 60, width: 1 },
  });
  slide.addText(label, {
    x: x + 0.16, y: y + 0.16, w: w - 0.32, h: 0.18,
    fontSize: 10.5, bold: true, color, margin: 0,
  });
  slide.addText(detail, {
    x: x + 0.16, y: y + 0.45, w: w - 0.32, h: 0.28,
    fontSize: 7.8, color: C.muted, fit: "shrink", margin: 0,
  });
}

function arrow(slide, x1, y1, x2, y2) {
  slide.addShape(pptx.ShapeType.line, {
    x: x1, y: y1, w: x2 - x1, h: y2 - y1,
    line: { color: C.line, width: 1.4, beginArrowType: "none", endArrowType: "triangle" },
  });
}

function addBars(slide, data, x, y, w, h, max = 1.0) {
  const labelW = 2.2;
  const gap = 0.22;
  const barH = 0.22;
  data.forEach((d, i) => {
    const yy = y + i * 0.56;
    slide.addText(d.label, {
      x, y: yy + 0.02, w: labelW, h: 0.16,
      fontSize: 8.8, color: C.ink, margin: 0,
    });
    slide.addShape(pptx.ShapeType.rect, {
      x: x + labelW, y: yy, w: w - labelW - 0.65, h: barH,
      fill: { color: C.light },
      line: { color: C.light },
    });
    slide.addShape(pptx.ShapeType.rect, {
      x: x + labelW, y: yy,
      w: (w - labelW - 0.65) * Math.min(d.value / max, 1),
      h: barH,
      fill: { color: d.color },
      line: { color: d.color },
    });
    slide.addText(d.value.toFixed(4), {
      x: x + w - 0.55, y: yy - 0.01, w: 0.5, h: 0.16,
      fontSize: 7.7, bold: true, color: d.color, align: "right", margin: 0,
    });
    if (d.delta) {
      slide.addText(d.delta, {
        x: x + labelW + (w - labelW - 0.65) * Math.min(d.value / max, 1) + gap,
        y: yy - 0.01, w: 0.82, h: 0.16,
        fontSize: 7.2, color: C.green, bold: true, margin: 0,
      });
    }
  });
}

function speaker(slide, text) {
  slide.addNotes(text);
}

{
  const slide = pptx.addSlide();
  slide.background = { color: "F6FAFD" };
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: W, h: H, fill: { color: "F6FAFD" }, line: { color: "F6FAFD" } });
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: W, h: 0.14, fill: { color: C.blue }, line: { color: C.blue } });
  chip(slide, "IR evaluation", 0.72, 0.74, C.cyan);
  chip(slide, "nDCG@10", 2.65, 0.74, C.blue);
  slide.addText("Member C", {
    x: 0.72, y: 1.35, w: 3.0, h: 0.28,
    fontSize: 13, bold: true, color: C.cyan, margin: 0,
  });
  slide.addText("Evaluating Aspect-Aware Retrieval", {
    x: 0.72, y: 1.72, w: 7.4, h: 0.62,
    fontFace: "Aptos Display", fontSize: 34, bold: true, color: C.ink,
    fit: "shrink", margin: 0,
  });
  slide.addText("Goal: test whether LLM-predicted aspect labels improve retrieval ranking beyond the original BM25 baseline.", {
    x: 0.76, y: 2.6, w: 7.2, h: 0.48,
    fontSize: 15.5, color: C.muted, fit: "shrink", margin: 0,
  });
  metricCard(slide, "Queries", "35", "aspect-focused search intents", 0.76, 4.05, 2.45, C.blue);
  metricCard(slide, "Games", "6", "query-game evaluation groups", 3.55, 4.05, 2.45, C.cyan);
  metricCard(slide, "Retrieved rows", "2100", "top-10 reviews per pair", 6.34, 4.05, 2.7, C.green);
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 9.5, y: 1.3, w: 2.85, h: 4.5,
    rectRadius: 0.06,
    fill: { color: C.white },
    line: { color: C.line, width: 1 },
  });
  slide.addText("Pipeline position", {
    x: 9.78, y: 1.66, w: 2.2, h: 0.2,
    fontSize: 10, bold: true, color: C.ink, margin: 0,
  });
  addFlowNode(slide, "A: BM25 retrieval", "top-10 reviews", 9.8, 2.12, 2.25, C.muted);
  arrow(slide, 10.94, 3.04, 10.94, 3.35);
  addFlowNode(slide, "B: aspect labels", "LLM predictions", 9.8, 3.36, 2.25, C.blue);
  arrow(slide, 10.94, 4.28, 10.94, 4.59);
  addFlowNode(slide, "C: evaluation", "BM25 vs rerank", 9.8, 4.6, 2.25, C.green);
  foot(slide, 1);
  speaker(slide, "This is my part, Member C. My goal was not to build another classifier, but to evaluate whether the aspect labels from Member B actually help retrieval. I compare the original BM25 ranking with an aspect-aware reranking over 35 queries, 6 games, and 2100 retrieved reviews.");
}

{
  const slide = pptx.addSlide();
  slide.background = { color: C.white };
  addTitle(slide, "Evaluation Design", "The experiment keeps the same retrieved reviews, then changes how they are ranked.");
  addFlowNode(slide, "Input 1: BM25 ranking", "Member A retrieved top-10 reviews for every query-game pair.", 0.78, 1.75, 3.2, C.muted);
  arrow(slide, 4.1, 2.2, 4.75, 2.2);
  addFlowNode(slide, "Input 2: predicted aspects", "Member B classified each retrieved review with LLM aspect labels.", 4.9, 1.75, 3.2, C.blue);
  arrow(slide, 8.22, 2.2, 8.87, 2.2);
  addFlowNode(slide, "Member C evaluation", "Compare BM25 against aspect-aware reranking.", 9.02, 1.75, 3.2, C.green);
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.8, y: 3.55, w: 5.45, h: 1.9,
    rectRadius: 0.06,
    fill: { color: C.panel },
    line: { color: C.line, width: 1 },
  });
  slide.addText("Binary aspect relevance", {
    x: 1.08, y: 3.88, w: 2.8, h: 0.23,
    fontSize: 12, bold: true, color: C.ink, margin: 0,
  });
  slide.addText("A retrieved review is relevant if the query aspect appears in the review's predicted aspects.", {
    x: 1.08, y: 4.28, w: 4.8, h: 0.44,
    fontSize: 13.2, color: C.muted, fit: "shrink", margin: 0,
  });
  slide.addText("query aspect in predicted_aspects  ->  1\notherwise  ->  0", {
    x: 1.08, y: 4.86, w: 4.4, h: 0.36,
    fontFace: "Aptos Mono", fontSize: 10.2, color: C.cyan, fit: "shrink", margin: 0,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 7.0, y: 3.55, w: 5.0, h: 1.9,
    rectRadius: 0.06,
    fill: { color: "F9FBFF" },
    line: { color: C.line, width: 1 },
  });
  slide.addText("Aspect-aware reranking rule", {
    x: 7.28, y: 3.88, w: 3.4, h: 0.23,
    fontSize: 12, bold: true, color: C.ink, margin: 0,
  });
  addBullets(slide, [
    "Promote reviews whose predicted aspects match the query aspect",
    "Use BM25 score as the second sorting signal",
    "Evaluate the new top-10 order with nDCG@10",
  ], 7.32, 4.3, 4.15, 0.85);
  foot(slide, 2);
  speaker(slide, "For the evaluation design, I kept the retrieval candidates the same. BM25 gives us the original top-10 reviews. Member B gives aspect labels for each review. Then I define relevance in a binary way: if the target query aspect is inside the predicted aspects, relevance is 1; otherwise it is 0. The reranking rule is simple: aspect match first, then BM25 score.");
}

{
  const slide = pptx.addSlide();
  slide.background = { color: "F8FBFD" };
  addTitle(slide, "Metric and Statistical Test", "The metric measures whether aspect-relevant reviews appear closer to the top.");
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.8, y: 1.65, w: 5.35, h: 3.95,
    rectRadius: 0.06,
    fill: { color: C.white },
    line: { color: C.line, width: 1 },
  });
  slide.addText("nDCG@10", {
    x: 1.1, y: 2.05, w: 2.2, h: 0.34,
    fontFace: "Aptos Display", fontSize: 24, bold: true, color: C.blue, margin: 0,
  });
  slide.addText("Higher score means relevant reviews are ranked earlier.", {
    x: 1.1, y: 2.55, w: 4.55, h: 0.32,
    fontSize: 13.5, color: C.muted, margin: 0,
  });
  slide.addText("DCG@10 / ideal DCG@10", {
    x: 1.1, y: 3.2, w: 4.2, h: 0.38,
    fontFace: "Aptos Mono", fontSize: 16, bold: true, color: C.ink, margin: 0,
  });
  addBullets(slide, [
    "Calculated separately for each query-game group",
    "Uses the top-10 ranking from each system",
    "Averaged across 210 groups",
  ], 1.16, 4.02, 4.4, 0.9);
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 7.0, y: 1.65, w: 5.35, h: 3.95,
    rectRadius: 0.06,
    fill: { color: C.white },
    line: { color: C.line, width: 1 },
  });
  slide.addText("Paired permutation test", {
    x: 7.3, y: 2.05, w: 3.6, h: 0.34,
    fontFace: "Aptos Display", fontSize: 21, bold: true, color: C.green, margin: 0,
  });
  slide.addText("Checks whether the improvement is consistent across the same query-game groups.", {
    x: 7.3, y: 2.55, w: 4.45, h: 0.45,
    fontSize: 13.2, color: C.muted, fit: "shrink", margin: 0,
  });
  metricCard(slide, "Evaluation groups", "210", "35 queries x 6 games", 7.3, 3.55, 2.1, C.cyan);
  metricCard(slide, "Ranking depth", "10", "top retrieved reviews", 9.75, 3.55, 2.1, C.amber);
  foot(slide, 3);
  speaker(slide, "The main metric is nDCG at 10. This is useful because we do not only care whether relevant reviews exist, but whether they appear near the top. I compute it for each query-game group, then average across 210 groups. I also use a paired permutation test, because both systems are evaluated on the same groups.");
}

{
  const slide = pptx.addSlide();
  slide.background = { color: C.white };
  addTitle(slide, "Main Result", "Aspect-aware reranking substantially improves aspect-level nDCG@10.");
  metricCard(slide, "BM25 baseline", "0.8756", "mean aspect nDCG@10", 0.82, 1.65, 2.75, C.muted);
  metricCard(slide, "Aspect-aware rerank", "0.9810", "mean aspect nDCG@10", 3.85, 1.65, 3.0, C.blue);
  metricCard(slide, "Mean delta", "+0.1053", "paired over 210 groups", 7.15, 1.65, 2.65, C.green);
  metricCard(slide, "p-value", "0.0001", "paired permutation test", 10.1, 1.65, 2.35, C.red);
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.86, y: 3.65, w: 11.45, h: 2.2,
    rectRadius: 0.06,
    fill: { color: C.panel },
    line: { color: C.line, width: 1 },
  });
  addBars(slide, [
    { label: "BM25 baseline", value: 0.8756, color: "687A8A" },
    { label: "Aspect-aware rerank", value: 0.9810, color: C.blue, delta: "+0.1053" },
  ], 1.28, 4.36, 9.7, 1.0);
  slide.addText("Interpretation: using aspect labels makes the ranking better aligned with the user's intended aspect, not just keyword similarity.", {
    x: 1.12, y: 6.12, w: 10.5, h: 0.34,
    fontSize: 13.4, bold: true, color: C.ink, fit: "shrink", margin: 0,
  });
  foot(slide, 4);
  speaker(slide, "The main result is that aspect-aware reranking improves nDCG from 0.8756 to 0.9810. The mean improvement is about 0.1053, and the paired permutation test gives p equals 0.0001. So the improvement is not just one or two lucky cases; it is consistent across the evaluation groups.");
}

{
  const slide = pptx.addSlide();
  slide.background = { color: "F8FBFD" };
  addTitle(slide, "Per-Aspect Pattern", "The reranker improves every evaluated aspect category.");
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.8, y: 1.55, w: 7.0, h: 4.85,
    rectRadius: 0.06,
    fill: { color: C.white },
    line: { color: C.line, width: 1 },
  });
  slide.addText("Mean nDCG@10 by aspect", {
    x: 1.08, y: 1.9, w: 3.1, h: 0.22,
    fontSize: 12, bold: true, color: C.ink, margin: 0,
  });
  addBars(slide, [
    { label: "combat / BM25", value: 0.8345, color: "8795A1" },
    { label: "combat / rerank", value: 0.9286, color: C.blue, delta: "+0.0940" },
    { label: "controls / BM25", value: 0.8367, color: "8795A1" },
    { label: "controls / rerank", value: 0.9762, color: C.blue, delta: "+0.1395" },
    { label: "graphics / BM25", value: 0.9362, color: "8795A1" },
    { label: "graphics / rerank", value: 1.0, color: C.blue, delta: "+0.0638" },
    { label: "price / BM25", value: 0.8502, color: "8795A1" },
    { label: "price / rerank", value: 1.0, color: C.blue, delta: "+0.1498" },
    { label: "story / BM25", value: 0.9204, color: "8795A1" },
    { label: "story / rerank", value: 1.0, color: C.blue, delta: "+0.0796" },
  ], 1.08, 2.42, 6.25, 3.5);
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 8.32, y: 1.55, w: 3.95, h: 4.85,
    rectRadius: 0.06,
    fill: { color: C.white },
    line: { color: C.line, width: 1 },
  });
  slide.addText("What this tells us", {
    x: 8.65, y: 1.92, w: 2.7, h: 0.22,
    fontSize: 12, bold: true, color: C.ink, margin: 0,
  });
  addBullets(slide, [
    "The gain is not limited to one aspect.",
    "Price and controls benefit the most.",
    "Graphics, price, and story reach perfect mean nDCG in this setup.",
    "The result supports aspect labels as useful IR context.",
  ], 8.72, 2.48, 3.0, 2.4);
  foot(slide, 5);
  speaker(slide, "Looking by aspect, the improvement appears in every category. The biggest gains are for price and controls. Some aspects reach a mean nDCG of 1 after reranking in this setup. My interpretation is that aspect labels add useful context when keyword matching alone is too broad.");
}

{
  const slide = pptx.addSlide();
  slide.background = { color: C.white };
  addTitle(slide, "Conclusion and Caveats", "The evaluation supports aspect-aware reranking, while keeping the relevance definition transparent.");
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.85, y: 1.52, w: 5.4, h: 4.4,
    rectRadius: 0.06,
    fill: { color: "F5FBFA" },
    line: { color: "BFE4DF", width: 1 },
  });
  slide.addText("Conclusion", {
    x: 1.2, y: 1.95, w: 2.4, h: 0.3,
    fontFace: "Aptos Display", fontSize: 22, bold: true, color: C.green, margin: 0,
  });
  addBullets(slide, [
    "Aspect-aware reranking improves mean nDCG@10 from 0.8756 to 0.9810.",
    "The improvement is statistically significant with p = 0.0001.",
    "This shows how LLM aspect labels can act as an IR context signal.",
  ], 1.22, 2.62, 4.45, 1.55);
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 7.08, y: 1.52, w: 5.4, h: 4.4,
    rectRadius: 0.06,
    fill: { color: "FFF9F1" },
    line: { color: "F4D39C", width: 1 },
  });
  slide.addText("Caveats", {
    x: 7.43, y: 1.95, w: 2.4, h: 0.3,
    fontFace: "Aptos Display", fontSize: 22, bold: true, color: C.amber, margin: 0,
  });
  addBullets(slide, [
    "The relevance signal comes from LLM-predicted aspects, not full human retrieval judgments.",
    "Member B validated the classifier on 230 gold reviews; best kappa was 0.540.",
    "So the score is best described as aspect-consistency evaluation.",
  ], 7.45, 2.62, 4.45, 1.75);
  slide.addText("One-sentence takeaway: Member C shows that adding aspect labels gives the retriever better context for ranking game reviews.", {
    x: 1.1, y: 6.35, w: 11.1, h: 0.34,
    fontSize: 14, bold: true, color: C.ink, align: "center", margin: 0,
  });
  foot(slide, 6);
  speaker(slide, "My conclusion is that the aspect-aware version gives better context to the retrieval system. The important caveat is that this is not a full human relevance judgment study. The relevance signal is based on predicted aspects. But since Member B validated the classifier on 230 gold reviews, we can still use it as a reasonable aspect-consistency evaluation.");
}

await pptx.writeFile({ fileName: "presentation/member_c_evaluation.pptx" });
