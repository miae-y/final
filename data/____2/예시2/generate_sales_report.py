import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

INPUT_FILE = Path('sales_2025.csv')
OUTPUT_FILE = Path('sales_report.html')

if not INPUT_FILE.exists():
    raise FileNotFoundError(INPUT_FILE)

rows = []
with INPUT_FILE.open('r', encoding='utf-8-sig', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        rows.append(row)

sales = 0.0
quantity = 0
orders = set()
customers = set()
monthly_sales = defaultdict(float)
channel_sales = Counter()
category_sales = Counter()
store_sales = Counter()
product_sales = Counter()
region_sales = Counter()
status_counts = Counter()
payment_counts = Counter()
gender_counts = Counter()
age_counts = Counter()

for row in rows:
    orders.add(row['주문번호'])
    customers.add(row['고객ID'])
    try:
        amount = float(row['매출액'])
    except ValueError:
        amount = 0.0
    sales += amount
    try:
        qty = int(row['수량'])
    except ValueError:
        qty = 0
    quantity += qty
    ym = row['주문일자'][:7]
    monthly_sales[ym] += amount
    channel_sales[row['채널']] += amount
    category_sales[row['카테고리']] += amount
    store_sales[row['매장명']] += amount
    product_sales[row['상품명']] += amount
    region_sales[row['지역']] += amount
    status_counts[row['주문상태']] += 1
    payment_counts[row['결제수단']] += 1
    gender_counts[row['성별']] += 1
    age_counts[row['연령']] += 1

monthly_labels = sorted(monthly_sales)
monthly_values = [round(monthly_sales[m], 0) for m in monthly_labels]
channel_items = channel_sales.most_common()
category_items = category_sales.most_common(10)
top_stores = store_sales.most_common(8)
product_items = product_sales.most_common(8)
payment_items = payment_counts.most_common(6)
status_items = status_counts.most_common()
region_items = region_sales.most_common(8)

department_filters = {
    '리테일': lambda row: row['채널'] == '오프라인',
    '아울렛': lambda row: row['채널'] == '아울렛',
    '온라인': lambda row: row['채널'] == '온라인',
    '핸드백': lambda row: row['카테고리'] == '가방',
}
segment_data = {name: {'sales': 0.0, 'orders': set(), 'customers': set(), 'qty': 0} for name in department_filters}
for row in rows:
    for name, matcher in department_filters.items():
        if matcher(row):
            try:
                amount = float(row['매출액'])
            except ValueError:
                amount = 0.0
            segment_data[name]['sales'] += amount
            segment_data[name]['orders'].add(row['주문번호'])
            segment_data[name]['customers'].add(row['고객ID'])
            try:
                segment_data[name]['qty'] += int(row['수량'])
            except ValueError:
                pass
segment_summaries = sorted([
    {
        'name': name,
        'sales': data['sales'],
        'orders': len(data['orders']),
        'customers': len(data['customers']),
        'avg': round(data['sales'] / len(data['orders']) if data['orders'] else 0),
    }
    for name, data in segment_data.items()
], key=lambda item: item['sales'], reverse=True)
segment_labels = [item['name'] for item in segment_summaries]
segment_values = [round(item['sales'], 0) for item in segment_summaries]

department_rows = {'전체': rows}
for name, matcher in department_filters.items():
    department_rows[name] = [row for row in rows if matcher(row)]

def build_chart_data(rowset):
    ms = defaultdict(float)
    ch = Counter()
    cat = Counter()
    store = Counter()
    prod = Counter()
    pay = Counter()
    for row in rowset:
        try:
            amount = float(row['매출액'])
        except ValueError:
            amount = 0.0
        ym = row['주문일자'][:7]
        ms[ym] += amount
        ch[row['채널']] += amount
        cat[row['카테고리']] += amount
        store[row['매장명']] += amount
        prod[row['상품명']] += amount
        pay[row['결제수단']] += 1
    monthly_keys = sorted(ms)
    return {
        'monthlyLabels': monthly_keys,
        'monthlyValues': [round(ms[m], 0) for m in monthly_keys],
        'channelLabels': [item[0] for item in ch.most_common()],
        'channelValues': [round(item[1], 0) for item in ch.most_common()],
        'categoryLabels': [item[0] for item in cat.most_common(10)],
        'categoryValues': [round(item[1], 0) for item in cat.most_common(10)],
        'storeLabels': [item[0] for item in store.most_common(8)],
        'storeValues': [round(item[1], 0) for item in store.most_common(8)],
        'productLabels': [item[0] for item in prod.most_common(8)],
        'productValues': [round(item[1], 0) for item in prod.most_common(8)],
        'paymentLabels': [item[0] for item in pay.most_common(6)],
        'paymentValues': [item[1] for item in pay.most_common(6)],
    }

def build_kpi_data(rowset):
    sales = 0.0
    quantity = 0
    orders = set()
    customers = set()
    for row in rowset:
        try:
            amount = float(row['매출액'])
        except ValueError:
            amount = 0.0
        sales += amount
        try:
            quantity += int(row['수량'])
        except ValueError:
            pass
        orders.add(row['주문번호'])
        customers.add(row['고객ID'])
    return {
        '총 매출액': f"{sales:,.0f}원",
        '총 주문건수': f"{len(orders):,}",
        '고객 수': f"{len(customers):,}",
        '총 판매 수량': f"{quantity:,}",
        '평균 주문 금액': f"{(sales / len(orders) if orders else 0):,.0f}원",
    }

department_chart_data = {name: build_chart_data(rowset) for name, rowset in department_rows.items()}
department_kpi_data = {name: build_kpi_data(rowset) for name, rowset in department_rows.items()}

high_month = monthly_labels[monthly_values.index(max(monthly_values))]
low_month = monthly_labels[monthly_values.index(min(monthly_values))]
return_rate = round(status_counts.get('반품', 0) / sum(status_counts.values()) * 100, 1)
online_share = round(channel_sales.get('온라인', 0) / sales * 100, 1) if sales else 0

kpis = {
    '총 매출액': f"{sales:,.0f}원",
    '총 주문건수': f"{len(orders):,}",
    '고객 수': f"{len(customers):,}",
    '총 판매 수량': f"{quantity:,}",
    '평균 주문 금액': f"{(sales / len(orders) if orders else 0):,.0f}원",
}

html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>게스코리아 2025 판매 대시보드</title>
  <style>
    body {{ margin: 0; padding: 0; background: #F5F6F8; color: #333333; font-family: 'Apple SD Gothic Neo', sans-serif; }}
    .container {{ width: min(1320px, calc(100% - 32px)); margin: 0 auto; padding: 32px 0; }}
    .hero {{ display: grid; grid-template-columns: 1fr auto; gap: 24px; align-items: center; margin-bottom: 32px; }}
    .hero-title {{ margin: 0; font-size: clamp(2.6rem, 4vw, 3.6rem); line-height: 1.02; color: #1F3A5F; }}
    .hero-desc {{ margin: 16px 0 0; color: #333333; font-size: 1rem; line-height: 1.8; max-width: 72ch; }}
    .filter-bar {{ display: flex; flex-wrap: wrap; align-items: center; gap: 12px; margin: 16px 0 24px; }}
    .filter-label {{ color: #1F3A5F; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; font-size: 0.94rem; }}
    .filter-button {{ border: 1px solid rgba(31, 58, 95, 0.18); background: #FFFFFF; color: #1F3A5F; padding: 10px 18px; border-radius: 999px; cursor: pointer; transition: all 0.2s ease; }}
    .filter-button:hover {{ background: #F5F6F8; }}
    .filter-button.active {{ background: #1F3A5F; color: #FFD54F; border-color: #1F3A5F; }}
    .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap: 20px; margin-bottom: 32px; }}
    .kpi-card {{ position: relative; overflow: hidden; border-radius: 22px; padding: 26px 26px 24px; background: #FFFFFF; border: 1px solid rgba(31, 58, 95, 0.12); box-shadow: 0 24px 48px rgba(31, 58, 95, 0.08); }}
    .kpi-card::before {{ content: ''; position: absolute; top: -16px; right: -16px; width: 120px; height: 120px; background: rgba(255, 213, 79, 0.16); border-radius: 50%; }}
    .kpi-card strong {{ display: block; margin-bottom: 14px; color: #1F3A5F; letter-spacing: 0.14em; font-size: 0.9rem; text-transform: uppercase; }}
    .kpi-card span {{ font-size: 2.4rem; font-weight: 800; color: #333333; }}
    .dashboard-grid {{ display: grid; grid-template-columns: 2fr 1fr; gap: 24px; margin-bottom: 28px; }}
    .panel {{ background: #FFFFFF; border: 1px solid rgba(31, 58, 95, 0.12); border-radius: 24px; padding: 28px; box-shadow: 0 24px 56px rgba(31, 58, 95, 0.08); }}
    .panel h2 {{ margin: 0 0 20px; font-size: 1.3rem; color: #1F3A5F; }}
    .segment-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 16px; margin-bottom: 24px; }}
    .segment-card {{ background: #F5F6F8; border: 1px solid rgba(31, 58, 95, 0.12); border-radius: 18px; padding: 18px 20px; }}
    .segment-card strong {{ display: block; color: #1F3A5F; margin-bottom: 10px; font-size: 1rem; }}
    .segment-card span {{ display: block; font-size: 1.8rem; font-weight: 700; color: #333333; margin-bottom: 8px; }}
    .segment-card p {{ margin: 0; color: #333333; line-height: 1.6; font-size: 0.95rem; }}
    .chart-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
    .chart-box {{ position: relative; min-height: 360px; height: 360px; }}
    .chart-box canvas {{ width: 100% !important; height: 100% !important; display: block; }}
    .insight-list {{ list-style: none; margin: 0; padding: 0; display: grid; gap: 16px; }}
    .insight-card {{ background: #F5F6F8; border: 1px solid rgba(31, 58, 95, 0.12); border-radius: 18px; padding: 18px 20px; }}
    .insight-card strong {{ display: block; margin-bottom: 8px; color: #1F3A5F; font-size: 0.98rem; }}
    .insight-card p {{ margin: 0; color: #333333; line-height: 1.7; }}
    .metric-chip {{ display: inline-flex; align-items: center; gap: 8px; padding: 10px 14px; border-radius: 999px; background: #FFD54F; color: #1F3A5F; font-weight: 700; margin-bottom: 10px; }}
    .table-box {{ margin-top: 24px; }}
    .table-box table {{ width: 100%; border-collapse: separate; border-spacing: 0 10px; }}
    .table-box th, .table-box td {{ padding: 14px 16px; }}
    .table-box th {{ color: #1F3A5F; font-size: 0.85rem; letter-spacing: 0.14em; text-transform: uppercase; border: none; }}
    .table-box td {{ background: #F5F6F8; color: #333333; border: none; }}
    @media (max-width: 1080px) {{ .dashboard-grid, .chart-grid {{ grid-template-columns: 1fr; }} }}
    @media (max-width: 640px) {{ .hero {{ grid-template-columns: 1fr; }} .kpi-card span {{ font-size: 2rem; }} }}
  </style>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
  <div class="container">
    <div class="hero">
      <div>
        <h1 class="hero-title">게스코리아 2025 판매 대시보드</h1>
        <p class="hero-desc">2025년 게스코리아 판매 데이터를 고급 대시보드 스타일로 재구성했습니다. 핵심 매출 흐름과 채널별 비중, 상위 상품과 매장 퍼포먼스를 한눈에 확인하세요.</p>
      </div>
    </div>
    <div class="filter-bar">
      <span class="filter-label">부서 필터</span>
      <button class="filter-button active" data-filter="전체">전체</button>
      <button class="filter-button" data-filter="리테일">리테일</button>
      <button class="filter-button" data-filter="아울렛">아울렛</button>
      <button class="filter-button" data-filter="온라인">온라인</button>
      <button class="filter-button" data-filter="핸드백">핸드백</button>
    </div>
    <div class="kpi-grid">
"""
for label, value in kpis.items():
    html += f"      <div class='kpi-card'><strong>{label}</strong><span data-kpi-key=\"{label}\">{value}</span></div>\n"
html += """
    </div>
    <div class="panel" style="margin-bottom: 28px;">
      <h2>부서별 매출 요약</h2>
      <div class="segment-grid">
"""
for segment in segment_summaries:
    html += f"          <div class='segment-card'><strong>{segment['name']}</strong><span>{segment['sales']:,.0f}원</span><p>주문 {segment['orders']:,} / 고객 {segment['customers']:,} / 평균 {segment['avg']:,.0f}원</p></div>\n"
html += f"""
      </div>
      <div class="chart-box"><canvas id="deptSales"></canvas></div>
    </div>
    <div class="dashboard-grid">
      <div>
        <div class="panel">
          <h2>세부 매출 인사이트</h2>
          <ul class="insight-list">
            <li class="insight-card"><strong>최고 매출 월</strong><p>{high_month}에 가장 높은 월별 매출을 기록했습니다.</p></li>
            <li class="insight-card"><strong>최저 매출 월</strong><p>{low_month}은 연중 가장 낮은 매출입니다. 시즌 대비 추가 프로모션이 필요합니다.</p></li>
            <li class="insight-card"><strong>온라인 채널 점유율</strong><p>온라인 매출 비중은 전체의 {online_share}%로, 디지털 채널 확장이 중요한 시점입니다.</p></li>
            <li class="insight-card"><strong>반품률</strong><p>반품 비율은 전체 주문의 {return_rate}%로, 고객 만족 및 교환 정책 분석이 필요합니다.</p></li>
          </ul>
        </div>
        <div class="panel" style="margin-top:24px;">
          <h2>추가 지표</h2>
          <div class="metric-chip">월 평균 매출: {int(sales / 12):,}원</div>
          <div class="metric-chip">총 주문 대비 고객 비율: {round(len(customers) / len(orders) * 100, 1)}%</div>
          <div class="metric-chip">판매 수량 대비 평균 단가: {round(sales / quantity):,}원</div>
        </div>
      </div>
      <div class="panel">
        <h2>월별 매출 추이</h2>
        <div class="chart-box"><canvas id="monthlySales"></canvas></div>
      </div>
    </div>
    <div class="chart-grid">
      <div class="panel">
        <h2>채널별 매출 비중</h2>
        <div class="chart-box"><canvas id="channelShare"></canvas></div>
      </div>
      <div class="panel">
        <h2>결제 수단 비중</h2>
        <div class="chart-box"><canvas id="paymentShare"></canvas></div>
      </div>
      <div class="panel">
        <h2>카테고리별 상위 매출</h2>
        <div class="chart-box"><canvas id="categorySales"></canvas></div>
      </div>
      <div class="panel">
        <h2>상위 매장별 매출</h2>
        <div class="chart-box"><canvas id="storeSales"></canvas></div>
      </div>
    </div>
    <div class="chart-grid">
      <div class="panel" style="grid-column: span 2;">
        <h2>Top 8 상품 매출</h2>
        <div class="chart-box"><canvas id="productSales"></canvas></div>
      </div>
    </div>
    <div class="table-box panel">
      <h2>주문 상태 분포</h2>
      <table>
        <thead><tr><th>주문 상태</th><th>건수</th></tr></thead>
        <tbody>
"""
for status, count in status_items:
    html += f"          <tr><td>{status}</td><td>{count:,}</td></tr>\n"
html += """
        </tbody>
      </table>
    </div>
    <div class="table-box panel">
      <h2>지역별 상위 매출</h2>
      <table>
        <thead><tr><th>지역</th><th>매출액</th></tr></thead>
        <tbody>
"""
for region, amount in region_items:
    html += f"          <tr><td>{region}</td><td>{amount:,.0f}원</td></tr>\n"
html += """
        </tbody>
      </table>
    </div>
  </div>
  <script>
html += f"""
    const kpiData = {json.dumps(department_kpi_data, ensure_ascii=False)};
    const departmentData = {json.dumps(department_chart_data, ensure_ascii=False)};
    const initialData = departmentData['전체'];
    const monthlyLabels = initialData.monthlyLabels;
    const monthlyValues = initialData.monthlyValues;
    const channelLabels = initialData.channelLabels;
    const channelValues = initialData.channelValues;
    const categoryLabels = initialData.categoryLabels;
    const categoryValues = initialData.categoryValues;
    const storeLabels = initialData.storeLabels;
    const storeValues = initialData.storeValues;
    const productLabels = initialData.productLabels;
    const productValues = initialData.productValues;
    const paymentLabels = initialData.paymentLabels;
    const paymentValues = initialData.paymentValues;
    const segment_labels = {json.dumps(segment_labels, ensure_ascii=False)};
    const segment_values = {json.dumps(segment_values, ensure_ascii=False)};
"""
html += """

    function makeChart(ctx, type, data, options) {
      return new Chart(ctx, {
        type,
        data,
        options: Object.assign({ responsive: true, maintainAspectRatio: false }, options)
      });
    }

    const monthlyChart = makeChart(document.getElementById('monthlySales'), 'line', {
      labels: monthlyLabels,
      datasets: [{
        label: '매출액',
        data: monthlyValues,
        borderColor: '#1F3A5F',
        backgroundColor: 'rgba(255, 213, 79, 0.18)',
        fill: true,
        tension: 0.36,
        pointRadius: 5,
        pointBackgroundColor: '#FFD54F',
      }]
    }, {
      plugins: { legend: { display: false } },
      scales: {
        y: { ticks: { callback: value => value.toLocaleString() + '원', color: '#cbd5e1' }, grid: { color: 'rgba(148, 163, 184, 0.16)' } },
        x: { ticks: { color: '#cbd5e1' }, grid: { display: false } }
      }
    });

    const channelChart = makeChart(document.getElementById('channelShare'), 'doughnut', {
      labels: channelLabels,
      datasets: [{
        data: channelValues,
        backgroundColor: ['#1F3A5F', '#FFD54F', '#A0AEC0'],
        hoverOffset: 10,
      }]
    }, {
      plugins: { legend: { position: 'bottom', labels: { color: '#e2e8f0' } } }
    });

    const paymentChart = makeChart(document.getElementById('paymentShare'), 'pie', {
      labels: paymentLabels,
      datasets: [{
        data: paymentValues,
        backgroundColor: ['#1F3A5F', '#FFD54F', '#A0AEC0', '#CBD5E1', '#7C8BA3', '#E2E8F0'],
      }]
    }, {
      plugins: { legend: { position: 'bottom', labels: { color: '#e2e8f0' } } }
    });

    const deptChart = makeChart(document.getElementById('deptSales'), 'bar', {
      labels: segment_labels,
      datasets: [{
        label: '부서별 매출',
        data: segment_values,
        backgroundColor: ['#1F3A5F', '#FFD54F', '#7C8BA3', '#CBD5E1'],
        borderRadius: 12,
      }]
    }, {
      plugins: { legend: { display: false } },
      scales: { x: { ticks: { color: '#cbd5e1' }, grid: { display: false } }, y: { ticks: { callback: value => value.toLocaleString() + '원', color: '#cbd5e1' }, grid: { color: 'rgba(148, 163, 184, 0.16)' } } }
    });

    const categoryChart = makeChart(document.getElementById('categorySales'), 'bar', {
      labels: categoryLabels,
      datasets: [{
        label: '매출액',
        data: categoryValues,
        backgroundColor: ['#1F3A5F', '#FFD54F', '#7C8BA3', '#CBD5E1', '#7C8BA3', '#1F3A5F', '#FFD54F', '#A0AEC0'],
        borderRadius: 12,
      }]
    }, {
      indexAxis: 'y',
      plugins: { legend: { display: false } },
      scales: { x: { ticks: { callback: value => value.toLocaleString() + '원', color: '#cbd5e1' }, grid: { color: 'rgba(148, 163, 184, 0.16)' } }, y: { ticks: { color: '#cbd5e1' } } }
    });

    const storeChart = makeChart(document.getElementById('storeSales'), 'bar', {
      labels: storeLabels,
      datasets: [{
        label: '매출액',
        data: storeValues,
        backgroundColor: '#1F3A5F',
        borderRadius: 10,
      }]
    }, {
      indexAxis: 'y',
      plugins: { legend: { display: false } },
      scales: { x: { ticks: { callback: value => value.toLocaleString() + '원', color: '#cbd5e1' }, grid: { color: 'rgba(148, 163, 184, 0.16)' } }, y: { ticks: { color: '#cbd5e1' } } }
    });

    const productChart = makeChart(document.getElementById('productSales'), 'bar', {
      labels: productLabels,
      datasets: [{
        label: '매출액',
        data: productValues,
        backgroundColor: '#FFD54F',
        borderRadius: 10,
      }]
    }, {
      indexAxis: 'y',
      plugins: { legend: { display: false } },
      scales: { x: { ticks: { callback: value => value.toLocaleString() + '원', color: '#cbd5e1' }, grid: { color: 'rgba(148, 163, 184, 0.16)' } }, y: { ticks: { color: '#cbd5e1' } } }
    });

    function updateDepartmentCharts(department) {
      const data = departmentData[department] || departmentData['전체'];
      monthlyChart.data.labels = data.monthlyLabels;
      monthlyChart.data.datasets[0].data = data.monthlyValues;
      monthlyChart.update();

      channelChart.data.labels = data.channelLabels;
      channelChart.data.datasets[0].data = data.channelValues;
      channelChart.update();

      paymentChart.data.labels = data.paymentLabels;
      paymentChart.data.datasets[0].data = data.paymentValues;
      paymentChart.update();

      categoryChart.data.labels = data.categoryLabels;
      categoryChart.data.datasets[0].data = data.categoryValues;
      categoryChart.update();

      storeChart.data.labels = data.storeLabels;
      storeChart.data.datasets[0].data = data.storeValues;
      storeChart.update();

      productChart.data.labels = data.productLabels;
      productChart.data.datasets[0].data = data.productValues;
      productChart.update();
      updateKPIValues(department);
    }

    function updateKPIValues(department) {
      const kpis = kpiData[department] || kpiData['전체'];
      document.querySelectorAll('[data-kpi-key]').forEach(el => {
        const key = el.getAttribute('data-kpi-key');
        if (kpis[key] !== undefined) {
          el.textContent = kpis[key];
        }
      });
    }

    const filterButtons = document.querySelectorAll('.filter-button');
    filterButtons.forEach(button => {
      button.addEventListener('click', () => {
        filterButtons.forEach(btn => btn.classList.toggle('active', btn === button));
        updateDepartmentCharts(button.dataset.filter);
      });
    });
  </script>
</body>
</html>
"""
OUTPUT_FILE.write_text(html, encoding='utf-8')
print(f"Generated {OUTPUT_FILE}")
