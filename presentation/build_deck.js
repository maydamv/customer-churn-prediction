// Final-defense deck for the Customer Churn Prediction project.
const pptxgen = require("pptxgenjs");
const sizeOf = (() => { try { return require("image-size"); } catch { return null; } })();

const C = {
  bg: "0F1220", card: "1A1E30", card2: "232840", line: "2E3450",
  txt: "FFFFFF", soft: "D8DCEF", muted: "9AA0BD",
  accent: "6C8CFF", coral: "EF4767", green: "3ECF8E", gold: "F0A04B",
};
const FH = "Bookman Old Style"; // header serif (safe list)
const FB = "Calibri";           // body sans (safe list)

const p = new pptxgen();
p.defineLayout({ name: "W", width: 13.333, height: 7.5 });
p.layout = "W";
const W = 13.333, H = 7.5;

function slide(dark = true) {
  const s = p.addSlide();
  s.background = { color: dark ? C.bg : "F4F5FB" };
  return s;
}
function card(s, x, y, w, h, fill = C.card) {
  s.addShape(p.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.12,
    fill: { color: fill }, line: { color: C.line, width: 1 } });
}
// kicker + title block used on content slides
function head(s, kicker, title, tColor = C.txt) {
  s.addText(kicker.toUpperCase(), { x: 0.6, y: 0.42, w: 12, h: 0.3,
    fontFace: FB, fontSize: 13, bold: true, color: C.accent, charSpacing: 2, margin: 0 });
  s.addText(title, { x: 0.6, y: 0.72, w: 12.1, h: 0.85,
    fontFace: FH, fontSize: 30, bold: true, color: tColor, margin: 0 });
}
// fit an image inside a box preserving aspect ratio, centered
function fitImg(s, path, bx, by, bw, bh) {
  let ratio = 1.4;
  if (sizeOf) { try { const d = sizeOf(path); ratio = d.width / d.height; } catch {} }
  else { const R = { "pr_curves.png":1.27,"confusion_matrix.png":1.12,"shap_summary.png":1.27,
    "sensitivity.png":1.6,"engagement_by_churn.png":1.88,"churn_by_segment.png":2.89,
    "demo_high.png":1.44,"demo_low.png":1.44 };
    for (const k in R) if (path.endsWith(k)) ratio = R[k]; }
  let w = bw, h = w / ratio;
  if (h > bh) { h = bh; w = h * ratio; }
  s.addImage({ path, x: bx + (bw - w) / 2, y: by + (bh - h) / 2, w, h });
}

// ---------- 1. TITLE ----------
{
  const s = slide();
  s.addShape(p.ShapeType.roundRect, { x: -1.2, y: -1.5, w: 5, h: 5, rectRadius: 2.5,
    fill: { color: C.accent, transparency: 88 }, line: { type: "none" } });
  s.addShape(p.ShapeType.roundRect, { x: 9.5, y: 4.6, w: 5, h: 5, rectRadius: 2.5,
    fill: { color: C.coral, transparency: 90 }, line: { type: "none" } });

  s.addText("FINAL PROJECT · MACHINE LEARNING", { x: 0.9, y: 1.35, w: 8, h: 0.35,
    fontFace: FB, fontSize: 14, bold: true, color: C.accent, charSpacing: 2, margin: 0 });
  s.addText("Customer Churn Prediction\nfor Subscription Businesses", { x: 0.85, y: 1.8, w: 8.2, h: 1.9,
    fontFace: FH, fontSize: 40, bold: true, color: C.txt, lineSpacingMultiple: 1.0, margin: 0 });
  s.addText("Using machine learning to retain more and earn more", { x: 0.9, y: 3.75, w: 8, h: 0.5,
    fontFace: FB, fontSize: 18, italic: true, color: C.soft, margin: 0 });
  s.addText([
    { text: "Mayda Morales", options: { bold: true, color: C.txt } },
    { text: "     Harbour Space", options: { color: C.muted } },
  ], { x: 0.9, y: 4.5, w: 8, h: 0.4, fontFace: FB, fontSize: 15, margin: 0 });

  // product teaser card (mimics the live demo result)
  const cx = 9.55, cy = 2.15, cw = 3.1, ch = 3.2;
  card(s, cx, cy, cw, ch, C.card);
  s.addText("AT-RISK CUSTOMER", { x: cx, y: cy + 0.25, w: cw, h: 0.3, align: "center",
    fontFace: FB, fontSize: 11, bold: true, color: C.muted, charSpacing: 1, margin: 0 });
  s.addText("94.9%", { x: cx, y: cy + 0.6, w: cw, h: 1.1, align: "center",
    fontFace: FH, fontSize: 54, bold: true, color: C.coral, margin: 0 });
  s.addText("churn probability", { x: cx, y: cy + 1.7, w: cw, h: 0.3, align: "center",
    fontFace: FB, fontSize: 12, color: C.soft, margin: 0 });
  s.addShape(p.ShapeType.roundRect, { x: cx + 0.9, y: cy + 2.1, w: cw - 1.8, h: 0.42, rectRadius: 0.21,
    fill: { color: C.coral, transparency: 82 }, line: { color: C.coral, width: 1 } });
  s.addText("HIGH RISK", { x: cx + 0.9, y: cy + 2.11, w: cw - 1.8, h: 0.4, align: "center",
    fontFace: FB, fontSize: 12, bold: true, color: C.coral, margin: 0 });
  s.addText("→ personal outreach + retention offer", { x: cx, y: cy + 2.65, w: cw, h: 0.4, align: "center",
    fontFace: FB, fontSize: 10.5, italic: true, color: C.muted, margin: 0 });

  s.addNotes("Final defense of the churn prediction project. We predict which subscribers will cancel within 30 days so the retention team can act early. On the right is the live demo we will run at the end.");
}

// ---------- 2. DOMAIN ----------
{
  const s = slide();
  head(s, "Domain", "Subscription businesses run on recurring revenue");
  const items = [
    ["SaaS & cloud tools", "Monthly or annual seats; revenue depends on customers renewing, not buying once."],
    ["Content & media", "Streaming, news, learning platforms billed on a rolling subscription."],
    ["Wellness & apps", "Fitness, meditation, habit apps with recurring memberships."],
  ];
  const bx = 0.6, bw = 4.0, gap = 0.25, by = 2.1, bh = 2.7;
  items.forEach((it, i) => {
    const x = bx + i * (bw + gap);
    card(s, x, by, bw, bh);
    s.addShape(p.ShapeType.roundRect, { x: x + 0.3, y: by + 0.3, w: 0.55, h: 0.55, rectRadius: 0.27,
      fill: { color: C.accent, transparency: 78 }, line: { type: "none" } });
    s.addText(String(i + 1), { x: x + 0.3, y: by + 0.3, w: 0.55, h: 0.55, align: "center",
      fontFace: FH, fontSize: 20, bold: true, color: C.accent, margin: 0 });
    s.addText(it[0], { x: x + 0.3, y: by + 1.0, w: bw - 0.6, h: 0.5,
      fontFace: FH, fontSize: 17, bold: true, color: C.txt, margin: 0 });
    s.addText(it[1], { x: x + 0.3, y: by + 1.5, w: bw - 0.6, h: 1.05,
      fontFace: FB, fontSize: 13, color: C.muted, margin: 0 });
  });
  card(s, 0.6, 5.05, 12.13, 1.7, C.card2);
  s.addText("The shared challenge", { x: 0.9, y: 5.25, w: 11.6, h: 0.35,
    fontFace: FB, fontSize: 13, bold: true, color: C.gold, charSpacing: 1, margin: 0 });
  s.addText("Growth is not just about acquiring users — it is about keeping them. When customers cancel silently, recurring revenue erodes and the business must keep buying new users just to stand still.",
    { x: 0.9, y: 5.6, w: 11.6, h: 1.0, fontFace: FB, fontSize: 15, color: C.soft, margin: 0 });
  s.addNotes("Our domain is subscription businesses — SaaS, content, wellness. They all live on recurring revenue, so keeping customers matters as much as acquiring them.");
}

// ---------- 3. PROBLEM + WHY ----------
{
  const s = slide();
  head(s, "The problem & why it matters", "Silent churn quietly drains recurring revenue");
  card(s, 0.6, 2.0, 6.0, 2.05, C.card);
  s.addText("Problem statement", { x: 0.9, y: 2.2, w: 5.4, h: 0.35,
    fontFace: FB, fontSize: 13, bold: true, color: C.accent, charSpacing: 1, margin: 0 });
  s.addText("Customers cancel with little warning. By the time churn shows up in the numbers, the revenue is already gone and win-back is expensive.",
    { x: 0.9, y: 2.55, w: 5.4, h: 1.4, fontFace: FB, fontSize: 15, color: C.soft, margin: 0 });
  card(s, 6.75, 2.0, 5.98, 2.05, C.card);
  s.addText("Why it matters", { x: 7.05, y: 2.2, w: 5.4, h: 0.35,
    fontFace: FB, fontSize: 13, bold: true, color: C.green, charSpacing: 1, margin: 0 });
  s.addText([
    { text: "Retention is far cheaper than acquisition.\n", options: { breakLine: true } },
    { text: "A 5% lift in retention can raise profits 25–95% ", options: {} },
    { text: "(Reichheld & Sasser, 1990).", options: { italic: true, color: C.muted } },
  ], { x: 7.05, y: 2.55, w: 5.4, h: 1.4, fontFace: FB, fontSize: 15, color: C.soft, margin: 0 });

  const stats = [
    ["~5%", "monthly churn", "in a healthy subscription business", C.coral],
    ["12 mo", "revenue lost", "per churning customer, on average", C.gold],
    ["20%", "reduction target", "relative — our business goal", C.green],
  ];
  const bx = 0.6, bw = 3.97, gap = 0.11, by = 4.35, bh = 2.35;
  stats.forEach((st, i) => {
    const x = bx + i * (bw + gap);
    card(s, x, by, bw, bh, C.card2);
    s.addText(st[0], { x, y: by + 0.3, w: bw, h: 0.95, align: "center",
      fontFace: FH, fontSize: 46, bold: true, color: st[3], margin: 0 });
    s.addText(st[1], { x, y: by + 1.3, w: bw, h: 0.4, align: "center",
      fontFace: FB, fontSize: 16, bold: true, color: C.txt, margin: 0 });
    s.addText(st[2], { x: x + 0.2, y: by + 1.72, w: bw - 0.4, h: 0.5, align: "center",
      fontFace: FB, fontSize: 12, color: C.muted, margin: 0 });
  });
  s.addNotes("The problem is silent churn. It matters because retaining a customer is far cheaper than acquiring a new one — a 5% retention lift can raise profits 25 to 95%. Our goal: cut monthly churn by 20% relative.");
}

// ---------- 4. ML FORMULATION ----------
{
  const s = slide();
  head(s, "Machine learning formulation", "A supervised, time-aware classification problem");
  const rows = [
    ["Task", "Supervised binary classification"],
    ["Target", "churn_30d — will the customer cancel within 30 days? (1 / 0)"],
    ["Inputs", "Profile + subscription + behavioural engagement signals, known up to today"],
    ["Primary metric", "F2-score — weights recall higher (missing a churner costs more than a false alert)"],
    ["Secondary", "AUC for overall discriminative power"],
    ["Validation", "Time-based split — train on the past, test on the future (no data leakage)"],
  ];
  const by = 2.05, rh = 0.78, x = 0.6, w = 12.13;
  rows.forEach((r, i) => {
    const y = by + i * (rh + 0.03);
    card(s, x, y, w, rh, i % 2 ? C.card : C.card2);
    s.addText(r[0], { x: x + 0.3, y, w: 2.9, h: rh, valign: "middle",
      fontFace: FH, fontSize: 15, bold: true, color: C.accent, margin: 0 });
    s.addText(r[1], { x: x + 3.3, y, w: w - 3.6, h: rh, valign: "middle",
      fontFace: FB, fontSize: 15, color: C.soft, margin: 0 });
  });
  s.addNotes("Formally: supervised binary classification. Target is whether a customer cancels within 30 days. We optimise F2 because recall matters more than precision here, and we validate on a time-based split to mimic production and avoid leakage.");
}

// ---------- 5. SOLUTION OVERVIEW ----------
{
  const s = slide();
  head(s, "Solution overview", "An end-to-end pipeline, from raw data to action");
  const steps = [
    ["Data", "Public Telco base adapted to a SaaS scenario + engagement features"],
    ["Model", "SMOTE for imbalance; Logistic Reg., Random Forest, XGBoost"],
    ["Evaluate", "F2-tuned threshold; AUC, recall, precision on a future test set"],
    ["Explain", "SHAP shows why each customer is flagged"],
    ["Act", "Weekly batch scores → risk tiers → retention actions"],
  ];
  const n = steps.length, bx = 0.6, gap = 0.28, bw = (12.13 - gap * (n - 1)) / n, by = 2.4, bh = 3.0;
  steps.forEach((st, i) => {
    const x = bx + i * (bw + gap);
    card(s, x, by, bw, bh);
    s.addShape(p.ShapeType.roundRect, { x: x + bw / 2 - 0.32, y: by + 0.32, w: 0.64, h: 0.64, rectRadius: 0.32,
      fill: { color: C.accent }, line: { type: "none" } });
    s.addText(String(i + 1), { x: x + bw / 2 - 0.32, y: by + 0.32, w: 0.64, h: 0.64, align: "center",
      fontFace: FH, fontSize: 24, bold: true, color: "FFFFFF", margin: 0 });
    s.addText(st[0], { x, y: by + 1.15, w: bw, h: 0.45, align: "center",
      fontFace: FH, fontSize: 18, bold: true, color: C.txt, margin: 0 });
    s.addText(st[1], { x: x + 0.18, y: by + 1.62, w: bw - 0.36, h: 1.25, align: "center",
      fontFace: FB, fontSize: 12, color: C.muted, margin: 0 });
    if (i < n - 1)
      s.addText("›", { x: x + bw - 0.02, y: by + 1.0, w: gap, h: 0.6, align: "center",
        fontFace: FB, fontSize: 26, bold: true, color: C.accent, margin: 0 });
  });
  card(s, 0.6, 5.75, 12.13, 0.95, C.card2);
  s.addText([
    { text: "Deliverables:  ", options: { bold: true, color: C.gold } },
    { text: "reproducible pipeline (Python)  ·  executed notebook  ·  trained model  ·  interactive web demo", options: { color: C.soft } },
  ], { x: 0.9, y: 5.75, w: 11.6, h: 0.95, valign: "middle", fontFace: FB, fontSize: 14, margin: 0 });
  s.addNotes("The solution is a full pipeline: adapt the data, handle imbalance and train several models, evaluate on a future test set, explain predictions with SHAP, and turn weekly scores into concrete retention actions.");
}

// ---------- 6. DATASET ----------
{
  const s = slide();
  head(s, "Dataset", "Real public data, adapted to a SaaS scenario");
  const bullets = [
    [{ text: "Base: ", options: { bold: true, color: C.txt } }, { text: "Kaggle Telco Customer Churn — 7,043 real, labelled customers.", options: { color: C.soft } }],
    [{ text: "Adapted: ", options: { bold: true, color: C.txt } }, { text: "columns reinterpreted (tenure → months subscribed, contract → plan).", options: { color: C.soft } }],
    [{ text: "Engagement: ", options: { bold: true, color: C.txt } }, { text: "5 behavioural features (logins, features used, tickets, recency, usage trend).", options: { color: C.soft } }],
    [{ text: "Realism: ", options: { bold: true, color: C.txt } }, { text: "churn downsampled to 5% → final 5,446 customers, ~25 features.", options: { color: C.soft } }],
  ];
  const bx = 0.6, bw = 5.7, by = 2.1;
  bullets.forEach((b, i) => {
    const y = by + i * 1.02;
    s.addShape(p.ShapeType.roundRect, { x: bx, y: y + 0.06, w: 0.16, h: 0.16, rectRadius: 0.08,
      fill: { color: C.accent }, line: { type: "none" } });
    s.addText(b, { x: bx + 0.35, y: y - 0.12, w: bw - 0.35, h: 0.95, fontFace: FB, fontSize: 14.5, margin: 0 });
  });
  s.addText([
    { text: "Honest note:  ", options: { bold: true, color: C.gold } },
    { text: "engagement features are synthetic but literature-grounded; production would use real telemetry (see feature notes in the repo).", options: { color: C.muted, italic: true } },
  ], { x: bx, y: 6.15, w: bw, h: 0.9, fontFace: FB, fontSize: 12.5, margin: 0 });

  card(s, 6.65, 2.05, 6.08, 4.7, "FFFFFF");
  fitImg(s, "outputs/eda/engagement_by_churn.png", 6.85, 2.25, 5.68, 4.3);
  s.addNotes("We start from the real Kaggle Telco dataset and adapt it to a subscription scenario, adding five engagement features the literature flags as the strongest churn signals, then downsample to a realistic 5% churn. The chart shows churners and non-churners separate on these behaviours.");
}

// ---------- 7. MODELING & RESULTS ----------
{
  const s = slide();
  head(s, "Modeling & results", "Meets the targets: AUC ≈ 0.93, churner recall ≈ 0.84");
  // metrics table
  const tx = 0.6, tw = 5.2, ty = 2.05;
  const rows = [
    ["Model", "F2", "AUC", "Recall"],
    ["Logistic Reg.", "0.56", "0.94", "0.87"],
    ["Random Forest ★", "0.58", "0.93", "0.84"],
    ["XGBoost", "0.53", "0.93", "0.78"],
  ];
  const rh = 0.62;
  rows.forEach((r, i) => {
    const y = ty + i * rh;
    const best = i === 2;
    s.addShape(p.ShapeType.roundRect, { x: tx, y, w: tw, h: rh - 0.06, rectRadius: 0.06,
      fill: { color: i === 0 ? C.accent : best ? C.card : C.card2, transparency: i === 0 ? 20 : 0 },
      line: { color: best ? C.accent : C.line, width: best ? 1.5 : 1 } });
    const cols = [0, 2.2, 3.2, 4.1], cw = [2.2, 1.0, 0.9, 1.1];
    r.forEach((cell, j) => {
      s.addText(cell, { x: tx + cols[j] + 0.15, y, w: cw[j], h: rh - 0.06, valign: "middle",
        align: j === 0 ? "left" : "center", fontFace: j === 0 ? FB : FH,
        fontSize: i === 0 ? 13 : 14, bold: i === 0 || best,
        color: i === 0 ? C.txt : best ? C.accent : C.soft, margin: 0 });
    });
  });
  s.addText([
    { text: "F2 is the primary metric (recall-weighted). ", options: { color: C.soft } },
    { text: "Low precision (~0.26) is expected at a 5% base rate with a recall-first threshold.", options: { color: C.muted, italic: true } },
  ], { x: tx, y: ty + 4 * rh + 0.15, w: tw, h: 1.2, fontFace: FB, fontSize: 12.5, margin: 0 });

  card(s, 6.05, 2.0, 3.3, 4.75, "FFFFFF");
  fitImg(s, "outputs/figures/pr_curves.png", 6.2, 2.15, 3.0, 4.45);
  card(s, 9.45, 2.0, 3.28, 4.75, "FFFFFF");
  fitImg(s, "outputs/figures/confusion_matrix.png", 9.6, 2.15, 2.98, 4.45);
  s.addNotes("Three models trained. Random Forest is the best by F2. It hits the proposal targets — AUC around 0.93 and churner recall around 0.84. Precision is low, which is normal at a 5% base rate when we deliberately favour recall; the PR curve and confusion matrix show the trade-off.");
}

// ---------- 8. SHAP ----------
{
  const s = slide();
  head(s, "Interpretability", "SHAP tells the team why a customer is at risk");
  card(s, 0.6, 2.05, 6.5, 4.7, "FFFFFF");
  fitImg(s, "outputs/figures/shap_summary.png", 0.75, 2.2, 6.2, 4.4);
  const notes = [
    ["Actionable, not a black box", "Every score comes with the features that drove it."],
    ["Top drivers match the domain", "Plan type, tenure, usage trend, logins and recency."],
    ["Personalised interventions", "The success team tailors the offer to the actual reason."],
  ];
  const nx = 7.35, nw = 5.4, ny = 2.2;
  notes.forEach((it, i) => {
    const y = ny + i * 1.5;
    card(s, nx, y, nw, 1.35, C.card);
    s.addText(it[0], { x: nx + 0.3, y: y + 0.2, w: nw - 0.6, h: 0.4,
      fontFace: FH, fontSize: 16, bold: true, color: C.accent, margin: 0 });
    s.addText(it[1], { x: nx + 0.3, y: y + 0.62, w: nw - 0.6, h: 0.6,
      fontFace: FB, fontSize: 13, color: C.soft, margin: 0 });
  });
  s.addNotes("Interpretability is non-negotiable for a retention team. SHAP shows, per customer, which features push the risk up or down — and the top drivers line up with the domain, so interventions can be personalised.");
}

// ---------- 9. BUSINESS IMPACT ----------
{
  const s = slide();
  head(s, "Business impact & sensitivity", "The 20% target is derived, not assumed");
  card(s, 0.6, 2.05, 6.0, 1.55, C.card2);
  s.addText([
    { text: "churn reduction  =  recall × intervention success\n", options: { bold: true, color: C.txt, breakLine: true } },
    { text: "0.84 × 24%  ≈  20%", options: { color: C.green, bold: true } },
  ], { x: 0.9, y: 2.2, w: 5.4, h: 1.25, valign: "middle", fontFace: FH, fontSize: 18, margin: 0 });

  const stats = [["€22K", "net benefit · year 1", C.green], ["€42K", "net benefit · year 2+", C.green]];
  stats.forEach((st, i) => {
    const x = 0.6 + i * 3.05, w = 2.95;
    card(s, x, 3.8, w, 1.5, C.card);
    s.addText(st[0], { x, y: 3.95, w, h: 0.7, align: "center", fontFace: FH, fontSize: 34, bold: true, color: st[2], margin: 0 });
    s.addText(st[1], { x, y: 4.68, w, h: 0.4, align: "center", fontFace: FB, fontSize: 12.5, color: C.muted, margin: 0 });
  });
  card(s, 0.6, 5.45, 6.0, 1.3, C.card);
  s.addText([
    { text: "Sensitivity finding:  ", options: { bold: true, color: C.gold } },
    { text: "because precision is low, we contact ~1,600/mo to save 100. Even €5 outreach cost per contact flips ROI negative — so precision / top-N targeting is the key lever.", options: { color: C.soft } },
  ], { x: 0.9, y: 5.55, w: 5.4, h: 1.1, valign: "middle", fontFace: FB, fontSize: 12.5, margin: 0 });

  card(s, 6.75, 2.05, 5.98, 4.7, "FFFFFF");
  fitImg(s, "outputs/figures/sensitivity.png", 6.95, 2.25, 5.58, 4.3);
  s.addNotes("Addressing the reviewer feedback: instead of asserting 20%, we derive it — reduction equals recall times how often an intervention works. That gives the proposal's 22K first-year and 42K thereafter. The sensitivity analysis also exposes a real limitation: low precision means high outreach volume, so improving precision matters before scaling.");
}

// ---------- 10. LIVE DEMO ----------
{
  const s = slide();
  head(s, "Live demo", "Query the trained model in real time");
  card(s, 0.6, 2.05, 7.7, 4.7, "FFFFFF");
  fitImg(s, "presentation/assets/demo_high.png", 0.7, 2.15, 7.5, 4.5);

  const nx = 8.5, nw = 4.23;
  const steps = [
    ["Enter a customer", "Profile, subscription and 30-day engagement."],
    ["Model responds", "Churn probability + risk tier + suggested action."],
    ["See the why", "Top SHAP drivers behind the score."],
  ];
  steps.forEach((st, i) => {
    const y = 2.15 + i * 1.15;
    s.addShape(p.ShapeType.roundRect, { x: nx, y, w: 0.5, h: 0.5, rectRadius: 0.25,
      fill: { color: C.coral, transparency: 75 }, line: { type: "none" } });
    s.addText(String(i + 1), { x: nx, y, w: 0.5, h: 0.5, align: "center", fontFace: FH, fontSize: 18, bold: true, color: C.coral, margin: 0 });
    s.addText(st[0], { x: nx + 0.7, y: y - 0.05, w: nw - 0.7, h: 0.4, fontFace: FH, fontSize: 16, bold: true, color: C.txt, margin: 0 });
    s.addText(st[1], { x: nx + 0.7, y: y + 0.33, w: nw - 0.7, h: 0.7, fontFace: FB, fontSize: 12.5, color: C.muted, margin: 0 });
  });
  card(s, nx, 5.7, nw, 1.05, C.card2);
  s.addText([
    { text: "Run it locally\n", options: { bold: true, color: C.accent, breakLine: true } },
    { text: "python app.py  →  localhost:5000", options: { color: C.soft, fontFace: "Consolas" } },
  ], { x: nx + 0.25, y: 5.72, w: nw - 0.5, h: 1.0, valign: "middle", fontFace: FB, fontSize: 13, margin: 0 });
  s.addNotes("Now the live demo. This is the actual trained model served by a small Flask app. I load an at-risk customer, the model returns 94.9% churn, high risk, the suggested action, and the SHAP drivers behind it. Then I'll load a loyal customer to show a low-risk case.");
}

// ---------- 11. CONCLUSION ----------
{
  const s = slide();
  s.addShape(p.ShapeType.roundRect, { x: 8.8, y: -1.6, w: 6, h: 6, rectRadius: 3,
    fill: { color: C.accent, transparency: 88 }, line: { type: "none" } });
  s.addText("CONCLUSION", { x: 0.9, y: 0.85, w: 8, h: 0.35,
    fontFace: FB, fontSize: 14, bold: true, color: C.accent, charSpacing: 2, margin: 0 });
  s.addText("Technically sound and financially attractive", { x: 0.9, y: 1.25, w: 11.5, h: 0.9,
    fontFace: FH, fontSize: 30, bold: true, color: C.txt, margin: 0 });

  const cols = [
    ["What works", [
      "Meets targets: AUC ≈ 0.93, recall ≈ 0.84",
      "Explainable (SHAP) and production-shaped",
      "Derived, transparent ROI + sensitivity",
    ], C.green],
    ["Next steps", [
      "Pilot on 1,000 customers",
      "A/B test retention interventions",
      "Improve precision; cloud batch scoring",
    ], C.gold],
  ];
  cols.forEach((col, i) => {
    const x = 0.6 + i * 6.1, w = 5.9;
    card(s, x, 2.4, w, 3.0);
    s.addText(col[0], { x: x + 0.35, y: 2.62, w: w - 0.7, h: 0.45, fontFace: FH, fontSize: 19, bold: true, color: col[2], margin: 0 });
    col[1].forEach((t, j) => {
      const y = 3.2 + j * 0.66;
      s.addShape(p.ShapeType.roundRect, { x: x + 0.35, y: y + 0.07, w: 0.15, h: 0.15, rectRadius: 0.07, fill: { color: col[2] }, line: { type: "none" } });
      s.addText(t, { x: x + 0.62, y: y - 0.08, w: w - 1.0, h: 0.6, fontFace: FB, fontSize: 14, color: C.soft, margin: 0 });
    });
  });
  card(s, 0.6, 5.65, 12.13, 1.05, C.card2);
  s.addText([
    { text: "Source code:  ", options: { bold: true, color: C.accent } },
    { text: "github.com/maydamv/customer-churn-prediction", options: { color: C.txt, fontFace: "Consolas" } },
    { text: "        Thank you — questions welcome.", options: { color: C.muted, italic: true } },
  ], { x: 0.9, y: 5.65, w: 11.6, h: 1.05, valign: "middle", fontFace: FB, fontSize: 15, margin: 0 });
  s.addNotes("To wrap up: the project meets its technical targets, is explainable and production-shaped, and has a transparent, stress-tested ROI. Next steps are a pilot, A/B testing the interventions, and improving precision before scaling. Code is on GitHub. Thank you.");
}

p.writeFile({ fileName: "presentation/Churn_Prediction_Final_Presentation.pptx" })
  .then(f => console.log("wrote", f));
