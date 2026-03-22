const API_BASE = "http://127.0.0.1:8000/api/v1";
const URLS = {
  dashboard: `${API_BASE}/dashboard`,
  prediction: `${API_BASE}/predictions/latest`,
  predictionLayer: `${API_BASE}/map/predictions`,
  predictionAnalytics: `${API_BASE}/map/analytics`,
  runScenario: `${API_BASE}/scenarios/run`,
  platformStatus: `${API_BASE}/admin/platform-status`,
  sourcePolicy: `${API_BASE}/admin/source-policy`,
  segmentationOverview: `${API_BASE}/admin/segmentation-overview`,
  fallbackDashboard: "./mock/dashboard.json",
};

const I18N = {
  en: {
    documentTitle: "Spatio-Eco Platform",
    brandEyebrow: "Spatio-Eco Platform",
    navOverview: "Overview",
    navModels: "Models",
    navOperations: "Operations",
    navResearch: "Research",
    heroTitle: "Carbon sink monitoring and forecasting workspace",
    heroDescription:
      "The local platform keeps model training, backend APIs, and frontend presentation on this machine, while real SAM-2 segmentation remains reserved for remote GPU execution.",
    modelsHeroTitle: "Model evaluation and forecast laboratory",
    modelsHeroDescription: "Focus on model metrics, multi-step forecasts, and hotspot ranking.",
    operationsHeroTitle: "Operations and remote segmentation control",
    operationsHeroDescription: "Track source policy, remote SAM-2 status, service readiness, and member boundaries.",
    researchHeroTitle: "Research notes, references, and delivery scope",
    researchHeroDescription: "Keep the project documentation and roadmap readable for review and handoff.",
    platformPhaseLabel: "Platform Phase",
    businessMapTag: "Business Map",
    forecastWorkspaceTitle: "Forecast workspace",
    modelLabel: "Model",
    compareLabel: "Compare",
    horizonLabel: "Horizon",
    forecastButton: "Forecast",
    hotspotsButton: "Hotspots",
    modelGapButton: "Model Gap",
    scenarioDeltaButton: "Scenario Delta",
    resetButton: "Reset",
    mapFallback: "Cesium is unavailable in the current browser session. The map will stay in panel mode.",
    sourcePolicyTag: "Source Policy",
    sentinel2SwitchTitle: "Sentinel-2 switch panel",
    remoteSegmentationTag: "Remote Segmentation",
    sam2StatusTitle: "SAM-2 execution status",
    hotspotWatchTag: "Hotspot Watch",
    businessHotspotsTitle: "Business hotspots",
    scenarioApiTag: "Scenario API",
    liveScenarioTitle: "Live scenario run",
    presetLabel: "Preset",
    nodeIdsLabel: "Node IDs",
    intensityLabel: "Intensity",
    hopsLabel: "Hops",
    attenuationLabel: "Attenuation",
    temporalModeLabel: "Temporal Mode",
    runScenarioButton: "Run scenario",
    managementTag: "Management",
    platformOverviewTitle: "Platform overview",
    modelRegistryTag: "Model Registry",
    modelMetricsTitle: "Model metrics",
    predictionSummaryTag: "Prediction Summary",
    forecastBreakdownTitle: "Forecast breakdown",
    servicesTag: "Services",
    architectureLayersTitle: "Architecture layers",
    membersTag: "Members",
    teamStatusTitle: "Team status",
    documentsTag: "Documents",
    projectReferencesTitle: "Project references",
    roadmapTag: "Roadmap",
    nextStepsTitle: "Next steps",
    noCompare: "No compare",
    auto: "Auto",
    prefer: "Prefer",
    preferred: "Preferred",
    reserve: "Reserve",
    ready: "ready",
    waiting: "waiting",
    yes: "Yes",
    no: "No",
    count: "Count",
    minMax: "Min / Max",
    mean: "Mean",
    target: "Target",
    sentinelSource: "Sentinel-2 source",
    policy: "Policy",
    remoteJobs: "Remote jobs",
    modelLeader: "Model leader",
    sourceMode: "Source mode",
    policyMode: "Policy mode",
    effectiveSource: "Effective source",
    reason: "Reason",
    rows: "Rows",
    current: "Current",
    latestBundle: "Latest bundle",
    jobs: "Jobs",
    completion: "Completion",
    csvRows: "CSV rows",
    nextAction: "Next action",
    topHotspots: "Top hotspots",
    positiveGap: "Positive model gap",
    noGap: "No comparison gap available",
    serviceSummary: "Service summary",
    active: "Active",
    scaffolded: "Scaffolded",
    pending: "Pending",
    dataSummary: "Data summary",
    recommendedNext: "Recommended next",
    hotspotDistribution: "Hotspot distribution",
    critical: "Critical",
    high: "High",
    elevated: "Elevated",
    stable: "Stable",
    mae: "MAE",
    rmse: "RMSE",
    changedNodes: "Changed nodes",
    deltaMean: "Delta mean",
    deltaMax: "Delta max",
    running: "Running...",
    scenarioUnavailable: "Scenario API is unavailable in fallback mode.",
    updateFailed: "Source policy update failed",
    scenarioFailed: "Scenario run failed",
    low: "Low",
    highValue: "High",
    panelMode: "panel mode",
    noItems: "no items",
    cells: "cells",
    min: "min",
    max: "max",
    presetIndustrialExpansion: "Industrial expansion",
    presetGreeningRestoration: "Greening restoration",
    temporalLinear: "Linear",
    temporalUniform: "Uniform",
    temporalLast: "Last-step boost",
  },
  zh: {
    documentTitle: "Spatio-Eco 平台",
    brandEyebrow: "Spatio-Eco 平台",
    navOverview: "总览",
    navModels: "模型",
    navOperations: "运维",
    navResearch: "科研",
    heroTitle: "碳汇监测与预测工作台",
    heroDescription: "本地平台承载模型结果、后端接口与前端展示，真实 SAM-2 分割保留给远程 GPU 执行。",
    modelsHeroTitle: "模型评估与预测实验室",
    modelsHeroDescription: "集中展示模型指标、多步预测结果和热点排序。",
    operationsHeroTitle: "运维与远程分割控制台",
    operationsHeroDescription: "跟踪数据源策略、远程 SAM-2 状态、服务可用性和成员边界。",
    researchHeroTitle: "科研文档、资料与交付范围",
    researchHeroDescription: "把项目文档和路线图整理成适合答辩与交接的形式。",
    platformPhaseLabel: "平台阶段",
    businessMapTag: "业务地图",
    forecastWorkspaceTitle: "预测工作区",
    modelLabel: "模型",
    compareLabel: "对比",
    horizonLabel: "预测期",
    forecastButton: "预测值",
    hotspotsButton: "热点",
    modelGapButton: "模型差异",
    scenarioDeltaButton: "情景增量",
    resetButton: "重置",
    mapFallback: "当前浏览器无法加载 Cesium，地图将保持面板模式。",
    sourcePolicyTag: "数据源策略",
    sentinel2SwitchTitle: "Sentinel-2 切换面板",
    remoteSegmentationTag: "远程分割",
    sam2StatusTitle: "SAM-2 执行状态",
    hotspotWatchTag: "热点观察",
    businessHotspotsTitle: "业务热点",
    scenarioApiTag: "情景推演",
    liveScenarioTitle: "实时情景运行",
    presetLabel: "预设",
    nodeIdsLabel: "节点 ID",
    intensityLabel: "强度",
    hopsLabel: "传播跳数",
    attenuationLabel: "衰减系数",
    temporalModeLabel: "时间模式",
    runScenarioButton: "运行情景",
    managementTag: "管理",
    platformOverviewTitle: "平台概览",
    modelRegistryTag: "模型登记",
    modelMetricsTitle: "模型指标",
    predictionSummaryTag: "预测摘要",
    forecastBreakdownTitle: "预测拆解",
    servicesTag: "服务",
    architectureLayersTitle: "架构层级",
    membersTag: "成员",
    teamStatusTitle: "团队状态",
    documentsTag: "文档",
    projectReferencesTitle: "项目资料",
    roadmapTag: "路线图",
    nextStepsTitle: "下一步",
    noCompare: "不对比",
    auto: "自动",
    prefer: "设为偏好",
    preferred: "已偏好",
    reserve: "预留",
    ready: "已就绪",
    waiting: "等待中",
    yes: "是",
    no: "否",
    count: "数量",
    minMax: "最小 / 最大",
    mean: "均值",
    target: "目标",
    sentinelSource: "Sentinel-2 来源",
    policy: "策略",
    remoteJobs: "远程任务",
    modelLeader: "当前领先模型",
    sourceMode: "来源模式",
    policyMode: "策略模式",
    effectiveSource: "生效来源",
    reason: "原因",
    rows: "行数",
    current: "当前使用",
    latestBundle: "最新 bundle",
    jobs: "任务数",
    completion: "完成度",
    csvRows: "CSV 行数",
    nextAction: "下一步动作",
    topHotspots: "热点节点",
    positiveGap: "正向模型差异",
    noGap: "当前无可用差异",
    serviceSummary: "服务概况",
    active: "已激活",
    scaffolded: "已搭骨架",
    pending: "待补齐",
    dataSummary: "数据概况",
    recommendedNext: "建议下一步",
    hotspotDistribution: "热点分布",
    critical: "关键",
    high: "高",
    elevated: "中",
    stable: "稳定",
    mae: "MAE",
    rmse: "RMSE",
    changedNodes: "变更节点",
    deltaMean: "增量均值",
    deltaMax: "增量最大值",
    running: "运行中...",
    scenarioUnavailable: "当前为回退模式，情景推演接口不可用。",
    updateFailed: "数据源策略更新失败",
    scenarioFailed: "情景推演运行失败",
    low: "低",
    highValue: "高",
    panelMode: "面板模式",
    noItems: "无数据",
    cells: "网格数",
    min: "最小",
    max: "最大",
    presetIndustrialExpansion: "工业扩张",
    presetGreeningRestoration: "生态修复",
    temporalLinear: "线性",
    temporalUniform: "均匀",
    temporalLast: "末步增强",
  },
};

const state = {
  apiAvailable: true,
  dashboard: null,
  platformStatus: null,
  sourcePolicy: null,
  segmentationOverview: null,
  predictionPayload: null,
  predictionLayer: null,
  analytics: null,
  deltaItems: null,
  viewer: null,
  mapMode: "forecast",
  language: (() => {
    const saved = window.localStorage.getItem("spatio_eco_lang");
    if (saved === "zh" || saved === "en") return saved;
    return String(navigator.language || "").toLowerCase().startsWith("zh") ? "zh" : "en";
  })(),
};

const e = (id) => document.getElementById(id);
const locale = () => (state.language === "zh" ? "zh-CN" : "en-US");
const t = (key) => (I18N[state.language] && I18N[state.language][key]) || I18N.en[key] || key;
const has = (id) => Boolean(e(id));

function fmt(value, digits = 4) {
  const n = Number(value);
  if (!Number.isFinite(n)) return "n/a";
  return n.toFixed(digits);
}

function compact(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return "n/a";
  if (Math.abs(n) >= 1000) return n.toLocaleString(locale(), { maximumFractionDigits: 2 });
  if (Math.abs(n) >= 1) return n.toFixed(3);
  if (Math.abs(n) >= 0.01) return n.toFixed(5);
  return n.toExponential(2);
}

function nice(text) {
  return String(text || "").replace(/_/g, " ");
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

async function loadOptional(url, fallbackValue) {
  try {
    return await fetchJson(url);
  } catch {
    return fallbackValue;
  }
}

function sourcePolicyFallback(dashboard) {
  const sentinel2 = dashboard.data_sources.sentinel2_switch;
  return {
    policy: { mode: "auto", preferred_source_key: null, updated_at: null },
    effective_mode: "auto",
    effective_reason: "fallback_mock",
    active_key: sentinel2.active_key,
    active_name: sentinel2.active_name,
    active_path: sentinel2.active_path,
    options: sentinel2.items,
  };
}

function segmentationFallback(dashboard) {
  return dashboard.data_sources.segmentation_remote;
}

function platformFallback(dashboard) {
  return (
    dashboard.management || {
      service_summary: { total: dashboard.architecture.length, active: 2, scaffolded: 2, pending_fill: 2 },
      data_summary: {
        ready_data_count: dashboard.data_sources.items.length,
        tracked_data_count: dashboard.data_sources.items.length,
        active_sentinel2_source: dashboard.data_sources.sentinel2_switch.active_key,
        effective_source_mode: "auto",
      },
      model_summary: {
        count: dashboard.models.length,
        leader_key: dashboard.default_models.multi_step,
        leader_rmse: dashboard.models[1].metrics.rmse,
        leader_mae: dashboard.models[1].metrics.mae,
      },
      segmentation_summary: {
        job_count: dashboard.data_sources.segmentation_remote.latest_bundle_job_count || 0,
        complete_scene_count: 0,
        completion_rate: 0,
        sam2_feature_ready: false,
        next_action: "wait_for_remote_results",
      },
      recommendations: dashboard.roadmap,
    }
  );
}

function applyStaticText() {
  document.title = t("documentTitle");
  document.documentElement.lang = state.language === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll("[data-page-link]").forEach((node) => {
    node.classList.toggle("is-active", node.dataset.pageLink === document.body.dataset.page);
  });
  if (has("lang-zh")) e("lang-zh").classList.toggle("is-active", state.language === "zh");
  if (has("lang-en")) e("lang-en").classList.toggle("is-active", state.language === "en");

  const preset = document.querySelector('select[name="preset"]');
  if (preset) {
    Array.from(preset.options).forEach((option) => {
      if (option.value === "industrial_expansion") option.textContent = t("presetIndustrialExpansion");
      if (option.value === "greening_restoration") option.textContent = t("presetGreeningRestoration");
    });
  }
  const temporal = document.querySelector('select[name="temporal_mode"]');
  if (temporal) {
    Array.from(temporal.options).forEach((option) => {
      if (option.value === "linear") option.textContent = t("temporalLinear");
      if (option.value === "uniform") option.textContent = t("temporalUniform");
      if (option.value === "last") option.textContent = t("temporalLast");
    });
  }
}

function setLanguage(language) {
  if (!["zh", "en"].includes(language) || language === state.language) return;
  state.language = language;
  window.localStorage.setItem("spatio_eco_lang", language);
  applyStaticText();
  if (state.dashboard) renderAll();
}

function renderHero() {
  if (!has("project-phase") || !has("hero-meta") || !has("hero-stack")) return;
  const project = state.dashboard.project;
  const sourcePolicy = state.sourcePolicy;
  e("project-phase").textContent = `${project.phase} / ${project.study_area.status}`;
  e("hero-meta").innerHTML = `
    <span class="hero-chip">${project.study_area.name}</span>
    <span class="hero-chip">${project.study_area.node_count} grid cells</span>
    <span class="hero-chip">${project.study_area.time_granularity}</span>
    <span class="hero-chip">${project.study_area.time_range.join(" to ")}</span>
  `;
  e("hero-stack").innerHTML = `
    <div class="hero-kv"><span>${t("target")}</span><strong>${project.study_area.current_target}</strong></div>
    <div class="hero-kv"><span>${t("sentinelSource")}</span><strong>${sourcePolicy.active_name}</strong></div>
    <div class="hero-kv"><span>${t("policy")}</span><strong>${sourcePolicy.policy.mode} / ${sourcePolicy.effective_mode}</strong></div>
  `;
}

function renderMetricsStrip() {
  if (!has("metrics-strip")) return;
  const dashboard = state.dashboard;
  const platformStatus = state.platformStatus;
  const segmentation = state.segmentationOverview;
  const tiles = [
    { label: t("modelLeader"), value: platformStatus.model_summary.leader_key, detail: `RMSE ${fmt(platformStatus.model_summary.leader_rmse, 5)}` },
    { label: t("sourceMode"), value: platformStatus.data_summary.effective_source_mode, detail: dashboard.data_sources.sentinel2_switch.active_key },
    { label: t("remoteJobs"), value: segmentation.job_count || 0, detail: `${t("completion")}: ${Math.round((segmentation.completion_rate || 0) * 100)}%` },
    { label: t("modelLabel"), value: dashboard.default_models.multi_step, detail: dashboard.project.study_area.name },
  ];
  e("metrics-strip").innerHTML = tiles
    .map(
      (tile) => `
        <article class="metric-tile">
          <span>${tile.label}</span>
          <strong>${tile.value}</strong>
          <p>${tile.detail}</p>
        </article>
      `,
    )
    .join("");
}

function renderSourcePolicyPanel() {
  if (!has("source-policy-summary") || !has("source-policy-grid")) return;
  const sourcePolicy = state.sourcePolicy;
  e("source-policy-summary").innerHTML = `
    <div class="hero-kv policy-kv"><span>${t("policyMode")}</span><strong>${sourcePolicy.policy.mode}</strong></div>
    <div class="hero-kv policy-kv"><span>${t("effectiveSource")}</span><strong>${sourcePolicy.active_name}</strong></div>
    <div class="hero-kv policy-kv"><span>${t("reason")}</span><strong>${nice(sourcePolicy.effective_reason)}</strong></div>
  `;
  e("source-policy-grid").innerHTML = sourcePolicy.options
    .map((item) => {
      const isPreferred = sourcePolicy.policy.preferred_source_key === item.key;
      const isActive = sourcePolicy.active_key === item.key;
      const buttonLabel = item.key === "sam2_remote" && !item.available ? t("reserve") : isPreferred ? t("preferred") : t("prefer");
      return `
        <article class="mini-card">
          <div class="section-head">
            <h3>${item.name}</h3>
            <span class="status-pill ${item.available ? "active" : "pending_fill"}">${item.available ? t("ready") : t("waiting")}</span>
          </div>
          <p>${item.description}</p>
          <p><strong>${t("rows")}:</strong> ${item.rows}</p>
          <p><strong>${t("current")}:</strong> ${isActive ? t("yes") : t("no")}</p>
          <p class="path-text">${item.path}</p>
          <div class="button-row">
            <button class="inline-button ${isPreferred ? "selected" : ""}" data-source-mode="manual" data-source-key="${item.key}" type="button">${buttonLabel}</button>
            <button class="inline-button ghost" data-source-mode="auto" type="button">${t("auto")}</button>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderSegmentationStatus() {
  if (!has("segmentation-status")) return;
  const item = state.segmentationOverview;
  e("segmentation-status").innerHTML = `
    <article class="mini-card">
      <div class="section-head">
        <h3>Remote bundle</h3>
        <span class="status-pill ${item.job_count ? "active" : "pending_fill"}">${item.job_count ? t("ready") : t("waiting")}</span>
      </div>
      <p><strong>${t("latestBundle")}:</strong> ${item.latest_bundle_dir || "not exported yet"}</p>
      <p><strong>${t("jobs")}:</strong> ${item.job_count || 0}</p>
      <p><strong>${t("completion")}:</strong> ${Math.round((item.completion_rate || 0) * 100)}%</p>
    </article>
    <article class="mini-card">
      <div class="section-head">
        <h3>SAM-2</h3>
        <span class="status-pill ${item.sam2_feature_ready ? "active" : "pending_fill"}">${item.sam2_feature_ready ? t("ready") : t("pending")}</span>
      </div>
      <p><strong>${t("csvRows")}:</strong> ${item.sam2_feature_rows || 0}</p>
      <p><strong>${t("nextAction")}:</strong> ${nice(item.next_action)}</p>
      <p class="path-text">${item.sam2_feature_path || ""}</p>
    </article>
  `;
}

function renderHotspotList() {
  if (!has("hotspot-list") || !state.analytics) return;
  const summary = state.analytics.summary;
  e("hotspot-list").innerHTML = `
    <article class="mini-card">
      <div class="section-head">
        <h3>${t("topHotspots")}</h3>
        <span class="status-pill active">${state.analytics.horizon}</span>
      </div>
      <ul class="compact-list">
        ${(summary.top_hotspots || []).map((item) => `<li>node ${item.node_id}<strong>${compact(item.value)}</strong></li>`).join("")}
      </ul>
    </article>
    <article class="mini-card">
      <div class="section-head">
        <h3>${t("positiveGap")}</h3>
        <span class="status-pill active">${state.analytics.compare_model_key || "none"}</span>
      </div>
      <ul class="compact-list">
        ${
          (summary.top_positive_gap || []).length
            ? summary.top_positive_gap.map((item) => `<li>node ${item.node_id}<strong>${compact(item.value)}</strong></li>`).join("")
            : `<li>${t("noGap")}</li>`
        }
      </ul>
    </article>
  `;
}

function renderManagement() {
  if (!has("management-grid")) return;
  const p = state.platformStatus;
  e("management-grid").innerHTML = `
    <article class="mini-card">
      <div class="section-head"><h3>${t("serviceSummary")}</h3><span class="status-pill active">${p.service_summary.total}</span></div>
      <p><strong>${t("active")}:</strong> ${p.service_summary.active}</p>
      <p><strong>${t("scaffolded")}:</strong> ${p.service_summary.scaffolded}</p>
      <p><strong>${t("pending")}:</strong> ${p.service_summary.pending_fill}</p>
    </article>
    <article class="mini-card">
      <div class="section-head"><h3>${t("dataSummary")}</h3><span class="status-pill active">${p.data_summary.ready_data_count}/${p.data_summary.tracked_data_count}</span></div>
      <p><strong>${t("sentinelSource")}:</strong> ${p.data_summary.active_sentinel2_source}</p>
      <p><strong>${t("sourceMode")}:</strong> ${p.data_summary.effective_source_mode}</p>
    </article>
    <article class="mini-card">
      <div class="section-head"><h3>${t("modelLeader")}</h3><span class="status-pill active">${p.model_summary.leader_key}</span></div>
      <p><strong>${t("mae")}:</strong> ${fmt(p.model_summary.leader_mae, 5)}</p>
      <p><strong>${t("rmse")}:</strong> ${fmt(p.model_summary.leader_rmse, 5)}</p>
    </article>
    <article class="mini-card">
      <div class="section-head"><h3>${t("recommendedNext")}</h3><span class="status-pill pending_fill">${nice(p.segmentation_summary.next_action)}</span></div>
      <ul class="compact-list">${(p.recommendations || []).map((item) => `<li>${item}</li>`).join("")}</ul>
    </article>
  `;
}

function renderModels() {
  if (!has("model-grid")) return;
  e("model-grid").innerHTML = state.dashboard.models
    .map((item) => {
      const defaults = state.dashboard.default_models;
      const isDefault = item.key === defaults.single_step || item.key === defaults.multi_step;
      return `
        <article class="model-card">
          <div class="section-head"><h3>${item.name}</h3><span class="status-pill active">${item.horizon}</span></div>
          <p>${item.owner} / ${item.stage}${isDefault ? " / default" : ""}</p>
          <div class="metric-row">
            <div class="metric-chip"><span>${t("mae")}</span><strong>${fmt(item.metrics.mae, 5)}</strong></div>
            <div class="metric-chip"><span>${t("rmse")}</span><strong>${fmt(item.metrics.rmse, 5)}</strong></div>
          </div>
        </article>
      `;
    })
    .join("");
}

function buildPredictionPreview(payload) {
  const byHorizon = {};
  const horizons = payload.predictions_by_horizon || {};
  Object.entries(horizons).forEach(([horizon, nodeMap]) => {
    const values = Object.values(nodeMap).map(Number);
    const topNodes = Object.entries(nodeMap)
      .map(([nodeId, value]) => ({ node_id: nodeId, value: Number(value) }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 5);
    byHorizon[horizon] = {
      count: values.length,
      min: values.length ? Math.min(...values) : 0,
      max: values.length ? Math.max(...values) : 0,
      mean: values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : 0,
      top_nodes: topNodes,
    };
  });
  return { by_horizon: byHorizon };
}

function renderPredictionSummary() {
  if (!has("prediction-grid") || !state.analytics) return;
  const preview = state.predictionPayload ? buildPredictionPreview(state.predictionPayload) : state.dashboard.prediction_preview;
  const cards = Object.entries(preview.by_horizon || {})
    .map(
      ([timestamp, stats]) => `
        <article class="forecast-card">
          <h3>${timestamp}</h3>
          <p>${t("count")}: ${stats.count}</p>
          <p>${t("minMax")}: ${compact(stats.min)} / ${compact(stats.max)}</p>
          <p>${t("mean")}: ${compact(stats.mean)}</p>
          <ul class="compact-list">${stats.top_nodes.map((node) => `<li>node ${node.node_id}<strong>${compact(node.value)}</strong></li>`).join("")}</ul>
        </article>
      `,
    )
    .join("");
  const hotspot = state.analytics.summary.category_counts;
  e("prediction-grid").innerHTML = `
    ${cards}
    <article class="forecast-card">
      <h3>${t("hotspotDistribution")}</h3>
      <p>${t("critical")}: ${hotspot.critical}</p>
      <p>${t("high")}: ${hotspot.high}</p>
      <p>${t("elevated")}: ${hotspot.elevated}</p>
      <p>${t("stable")}: ${hotspot.stable}</p>
    </article>
  `;
}

function renderArchitecture() {
  if (!has("architecture-grid")) return;
  e("architecture-grid").innerHTML = state.dashboard.architecture
    .map(
      (item) => `
        <article class="mini-card">
          <div class="section-head"><h3>${item.layer}</h3><span class="status-pill ${item.status}">${nice(item.status)}</span></div>
          <p><strong>${item.owner}</strong></p>
          <p>${item.current_scope}</p>
          <p><strong>${t("nextAction")}:</strong> ${item.next_fill}</p>
        </article>
      `,
    )
    .join("");
}

function renderMembers() {
  if (!has("member-grid")) return;
  e("member-grid").innerHTML = state.dashboard.members
    .map(
      (item) => `
        <article class="mini-card">
          <div class="section-head"><h3>${item.member}</h3><span class="status-pill ${item.status}">${nice(item.status)}</span></div>
          <p><strong>${item.role}</strong></p>
          <p><strong>${t("active")}:</strong> ${item.completed.join("; ")}</p>
          <p><strong>${t("nextStepsTitle")}:</strong> ${item.remaining.join("; ")}</p>
        </article>
      `,
    )
    .join("");
}

function renderDocs() {
  if (!has("docs-grid")) return;
  e("docs-grid").innerHTML = state.dashboard.docs
    .map(
      (item) => `
        <article class="mini-card">
          <div class="section-head"><h3>${item.title}</h3><span class="status-pill active">${item.group}</span></div>
          <p class="path-text">${item.path}</p>
        </article>
      `,
    )
    .join("");
}

function renderRoadmap() {
  if (!has("roadmap-list")) return;
  e("roadmap-list").innerHTML = state.dashboard.roadmap.map((item) => `<li>${item}</li>`).join("");
}

function renderScenarioSummary(summaryBlock) {
  if (!has("scenario-panel") || !summaryBlock || !summaryBlock.summary) return;
  const summary = summaryBlock.summary;
  e("scenario-panel").innerHTML = `
    <p><strong>${summaryBlock.name}</strong></p>
    <p>${t("horizonLabel")}: ${summary.forecast_horizon}</p>
    <p>${t("changedNodes")}: ${summary.changed_nodes.join(", ")}</p>
    <p>${t("deltaMean")}: ${compact(summary.delta_summary.mean)}</p>
    <p>${t("deltaMax")}: ${compact(summary.delta_summary.max)}</p>
    <ul class="compact-list">${Object.entries(summary.feature_deltas).map(([key, value]) => `<li>${key}<strong>${compact(value)}</strong></li>`).join("")}</ul>
  `;
}

function populateModelControls() {
  const models = state.dashboard.models;
  const defaults = state.dashboard.default_models;
  const modelOptions = models
    .map((model) => `<option value="${model.key}" ${model.key === defaults.multi_step ? "selected" : ""}>${model.name}</option>`)
    .join("");
  if (has("model-select")) e("model-select").innerHTML = modelOptions;
  if (has("scenario-model-select")) e("scenario-model-select").innerHTML = modelOptions;
  if (has("compare-model-select")) {
    e("compare-model-select").innerHTML = [
      `<option value="">${t("noCompare")}</option>`,
      ...models.map((model) => `<option value="${model.key}" ${model.key === "lstm_multistep_baseline" ? "selected" : ""}>${model.name}</option>`),
    ].join("");
  }
}

function populateHorizonSelect(payload, previousValue) {
  if (!has("horizon-select")) return;
  const horizons = payload.forecast_timestamps || [];
  const selected = horizons.includes(previousValue) ? previousValue : horizons[0];
  e("horizon-select").innerHTML = horizons.map((item) => `<option value="${item}" ${item === selected ? "selected" : ""}>${item}</option>`).join("");
}

function ensureCesiumViewer() {
  if (!has("cesium-container") || !has("map-fallback")) return null;
  if (!window.Cesium) {
    e("map-fallback").classList.remove("hidden");
    return null;
  }
  if (state.viewer) {
    e("map-fallback").classList.add("hidden");
    return state.viewer;
  }
  const Cesium = window.Cesium;
  const viewer = new Cesium.Viewer("cesium-container", {
    animation: false,
    timeline: false,
    geocoder: false,
    homeButton: false,
    sceneModePicker: false,
    navigationHelpButton: false,
    fullscreenButton: false,
    baseLayerPicker: false,
    infoBox: false,
    selectionIndicator: false,
    imageryProvider: new Cesium.OpenStreetMapImageryProvider({ url: "https://tile.openstreetmap.org/" }),
  });
  viewer.scene.globe.depthTestAgainstTerrain = false;
  viewer.camera.flyTo({ destination: Cesium.Rectangle.fromDegrees(118.3, 31.2, 119.3, 32.7), duration: 0 });
  state.viewer = viewer;
  e("map-fallback").classList.add("hidden");
  return viewer;
}

function forecastColor(Cesium, value, min, max) {
  const span = Math.max(max - min, 1e-6);
  const ratio = (value - min) / span;
  return Cesium.Color.fromHsl(0.62 - ratio * 0.52, 0.78, 0.52, 0.78);
}

function riskColor(Cesium, level) {
  if (level === "critical") return Cesium.Color.fromCssColorString("#c6512d").withAlpha(0.82);
  if (level === "high") return Cesium.Color.fromCssColorString("#dd7c39").withAlpha(0.82);
  if (level === "elevated") return Cesium.Color.fromCssColorString("#e7b760").withAlpha(0.82);
  return Cesium.Color.fromCssColorString("#20756e").withAlpha(0.78);
}

function gapColor(Cesium, value) {
  return value >= 0
    ? Cesium.Color.fromCssColorString("#d85d43").withAlpha(0.78)
    : Cesium.Color.fromCssColorString("#0f6d70").withAlpha(0.78);
}

function mapConfig() {
  if (state.mapMode === "delta") {
    return { items: state.deltaItems || [], label: t("scenarioDeltaButton"), legend: [[t("positiveGap"), "legend-positive"], [t("scenarioDeltaButton"), "legend-negative"]], value: (item) => Number(item.value) };
  }
  if (!state.analytics) return { items: [], label: t("businessMapTag"), legend: [], value: () => 0 };
  if (state.mapMode === "hotspots") {
    return { items: state.analytics.items, label: t("hotspotsButton"), legend: [[t("critical"), "legend-critical"], [t("high"), "legend-high"], [t("elevated"), "legend-elevated"], [t("stable"), "legend-stable"]], value: (item) => Number(item.risk_score || 0) };
  }
  if (state.mapMode === "gap") {
    return { items: state.analytics.items.filter((item) => typeof item.comparison_gap === "number"), label: t("modelGapButton"), legend: [[t("positiveGap"), "legend-positive"], [t("noGap"), "legend-negative"]], value: (item) => Number(item.comparison_gap || 0) };
  }
  return { items: state.predictionLayer ? state.predictionLayer.items : [], label: t("forecastButton"), legend: [[t("low"), "legend-stable"], [t("highValue"), "legend-critical"]], value: (item) => Number(item.value) };
}

function renderLegend(label, entries) {
  if (!has("map-legend")) return;
  e("map-legend").innerHTML = `
    <div class="legend-title">${label}</div>
    <div class="legend-items">${entries.map(([text, cls]) => `<span class="legend-item"><i class="legend-swatch ${cls}"></i>${text}</span>`).join("")}</div>
  `;
}

function renderCurrentMap() {
  if (!has("map-status")) return;
  const config = mapConfig();
  renderLegend(config.label, config.legend);
  const viewer = ensureCesiumViewer();
  if (!viewer) {
    e("map-status").textContent = `${config.label} / ${t("panelMode")}`;
    return;
  }
  const items = config.items || [];
  if (!items.length) {
    viewer.entities.removeAll();
    e("map-status").textContent = `${config.label} / ${t("noItems")}`;
    return;
  }

  const values = items.map(config.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  viewer.entities.removeAll();
  const Cesium = window.Cesium;
  items.forEach((item) => {
    const baseValue = config.value(item);
    let material = forecastColor(Cesium, baseValue, min, max);
    let extrudedHeight = 600 + ((baseValue - min) / Math.max(max - min, 1e-6)) * 9000;
    if (state.mapMode === "hotspots") {
      material = riskColor(Cesium, item.risk_level);
      extrudedHeight = 800 + Number(item.risk_score || 0) * 9000;
    } else if (state.mapMode === "gap") {
      material = gapColor(Cesium, Number(item.comparison_gap || 0));
      extrudedHeight = 300 + Math.abs(Number(item.comparison_gap || 0)) * 100000;
    } else if (state.mapMode === "delta") {
      material = gapColor(Cesium, baseValue);
      extrudedHeight = Math.max(200, Math.abs(baseValue) * 90000);
    }
    viewer.entities.add({
      rectangle: {
        coordinates: Cesium.Rectangle.fromDegrees(item.min_lon, item.min_lat, item.max_lon, item.max_lat),
        material,
        outline: true,
        outlineColor: Cesium.Color.fromCssColorString("#f4efe7").withAlpha(0.22),
        height: 0,
        extrudedHeight,
      },
      description: `node ${item.node_id}<br/>value: ${compact(baseValue)}`,
    });
  });
  e("map-status").textContent = `${config.label} / ${t("cells")} ${items.length} / ${t("min")} ${compact(min)} / ${t("max")} ${compact(max)}`;
}

function setToolbarState(mode) {
  [["show-forecast", "forecast"], ["show-hotspots", "hotspots"], ["show-gap", "gap"], ["show-delta", "delta"]].forEach(([id, value]) => {
    if (has(id)) e(id).classList.toggle("is-active", value === mode);
  });
}

async function refreshAnalyticsAndMap({ preserveHorizon = true } = {}) {
  if (!has("model-select")) return;
  const modelKey = e("model-select").value;
  const compareKey = has("compare-model-select") ? e("compare-model-select").value : "";
  const previous = preserveHorizon && has("horizon-select") ? e("horizon-select").value : null;

  state.predictionPayload = await fetchJson(`${URLS.prediction}?model_key=${encodeURIComponent(modelKey)}`);
  populateHorizonSelect(state.predictionPayload, previous);
  const horizon = has("horizon-select") ? e("horizon-select").value : "";
  state.predictionLayer = await fetchJson(`${URLS.predictionLayer}?model_key=${encodeURIComponent(modelKey)}&horizon=${encodeURIComponent(horizon)}`);
  state.analytics = await fetchJson(`${URLS.predictionAnalytics}?model_key=${encodeURIComponent(modelKey)}&horizon=${encodeURIComponent(horizon)}&compare_model_key=${encodeURIComponent(compareKey)}`);
  renderHotspotList();
  renderPredictionSummary();
  if (state.mapMode !== "delta") state.mapMode = "forecast";
  setToolbarState(state.mapMode);
  renderCurrentMap();
}

async function handleSourcePolicyClick(event) {
  const button = event.target.closest("[data-source-mode]");
  if (!button || !state.apiAvailable) return;
  button.disabled = true;
  try {
    state.sourcePolicy = await fetchJson(URLS.sourcePolicy, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode: button.dataset.sourceMode, preferred_source_key: button.dataset.sourceKey || null }),
    });
    state.dashboard = await fetchJson(URLS.dashboard);
    state.platformStatus = await fetchJson(URLS.platformStatus);
    state.segmentationOverview = await fetchJson(URLS.segmentationOverview);
    renderAll();
  } catch (error) {
    window.alert(`${t("updateFailed")}: ${error.message}`);
  } finally {
    button.disabled = false;
  }
}

async function handleScenarioSubmit(event) {
  event.preventDefault();
  if (!has("scenario-panel")) return;
  if (!state.apiAvailable) {
    e("scenario-panel").innerHTML = `<p>${t("scenarioUnavailable")}</p>`;
    return;
  }
  const button = e("scenario-submit");
  const form = new FormData(event.currentTarget);
  button.disabled = true;
  button.textContent = t("running");
  try {
    const response = await fetchJson(URLS.runScenario, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model_key: form.get("model_key"),
        preset: form.get("preset"),
        intensity: Number(form.get("intensity")),
        node_ids: String(form.get("node_ids")).split(",").map((item) => item.trim()).filter(Boolean),
        graph_propagation: { hops: Number(form.get("hops")), attenuation: Number(form.get("attenuation")), blend_mode: "sum" },
        temporal_profile: { mode: form.get("temporal_mode"), start_weight: 0.35, end_weight: 1.0 },
      }),
    });
    state.deltaItems = response.delta_layer;
    state.mapMode = "delta";
    setToolbarState("delta");
    renderScenarioSummary({ name: "Live scenario result", summary: response.summary });
    renderCurrentMap();
  } catch (error) {
    e("scenario-panel").innerHTML = `<p>${t("scenarioFailed")}: ${error.message}</p>`;
  } finally {
    button.disabled = false;
    button.textContent = t("runScenarioButton");
  }
}

function bindEvents() {
  if (has("lang-zh")) e("lang-zh").addEventListener("click", () => setLanguage("zh"));
  if (has("lang-en")) e("lang-en").addEventListener("click", () => setLanguage("en"));
  if (has("model-select")) e("model-select").addEventListener("change", () => refreshAnalyticsAndMap({ preserveHorizon: false }));
  if (has("compare-model-select")) e("compare-model-select").addEventListener("change", () => refreshAnalyticsAndMap());
  if (has("horizon-select")) e("horizon-select").addEventListener("change", () => refreshAnalyticsAndMap());
  if (has("scenario-form")) e("scenario-form").addEventListener("submit", handleScenarioSubmit);
  if (has("source-policy-grid")) e("source-policy-grid").addEventListener("click", handleSourcePolicyClick);
  if (has("show-forecast")) e("show-forecast").addEventListener("click", () => { state.mapMode = "forecast"; setToolbarState("forecast"); renderCurrentMap(); });
  if (has("show-hotspots")) e("show-hotspots").addEventListener("click", () => { state.mapMode = "hotspots"; setToolbarState("hotspots"); renderCurrentMap(); });
  if (has("show-gap")) e("show-gap").addEventListener("click", () => { state.mapMode = "gap"; setToolbarState("gap"); renderCurrentMap(); });
  if (has("show-delta")) e("show-delta").addEventListener("click", () => { if (state.deltaItems) { state.mapMode = "delta"; setToolbarState("delta"); renderCurrentMap(); } });
  if (has("reset-map")) e("reset-map").addEventListener("click", () => {
    state.mapMode = "forecast";
    setToolbarState("forecast");
    renderCurrentMap();
    if (state.viewer && window.Cesium) {
      state.viewer.camera.flyTo({ destination: window.Cesium.Rectangle.fromDegrees(118.3, 31.2, 119.3, 32.7), duration: 0.5 });
    }
  });
}

function renderAll() {
  applyStaticText();
  renderHero();
  renderMetricsStrip();
  renderSourcePolicyPanel();
  renderSegmentationStatus();
  renderHotspotList();
  renderManagement();
  renderModels();
  renderPredictionSummary();
  renderArchitecture();
  renderMembers();
  renderDocs();
  renderRoadmap();
  renderScenarioSummary(state.dashboard.scenario_preview);
  if (has("model-select")) populateModelControls();
  setToolbarState(state.mapMode);
  renderCurrentMap();
}

async function bootstrap() {
  applyStaticText();
  const dashboardResult = await loadDashboard();
  state.apiAvailable = !dashboardResult.fallback;
  state.dashboard = dashboardResult.payload;
  state.platformStatus = state.apiAvailable ? await loadOptional(URLS.platformStatus, platformFallback(state.dashboard)) : platformFallback(state.dashboard);
  state.sourcePolicy = state.apiAvailable ? await loadOptional(URLS.sourcePolicy, sourcePolicyFallback(state.dashboard)) : sourcePolicyFallback(state.dashboard);
  state.segmentationOverview = state.apiAvailable ? await loadOptional(URLS.segmentationOverview, segmentationFallback(state.dashboard)) : segmentationFallback(state.dashboard);
  state.analytics = state.apiAvailable
    ? await loadOptional(`${URLS.predictionAnalytics}?model_key=${encodeURIComponent(state.dashboard.default_models.multi_step)}`, state.dashboard.business_preview)
    : state.dashboard.business_preview;
  bindEvents();
  if (state.apiAvailable && has("model-select")) {
    populateModelControls();
    await refreshAnalyticsAndMap({ preserveHorizon: false });
  } else {
    renderAll();
  }
}

bootstrap();
