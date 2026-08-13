// Dynamic interactions for PMLA-SCWE Web Console

document.addEventListener("DOMContentLoaded", () => {
  // Initialize Chart.js visualizers if canvas elements exist
  initAnalyticsCharts();
  
  // Bind asynchronous attendance handlers
  initAttendanceSubmit();
});

function initAnalyticsCharts() {
  const lhsCanvas = document.getElementById("lhsChart");
  if (!lhsCanvas) return;

  // Retrieve values from data-attributes in HTML
  const scoreAcademic = parseFloat(lhsCanvas.dataset.academic || 0);
  const scoreProgress = parseFloat(lhsCanvas.dataset.progress || 0);
  const scoreAttendance = parseFloat(lhsCanvas.dataset.attendance || 0);
  const scoreWellness = parseFloat(lhsCanvas.dataset.wellness || 0);
  const scoreHealth = parseFloat(lhsCanvas.dataset.health || 0);

  // Initialize Bar Chart for LHS Breakdown
  new Chart(lhsCanvas, {
    type: 'bar',
    data: {
      labels: ['Academic Avg (40%)', 'Weekly Progress (25%)', 'Attendance Rate (20%)', 'Digital Wellness (15%)'],
      datasets: [{
        label: 'Metric Value (%)',
        data: [scoreAcademic, scoreProgress, scoreAttendance, scoreWellness],
        backgroundColor: [
          'rgba(62, 166, 255, 0.65)',
          'rgba(255, 122, 0, 0.65)',
          'rgba(52, 168, 83, 0.65)',
          'rgba(255, 214, 0, 0.65)'
        ],
        borderColor: [
          '#3EA6FF',
          '#FF7A00',
          '#34A853',
          '#FFD600'
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
            color: '#AAAAAA'
          }
        },
        x: {
          grid: {
            display: false
          },
          ticks: {
            color: '#AAAAAA'
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
          statusMsg.style.color = "#34A853";
        }
      } else {
        if (statusMsg) {
          statusMsg.textContent = data.message || "Failed to save attendance.";
          statusMsg.style.color = "#FF0000";
        }
      }
    })
    .catch(err => {
      if (statusMsg) {
        statusMsg.textContent = "Connection error. Failed to save.";
        statusMsg.style.color = "#FF0000";
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
