const API_BASE = "http://127.0.0.1:8000/api/v1";
const URLS = {
  dashboard: `${API_BASE}/dashboard`,
  prediction: `${API_BASE}/predictions/latest`,
  predictionLayer: `${API_BASE}/map/predictions`,
  analytics: `${API_BASE}/map/analytics`,
  runScenario: `${API_BASE}/scenarios/run`,
  platformStatus: `${API_BASE}/admin/platform-status`,
  sourcePolicy: `${API_BASE}/admin/source-policy`,
  segmentationOverview: `${API_BASE}/admin/segmentation-overview`,
  dataSources: `${API_BASE}/data-sources`,
  fallbackDashboard: "./mock/dashboard.json",
};

const NO_COMPARE = "__none__";

const I18N = {
  en: {
    documentTitle: "Spatio-Eco Platform",
    brandEyebrow: "Spatio-Eco Platform",
    navOverview: "Overview",
    navModels: "Models",
    navOperations: "Operations",
    navResearch: "Research",
    backendHealthLink: "Backend Health",
    modelApiLink: "Model API",
    opsApiLink: "Operations API",
    architectureApiLink: "Architecture API",
    overviewHeroEyebrow: "Operational Workspace",
    overviewHeroTitle: "Regional carbon sink operations cockpit",
    overviewHeroDescription:
      "Use the active quarterly model, source switch, and live scenario controls to monitor what the platform can already deliver on this laptop.",
    overviewIntroTag: "Mission Board",
    overviewIntroTitle: "Operate around one clear question",
    overviewIntroText:
      "Which model is currently leading, which Sentinel-2 source is active, and how does a policy intervention alter the forecasted carbon sink pattern?",
    modelsHeroEyebrow: "Model Lab",
    modelsHeroTitle: "Benchmark, compare, and defend the current model stack",
    modelsHeroDescription:
      "Keep the model discussion focused on measurable differences: RMSE, MAE, horizon-specific behavior, and scenario response.",
    modelsIntroTag: "Evaluation Spine",
    modelsIntroTitle: "Keep one lab view for both development and review",
    modelsIntroText:
      "This page should answer which model is leading, why it leads, how stable the gain is, and where the graph model still fails to outperform the baseline.",
    operationsHeroEyebrow: "Operations Center",
    operationsHeroTitle: "Run the local platform with clear boundaries",
    operationsHeroDescription:
      "Track source switching, remote segmentation readiness, service health, and team ownership without mixing operational status with model evaluation.",
    operationsIntroTag: "Operational Scope",
    operationsIntroTitle: "Separate what is local, what is remote, and what is still scaffolded",
    operationsIntroText:
      "The platform is already usable on this laptop, but real SAM-2 segmentation remains a remote-GPU task. This page keeps that boundary explicit.",
    researchHeroEyebrow: "Research Desk",
    researchHeroTitle: "Document the methodology, boundary, and evidence chain",
    researchHeroDescription:
      "Keep the project readable for competition review, code handoff, and later migration to a remote GPU workflow.",
    researchIntroTag: "Research Context",
    researchIntroTitle: "Make the prototype legible as a scientific system",
    researchIntroText:
      "Explain the study area, data lineage, architecture, member scope, and next validation steps with enough rigor to support reporting and review.",
    platformPhaseLabel: "Platform Phase",
    forecastDeckTag: "Forecast Deck",
    forecastWorkspaceTitle: "Spatial forecast workspace",
    missionBriefTag: "Mission Brief",
    missionBriefTitle: "Current operating picture",
    scenarioLabTag: "Scenario Lab",
    hotspotQueueTag: "Hotspot Queue",
    sourcePolicyTag: "Source Policy",
    sentinel2SwitchTitle: "Sentinel-2 source governance",
    segmentationTrackTag: "Segmentation Track",
    sam2StatusTitle: "Remote SAM-2 readiness",
    platformStatusTag: "Platform Status",
    platformOverviewTitle: "Execution status and next actions",
    forecastSummaryTag: "Forecast Summary",
    forecastBreakdownTitle: "Forecast horizon breakdown",
    labControlsTag: "Lab Controls",
    labControlsTitle: "Select the active benchmark view",
    modelRegistryTag: "Model Registry",
    modelMetricsTitle: "Current model artifacts",
    benchmarkDeckTag: "Benchmark Deck",
    benchmarkDeckTitle: "Winner, runner-up, and baseline gap",
    gapAnalysisTag: "Gap Analysis",
    gapAnalysisTitle: "Where the graph model gains or loses",
    scenarioResponseTag: "Scenario Response",
    scenarioResponseTitle: "Reference scenario sensitivity",
    commandBoardTag: "Command Board",
    commandBoardTitle: "Current execution state",
    dataInventoryTag: "Data Inventory",
    dataInventoryTitle: "Tracked sources and readiness",
    servicesTag: "Services",
    architectureLayersTitle: "Service boundaries and next fill",
    membersTag: "Members",
    teamStatusTitle: "Delivery ownership and remaining work",
    studyDesignTag: "Study Design",
    studyDesignTitle: "Study area and training target",
    documentsTag: "Documents",
    projectReferencesTitle: "Key references and implementation notes",
    methodologyTag: "Methodology",
    methodologyTitle: "Dataset lineage and scientific guardrails",
    roadmapTag: "Roadmap",
    nextStepsTitle: "Immediate next milestones",
    businessHotspotsTitle: "Priority hotspot watchlist",
    liveScenarioTitle: "Live scenario simulation",
  },
  zh: {
    documentTitle: "Spatio-Eco 平台",
    brandEyebrow: "Spatio-Eco 平台",
    navOverview: "总览",
    navModels: "模型",
    navOperations: "运维",
    navResearch: "科研",
    backendHealthLink: "后端健康检查",
    modelApiLink: "模型接口",
    opsApiLink: "运维接口",
    architectureApiLink: "架构接口",
    overviewHeroEyebrow: "业务驾驶舱",
    overviewHeroTitle: "区域碳汇监测与预测总览台",
    overviewHeroDescription: "围绕当前季度模型、数据源切换和情景推演，查看本机已经能稳定交付的内容。",
    overviewIntroTag: "任务焦点",
    overviewIntroTitle: "围绕一个明确问题组织总览页",
    overviewIntroText: "当前哪个模型领先、正在使用哪套 Sentinel-2 特征源、一次政策干预将如何改变预测格局。",
    modelsHeroEyebrow: "模型实验室",
    modelsHeroTitle: "用可度量指标解释当前模型体系",
    modelsHeroDescription: "把讨论聚焦到 RMSE、MAE、预测步长表现和情景响应，而不是停留在模型名称本身。",
    modelsIntroTag: "评估主线",
    modelsIntroTitle: "让开发视图和答辩视图使用同一套模型叙事",
    modelsIntroText: "这一页回答谁领先、为什么领先、优势是否稳定，以及图模型在哪些地方仍未显著优于基线。",
    operationsHeroEyebrow: "运维中心",
    operationsHeroTitle: "把本地能力、远程能力和预留能力分清楚",
    operationsHeroDescription: "统一查看数据源切换、远程分割状态、服务健康度和成员边界，但不与模型评价混在一起。",
    operationsIntroTag: "运行边界",
    operationsIntroTitle: "明确哪些在本地运行，哪些必须远程执行，哪些仍是骨架",
    operationsIntroText: "本地平台已经可用，但真实 SAM-2 仍然是远程 GPU 任务，这一页专门把这条边界讲清楚。",
    researchHeroEyebrow: "科研台账",
    researchHeroTitle: "把方法、边界和证据链整理成可复核的系统",
    researchHeroDescription: "这一页用于支撑比赛汇报、代码移交以及后续迁移到远程 GPU 的工程说明。",
    researchIntroTag: "科研语境",
    researchIntroTitle: "让当前原型具备科研叙述上的完整性",
    researchIntroText: "清楚解释研究区、数据血缘、系统结构、成员职责和下一步验证路径。",
    platformPhaseLabel: "平台阶段",
    forecastDeckTag: "预测工作区",
    forecastWorkspaceTitle: "空间预测工作台",
    missionBriefTag: "任务摘要",
    missionBriefTitle: "当前运行态势",
    scenarioLabTag: "情景实验",
    hotspotQueueTag: "热点清单",
    sourcePolicyTag: "数据源策略",
    sentinel2SwitchTitle: "Sentinel-2 特征源治理",
    segmentationTrackTag: "分割链路",
    sam2StatusTitle: "远程 SAM-2 就绪情况",
    platformStatusTag: "平台状态",
    platformOverviewTitle: "执行状态与下一步动作",
    forecastSummaryTag: "预测摘要",
    forecastBreakdownTitle: "分步长预测概览",
    labControlsTag: "实验控制",
    labControlsTitle: "选择当前对比视图",
    modelRegistryTag: "模型注册表",
    modelMetricsTitle: "当前模型制品",
    benchmarkDeckTag: "对比面板",
    benchmarkDeckTitle: "领先者、追赶者与基线差距",
    gapAnalysisTag: "差异分析",
    gapAnalysisTitle: "图模型在哪里真正赢，哪里还没赢",
    scenarioResponseTag: "情景响应",
    scenarioResponseTitle: "参考情景敏感性",
    commandBoardTag: "指挥面板",
    commandBoardTitle: "当前执行状态",
    dataInventoryTag: "数据盘点",
    dataInventoryTitle: "已跟踪数据源与就绪度",
    servicesTag: "服务层",
    architectureLayersTitle: "服务边界与待补内容",
    membersTag: "成员分工",
    teamStatusTitle: "责任边界与剩余工作",
    studyDesignTag: "研究设计",
    studyDesignTitle: "研究区与训练目标",
    documentsTag: "文档",
    projectReferencesTitle: "关键参考与实现说明",
    methodologyTag: "方法说明",
    methodologyTitle: "数据血缘与科研约束",
    roadmapTag: "路线图",
    nextStepsTitle: "近期里程碑",
    businessHotspotsTitle: "优先热点观察清单",
    liveScenarioTitle: "在线情景推演",
  },
};

Object.assign(I18N.en, {
  modelLabel: "Model",
  compareLabel: "Compare",
  horizonLabel: "Horizon",
  presetLabel: "Preset",
  nodeIdsLabel: "Node IDs",
  intensityLabel: "Intensity",
  hopsLabel: "Hops",
  attenuationLabel: "Attenuation",
  temporalModeLabel: "Temporal Mode",
  forecastButton: "Forecast",
  hotspotsButton: "Hotspots",
  modelGapButton: "Model Gap",
  scenarioDeltaButton: "Scenario Delta",
  resetButton: "Reset",
  runScenarioButton: "Run scenario",
  mapFallback: "Cesium is unavailable in the current browser session. The rest of the platform remains usable.",
  presetIndustrialExpansion: "Industrial expansion",
  presetGreeningRestoration: "Greening restoration",
  temporalLinear: "Linear",
  temporalUniform: "Uniform",
  temporalLast: "Last-step boost",
  studyArea: "Study area",
  timeRange: "Time range",
  targetName: "Target",
  activeSource: "Active source",
  sourceMode: "Source mode",
  modelLeader: "Model leader",
  bestRmse: "Best RMSE",
  bestMae: "Best MAE",
  trackedNodes: "Tracked nodes",
  remoteJobs: "Remote jobs",
  completion: "Completion",
  nextAction: "Next action",
  noCompare: "No compare",
  policyMode: "Policy mode",
  effectiveSource: "Effective source",
  effectiveReason: "Effective reason",
  rows: "Rows",
  owner: "Owner",
  status: "Status",
  horizon: "Horizon",
  bestValLoss: "Best val loss",
  min: "Min",
  max: "Max",
  mean: "Mean",
  count: "Count",
  cells: "Cells",
  active: "Active",
  scaffolded: "Scaffolded",
  pendingFill: "Pending fill",
  remoteOnly: "Remote only",
  ready: "Ready",
  waiting: "Waiting",
  available: "Available",
  unavailable: "Unavailable",
  yes: "Yes",
  no: "No",
  critical: "Critical",
  high: "High",
  elevated: "Elevated",
  stable: "Stable",
  auto: "Auto",
  manual: "Manual",
  autoFallback: "Auto fallback",
  quarterlyProxy: "Quarterly proxy",
  sam2Remote: "SAM-2 remote",
  switchToAuto: "Switch to auto",
  preferQuarterlyProxy: "Prefer quarterly proxy",
  preferSam2Remote: "Prefer SAM-2 remote",
  liveApiMode: "Live API mode",
  fallbackMode: "Fallback mode",
  selectedHorizon: "Selected horizon",
  topHotspots: "Top hotspots",
  positiveGap: "Positive gap",
  negativeGap: "Negative gap",
  changedNodes: "Changed nodes",
  deltaMean: "Delta mean",
  deltaMax: "Delta max",
  running: "Running...",
  scenarioUnavailable: "Scenario API is unavailable in fallback mode.",
  updateFailed: "Source policy update failed.",
  scenarioFailed: "Scenario run failed.",
  methodologyNoteOne: "Quarterly prototype focused on integration and method validation.",
  methodologyNoteTwo: "Sentinel-2 will switch from proxy features to remote SAM-2 outputs.",
  methodologyNoteThree: "ERA5, EDGAR, and QC-filtered GPP labels already feed the current model.",
  methodologyNoteFour: "Real SAM-2 stays remote because this laptop is not suited for stable batch segmentation.",
});

Object.assign(I18N.zh, {
  modelLabel: "模型",
  compareLabel: "对比模型",
  horizonLabel: "预测步长",
  presetLabel: "预设情景",
  nodeIdsLabel: "节点 ID",
  intensityLabel: "强度",
  hopsLabel: "传播跳数",
  attenuationLabel: "衰减系数",
  temporalModeLabel: "时间传播模式",
  forecastButton: "预测值",
  hotspotsButton: "热点等级",
  modelGapButton: "模型差值",
  scenarioDeltaButton: "情景增量",
  resetButton: "重置",
  runScenarioButton: "运行情景",
  mapFallback: "当前浏览器会话无法加载 Cesium，平台其余功能仍可正常使用。",
  presetIndustrialExpansion: "工业扩张",
  presetGreeningRestoration: "生态修复",
  temporalLinear: "线性扩散",
  temporalUniform: "均匀扩散",
  temporalLast: "末步增强",
  studyArea: "研究区",
  timeRange: "时间范围",
  targetName: "目标变量",
  activeSource: "当前特征源",
  sourceMode: "数据源模式",
  modelLeader: "当前领先模型",
  bestRmse: "最佳 RMSE",
  bestMae: "最佳 MAE",
  trackedNodes: "网格节点数",
  remoteJobs: "远程任务数",
  completion: "完成率",
  nextAction: "下一步动作",
  noCompare: "不对比",
  policyMode: "策略模式",
  effectiveSource: "实际生效源",
  effectiveReason: "生效原因",
  rows: "行数",
  owner: "负责人",
  status: "状态",
  horizon: "步长类型",
  bestValLoss: "最佳验证损失",
  min: "最小值",
  max: "最大值",
  mean: "均值",
  count: "数量",
  cells: "单元数",
  active: "运行中",
  scaffolded: "已搭骨架",
  pendingFill: "待补全",
  remoteOnly: "仅远程执行",
  ready: "已就绪",
  waiting: "待完成",
  available: "可用",
  unavailable: "不可用",
  yes: "是",
  no: "否",
  critical: "极高",
  high: "高",
  elevated: "中",
  stable: "稳定",
  auto: "自动",
  manual: "手动",
  autoFallback: "自动回退",
  quarterlyProxy: "季度代理特征",
  sam2Remote: "远程 SAM-2 特征",
  switchToAuto: "切回自动策略",
  preferQuarterlyProxy: "优先季度代理",
  preferSam2Remote: "优先 SAM-2",
  liveApiMode: "在线接口模式",
  fallbackMode: "本地回退模式",
  selectedHorizon: "当前步长",
  topHotspots: "热点节点",
  positiveGap: "正向优势",
  negativeGap: "负向差距",
  changedNodes: "变化节点",
  deltaMean: "平均增量",
  deltaMax: "最大增量",
  running: "运行中...",
  scenarioUnavailable: "当前处于回退模式，无法调用在线情景接口。",
  updateFailed: "更新数据源策略失败。",
  scenarioFailed: "情景运行失败。",
  methodologyNoteOne: "当前季度版原型更偏向平台联调和方法验证。",
  methodologyNoteTwo: "Sentinel-2 将从代理特征切换到远程 SAM-2 输出。",
  methodologyNoteThree: "ERA5、EDGAR 和质量过滤后的 GPP 标签已经接入当前模型。",
  methodologyNoteFour: "真实 SAM-2 保持远程执行，因为这台笔记本不适合稳定批处理分割。",
});

const state = {
  page: document.body.dataset.page || "overview",
  language: (() => {
    const saved = window.localStorage.getItem("spatio_eco_lang");
    if (saved === "zh" || saved === "en") return saved;
    return String(navigator.language || "").toLowerCase().startsWith("zh") ? "zh" : "en";
  })(),
  apiAvailable: true,
  eventsBound: false,
  dashboard: null,
  platformStatus: null,
  sourcePolicy: null,
  segmentationOverview: null,
  predictionPayload: null,
  predictionLayer: null,
  analytics: null,
  deltaItems: [],
  scenarioSummary: null,
  scenarioName: null,
  viewer: null,
  mapMode: "forecast",
  selectedModel: null,
  compareModel: null,
  selectedHorizon: null,
};

const el = (id) => document.getElementById(id);
const has = (id) => Boolean(el(id));
const t = (key) => I18N[state.language]?.[key] || I18N.en[key] || key;
const locale = () => (state.language === "zh" ? "zh-CN" : "en-US");

function setHTML(id, html) {
  if (has(id)) el(id).innerHTML = html;
}

function esc(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function nice(value) {
  return String(value ?? "").replace(/_/g, " ");
}

function compact(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return "n/a";
  if (Math.abs(n) >= 1000) return n.toLocaleString(locale(), { maximumFractionDigits: 2 });
  if (Math.abs(n) >= 1) return n.toLocaleString(locale(), { maximumFractionDigits: 3 });
  if (Math.abs(n) >= 0.01) return n.toLocaleString(locale(), { maximumFractionDigits: 5 });
  return n.toExponential(2);
}

function percent(value) {
  const n = Number(value);
  return Number.isFinite(n) ? `${(n * 100).toFixed(1)}%` : "n/a";
}

function query(base, params) {
  const url = new URL(base, window.location.href);
  Object.entries(params || {}).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== "") {
      url.searchParams.set(key, String(value));
    }
  });
  return url.toString();
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, { cache: "no-store", ...options });
  if (!response.ok) throw new Error(`${url} -> ${response.status}`);
  return response.json();
}

async function loadDashboard() {
  try {
    return { payload: await fetchJson(URLS.dashboard), fallback: false };
  } catch {
    return { payload: await fetchJson(URLS.fallbackDashboard), fallback: true };
  }
}

async function loadOptional(url, fallback) {
  try {
    return await fetchJson(url);
  } catch {
    return fallback;
  }
}

function statusText(status) {
  const value = String(status || "").toLowerCase();
  if (value === "pending_fill") return t("pendingFill");
  if (value === "remote_only") return t("remoteOnly");
  if (value === "auto_fallback") return t("autoFallback");
  return t(value) || nice(status);
}

function statusTone(status) {
  const value = String(status || "").toLowerCase();
  if (["active", "ready", "available"].includes(value)) return "good";
  if (["critical"].includes(value)) return "risk";
  if (["scaffolded", "high", "elevated"].includes(value)) return "warn";
  return "muted";
}

function sourceName(key) {
  if (key === "quarterly_proxy") return t("quarterlyProxy");
  if (key === "sam2_remote") return t("sam2Remote");
  return nice(key);
}

function pill(text, tone = "neutral") {
  return `<span class="pill pill--${tone}">${esc(text)}</span>`;
}

function fact(label, value, detail = "", tone = "neutral") {
  return `<article class="fact-card fact-card--${tone}"><span>${esc(label)}</span><strong>${esc(value)}</strong>${detail ? `<p>${esc(detail)}</p>` : ""}</article>`;
}

function item({ eyebrow = "", title = "", meta = "", body = "", tone = "neutral", footer = "" }) {
  return `<article class="stack-item stack-item--${tone}">${eyebrow ? `<p class="item-eyebrow">${esc(eyebrow)}</p>` : ""}<div class="item-head"><h3>${esc(title)}</h3>${meta ? `<span class="item-meta">${esc(meta)}</span>` : ""}</div>${body ? `<p class="item-body">${esc(body)}</p>` : ""}${footer ? `<div class="item-footer">${footer}</div>` : ""}</article>`;
}

function metric(label, value, detail, tone = "teal") {
  return `<article class="metric-tile metric-tile--${tone}"><span>${esc(label)}</span><strong>${esc(value)}</strong><p>${esc(detail)}</p></article>`;
}

function summaryFromPayload(payload) {
  if (!payload) return null;
  const horizons = payload.predictions_by_horizon || (payload.predictions ? { [payload.prediction_timestamp_to || "latest"]: payload.predictions } : {});
  const byHorizon = {};
  Object.entries(horizons).forEach(([horizon, nodeMap]) => {
    const values = Object.values(nodeMap || {}).map(Number).filter(Number.isFinite);
    const mean = values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : 0;
    byHorizon[horizon] = {
      count: values.length,
      min: values.length ? Math.min(...values) : 0,
      max: values.length ? Math.max(...values) : 0,
      mean,
      top_nodes: Object.entries(nodeMap || {})
        .map(([nodeId, value]) => ({ node_id: nodeId, value: Number(value) }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 3),
    };
  });
  return { forecast_timestamps: payload.forecast_timestamps || Object.keys(byHorizon), by_horizon: byHorizon };
}

function renderStaticText() {
  document.documentElement.lang = state.language === "zh" ? "zh-CN" : "en";
  document.title = `${t("documentTitle")} | ${t({ overview: "navOverview", models: "navModels", operations: "navOperations", research: "navResearch" }[state.page])}`;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  el("lang-zh")?.classList.toggle("is-active", state.language === "zh");
  el("lang-en")?.classList.toggle("is-active", state.language === "en");
}

function renderHero() {
  if (!state.dashboard) return;
  const study = state.dashboard.project?.study_area || {};
  setHTML(
    "hero-meta",
    [
      `${t("studyArea")}: ${study.name || "n/a"}`,
      `${t("timeRange")}: ${(study.time_range || []).join(" to ")}`,
      `${t("targetName")}: ${nice(study.current_target || "")}`,
      `${t("activeSource")}: ${sourceName(state.dashboard.data_sources?.sentinel2_switch?.active_key)}`,
      state.apiAvailable ? t("liveApiMode") : t("fallbackMode"),
    ].map((value) => `<span class="hero-chip">${esc(value)}</span>`).join(""),
  );
  if (has("project-phase")) el("project-phase").textContent = state.dashboard.project?.phase || "Platform MVP";
  const leader = state.platformStatus?.model_summary || {};
  const segmentation = state.segmentationOverview || {};
  setHTML(
    "hero-stack",
    [
      { label: t("platformPhaseLabel"), value: state.dashboard.project?.phase || "Platform MVP" },
      { label: t("modelLeader"), value: leader.leader_name || "n/a" },
      { label: t("activeSource"), value: sourceName(state.dashboard.data_sources?.sentinel2_switch?.active_key) },
      { label: t("remoteJobs"), value: String(segmentation.job_count || 0) },
    ].map((row) => `<div class="hero-kv"><span>${esc(row.label)}</span><strong>${esc(row.value)}</strong></div>`).join(""),
  );
}

function renderMetrics() {
  if (!state.dashboard || !state.platformStatus) return;
  const study = state.dashboard.project?.study_area || {};
  const leader = state.platformStatus.model_summary || {};
  const segmentation = state.segmentationOverview || {};
  const hotspots = state.analytics?.summary?.top_hotspots || state.dashboard.business_preview?.summary?.top_hotspots || [];
  setHTML("metrics-strip", [
    metric(t("modelLeader"), leader.leader_name || "n/a", `${t("bestRmse")}: ${compact(leader.leader_rmse)}`, "teal"),
    metric(t("trackedNodes"), String(study.node_count || 0), `${t("timeRange")}: ${(study.time_range || []).join(" to ")}`, "ink"),
    metric(t("activeSource"), sourceName(state.dashboard.data_sources?.sentinel2_switch?.active_key), `${t("sourceMode")}: ${statusText(state.dashboard.data_sources?.sentinel2_switch?.effective_mode)}`, "burnt"),
    metric(t("topHotspots"), String(hotspots.length), `${t("completion")}: ${percent(segmentation.completion_rate || 0)}`, "olive"),
  ].join(""));
}

function renderOverviewStory() {
  if (!has("overview-story") || !state.platformStatus) return;
  const leader = state.platformStatus.model_summary || {};
  const segmentation = state.segmentationOverview || {};
  setHTML("overview-story", [
    fact(t("modelLeader"), leader.leader_name || "n/a", `${t("bestRmse")}: ${compact(leader.leader_rmse)}`, "good"),
    fact(t("activeSource"), sourceName(state.dashboard.data_sources?.sentinel2_switch?.active_key), `${t("policyMode")}: ${statusText(state.dashboard.data_sources?.sentinel2_switch?.effective_mode)}`, "warn"),
    fact(t("selectedHorizon"), state.selectedHorizon || state.analytics?.horizon || "n/a", `${t("compareLabel")}: ${(state.dashboard.models || []).find((model) => model.key === state.compareModel)?.name || t("noCompare")}`, "ink"),
    fact(t("nextAction"), segmentation.next_action || "n/a", `${t("rows")}: ${segmentation.sam2_feature_rows || 0}`, "muted"),
  ].join(""));
}

function renderSourcePolicy() {
  if (!state.sourcePolicy) return;
  const options = state.sourcePolicy.options || [];
  setHTML("source-policy-summary", `<div class="policy-summary-card"><div class="policy-meta-grid">${fact(t("policyMode"), statusText(state.sourcePolicy.policy?.mode || state.sourcePolicy.effective_mode), "", "good")}${fact(t("effectiveSource"), sourceName(state.sourcePolicy.active_key), "", "ink")}${fact(t("effectiveReason"), nice(state.sourcePolicy.effective_reason), "", "warn")}</div><div class="button-row"><button class="inline-button ${state.sourcePolicy.policy?.mode === "auto" ? "selected" : ""}" data-source-mode="auto">${esc(t("switchToAuto"))}</button><button class="inline-button ${state.sourcePolicy.policy?.preferred_source_key === "quarterly_proxy" ? "selected" : ""}" data-source-mode="manual" data-preferred-source="quarterly_proxy">${esc(t("preferQuarterlyProxy"))}</button><button class="inline-button ${state.sourcePolicy.policy?.preferred_source_key === "sam2_remote" ? "selected" : ""}" data-source-mode="manual" data-preferred-source="sam2_remote">${esc(t("preferSam2Remote"))}</button></div></div>`);
  setHTML("source-policy-grid", options.map((option) => item({
    eyebrow: `${t("rows")}: ${option.rows ?? 0}`,
    title: sourceName(option.key),
    meta: option.available ? t("available") : t("unavailable"),
    body: option.description || "",
    tone: option.key === state.sourcePolicy.active_key ? "good" : (option.available ? "warn" : "muted"),
    footer: `${pill(option.stage || "", "muted")} ${pill(`${t("rows")}: ${option.rows ?? 0}`, "neutral")}`,
  })).join(""));
}

function renderSegmentation() {
  if (!has("segmentation-status") || !state.segmentationOverview) return;
  const info = state.segmentationOverview;
  setHTML("segmentation-status", [
    item({ eyebrow: t("remoteJobs"), title: String(info.job_count || 0), meta: `${t("completion")}: ${percent(info.completion_rate || 0)}`, body: `${t("nextAction")}: ${info.next_action || "n/a"}`, tone: info.sam2_feature_ready ? "good" : "warn" }),
    item({ eyebrow: "Bundle", title: info.latest_bundle_dir ? info.latest_bundle_dir.split(/[\\/]/).pop() : "n/a", meta: `${t("rows")}: ${info.sam2_feature_rows || 0}`, body: info.sam2_feature_path || "", tone: info.latest_bundle_dir ? "ink" : "muted" }),
    item({ eyebrow: "CSV", title: info.sam2_feature_ready ? t("ready") : t("waiting"), meta: `${t("count")}: ${info.complete_scene_count || 0}`, body: info.import_summary_path || "", tone: info.sam2_feature_ready ? "good" : "muted" }),
  ].join(""));
}

function renderHotspots() {
  if (!has("hotspot-list")) return;
  const list = state.analytics?.summary?.top_hotspots || [];
  setHTML("hotspot-list", (list.length ? list.slice(0, 6) : [{ node_id: "n/a", value: 0 }]).map((row, index) => {
    const detail = (state.analytics?.items || []).find((item) => String(item.node_id) === String(row.node_id));
    return item({
      eyebrow: `#${index + 1}`,
      title: `Node ${row.node_id}`,
      meta: detail ? statusText(detail.risk_level) : t("stable"),
      body: `${t("targetName")}: ${compact(row.value)}`,
      tone: detail ? statusTone(detail.risk_level) : "muted",
    });
  }).join(""));
}

function renderManagement() {
  if (!has("management-grid") || !state.platformStatus) return;
  const info = state.platformStatus;
  const cards = [
    fact(t("servicesTag"), `${info.service_summary?.active || 0}/${info.service_summary?.total || 0}`, `${t("scaffolded")}: ${info.service_summary?.scaffolded || 0}`, "good"),
    fact(t("dataInventoryTag"), `${info.data_summary?.ready_data_count || 0}/${info.data_summary?.tracked_data_count || 0}`, `${t("effectiveSource")}: ${sourceName(info.data_summary?.active_sentinel2_source)}`, "ink"),
    fact(t("modelLeader"), info.model_summary?.leader_name || "n/a", `${t("bestMae")}: ${compact(info.model_summary?.leader_mae)}`, "warn"),
    fact("SAM-2", info.segmentation_summary?.sam2_feature_ready ? t("ready") : t("waiting"), `${t("completion")}: ${percent(info.segmentation_summary?.completion_rate || 0)}`, "muted"),
  ].join("");
  const notes = (info.recommendations || []).map((text) => `<li>${esc(text)}</li>`).join("");
  setHTML("management-grid", `<div class="story-grid">${cards}</div><div class="note-card"><ul class="compact-list">${notes}</ul></div>`);
}

function renderPredictionSummary() {
  if (!has("prediction-grid")) return;
  const summary = state.predictionPayload ? summaryFromPayload(state.predictionPayload) : state.dashboard?.prediction_preview;
  if (!summary) return;
  setHTML("prediction-grid", Object.entries(summary.by_horizon || {}).map(([horizon, data]) => item({
    eyebrow: horizon,
    title: `${t("count")}: ${data.count || 0}`,
    meta: `${t("mean")}: ${compact(data.mean)}`,
    body: `${t("min")}: ${compact(data.min)} | ${t("max")}: ${compact(data.max)}`,
    tone: horizon === (state.selectedHorizon || summary.forecast_timestamps?.[0]) ? "good" : "neutral",
    footer: (data.top_nodes || []).map((node) => pill(`Node ${node.node_id}: ${compact(node.value)}`, "muted")).join(""),
  })).join(""));
}

function renderModels() {
  if (!has("model-grid") || !state.dashboard) return;
  setHTML("model-grid", [...(state.dashboard.models || [])].sort((a, b) => Number(a.metrics?.rmse || 0) - Number(b.metrics?.rmse || 0)).map((model) => `
    <article class="model-card">
      <div class="item-head">
        <h3>${esc(model.name)}</h3>
        ${pill(statusText(model.stage), model.stage === "baseline" ? "muted" : "good")}
      </div>
      <div class="metric-row">
        ${pill(`${t("bestRmse")}: ${compact(model.metrics?.rmse)}`, "good")}
        ${pill(`${t("bestMae")}: ${compact(model.metrics?.mae)}`, "warn")}
        ${pill(`${t("horizon")}: ${nice(model.horizon)}`, "neutral")}
      </div>
      <p class="item-body">${esc(`${t("owner")}: ${model.owner} | ${t("bestValLoss")}: ${compact(model.best_val_loss)}`)}</p>
    </article>
  `).join(""));
}

function renderModelLabSummary() {
  if (!has("model-lab-summary") || !state.platformStatus) return;
  const leader = state.platformStatus.model_summary || {};
  const selected = (state.dashboard.models || []).find((model) => model.key === state.selectedModel);
  const compare = (state.dashboard.models || []).find((model) => model.key === state.compareModel);
  setHTML("model-lab-summary", [
    fact(t("modelLeader"), leader.leader_name || "n/a", `${t("bestRmse")}: ${compact(leader.leader_rmse)}`, "good"),
    fact(t("modelLabel"), selected?.name || "n/a", `${t("selectedHorizon")}: ${state.selectedHorizon || "n/a"}`, "ink"),
    fact(t("compareLabel"), compare?.name || t("noCompare"), compare ? `${t("bestRmse")}: ${compact(compare.metrics?.rmse)}` : "", "warn"),
    fact(t("topHotspots"), String(state.analytics?.summary?.top_hotspots?.length || 0), "", "muted"),
  ].join(""));
}

function renderBenchmark() {
  if (!has("benchmark-grid") || !state.dashboard) return;
  const models = [...(state.dashboard.models || [])].sort((a, b) => Number(a.metrics?.rmse || 0) - Number(b.metrics?.rmse || 0));
  const leader = models[0];
  const runnerUp = models[1];
  const baseline = models.find((model) => model.stage === "baseline");
  const cards = [];
  if (leader) cards.push(fact(t("modelLeader"), leader.name, `${t("bestRmse")}: ${compact(leader.metrics?.rmse)} | ${t("bestMae")}: ${compact(leader.metrics?.mae)}`, "good"));
  if (runnerUp) cards.push(fact("Runner-up", runnerUp.name, `ΔRMSE: ${compact(Number(runnerUp.metrics?.rmse || 0) - Number(leader.metrics?.rmse || 0))}`, "warn"));
  if (baseline) cards.push(fact("Baseline", baseline.name, `ΔRMSE: ${compact(Number(baseline.metrics?.rmse || 0) - Number(leader.metrics?.rmse || 0))}`, "muted"));
  setHTML("benchmark-grid", cards.join(""));
}

function renderGapAnalysis() {
  if (!has("gap-analysis")) return;
  const summary = state.analytics?.summary;
  if (!summary) return;
  const categories = Object.entries(summary.category_counts || {}).map(([key, value]) => pill(`${statusText(key)}: ${value}`, statusTone(key))).join("");
  const positive = (summary.top_positive_gap || []).slice(0, 3).map((row) => pill(`Node ${row.node_id}: ${compact(row.value)}`, "good")).join("");
  const negative = (summary.top_negative_gap || []).slice(0, 3).map((row) => pill(`Node ${row.node_id}: ${compact(row.value)}`, "risk")).join("");
  setHTML("gap-analysis", [
    item({ eyebrow: t("topHotspots"), title: t("positiveGap"), meta: state.analytics?.compare_model_name || t("noCompare"), body: `${t("selectedHorizon")}: ${state.analytics?.horizon || "n/a"}`, tone: "neutral", footer: categories }),
    item({ eyebrow: t("positiveGap"), title: state.analytics?.compare_model_name || t("noCompare"), body: "Nodes where the active model is higher than the comparison model.", tone: "good", footer: positive || pill(t("noCompare"), "muted") }),
    item({ eyebrow: t("negativeGap"), title: state.analytics?.compare_model_name || t("noCompare"), body: "Nodes where the active model is lower than the comparison model.", tone: "risk", footer: negative || pill(t("noCompare"), "muted") }),
  ].join(""));
}

function renderScenario(target = "scenario-panel") {
  if (!has(target)) return;
  const summary = state.scenarioSummary || state.dashboard?.scenario_preview?.summary;
  if (!summary) return;
  setHTML(target, item({
    eyebrow: state.scenarioName || state.dashboard?.scenario_preview?.name || "Scenario",
    title: `${t("changedNodes")}: ${(summary.changed_nodes || []).join(", ") || "n/a"}`,
    meta: `${t("selectedHorizon")}: ${summary.forecast_horizon || "n/a"}`,
    body: `${t("deltaMean")}: ${compact(summary.delta_summary?.mean)} | ${t("deltaMax")}: ${compact(summary.delta_summary?.max)}`,
    tone: "warn",
    footer: (summary.top_impacts || []).slice(0, 4).map((row) => pill(`Node ${row.node_id}: ${compact(row.value)}`, "warn")).join(""),
  }));
}

function renderDataRegistry() {
  if (!has("data-registry") || !state.dashboard) return;
  setHTML("data-registry", (state.dashboard.data_sources?.items || []).map((entry) => item({
    eyebrow: entry.key,
    title: entry.name,
    meta: entry.key === "sentinel2" ? `${t("effectiveSource")}: ${sourceName(state.dashboard.data_sources?.sentinel2_switch?.active_key)}` : `${t("rows")}: ${entry.rows ?? 0}`,
    body: entry.description || "",
    tone: entry.key === "sentinel2" || entry.exists ? "good" : "muted",
    footer: (entry.required_for || []).map((value) => pill(value, "muted")).join(""),
  })).join(""));
}

function renderArchitecture() {
  if (!has("architecture-grid") || !state.dashboard) return;
  setHTML("architecture-grid", (state.dashboard.architecture || []).map((entry) => item({
    eyebrow: entry.service,
    title: entry.layer,
    meta: statusText(entry.status),
    body: `${entry.current_scope} ${entry.next_fill}`,
    tone: statusTone(entry.status),
    footer: pill(`${t("owner")}: ${entry.owner}`, "muted"),
  })).join(""));
}

function renderMembers() {
  if (!has("member-grid") || !state.dashboard) return;
  setHTML("member-grid", (state.dashboard.members || []).map((member) => `
    <article class="stack-item stack-item--${statusTone(member.status)}">
      <p class="item-eyebrow">${esc(member.member)}</p>
      <div class="item-head">
        <h3>${esc(member.role)}</h3>
        <span class="item-meta">${esc(statusText(member.status))}</span>
      </div>
      <div class="two-list">
        <div><p class="mini-label">Done</p><ul class="compact-list">${(member.completed || []).map((text) => `<li>${esc(text)}</li>`).join("")}</ul></div>
        <div><p class="mini-label">Next</p><ul class="compact-list">${(member.remaining || []).map((text) => `<li>${esc(text)}</li>`).join("")}</ul></div>
      </div>
    </article>
  `).join(""));
}

function renderStudyBrief() {
  if (!has("study-brief") || !state.dashboard) return;
  const study = state.dashboard.project?.study_area || {};
  setHTML("study-brief", [
    fact(t("studyArea"), study.name || "n/a", `${t("trackedNodes")}: ${study.node_count || 0}`, "good"),
    fact(t("timeRange"), (study.time_range || []).join(" to "), nice(study.time_granularity || ""), "ink"),
    fact(t("targetName"), nice(study.current_target || ""), study.status || "", "warn"),
    fact(t("activeSource"), sourceName(state.dashboard.data_sources?.sentinel2_switch?.active_key), `${t("policyMode")}: ${statusText(state.dashboard.data_sources?.sentinel2_switch?.effective_mode)}`, "muted"),
  ].join(""));
}

function renderDocs() {
  if (!has("docs-grid") || !state.dashboard) return;
  setHTML("docs-grid", (state.dashboard.docs || []).map((doc) => item({
    eyebrow: doc.group || "",
    title: doc.title || "",
    meta: doc.path || "",
    body: "Public repository readable. Use README and docs as the main entry points.",
    tone: "neutral",
  })).join(""));
}

function renderMethodology() {
  if (!has("method-grid")) return;
  setHTML("method-grid", [
    t("methodologyNoteOne"),
    t("methodologyNoteTwo"),
    t("methodologyNoteThree"),
    t("methodologyNoteFour"),
  ].map((text, index) => item({ eyebrow: `0${index + 1}`, title: text, tone: index === 0 ? "good" : "muted" })).join(""));
}

function renderRoadmap() {
  if (!has("roadmap-list") || !state.dashboard) return;
  setHTML("roadmap-list", (state.dashboard.roadmap || []).map((text) => `<li>${esc(text)}</li>`).join(""));
}

function controls() {
  const models = state.dashboard?.models || [];
  if (has("model-select")) {
    el("model-select").innerHTML = models.map((model) => `<option value="${esc(model.key)}">${esc(model.name)}</option>`).join("");
    el("model-select").value = state.selectedModel || models[0]?.key || "";
  }
  if (has("compare-model-select")) {
    el("compare-model-select").innerHTML = `<option value="${NO_COMPARE}">${esc(t("noCompare"))}</option>${models.filter((model) => model.key !== (state.selectedModel || models[0]?.key)).map((model) => `<option value="${esc(model.key)}">${esc(model.name)}</option>`).join("")}`;
    el("compare-model-select").value = state.compareModel || NO_COMPARE;
    if (![...el("compare-model-select").options].some((option) => option.value === el("compare-model-select").value)) {
      el("compare-model-select").value = NO_COMPARE;
    }
  }
  if (has("scenario-model-select")) {
    el("scenario-model-select").innerHTML = models.map((model) => `<option value="${esc(model.key)}">${esc(model.name)}</option>`).join("");
    el("scenario-model-select").value = state.selectedModel || models[0]?.key || "";
  }
  if (has("horizon-select")) {
    const summary = state.predictionPayload ? summaryFromPayload(state.predictionPayload) : state.dashboard?.prediction_preview;
    const horizons = summary?.forecast_timestamps || [];
    el("horizon-select").innerHTML = horizons.map((value) => `<option value="${esc(value)}">${esc(value)}</option>`).join("");
    el("horizon-select").value = state.selectedHorizon || horizons[0] || "";
  }
}

function mapConfig() {
  if (state.mapMode === "hotspots") {
    return { title: t("hotspotsButton"), items: state.analytics?.items || [], value: (item) => item.risk_score ?? 0, color: (item) => ({ critical: "#c6542b", high: "#d98b39", elevated: "#d8b25c", stable: "#1f7a72" }[String(item.risk_level || "stable")] || "#1f7a72") };
  }
  if (state.mapMode === "gap") {
    return { title: t("modelGapButton"), items: (state.analytics?.items || []).filter((item) => item.comparison_gap !== null && item.comparison_gap !== undefined), value: (item) => item.comparison_gap ?? 0, color: (item) => Number(item.comparison_gap || 0) >= 0 ? "#146c67" : "#b94d31" };
  }
  if (state.mapMode === "delta") {
    return { title: t("scenarioDeltaButton"), items: state.deltaItems || [], value: (item) => item.value ?? 0, color: (item) => Number(item.value || 0) >= 0 ? "#b94d31" : "#146c67" };
  }
  return { title: t("forecastButton"), items: state.predictionLayer?.items || [], value: (item) => item.value ?? 0, color: (item, min, max) => {
    const value = Number(item.value || 0);
    const ratio = max > min ? (value - min) / (max - min) : 0.5;
    const red = Math.round(31 + (191 - 31) * ratio);
    const green = Math.round(122 + (90 - 122) * ratio);
    const blue = Math.round(114 + (48 - 114) * ratio);
    return `rgba(${red}, ${green}, ${blue}, 0.82)`;
  } };
}

function renderMap() {
  if (!has("cesium-container")) return;
  const config = mapConfig();
  const values = config.items.map((item) => Number(config.value(item))).filter(Number.isFinite);
  const min = values.length ? Math.min(...values) : 0;
  const max = values.length ? Math.max(...values) : 1;
  setHTML("map-legend", `<div class="legend-title">${esc(config.title)}</div><div class="legend-items">${pill(`${t("min")}: ${compact(min)}`, "muted")}${pill(`${t("max")}: ${compact(max)}`, "muted")}${pill(`${t("cells")}: ${config.items.length}`, "neutral")}</div>`);
  setHTML("map-status", `${pill(`${t("modelLabel")}: ${(state.dashboard.models || []).find((model) => model.key === state.selectedModel)?.name || "n/a"}`, "neutral")}${pill(`${t("selectedHorizon")}: ${state.selectedHorizon || "n/a"}`, "neutral")}`);
  setHTML("map-fallback", `<p class="fallback-title">${esc(t("mapFallback"))}</p><div class="fallback-list">${config.items.slice(0, 8).map((item) => `<div class="fallback-row"><span>Node ${esc(item.node_id)}</span><strong>${esc(compact(config.value(item)))}</strong></div>`).join("")}</div>`);
  el("map-fallback")?.classList.add("is-visible");
  if (!window.Cesium) return;
  if (!state.viewer) {
    state.viewer = new window.Cesium.Viewer("cesium-container", { animation: false, baseLayerPicker: false, fullscreenButton: false, geocoder: false, homeButton: false, infoBox: false, sceneModePicker: false, selectionIndicator: false, timeline: false, navigationHelpButton: false, terrainProvider: new window.Cesium.EllipsoidTerrainProvider() });
    state.viewer.imageryLayers.removeAll();
    state.viewer.scene.globe.baseColor = window.Cesium.Color.fromCssColorString("#23333c");
    state.viewer.useBrowserRecommendedResolution = false;
    state.viewer.resolutionScale = Math.min(window.devicePixelRatio || 1, 2);
    state.viewer.scene.msaaSamples = 4;
    window.addEventListener("resize", () => {
      if (!state.viewer) return;
      state.viewer.resolutionScale = Math.min(window.devicePixelRatio || 1, 2);
      state.viewer.resize();
    });
  }
  const viewer = state.viewer;
  viewer.entities.removeAll();
  config.items.forEach((item) => {
    if (![item.min_lon, item.min_lat, item.max_lon, item.max_lat].every((value) => Number.isFinite(Number(value)))) return;
    viewer.entities.add({ rectangle: { coordinates: window.Cesium.Rectangle.fromDegrees(Number(item.min_lon), Number(item.min_lat), Number(item.max_lon), Number(item.max_lat)), material: window.Cesium.Color.fromCssColorString(config.color(item, min, max)), outline: true, outlineColor: window.Cesium.Color.fromCssColorString("rgba(255,255,255,0.2)") } });
  });
  if (config.items.length) {
    const minLon = Math.min(...config.items.map((item) => Number(item.min_lon)));
    const minLat = Math.min(...config.items.map((item) => Number(item.min_lat)));
    const maxLon = Math.max(...config.items.map((item) => Number(item.max_lon)));
    const maxLat = Math.max(...config.items.map((item) => Number(item.max_lat)));
    viewer.camera.flyTo({ destination: window.Cesium.Rectangle.fromDegrees(minLon, minLat, maxLon, maxLat), duration: 0 });
  }
  el("map-fallback")?.classList.remove("is-visible");
}

function renderAll() {
  renderStaticText();
  renderHero();
  renderMetrics();
  controls();
  renderOverviewStory();
  renderSourcePolicy();
  renderSegmentation();
  renderHotspots();
  renderManagement();
  renderPredictionSummary();
  renderModels();
  renderModelLabSummary();
  renderBenchmark();
  renderGapAnalysis();
  renderScenario("scenario-panel");
  renderScenario("scenario-example");
  renderDataRegistry();
  renderArchitecture();
  renderMembers();
  renderStudyBrief();
  renderDocs();
  renderMethodology();
  renderRoadmap();
  renderMap();
}

async function refreshModelViews() {
  state.selectedModel = el("model-select")?.value || state.selectedModel;
  const compareValue = el("compare-model-select")?.value || state.compareModel || NO_COMPARE;
  state.compareModel = compareValue === NO_COMPARE ? null : compareValue;
  if (has("horizon-select")) state.selectedHorizon = el("horizon-select").value || state.selectedHorizon;
  if (!state.apiAvailable) {
    renderAll();
    return;
  }
  try {
    state.predictionPayload = await fetchJson(query(URLS.prediction, { model_key: state.selectedModel }));
    const summary = summaryFromPayload(state.predictionPayload);
    if (!summary?.forecast_timestamps?.includes(state.selectedHorizon)) {
      state.selectedHorizon = summary?.forecast_timestamps?.[0] || null;
    }
    state.predictionLayer = await fetchJson(query(URLS.predictionLayer, { model_key: state.selectedModel, horizon: state.selectedHorizon }));
    state.analytics = await fetchJson(query(URLS.analytics, { model_key: state.selectedModel, horizon: state.selectedHorizon, compare_model_key: state.compareModel }));
  } catch (error) {
    console.error(error);
    state.apiAvailable = false;
  }
  renderAll();
}

async function updateSourcePolicy(mode, preferred) {
  if (!state.apiAvailable) return;
  try {
    await fetchJson(URLS.sourcePolicy, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode, preferred_source_key: mode === "manual" ? preferred : null }),
    });
    state.sourcePolicy = await loadOptional(URLS.sourcePolicy, state.sourcePolicy);
    const dataSources = await loadOptional(URLS.dataSources, state.dashboard?.data_sources);
    if (dataSources && state.dashboard) state.dashboard.data_sources = dataSources;
    renderAll();
  } catch (error) {
    console.error(error);
    window.alert(t("updateFailed"));
  }
}

async function runScenario(event) {
  event.preventDefault();
  if (!state.apiAvailable) {
    window.alert(t("scenarioUnavailable"));
    return;
  }
  const submit = el("scenario-submit");
  const form = event.currentTarget;
  const formData = new FormData(form);
  submit.disabled = true;
  submit.textContent = t("running");
  try {
    const response = await fetchJson(URLS.runScenario, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model_key: formData.get("model_key"),
        preset: formData.get("preset"),
        node_ids: String(formData.get("node_ids") || "").split(",").map((value) => value.trim()).filter(Boolean),
        intensity: Number(formData.get("intensity") || 1),
        graph_propagation: { hops: Number(formData.get("hops") || 0), attenuation: Number(formData.get("attenuation") || 0) },
        temporal_profile: { mode: formData.get("temporal_mode") },
      }),
    });
    state.deltaItems = response.delta_layer || [];
    state.scenarioSummary = response.summary || null;
    state.scenarioName = response.scenario_request?.preset || "Scenario";
    state.mapMode = "delta";
    renderAll();
  } catch (error) {
    console.error(error);
    window.alert(t("scenarioFailed"));
  } finally {
    submit.disabled = false;
    submit.textContent = t("runScenarioButton");
  }
}

function bindEvents() {
  if (state.eventsBound) return;
  state.eventsBound = true;
  el("lang-zh")?.addEventListener("click", () => {
    state.language = "zh";
    window.localStorage.setItem("spatio_eco_lang", "zh");
    renderAll();
  });
  el("lang-en")?.addEventListener("click", () => {
    state.language = "en";
    window.localStorage.setItem("spatio_eco_lang", "en");
    renderAll();
  });
  el("model-select")?.addEventListener("change", refreshModelViews);
  el("compare-model-select")?.addEventListener("change", refreshModelViews);
  el("horizon-select")?.addEventListener("change", refreshModelViews);
  el("scenario-form")?.addEventListener("submit", runScenario);
  el("show-forecast")?.addEventListener("click", () => { state.mapMode = "forecast"; renderAll(); });
  el("show-hotspots")?.addEventListener("click", () => { state.mapMode = "hotspots"; renderAll(); });
  el("show-gap")?.addEventListener("click", () => { state.mapMode = "gap"; renderAll(); });
  el("show-delta")?.addEventListener("click", () => { state.mapMode = "delta"; renderAll(); });
  el("reset-map")?.addEventListener("click", () => { state.mapMode = "forecast"; renderAll(); });
  document.body.addEventListener("click", (event) => {
    const button = event.target.closest("[data-source-mode]");
    if (!button) return;
    updateSourcePolicy(button.dataset.sourceMode, button.dataset.preferredSource || null);
  });
}

async function bootstrap() {
  const { payload, fallback } = await loadDashboard();
  state.apiAvailable = !fallback;
  state.dashboard = payload;
  state.platformStatus = fallback ? payload.management : await loadOptional(URLS.platformStatus, payload.management);
  state.sourcePolicy = fallback ? payload.data_sources?.sentinel2_switch : await loadOptional(URLS.sourcePolicy, payload.data_sources?.sentinel2_switch);
  state.segmentationOverview = fallback ? payload.data_sources?.segmentation_remote : await loadOptional(URLS.segmentationOverview, payload.data_sources?.segmentation_remote);
  state.selectedModel = payload.default_models?.multi_step || payload.models?.[0]?.key || null;
  state.compareModel = payload.models?.find((model) => model.stage === "baseline")?.key || null;
  state.analytics = payload.business_preview || null;
  state.predictionLayer = payload.business_preview ? { items: payload.business_preview.items || [], horizon: payload.business_preview.horizon } : null;
  state.selectedHorizon = payload.business_preview?.horizon || null;
  state.scenarioSummary = payload.scenario_preview?.summary || null;
  state.scenarioName = payload.scenario_preview?.name || null;
  state.deltaItems = payload.scenario_preview?.delta_layer || [];
  renderAll();
  bindEvents();
  if (state.apiAvailable) await refreshModelViews();
}

bootstrap().catch((error) => {
  console.error(error);
  state.apiAvailable = false;
  renderAll();
});
