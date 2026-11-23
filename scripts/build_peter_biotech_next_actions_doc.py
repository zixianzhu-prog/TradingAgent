from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "peter-biotech-agent-next-actions-2026-11-16.docx"


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_borders(cell, color="D9D9D9", size="6"):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = "w:" + edge
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:color"), color)


def set_cell_margins(cell, top=110, start=120, bottom=110, end=120):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn("w:" + margin))
        if node is None:
            node = OxmlElement("w:" + margin)
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def prevent_row_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    cant_split = OxmlElement("w:cantSplit")
    cant_split.set(qn("w:val"), "true")
    tr_pr.append(cant_split)


def set_run_font(run, size=None, bold=None, color=None):
    run.font.name = "Arial Unicode MS"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial Unicode MS")
    run._element.rPr.rFonts.set(qn("w:cs"), "Arial Unicode MS")
    lang = run._element.rPr.find(qn("w:lang"))
    if lang is None:
        lang = OxmlElement("w:lang")
        run._element.rPr.append(lang)
    lang.set(qn("w:val"), "zh-CN")
    lang.set(qn("w:eastAsia"), "zh-CN")
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color is not None:
        run.font.color.rgb = RGBColor(*color)


def add_text(paragraph, text, bold=False, color=None, size=None):
    run = paragraph.add_run(text)
    set_run_font(run, size=size, bold=bold, color=color)
    return run


def style_table(table, widths=None):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for r_idx, row in enumerate(table.rows):
        prevent_row_split(row)
        if r_idx == 0:
            set_repeat_table_header(row)
        for c_idx, cell in enumerate(row.cells):
            set_cell_borders(cell)
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if widths and c_idx < len(widths):
                cell.width = Inches(widths[c_idx])
            if r_idx == 0:
                set_cell_shading(cell, "1F4E78")
                for paragraph in cell.paragraphs:
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in paragraph.runs:
                        set_run_font(run, size=9.5, bold=True, color=(255, 255, 255))
            else:
                if r_idx % 2 == 0:
                    set_cell_shading(cell, "F3F7FA")
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.space_after = Pt(0)
                    paragraph.paragraph_format.line_spacing = 1.08
                    for run in paragraph.runs:
                        set_run_font(run, size=9.5)


def add_bullet(doc, text, level=0):
    p = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.1
    add_text(p, text)
    return p


def add_number(doc, text):
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.12
    add_text(p, text)
    return p


def add_heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    p.paragraph_format.keep_with_next = True
    return p


doc = Document()
section = doc.sections[0]
section.page_width = Inches(8.5)
section.page_height = Inches(11)
section.top_margin = Inches(0.72)
section.bottom_margin = Inches(0.72)
section.left_margin = Inches(0.78)
section.right_margin = Inches(0.78)

styles = doc.styles
normal = styles["Normal"]
normal.font.name = "Arial Unicode MS"
normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial Unicode MS")
normal._element.rPr.rFonts.set(qn("w:cs"), "Arial Unicode MS")
normal.font.size = Pt(10.5)
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.15

for name, size, before, after in (
    ("Title", 25, 0, 8),
    ("Heading 1", 17, 14, 6),
    ("Heading 2", 13, 10, 4),
    ("Heading 3", 11.5, 8, 3),
):
    style = styles[name]
    style.font.name = "Arial Unicode MS"
    style._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial Unicode MS")
    style._element.rPr.rFonts.set(qn("w:cs"), "Arial Unicode MS")
    style.font.size = Pt(size)
    style.font.color.rgb = RGBColor(0, 0, 0)
    style.font.bold = name != "Title" or True
    style.paragraph_format.space_before = Pt(before)
    style.paragraph_format.space_after = Pt(after)

# Remove the decorative border inherited by some Word Title styles.
title_style_ppr = styles["Title"]._element.get_or_add_pPr()
title_border = title_style_ppr.find(qn("w:pBdr"))
if title_border is not None:
    title_style_ppr.remove(title_border)

title = doc.add_paragraph(style="Title")
title.alignment = WD_ALIGN_PARAGRAPH.LEFT
add_text(title, "前瞻生物科技研究 Agent 下一阶段行动计划", bold=True, size=25)

subtitle = doc.add_paragraph()
subtitle.paragraph_format.space_after = Pt(14)
add_text(subtitle, "Peter 会议笔记整理", bold=True, color=(31, 78, 121), size=11)
add_text(subtitle, "  2026 年 11 月 16 日", color=(90, 90, 90), size=10)

intro = doc.add_paragraph()
intro.paragraph_format.space_after = Pt(10)
add_text(intro, "结论  ", bold=True)
add_text(
    intro,
    "下一阶段应把现有 AI 医疗研究 Agent 升级为更早期的生物科技信号系统。系统需要从基础研究和新技术路线出发，追踪公司成立、融资、大药企采用、临床进展、FDA 反馈、核心人员变化和估值，再通过 Serenity 方法判断哪些公司真正控制了难以替代的环节。近期目标仍是研究和验证，不连接券商，也不执行真实交易。",
)

add_heading(doc, "一 会议需求转化", 1)
p = doc.add_paragraph()
add_text(p, "Peter 希望 Agent 更早看到趋势。", bold=True)
add_text(
    p,
    "现有系统已经能够收集新闻、SEC 文件、FDA 事件和市场数据。下一步需要把研究起点向前移动，从已经形成收入的公司延伸到理论突破、科研团队、早期公司和资本投入，同时保留财务、监管和负面证据审查。",
)

table = doc.add_table(rows=1, cols=3)
headers = ["Peter 的关注点", "系统应完成的任务", "预期输出"]
for i, h in enumerate(headers):
    table.rows[0].cells[i].text = h
rows = [
    ("新的理论和研究方向", "追踪 MIT 等研究机构、同行评审论文和预印本，识别可能形成新产品或新公司的技术路线", "技术主题、关键论文、研究团队和可商业化问题"),
    ("更早发现公司", "建立论文到研究者、公司、投资人、合作药企和临床资产的关系图", "早期公司观察名单及其证据链"),
    ("大药企是否真正采用", "区分研究合作、许可、采购、里程碑付款和真实收入", "采用强度、收入验证和客户依赖"),
    ("临床与 FDA 风险", "解释临床阶段、试验结果、FDA 批准、完整回复函和临床暂停的实际含义", "监管状态、主要缺口和下一检查点"),
    ("团队和资本信号", "追踪公开的高管变动、创始人增持、融资、董事变化和专业文章", "人员变化原因、资本信心和治理风险"),
    ("价格是否合理", "增加可比公司、融资后估值、稀释、现金跑道和情景估值", "观察、等待、可进一步研究的价格区间"),
]
for row_data in rows:
    cells = table.add_row().cells
    for i, value in enumerate(row_data):
        cells[i].text = value
style_table(table, widths=[1.55, 3.15, 2.0])

add_heading(doc, "二 优先研究的生物科技方向", 1)
p = doc.add_paragraph()
add_text(
    p,
    "系统不应只搜索带有 AI 标签的公司。它应先识别医疗和生物科技中尚未解决的问题，再判断新方法能否降低研发失败率、缩短开发周期、改善诊断或形成新的治疗方式。首批研究方向如下。",
)

tracks = [
    ("AI 药物发现和蛋白质设计", "分子生成、结构预测、靶点发现、计算化学和实验自动化", "是否被药企纳入真实研发流程，是否产生合同价值、里程碑或药物管线"),
    ("精准肿瘤学和临床基因组学", "液体活检、伴随诊断、多组学和临床数据网络", "数据规模是否形成壁垒，检测能否影响治疗决定，报销是否成立"),
    ("医学影像和临床决策", "影像 AI、心脏分析、神经监测和病理 AI", "FDA 许可、计费代码、保险覆盖、指南采用和医院工作流"),
    ("新型治疗平台", "细胞治疗、基因编辑、RNA、抗体和递送技术", "动物和早期临床结果能否转化为人体安全性、有效性和可制造性"),
    ("生物制造和研究基础设施", "测序设备、试剂、实验自动化、云计算和数据基础设施", "下游公司是否把它列为单一来源或难以替代的供应商"),
    ("生物安全和新发病原体", "疫情、耐药性、疫苗平台、政府储备和生物防御", "WHO 和政府事件是否带来持续采购，还是只有短期市场情绪"),
]
table = doc.add_table(rows=1, cols=3)
for i, h in enumerate(["研究方向", "主要技术", "核心验证问题"]):
    table.rows[0].cells[i].text = h
for row_data in tracks:
    cells = table.add_row().cells
    for i, value in enumerate(row_data):
        cells[i].text = value
style_table(table, widths=[1.75, 2.25, 2.7])

add_heading(doc, "三 新增信号体系", 1)
signals = [
    ("科研突破", "高质量论文、新方法、可重复实验结果、专利、研究团队持续发表", "论文热度不能单独证明商业价值，需要检查可制造性、临床适用性和知识产权归属"),
    ("公司形成和融资", "新公司成立、种子轮和后续融资、NIH 或政府资助、知名投资机构参与", "融资说明有人愿意承担风险，但不能证明技术有效"),
    ("大药企采用", "许可协议、共同研发、采购、里程碑付款、药企在财报或临床记录中使用该平台", "合作公告必须区分试点、可取消合同、一次性付款和持续收入"),
    ("临床进展", "IND 获准、一期安全性、二期有效性信号、三期主要终点、试验招募和终止", "样本量、终点设计、对照组、副作用和统计显著性需要分别判断"),
    ("人员和治理", "创始人增持、管理层增持、关键科学家加入或离职、董事变化、公开专业文章", "只使用公开职业信息和监管披露；离职本身不是看空证据，需要结合原因和后续安排"),
    ("负面事件", "严重不良反应、临床暂停、数据延迟、FDA 拒绝、制造问题、诉讼、融资压力和稀释", "负面事件触发相关 Serenity 门槛重新审查，而不是直接给出卖出结论"),
    ("价格和资金", "市值、现金跑道、债务、稀释、成交量、可比公司估值和市场已计价程度", "小于 10 亿美元可作为早期候选筛选条件，但不能替代流动性和基本面检查"),
]
table = doc.add_table(rows=1, cols=3)
for i, h in enumerate(["信号类别", "需要追踪的内容", "解释规则"]):
    table.rows[0].cells[i].text = h
for row_data in signals:
    cells = table.add_row().cells
    for i, value in enumerate(row_data):
        cells[i].text = value
style_table(table, widths=[1.25, 2.55, 2.9])

add_heading(doc, "四 临床和 FDA 状态的正确解释", 1)
p = doc.add_paragraph()
add_text(p, "动物实验通过不能直接上市。", bold=True)
add_text(
    p,
    "动物实验属于临床前研究，主要用于初步判断安全性、作用机制和剂量。一般还需要提交 IND，完成临床一期、二期和三期，并通过 FDA 的 NDA 或 BLA 审查。不同产品的具体路径会有所不同。",
)

table = doc.add_table(rows=1, cols=3)
for i, h in enumerate(["监管或研发状态", "它通常能证明什么", "它不能证明什么"]):
    table.rows[0].cells[i].text = h
reg_rows = [
    ("动物实验结果", "存在初步生物学作用或安全性信号", "不能证明人体安全、人体有效或可以上市"),
    ("IND 获准", "公司可以开始人体临床试验", "不能证明药物有效，也不是上市批准"),
    ("一期临床", "主要提供安全性、耐受性和剂量信息", "小样本疗效信号通常不能确认商业价值"),
    ("二期临床", "提供初步有效性和剂量选择依据", "仍可能在三期失败"),
    ("三期临床", "在更大样本中验证主要终点和风险收益", "仍需监管审查、制造检查和标签谈判"),
    ("FDA 批准", "产品可以按照批准用途在美国销售", "不保证报销、医院采用、盈利或股价上涨"),
    ("完整回复函 CRL", "FDA 暂不批准，并列出需要解决的问题", "不能简单等同于项目永久失败"),
    ("临床暂停", "监管机构要求暂停部分或全部试验", "严重程度取决于安全、数据、制造或程序原因"),
]
for row_data in reg_rows:
    cells = table.add_row().cells
    for i, value in enumerate(row_data):
        cells[i].text = value
style_table(table, widths=[1.35, 2.55, 2.8])

p = doc.add_paragraph()
add_text(p, "FDA 负面决定必须按原因拆解。", bold=True)
add_text(
    p,
    "安全性问题、疗效不足、样本或信息不完整、生产质量问题和标签分歧的含义不同。Agent 应读取 FDA 原文和公司披露，记录可修复性、预计时间、资金消耗和对核心论点的影响，不能只根据新闻中的 approved 或 rejected 做判断。",
)

add_heading(doc, "五 核心人物和管理团队追踪", 1)
p = doc.add_paragraph()
add_text(
    p,
    "人物追踪应围绕公开、可验证且与公司执行能力有关的信息。LinkedIn、公司网站、SEC 文件、论文作者信息和会议演讲可以作为公开来源，但社交媒体内容只能提供研究线索。",
)
for item in [
    "建立创始人、首席科学家、临床负责人、监管负责人和主要董事的公开档案。",
    "记录加入、离职、职位变化、公开增持或减持，以及核心人员是否继续发表与公司技术相关的研究。",
    "离职事件触发治理和执行门槛重审，重点检查离职原因、继任安排、临床或研发节点是否延期。",
    "管理层增持是信心信号之一，但必须结合交易规模、薪酬安排、融资需求和公司现金情况解释。",
    "不收集私人信息，不根据传闻推断个人动机，也不把一次发帖当成投资证据。",
]:
    add_bullet(doc, item)

add_heading(doc, "六 Serenity 和市场验证的升级", 1)
p = doc.add_paragraph()
add_text(
    p,
    "Serenity 仍然负责判断公司是否控制难以替代的供应链、数据、支付、临床或客户环节。新增信号不会直接提高等级，而是重新打开受影响的门槛。",
)

table = doc.add_table(rows=1, cols=3)
for i, h in enumerate(["新事件", "重新检查的 Serenity 门槛", "需要的验证"]):
    table.rows[0].cells[i].text = h
event_rows = [
    ("论文或新方法", "产业链位置、瓶颈证据、纯业务程度", "知识产权、可重复性、产品化路径和竞争方法"),
    ("大药企合作", "客户依赖、多节点控制、财报验证", "合同性质、付款、取消条款、收入和药物资产进展"),
    ("动物或临床结果", "反方论点、商业验证、财务耐久性", "样本、终点、副作用、下一阶段成本和时间"),
    ("FDA 决定", "监管壁垒、瓶颈、反方论点", "决定类型、原因、适应症、竞争产品和报销路径"),
    ("融资或内部人交易", "稀释、现金跑道、管理层与治理", "融资价格、稀释比例、资金用途和持续融资风险"),
    ("核心人员离职", "管理层与治理、执行风险", "原因、继任者、项目延期和内部控制"),
]
for row_data in event_rows:
    cells = table.add_row().cells
    for i, value in enumerate(row_data):
        cells[i].text = value
style_table(table, widths=[1.4, 2.4, 2.9])

add_heading(doc, "七 从研究结论到价格判断", 1)
p = doc.add_paragraph()
add_text(
    p,
    "Peter 提到需要把研究推进到价格是否合理、是否接近可执行决策的程度。近期仍保持 paper only。系统可以输出研究准备度和价格条件，但不自动下单。",
)
for item in [
    "按准备期、早期验证期、增长期和商业化期标记公司阶段。",
    "对市值低于 10 亿美元的候选重点检查现金跑道、融资历史、成交量和操纵风险。",
    "使用可比公司、收入倍数、研发资产价值和情景分析估算价格区间，并明确假设。",
    "设置等待条件，例如临床节点、FDA 反馈、药企付款、收入验证、估值回落或管理层问题解决。",
    "记录 Serenity 或行业意见领袖的公开判断和日期，进行结果对照，但不直接复制其结论。",
]:
    add_bullet(doc, item)

add_heading(doc, "八 开发行动计划", 1)
table = doc.add_table(rows=1, cols=4)
for i, h in enumerate(["优先级", "时间", "行动", "可交付结果"]):
    table.rows[0].cells[i].text = h
roadmap = [
    ("P0", "第 1 周", "建立六个生物科技方向的来源清单和术语表；定义论文、公司、人物、融资、资产和临床试验的数据结构", "生物科技主题配置和统一关系模型"),
    ("P0", "第 1 周", "接入 PubMed、bioRxiv、medRxiv、MIT 公开研究、NIH RePORTER、ClinicalTrials.gov、SEC 和 FDA 公开数据", "每日可重复的数据收集流程"),
    ("P0", "第 1 至 2 周", "构建论文到研究者、公司、投资者、大药企合作方和临床资产的映射", "可审计的研究关系图"),
    ("P0", "第 2 周", "增加 FDA 语义分类，区分批准、许可、完整回复函、临床暂停、安全、疗效、制造和信息缺口", "FDA 事件解释卡和门槛重审任务"),
    ("P1", "第 2 至 3 周", "增加公开核心人物追踪和管理层变化时间线", "关键人员页面和变化提醒"),
    ("P1", "第 3 周", "增加大药企采用强度、融资质量、现金跑道、稀释和估值评分", "公司阶段和价格准备度页面"),
    ("P1", "第 3 至 4 周", "进行历史回填和盲测，对照 XBI、随机、动量、直接询问通用模型和公开意见领袖", "验证报告和误报漏报分析"),
]
for row_data in roadmap:
    cells = table.add_row().cells
    for i, value in enumerate(row_data):
        cells[i].text = value
style_table(table, widths=[0.55, 0.95, 3.15, 2.05])

add_heading(doc, "九 评估指标", 1)
metrics = [
    "发现提前量  系统首次识别主题距离主流报道、融资或市场反应有多少天。",
    "公司映射精准度  映射出的公司中有多少具有产品、供应商或客户的真实关系。",
    "公司映射召回率  已知相关公司中有多少被系统找到。",
    "证据覆盖率  关键结论中有多少得到论文、SEC、FDA、临床或财报原文支持。",
    "误报和漏报  历史案例中触发但没有持续发展的主题，以及系统没有发现的重要主题。",
    "门槛预测价值  不同 Serenity 等级在后续临床、商业和价格表现中是否出现可重复差异。",
    "可审计性  每项结论能否追溯到时间、来源、原文、反证和证伪条件。",
]
for item in metrics:
    add_bullet(doc, item)

add_heading(doc, "十 下一次演示建议", 1)
p = doc.add_paragraph()
add_text(
    p,
    "下一次演示可以只选择一条技术路线，例如 AI 药物发现或精准肿瘤学。演示应从一篇前沿论文开始，展示研究者和公司关系、融资和大药企采用、动物和临床阶段、FDA 状态、管理层变化、Serenity 审查、估值和下一检查点。",
)
for item in [
    "展示 3 至 5 家市值较小或仍在早期验证阶段的上市公司。",
    "选择一个 FDA 批准案例和一个完整回复函或临床暂停案例，解释两者的差异。",
    "展示至少一个正面信号和一个反方信号，避免只呈现成功故事。",
    "给出研究优先级、等待条件和证伪条件，不给出自动买入或真实下单。",
]:
    add_bullet(doc, item)

add_heading(doc, "十一 近期边界", 1)
p = doc.add_paragraph()
add_text(
    p,
    "系统当前仍处于研究验证阶段。基础研究、融资、管理层交易和社交媒体内容都只能作为信号，不能单独证明技术有效或股票会上涨。所有数据来自公开来源。系统保持 dry run 和 paper only，不连接券商，不执行真实交易。",
)

footer = section.footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_text(footer, "前瞻生物科技研究 Agent  下一阶段行动计划", color=(100, 100, 100), size=8.5)

for paragraph in doc.paragraphs:
    for run in paragraph.runs:
        if run.font.name is None:
            set_run_font(run)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
doc.save(OUTPUT)
print(OUTPUT)
