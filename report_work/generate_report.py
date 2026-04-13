from __future__ import annotations

import csv
import json
import shutil
import subprocess
from pathlib import Path
from typing import Iterable

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

REPORT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = REPORT_ROOT.parent
TEMPLATE_PATH = next(REPORT_ROOT.glob('04-4*.docx'))
OUTPUT_DOCX = REPORT_ROOT / '2026024905_天穹智算——区域碳汇时空溯源与演化流式计算平台_作品报告.docx'
OUTPUT_PDF = REPORT_ROOT / '2026024905_天穹智算——区域碳汇时空溯源与演化流式计算平台_作品报告.pdf'
FIGURE_DIR = REPORT_ROOT / 'figures'


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def csv_row_count(path: Path) -> int:
    with path.open('r', encoding='utf-8-sig', newline='') as handle:
        reader = csv.reader(handle)
        next(reader, None)
        return sum(1 for _ in reader)


def collect_data() -> dict:
    data = {
        'feature_summary': load_json(REPO_ROOT / 'data' / 'processed' / 'features' / 'nanjing' / 'quarterly' / 'sentinel2_features.summary.json'),
        'dataset_meta': load_json(REPO_ROOT / 'services' / 'inference' / 'outputs' / 'stgnn_gcn_lstm_nanjing_quarterly_qc_edgar_hybrid_multistep' / 'dataset_meta.json'),
        'metrics_lstm': load_json(REPO_ROOT / 'services' / 'inference' / 'outputs' / 'lstm_baseline_nanjing_quarterly_qc_edgar_multistep' / 'metrics.json')['test_metrics'],
        'metrics_stgnn_single': load_json(REPO_ROOT / 'services' / 'inference' / 'outputs' / 'stgnn_gcn_lstm_nanjing_quarterly_qc_edgar_hybrid_norm' / 'metrics.json')['test_metrics'],
        'metrics_stgnn_multi': load_json(REPO_ROOT / 'services' / 'inference' / 'outputs' / 'stgnn_gcn_lstm_nanjing_quarterly_qc_edgar_hybrid_multistep' / 'metrics.json')['test_metrics'],
        'multi_seed_base': load_json(REPO_ROOT / 'services' / 'inference' / 'outputs' / 'multi_seed' / 'stgnn_gcn_lstm_nanjing_quarterly_qc_edgar_hybrid_multistep' / 'multi_seed_summary.json'),
        'multi_seed_combo': load_json(REPO_ROOT / 'services' / 'inference' / 'outputs' / 'multi_seed_combo064' / 'stgnn_gcn_lstm_nanjing_quarterly_qc_edgar_hybrid_multistep' / 'multi_seed_summary.json'),
        'sweep_summary': load_json(REPO_ROOT / 'services' / 'inference' / 'outputs' / 'adjacency_sweep' / 'stgnn_gcn_lstm_nanjing_quarterly_qc_edgar_hybrid_multistep__nanjing_quarterly_qc_edgar_hybrid' / 'sweep_summary.json'),
        'scenario': load_json(REPO_ROOT / 'services' / 'inference' / 'outputs' / 'stgnn_gcn_lstm_nanjing_quarterly_qc_edgar_hybrid_norm' / 'enhanced_scenario.json'),
        'data_counts': {
            'grid_nodes': csv_row_count(REPO_ROOT / 'data' / 'processed' / 'features' / 'nanjing' / 'quarterly' / 'grid_nodes.csv'),
            'sentinel2': csv_row_count(REPO_ROOT / 'data' / 'processed' / 'features' / 'nanjing' / 'quarterly' / 'sentinel2_features.csv'),
            'era5': csv_row_count(REPO_ROOT / 'data' / 'processed' / 'features' / 'nanjing' / 'quarterly' / 'era5_features.csv'),
            'edgar': csv_row_count(REPO_ROOT / 'data' / 'processed' / 'features' / 'nanjing' / 'quarterly' / 'edgar_features.csv'),
            'labels': csv_row_count(REPO_ROOT / 'data' / 'processed' / 'features' / 'nanjing' / 'quarterly' / 'labels_qc_complete.csv'),
        },
    }
    horizon = data['scenario'].get('forecast_timestamps', ['2025-Q1'])[0]
    delta_map = data['scenario'].get('delta_by_horizon', {}).get(horizon, {})
    delta_values = [abs(float(value)) for value in delta_map.values()]
    data['scenario_stats'] = {
        'horizon': horizon,
        'changed_nodes': len(data['scenario'].get('changed_nodes', [])),
        'max_abs_delta': max(delta_values) if delta_values else 0.0,
        'mean_abs_delta': sum(delta_values) / len(delta_values) if delta_values else 0.0,
        'gt_1e4': sum(value > 1e-4 for value in delta_values),
        'gt_1e3': sum(value > 1e-3 for value in delta_values),
    }
    return data


def ensure_figure_paths() -> dict[str, Path]:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    platform_target = FIGURE_DIR / 'fig3_platform.png'
    for candidate in [
        FIGURE_DIR / 'fig3_platform_wait90.png',
        FIGURE_DIR / 'fig3_platform_clear.png',
        REPO_ROOT / 'logs' / 'playwright' / 'docker-home-edge.png',
    ]:
        if candidate.exists():
            shutil.copyfile(candidate, platform_target)
            break
    figure_map = {
        'architecture': FIGURE_DIR / 'fig1_architecture.png',
        'pipeline': FIGURE_DIR / 'fig2_pipeline.png',
        'platform': platform_target,
        'metrics': FIGURE_DIR / 'fig4_metrics.png',
        'optimization': FIGURE_DIR / 'fig5_optimization.png',
    }
    missing = [str(path) for path in figure_map.values() if not path.exists()]
    if missing:
        raise FileNotFoundError('缺少图表素材：' + '; '.join(missing))
    return figure_map


def enable_update_fields_on_open(doc: Document) -> None:
    settings = doc.settings.element
    update_fields = settings.find(qn('w:updateFields'))
    if update_fields is None:
        update_fields = OxmlElement('w:updateFields')
        settings.append(update_fields)
    update_fields.set(qn('w:val'), 'true')


def trim_template(doc: Document) -> None:
    body = doc._element.body
    children = list(body.iterchildren())
    for child in children[10:-1]:
        body.remove(child)


def add_paragraph(doc: Document, text: str, style: str = '正文段落'):
    para = doc.add_paragraph(style=style)
    para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if style == '正文段落' else para.alignment
    run = para.add_run(text)
    if style == '正文段落':
        run.font.size = Pt(12)
    return para


def add_heading(doc: Document, text: str, level: int):
    return doc.add_paragraph(text, style=f'Heading {level}')


def add_hyperlink(paragraph, text: str, url: str):
    part = paragraph.part
    r_id = part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', True)
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)
    new_run = OxmlElement('w:r')
    r_pr = OxmlElement('w:rPr')
    color = OxmlElement('w:color')
    color.set(qn('w:val'), '0563C1')
    underline = OxmlElement('w:u')
    underline.set(qn('w:val'), 'single')
    r_pr.append(color)
    r_pr.append(underline)
    new_run.append(r_pr)
    text_node = OxmlElement('w:t')
    text_node.text = text
    new_run.append(text_node)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)


def add_seq_field(paragraph, label: str, default_text: str = '1'):
    fld = OxmlElement('w:fldSimple')
    fld.set(qn('w:instr'), f'SEQ {label} \\* ARABIC')
    run = OxmlElement('w:r')
    t = OxmlElement('w:t')
    t.text = default_text
    run.append(t)
    fld.append(run)
    paragraph._p.append(fld)


def add_caption(doc: Document, kind: str, title: str):
    para = doc.add_paragraph(style='Caption')
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.add_run(f'{kind} ')
    add_seq_field(para, kind)
    para.add_run(f'  {title}')
    return para


def add_figure(doc: Document, image_path: Path, title: str, width_cm: float):
    para = doc.add_paragraph(style='图表段落')
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.add_run().add_picture(str(image_path), width=Cm(width_cm))
    add_caption(doc, '图', title)


def set_cell_border(cell, **kwargs):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_borders = tc_pr.first_child_found_in('w:tcBorders')
    if tc_borders is None:
        tc_borders = OxmlElement('w:tcBorders')
        tc_pr.append(tc_borders)
    for edge in ('left', 'top', 'right', 'bottom'):
        edge_data = kwargs.get(edge)
        if edge_data is None:
            continue
        element = tc_borders.find(qn(f'w:{edge}'))
        if element is None:
            element = OxmlElement(f'w:{edge}')
            tc_borders.append(element)
        for key in ('val', 'sz', 'space', 'color'):
            if key in edge_data:
                element.set(qn(f'w:{key}'), str(edge_data[key]))


def format_cell(cell, text: str, bold: bool = False, align: int = WD_ALIGN_PARAGRAPH.CENTER):
    cell.text = ''
    para = cell.paragraphs[0]
    para.alignment = align
    para.paragraph_format.space_before = Pt(0)
    para.paragraph_format.space_after = Pt(0)
    run = para.add_run(text)
    run.bold = bold
    run.font.name = '宋体'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run.font.size = Pt(10.5)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER


def apply_three_line_table(table):
    line = {'val': 'single', 'sz': 12, 'space': 0, 'color': '000000'}
    nil = {'val': 'nil', 'sz': 0, 'space': 0, 'color': 'FFFFFF'}
    rows = table.rows
    last_index = len(rows) - 1
    for row in rows:
        for cell in row.cells:
            set_cell_border(cell, top=nil, left=nil, bottom=nil, right=nil)
    for cell in rows[0].cells:
        set_cell_border(cell, top=line, left=nil, bottom=line, right=nil)
    for cell in rows[last_index].cells:
        set_cell_border(cell, top=nil, left=nil, bottom=line, right=nil)


def add_table(doc: Document, title: str, headers: list[str], rows: Iterable[Iterable[str]], left_align_cols: set[int] | None = None):
    left_align_cols = left_align_cols or set()
    add_caption(doc, '表', title)
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    hdr = table.rows[0].cells
    for i, header in enumerate(headers):
        format_cell(hdr[i], header, bold=True)
    for row_values in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row_values):
            format_cell(cells[i], str(value), align=WD_ALIGN_PARAGRAPH.LEFT if i in left_align_cols else WD_ALIGN_PARAGRAPH.CENTER)
    apply_three_line_table(table)
    doc.add_paragraph('', style='图表段落')
    return table


def build_reference_paragraph(doc: Document, index: int, main_text: str, link: str | None = None):
    para = doc.add_paragraph(style='正文段落')
    para.paragraph_format.first_line_indent = Pt(0)
    para.paragraph_format.left_indent = Pt(0)
    para.paragraph_format.space_after = Pt(0)
    para.paragraph_format.space_before = Pt(0)
    para.add_run(f'[{index}] {main_text}')
    if link:
        para.add_run(' DOI/链接：')
        add_hyperlink(para, link, link)
    return para


def write_body(doc: Document, data: dict, figures: dict[str, Path]) -> None:
    add_heading(doc, '作品概述', 1)
    add_paragraph(doc, '“天穹智算——区域碳汇时空溯源与演化流式计算平台”面向“双碳”背景下区域碳汇精细化分析需求，围绕城市尺度碳源汇动态识别、网格级空间差异刻画、情景扰动下的演化响应评估三类核心问题，构建了“多源数据处理—图时序建模—服务聚合发布—前端交互呈现”的完整工程链路。作品以南京市为实证区域，将高精度季度 Sentinel-2 地表覆盖特征、ERA5 再分析气象变量、EDGAR 排放代理变量和质量控制标签统一到 309 个规则网格与 20 个季度时间片上，形成面向模型训练与平台展示的一体化数据底座，在不引入额外人工标注流程的前提下实现了季度尺度区域碳汇状态的持续更新与对比分析。')
    add_paragraph(doc, f'当前平台已经形成可运行的前后端一体化系统：后端以 FastAPI 为聚合层，前端以 Vue 3 与 Cesium 为可视化载体，推理层提供 LSTM 基线、单步 ST-GNN 和多步 ST-GNN 三类模型结果，并支持面向空间框选区域的情景推演。基于现有正式产物，最佳多步 ST-GNN 在测试集上取得了 MAE {data["metrics_stgnn_multi"]["mae"]:.4f}、RMSE {data["metrics_stgnn_multi"]["rmse"]:.4f} 的结果；在进一步进行邻接参数优化与 multi-seed 复验后，候选最优配置将 RMSE 进一步压降至 {data["multi_seed_combo"]["aggregate"]["rmse_min"]:.4f}。作品同时完成了 Docker 镜像发布与使用方精简交付目录整理，使平台具备“快速部署、直接访问、可复现实验”的交付能力。')

    add_heading(doc, '问题分析', 1)
    add_heading(doc, '问题来源', 2)
    add_paragraph(doc, '区域碳收支分析正从宏观统计逐步转向精细尺度、连续时序和可交互决策支持[1-4]。在城市与城市群尺度，碳汇能力并不是一个静态结果，而是会随着地表覆盖变化、气象条件波动以及人为排放压力变化而不断重塑；如果缺少网格级时空分析框架，管理部门往往只能获得年度总量或行政区平均值，难以识别局部生态修复成效、建成区扩张影响与高排放扰动的耦合关系。对高校团队而言，真正具有应用价值的作品也不应停留在离线建模，而要把数据预处理、模型训练、结果评估、情景推演和可视化发布连成一条完整链路。')
    add_heading(doc, '现有解决方案', 2)
    add_paragraph(doc, '已有研究已经在遥感碳监测、区域碳收支估算和图神经网络建模方面提供了扎实基础。卫星遥感与多源观测结合可以支持碳盘点、温室气体监测和区域生态系统碳汇核算[1][2][7]；围绕城市群或植被系统的时空碳收支研究，也为解释区域差异与驱动因素提供了方法框架[3][4]。与此同时，图神经网络与时空图模型已经在处理非欧式空间依赖、传播结构和时序耦合问题上展现出优势[5][6][11][12]。这些成果说明：区域碳汇问题既需要遥感与环境数据支撑，也适合采用图结构建模来刻画空间邻接与传输关系。')
    add_paragraph(doc, '但从工程落地角度看，现有公开方案仍存在两个明显缺口：一是很多研究以年度统计或论文级实验为主，缺乏适合业务复用的标准化数据装配与服务接口；二是已有平台型系统往往重展示、轻推演，或者重模型、轻交付，难以形成“数据—模型—服务—界面”闭环。本作品正是在这一缺口上展开设计，不追求脱离数据条件的宏大叙事，而是聚焦南京区域样本，在现有时序长度和数据规模约束下实现可运行、可优化、可验证的工程系统。')
    add_heading(doc, '本作品要解决的痛点问题', 2)
    add_paragraph(doc, '结合实际开发过程，本作品聚焦解决四项关键痛点：第一，季度尺度多源数据时空粒度不统一，直接用于训练会导致节点错位、时间错位和字段缺失；第二，单纯基于栅格独立建模难以表达风场影响、近邻传播与地类相似度，空间依赖被弱化后会直接影响碳汇预测稳定性；第三，模型实验往往停留在脚本级输出，难以被前端平台直接调用，也无法支撑用户从区域框选到结果解释的闭环交互；第四，作品交付若仍依赖本地源码环境，使用方难以快速部署，作品的展示性和可复现性都会受到限制。')
    add_heading(doc, '解决问题的思路', 2)
    add_paragraph(doc, '针对上述问题，作品采用了“高精度季度数据重建 + 图时序模型训练 + 服务聚合与情景推演 + 容器化交付”的总体思路。数据层先把遥感、气象、排放与标签信息统一到规则网格，形成结构清晰的季度特征矩阵；建模层通过 hybrid_wind_knn 邻接构造把距离、风向传播和相似特征耦合进图结构；服务层统一读取训练产物、预测结果和情景推演结果，并向前端输出仪表板、模型指标和区域推演结果；交付层则通过一键启动脚本与 Docker 镜像发布，降低环境依赖。')

    add_heading(doc, '技术方案', 1)
    add_heading(doc, '总体架构设计', 2)
    add_paragraph(doc, '作品总体架构如图所示，按照多源数据接入、遥感特征构建、图时序推理、场景推演、服务聚合和展示交付六个层次组织。这样的分层方式一方面便于将实验脚本、服务接口和前端界面解耦，另一方面也方便在后续扩展城市区域时复用相同的数据装配与部署流程。对于竞赛作品而言，这种架构保证了算法能力不是孤立存在，而是通过统一接口进入平台，直接服务于区域碳汇识别和演化分析任务。')
    add_figure(doc, figures['architecture'], '平台总体技术架构', 15.8)

    add_heading(doc, '数据融合、图建模与平台落地流程', 2)
    add_paragraph(doc, '从工程实现看，作品并未把“流式”简单理解为高并发消息系统，而是将其落实为一条可持续滚动更新的处理流水线：高精度季度遥感数据首先进入特征拼接与质量控制阶段，再与 ERA5、EDGAR 和标签信息按网格、季度对齐，随后构建带风向和相似度权重的邻接矩阵，供 ST-GNN 与 LSTM 模型训练使用；模型输出的预测结果、指标文件和最佳权重再被后端聚合，最终通过前端平台以地图、统计卡片和场景推演结果的形式对外提供服务。该流程既保留了科研实验对可解释性的要求，也满足平台产品对可部署性的要求。')
    add_figure(doc, figures['pipeline'], '数据融合、图建模与平台落地流程', 16.4)
    add_table(
        doc,
        '多源数据底座与处理结果概览',
        ['数据类别', '主要来源', '统一粒度', '结果规模'],
        [
            ['网格节点', '南京研究区规则网格', '空间网格', f"{data['data_counts']['grid_nodes']} 个节点"],
            ['遥感地表特征', '高精度季度 Sentinel-2', '309 节点 × 20 季度', f"{data['data_counts']['sentinel2']} 行"],
            ['气象特征', 'ERA5 再分析数据', '309 节点 × 20 季度', f"{data['data_counts']['era5']} 行"],
            ['排放代理', 'EDGAR 排放数据', '309 节点 × 20 季度', f"{data['data_counts']['edgar']} 行"],
            ['质量控制标签', '季度净碳通量标签', '节点-季度监督标签', f"{data['data_counts']['labels']} 行"],
        ],
    )

    add_heading(doc, '核心建模策略与参数组织', 2)
    add_paragraph(doc, '在模型设计上，作品没有选择一味堆叠复杂网络，而是根据现有数据规模采取了“轻量图结构 + 时序建模 + 结果复验”的稳健策略。正式训练集中共包含 20 个季度、309 个节点和 11 个输入特征，其中既包括 6 类地表覆盖与植被表征，也包括地表温度、风场、降水和排放代理变量。多步 ST-GNN 使用 4 个季度作为输入窗口，对未来 2 个季度进行滚动预测；单步 ST-GNN 则聚焦单期预测；LSTM 基线用于给出无图结构条件下的对照结果。邻接矩阵采用 hybrid_wind_knn 构造方式，把距离半径、k 近邻、风向传播与特征相似度一并纳入建图逻辑，这一设计在后续参数优化中也被证明比默认配置更有提升空间。')
    add_table(
        doc,
        '系统模块与核心职责',
        ['模块层', '核心实现', '输出结果'],
        [
            ['数据处理层', '季度遥感重建、ERA5/EDGAR 对齐、质量控制', '统一训练数据集与特征统计'],
            ['模型训练层', 'LSTM、多步 ST-GNN、单步 ST-GNN', '权重文件、预测结果、评估指标'],
            ['推演执行层', '区域框选、节点筛选、情景扰动与结果回写', 'baseline/scenario/delta 结果'],
            ['服务聚合层', 'FastAPI 接口、模型产物加载、场景任务执行', '仪表板接口、推演接口、健康检查'],
            ['前端展示层', 'Vue 3、Cesium、统计卡片与情景交互', '地图界面与模型展示'],
            ['交付部署层', '一键启动脚本、Docker 镜像与 Release 包', '可复现部署与快速交付'],
        ],
        left_align_cols={1, 2},
    )
    add_table(
        doc,
        '正式模型关键训练配置',
        ['模型', '输入窗口', '预测步长', '输入特征数', '关键设置'],
        [
            ['LSTM 多步基线', '4', '2', '11', 'hidden_dim=64，epochs=40'],
            ['ST-GNN 单步', '4', '1', '11', 'graph_hidden_dim=32，temporal_hidden_dim=64'],
            ['ST-GNN 多步', '4', '2', '11', 'hybrid_wind_knn 图结构，epochs=50'],
        ],
    )

    add_heading(doc, '系统实现', 1)
    add_heading(doc, '多源季度数据重建与标准化', 2)
    add_paragraph(doc, '在数据实现层，作品对“data_for_memberA”中的高精度季度 Sentinel-2 表进行了训练链路重建，并将其纳入正式处理流程。重建后的季度特征表覆盖 2020-Q1 至 2024-Q4，共 20 个时间点，形成 6180 条节点—季度记录，并保持 309 个节点在每个季度上的完整覆盖。为了保证训练输入质量，系统对时间格式、节点主键、数值字段和缺失情况进行了统一检查，避免了由于季度命名差异、模板列空缺和拼接链路不一致带来的训练噪声。相对于只保留少量地类比例的简化版本，这次重建后的正式表保留了 NDVI、林地比例、农田比例、水体比例、建成区比例和植被面积比例等核心遥感特征，为后续图建模提供了更稳定的输入基础。')
    add_heading(doc, '推理服务与情景推演实现', 2)
    add_paragraph(doc, '后端服务负责把模型产物转化为可调用平台能力。系统通过固定目录读取 metrics.json、latest_prediction.json 和 best.pt 等正式产物，并在需要执行情景推演时调用推理脚本完成区域节点筛选、节点属性扰动和结果回写。当前正式情景文件显示，在 2025-Q1 预测时点上，系统能够对用户框选的 {changed_nodes} 个节点执行扰动，并生成完整的 baseline、scenario 与 delta 结果；其中绝对差值大于 1e-4 的节点共有 {gt_1e4} 个，最大绝对差值为 {max_delta:.6f}。这一机制说明作品并不是简单展示离线指标，而是已经具备围绕空间交互执行动态推演的能力。'.format(changed_nodes=data['scenario_stats']['changed_nodes'], gt_1e4=data['scenario_stats']['gt_1e4'], max_delta=data['scenario_stats']['max_abs_delta']))
    add_heading(doc, '前端交互与交付形态', 2)
    add_paragraph(doc, '前端平台采用 Vue 3 + Cesium 组织交互界面，以南京研究区为主视图，整合了研究区域标识、当前季度、碳汇强度图层、统计面板和情景推演入口。围绕前端实际使用过程，作品重点修复了二次新建情景后无法重新框选区域、Cesium 生产构建渲染异常、启动脚本与浏览器自动跳转不一致等工程问题，并通过 Docker 化将前后端、反向代理和交付目录打包为统一发布方案。这样一来，评审或使用方不需要再次搭建 Python、Node.js 与本地训练环境，只需执行容器命令即可启动完整平台。图 3 展示了平台在地图底图与碳汇强度层清晰加载后的正式界面。')
    add_figure(doc, figures['platform'], '平台主界面与研究区碳汇强度展示', 16.2)

    add_heading(doc, '智能体使用情况', 1)
    add_paragraph(doc, '作品开发过程中引入了以 Codex 为代表的智能体协作方式，但始终坚持“人工主导决策、智能体辅助执行”的原则。智能体主要承担三类任务：一是代码与配置检视，例如定位前端地图显示异常、情景推演二次框选失效、Docker 生产构建兼容性等问题，并在不破坏平台接口的前提下给出修复方案；二是实验自动化支持，例如补齐 multi-seed 与 adjacency sweep 脚本，对比正式模型与候选模型的指标表现；三是交付文档辅助，例如整理 Docker 发布目录、Release 说明和作品报告初稿。所有关键修改均经过本地构建、接口回归和页面检查后才被保留，因此智能体在本作品中的角色更接近“工程增效器”，而不是脱离项目事实的自动生成工具。')
    add_paragraph(doc, '从使用效果看，智能体最大的价值不在于替代建模判断，而在于缩短工程闭环的调试时间。尤其在前后端联调、文档与部署材料整理、实验结果复核等高重复度工作中，智能体能够快速完成搜索、比对和脚本化实现，使团队把更多精力放在问题抽象、指标判断和结果解释上。这种协同方式与作品本身强调的“数据—模型—服务”闭环是一致的，也为后续作品维护提供了更高的可追溯性。')

    add_heading(doc, '测试分析', 1)
    add_heading(doc, '平台联调与数据完整性验证', 2)
    add_paragraph(doc, '作品测试不仅关注模型误差，还重点关注平台能否稳定调用正式产物。联调结果表明：后端健康检查、前端首页访问、仪表板读取、预测结果加载和情景推演执行均已通过；平台读取的研究区节点数量为 309，正式接入模型数量为 3，情景推演状态可返回 completed，说明平台链路已经从“可训练”进一步发展为“可部署、可调用、可展示”。在数据层面，正式季度 Sentinel-2 表、ERA5 表与 EDGAR 表均保持 6180 条记录规模，与 309 节点 × 20 季度的理论规模一致，训练输入没有出现链路断裂。')
    add_table(
        doc,
        '平台联调与情景推演验证结果',
        ['验证项', '结果'],
        [
            ['后端健康检查', '通过（/api/v1/health 返回 200）'],
            ['前端首页访问', '通过（平台主页返回 200）'],
            ['平台接入模型数量', '3 个正式模型产物'],
            ['预测结果覆盖规模', '309 个节点'],
            ['情景推演执行状态', 'completed'],
            ['情景推演影响统计', f"|Δ|>1e-4 节点 {data['scenario_stats']['gt_1e4']} 个，最大绝对差值 {data['scenario_stats']['max_abs_delta']:.6f}"],
        ],
        left_align_cols={1},
    )

    add_heading(doc, '模型效果对比', 2)
    add_paragraph(doc, '正式模型测试结果如图 4 和表 4 所示。与 LSTM 多步基线相比，单步 ST-GNN 和多步 ST-GNN 都表现出更优的误差水平，其中多步 ST-GNN 在 MAE 和 RMSE 两项指标上均取得当前正式最优结果。这说明在当前样本规模下，引入图结构对空间依赖进行编码是有效的；同时，多步预测方案相较于单步方案更适合承接平台面向未来季度滚动预测的任务。')
    add_figure(doc, figures['metrics'], '正式模型测试集误差对比', 16.0)
    add_table(
        doc,
        '正式模型测试指标对比',
        ['模型', 'MAE', 'RMSE', '结论'],
        [
            ['LSTM 多步基线', f"{data['metrics_lstm']['mae']:.6f}", f"{data['metrics_lstm']['rmse']:.6f}", '作为无图结构对照组'],
            ['ST-GNN 单步', f"{data['metrics_stgnn_single']['mae']:.6f}", f"{data['metrics_stgnn_single']['rmse']:.6f}", '空间建模有效，但单步预测略弱'],
            ['ST-GNN 多步', f"{data['metrics_stgnn_multi']['mae']:.6f}", f"{data['metrics_stgnn_multi']['rmse']:.6f}", '当前正式最优模型'],
        ],
        left_align_cols={3},
    )

    add_heading(doc, '优化复验与结果分析', 2)
    add_paragraph(doc, '在正式模型基础上，团队进一步开展了 multi-seed 与邻接参数扫描实验。结果显示，原始多 seed 复验并没有刷新当前正式模型的最优值，说明当前正式权重已经是这一组随机种子中的最好结果；而 adjacency sweep 则找到了更优的邻接组合 combo_064，其参数为 radius_km=18、k=8、wind_scale=0.45、similarity_weight=0.35。对该组合再次执行 multi-seed 复验后，最优 RMSE 从正式模型的 {base_rmse:.6f} 下降到 {combo_rmse:.6f}，最优 MAE 从 {base_mae:.6f} 下降到 {combo_mae:.6f}。虽然均值波动并未显著收敛，但该结果说明图结构参数仍然存在可优化空间，也为平台后续模型升级提供了可信候选。'.format(base_rmse=data['metrics_stgnn_multi']['rmse'], combo_rmse=data['multi_seed_combo']['aggregate']['rmse_min'], base_mae=data['metrics_stgnn_multi']['mae'], combo_mae=data['multi_seed_combo']['aggregate']['mae_min']))
    add_figure(doc, figures['optimization'], '邻接参数优化与 multi-seed 复验结果', 16.0)
    add_table(
        doc,
        '优化实验关键结果',
        ['实验项', 'MAE', 'RMSE', '说明'],
        [
            ['当前正式最优', f"{data['metrics_stgnn_multi']['mae']:.6f}", f"{data['metrics_stgnn_multi']['rmse']:.6f}", '正式平台默认多步 ST-GNN'],
            ['combo_064 最优', f"{data['multi_seed_combo']['aggregate']['mae_min']:.6f}", f"{data['multi_seed_combo']['aggregate']['rmse_min']:.6f}", '邻接参数优化后候选最优'],
            ['当前多 seed 均值', f"{data['multi_seed_base']['aggregate']['mae_mean']:.6f}", f"{data['multi_seed_base']['aggregate']['rmse_mean']:.6f}", '用于判断当前方案稳定性'],
            ['combo_064 多 seed 均值', f"{data['multi_seed_combo']['aggregate']['mae_mean']:.6f}", f"{data['multi_seed_combo']['aggregate']['rmse_mean']:.6f}", '提升主要体现于最优值而非方差收敛'],
        ],
        left_align_cols={3},
    )

    add_heading(doc, '作品总结', 1)
    add_heading(doc, '作品特色与创新点', 2)
    add_paragraph(doc, '本作品的创新性主要体现在三个方面。其一，作品没有把区域碳汇分析停留在单次离线建模，而是围绕季度尺度构建了可复用的数据处理、训练与服务发布闭环，形成了真正可运行的平台原型；其二，在图结构设计上，将距离半径、近邻连接、风向传播和特征相似度融合到 hybrid_wind_knn 邻接中，使空间传播关系更贴近区域碳汇问题本身；其三，作品重视交付和验证，完成了启动脚本、Docker 发布、Release 交付目录和前后端联调，使评审和使用方能够以较低门槛直接访问系统。')
    add_heading(doc, '应用推广', 2)
    add_paragraph(doc, '作品当前以南京研究区为样本完成验证，但其流程设计并不是与单一区域强绑定的定制脚本，而是按照“网格节点—季度特征—模型产物—服务接口—前端展示”的统一链路组织，因此具有较强的迁移潜力。只要目标区域能够提供规则网格节点、季度遥感特征、气象变量、排放代理变量以及相应的质量控制标签，现有的数据装配、特征拼接、图构建、模型训练、预测生成和服务聚合流程就可以复用到其他城市或城市群场景中。从工程实现角度看，本作品已经把训练数据规范、模型产物目录、接口读取方式和前端展示入口统一下来，这意味着迁移时并不需要从零重做平台，只需替换区域数据并按既有流程重新训练与部署即可。')
    add_paragraph(doc, '结合当前平台能力，作品在生态修复评估、土地利用变化跟踪、区域碳收支对比分析、城市群生态空间治理和教学展示等场景中都具有现实应用基础。例如，在生态修复与国土整治场景中，平台可以利用季度尺度变化持续观察植被恢复与建成区扩张对区域碳汇的影响；在区域横向比较场景中，可以以统一网格和统一时间粒度对不同片区的碳汇状态、扰动敏感性和演化趋势进行对照；在教学与科研训练场景中，作品又具备较强的可演示性，既能展示多源遥感与环境数据如何进入图时序模型，也能通过情景推演界面帮助使用者直观理解空间扰动是如何影响预测结果的。再结合已经完成的 Docker 镜像发布和精简交付目录，使用单位即使不具备完整源码环境，也可以较快完成平台部署和效果复现，这进一步增强了作品的推广可用性。')
    add_heading(doc, '作品展望', 2)
    add_paragraph(doc, '受限于当前样本长度与数据规模，作品后续仍有较为明确且可执行的深化方向。首先是在数据层继续补充更长时间跨度的季度序列，并逐步引入更加完整、稳定的高精度遥感特征，以进一步增强模型对季节波动、地类变化和跨阶段趋势的刻画能力。当前平台已经完成 2020-Q1 至 2024-Q4 的季度数据重建和正式训练，说明数据接入与规范化流程已经打通，后续需要做的并不是推翻现有体系，而是在既有链路上持续补齐时序长度、统一特征标准并加强质量控制，这会直接提升模型稳健性和跨时段泛化能力。')
    add_paragraph(doc, '其次是在模型和平台协同层面继续做增量优化。现有实验已经证明，邻接参数扫描可以在正式模型基础上带来一定提升，因此后续可以在完成更多 seed 复验和平台回归测试后，将当前候选最优图参数升级为正式模型配置；同时，进一步推动主地图强度层与后端推理结果的统一，使地图主视图、指标面板和情景推演结果在同一套正式产物上联动展示。除此之外，还可以继续完善使用方部署体验，例如围绕镜像版本管理、交付文档和结果更新机制形成更标准的发布流程。需要强调的是，这些展望都建立在现有工程链路、前后端平台、Docker 交付和模型训练体系已经跑通的基础上，属于能够逐步落地的工程完善方向，而不是脱离项目现实条件的空泛设想。')

    add_heading(doc, '参考文献', 1)
    references = [
        ('刘良云, 马会杰, 胡斯勒图, 马会良, 马会莲, 王力哲. 全球碳盘点卫星遥感监测方法、进展与挑战[J]. 遥感学报, 2022, 26(10): 1918-1934.', 'https://doi.org/10.11834/jrs.20221806'),
        ('丁雷, 马会杰, 刘良云. 温室气体的卫星遥感——进展与趋势[J]. 遥感学报, 2023, 27(10): 2300-2325.', 'https://doi.org/10.11834/jrs.20233057'),
        ('夏四友, 杨宇. 基于主体功能区的京津冀城市群碳收支时空分异与碳补偿分区[J]. 地理学报, 2022, 77(3): 679-696.', 'https://doi.org/10.11821/dlxb202203013'),
        ('刘文利, 马会瑞, 韩升. 中国植被碳源/汇时空演变特征及其驱动因素[J]. 生态学报, 2024, 44(4): 1416-1429.', 'https://doi.org/10.20103/j.stxb.202303090445'),
        ('王健宗, 孔令炜, 黄章成, 肖京. 图神经网络综述[J]. 计算机工程, 2021, 47(2): 1-14.', 'https://doi.org/10.19678/j.issn.1000-3428.0058382'),
        ('姜山, 丁治明, 朱美玲, 严瑾, 徐馨润. 面向时空图建模的图小波卷积神经网络模型[J]. 软件学报, 2021, 32(11): 3486-3500.', 'https://doi.org/10.13328/j.cnki.jos.006170'),
        ('Drusch M, Del Bello U, Carlier S, et al. Sentinel-2: ESA’s Optical High-Resolution Mission for GMES Operational Services[J]. Remote Sensing of Environment, 2012, 120: 25-36.', 'https://doi.org/10.1016/j.rse.2011.11.026'),
        ('Hersbach H, Bell B, Berrisford P, et al. ERA5 hourly data on single levels from 1940 to present[DB/OL]. Copernicus Climate Change Service Climate Data Store, 2023.', 'https://doi.org/10.24381/cds.adbb2d47'),
        ('Crippa M, Guizzardi D, Solazzo E, et al. EDGAR v6.0 Greenhouse Gas Emissions[DB/OL]. European Commission, Joint Research Centre, 2024.', 'https://doi.org/10.2905/JRC.787T5VR'),
        ('Hochreiter S, Schmidhuber J. Long Short-Term Memory[J]. Neural Computation, 1997, 9(8): 1735-1780.', 'https://doi.org/10.1162/neco.1997.9.8.1735'),
        ('Kipf T N, Welling M. Semi-Supervised Classification with Graph Convolutional Networks[EB/OL]. arXiv:1609.02907, 2017.', 'https://arxiv.org/abs/1609.02907'),
        ('Yu B, Yin H, Zhu Z. Spatio-Temporal Graph Convolutional Networks: A Deep Learning Framework for Traffic Forecasting in Transportation Networks[C]//Proceedings of the 27th International Joint Conference on Artificial Intelligence. 2018: 3634-3640.', 'https://www.ijcai.org/proceedings/2018/0505.pdf'),
    ]
    for idx, (main_text, link) in enumerate(references, start=1):
        build_reference_paragraph(doc, idx, main_text, link)


def render_preview_pdf(docx_path: Path, pdf_path: Path) -> int:
    script = '''
from pathlib import Path
import sys
import win32com.client

docx = Path(sys.argv[1])
pdf = Path(sys.argv[2])
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = 0
try:
    doc = word.Documents.Open(str(docx), ReadOnly=True)
    if doc.TablesOfContents.Count:
        doc.TablesOfContents(1).Update()
    doc.Fields.Update()
    doc.Repaginate()
    doc.ExportAsFixedFormat(str(pdf), 17)
    print(doc.ComputeStatistics(2))
    doc.Close(False)
finally:
    word.Quit()
'''
    completed = subprocess.run(
        ['python', '-', str(docx_path), str(pdf_path)],
        input=script,
        capture_output=True,
        text=True,
        check=True,
    )
    numbers = [line.strip() for line in completed.stdout.splitlines() if line.strip().isdigit()]
    return int(numbers[-1]) if numbers else -1


def validate_output(docx_path: Path) -> None:
    doc = Document(str(docx_path))
    forbidden = ['填写说明', '快捷键', '示例（', '正式编撰文档时删除']
    found = []
    for para in doc.paragraphs:
        for token in forbidden:
            if token in para.text:
                found.append(token)
    if found:
        raise RuntimeError('文档仍包含模板残留：' + ', '.join(sorted(set(found))))


def main() -> None:
    data = collect_data()
    figures = ensure_figure_paths()
    doc = Document(str(TEMPLATE_PATH))
    trim_template(doc)
    enable_update_fields_on_open(doc)
    write_body(doc, data, figures)
    doc.save(str(OUTPUT_DOCX))
    validate_output(OUTPUT_DOCX)
    pages = render_preview_pdf(OUTPUT_DOCX, OUTPUT_PDF)
    print(f'docx={OUTPUT_DOCX}')
    print(f'pdf={OUTPUT_PDF}')
    print(f'pages={pages}')


if __name__ == '__main__':
    main()
