async function loadSummary() {
  const res = await fetch("/api/dashboard/summary");
  if (!res.ok) return null;
  return await res.json();
}

function currency(v) {
  const n = Number(v || 0);
  return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

async function main() {
  const el = document.getElementById("byCategoryChart");
  if (!el) return;

  const data = await loadSummary();
  if (!data) return;

  const labels = data.by_category.map((r) => r.category);
  const allocated = data.by_category.map((r) => r.allocated);
  const disbursed = data.by_category.map((r) => r.disbursed);

  // eslint-disable-next-line no-undef
  new Chart(el, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Allocated (₱)",
          data: allocated,
          backgroundColor: "rgba(13, 110, 253, 0.25)",
          borderColor: "rgba(13, 110, 253, 0.85)",
          borderWidth: 1,
        },
        {
          label: "Disbursed (₱)",
          data: disbursed,
          backgroundColor: "rgba(25, 135, 84, 0.25)",
          borderColor: "rgba(25, 135, 84, 0.85)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.dataset.label} ${currency(ctx.raw)}`,
          },
        },
        legend: { position: "bottom" },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (v) => currency(v),
          },
        },
      },
    },
  });
}

main();
