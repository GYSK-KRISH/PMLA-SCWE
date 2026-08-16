// Dynamic interactions for PMLA-SCWE Web Console

document.addEventListener("DOMContentLoaded", () => {
  // Initialize Chart.js visualizers if canvas elements exist
  initAnalyticsCharts();
  
  // Bind asynchronous attendance handlers
  initAttendanceSubmit();

  // Initialize mobile sidebar toggle overlays
  initMobileSidebar();

  // Animate KPI statistics count loading
  animateCounters();
});

function initMobileSidebar() {
  const sidebar = document.querySelector(".sidebar");
  const sidebarToggle = document.getElementById("sidebarToggle");
  const sidebarOverlay = document.getElementById("sidebarOverlay");
  const hamburgerMenuIcon = document.querySelector(".hamburger-menu-icon");

  if (!sidebar) return;

  function openSidebar() {
    sidebar.classList.add("open");
    if (sidebarOverlay) sidebarOverlay.classList.add("active");
  }

  function closeSidebar() {
    sidebar.classList.remove("open");
    if (sidebarOverlay) sidebarOverlay.classList.remove("active");
  }

  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", openSidebar);
  }

  if (sidebarOverlay) {
    sidebarOverlay.addEventListener("click", closeSidebar);
  }

  if (hamburgerMenuIcon) {
    hamburgerMenuIcon.addEventListener("click", closeSidebar);
  }
}

function animateCounters() {
  const counters = document.querySelectorAll(".kpi-card .value");
  
  counters.forEach(counter => {
    const text = counter.textContent.trim();
    const isPercentage = text.endsWith("%");
    const isPending = text.toLowerCase() === "pending";
    if (isPending) return;

    const numericString = text.replace("%", "");
    const targetVal = parseFloat(numericString);
    if (isNaN(targetVal)) return;

    const duration = 800; // 800ms animation
    const startTime = performance.now();

    function updateCounter(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing curve (easeOutQuad)
      const easeProgress = progress * (2 - progress);
      const currentVal = targetVal * easeProgress;

      if (isPercentage) {
        counter.textContent = currentVal.toFixed(1) + "%";
      } else {
        counter.textContent = Math.floor(currentVal).toString();
      }

      if (progress < 1) {
        requestAnimationFrame(updateCounter);
      } else {
        // Enforce exact final value
        counter.textContent = text;
      }
    }

    requestAnimationFrame(updateCounter);
  });
}

function initAnalyticsCharts() {
  const lhsCanvas = document.getElementById("lhsChart");
  if (!lhsCanvas) return;

  // Retrieve values from data-attributes in HTML
  const scoreAcademic = parseFloat(lhsCanvas.dataset.academic || 0);
  const scoreProgress = parseFloat(lhsCanvas.dataset.progress || 0);
  const scoreAttendance = parseFloat(lhsCanvas.dataset.attendance || 0);
  const scoreWellness = parseFloat(lhsCanvas.dataset.wellness || 0);

  // Initialize Bar Chart for LHS Breakdown
  new Chart(lhsCanvas, {
    type: 'bar',
    data: {
      labels: ['Academic Avg (40%)', 'Weekly Progress (25%)', 'Attendance Rate (20%)', 'Digital Wellness (15%)'],
      datasets: [{
        label: 'Metric Value (%)',
        data: [scoreAcademic, scoreProgress, scoreAttendance, scoreWellness],
        backgroundColor: [
          'rgba(77, 141, 255, 0.65)',   // Blue Accent
          'rgba(255, 122, 0, 0.65)',
          'rgba(48, 196, 141, 0.65)',   // Success green
          'rgba(124, 92, 255, 0.65)'    // Purple Accent
        ],
        borderColor: [
          '#4D8DFF',
          '#FF7A00',
          '#30C48D',
          '#7C5CFF'
        ],
        borderWidth: 1.5,
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          grid: {
            color: 'rgba(255,255,255,0.05)'
          },
          ticks: {
            color: '#8D96A8'
          }
        },
        x: {
          grid: {
            display: false
          },
          ticks: {
            color: '#8D96A8'
          }
        }
      },
      plugins: {
        legend: {
          display: false
        }
      }
    }
  });
}

// Bind asynchronous attendance handlers
function initAttendanceSubmit() {
  const form = document.getElementById("attendanceForm");
  if (!form) return;

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const saveBtn = document.getElementById("saveAttendanceBtn");
    const statusMsg = document.getElementById("attendanceStatusMsg");
    
    if (saveBtn) {
      saveBtn.disabled = true;
      saveBtn.value = "Saving...";
    }

    const formData = new FormData(form);
    
    fetch(form.action, {
      method: "POST",
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        if (statusMsg) {
          statusMsg.textContent = "Attendance saved successfully!";
          statusMsg.style.color = "#30C48D";
        }
      } else {
        if (statusMsg) {
          statusMsg.textContent = data.message || "Failed to save attendance.";
          statusMsg.style.color = "#E5484D";
        }
      }
    })
    .catch(err => {
      if (statusMsg) {
        statusMsg.textContent = "Connection error. Failed to save.";
        statusMsg.style.color = "#E5484D";
      }
    })
    .finally(() => {
      if (saveBtn) {
        saveBtn.disabled = false;
        saveBtn.value = "SAVE ALL ATTENDANCE";
      }
      setTimeout(() => {
        if (statusMsg) statusMsg.textContent = "";
      }, 4000);
    });
  });
}
