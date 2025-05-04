const BACKEND_HEALTH_URL = window.env?.BACKEND_URL;
const NOTIFIER_HEALTH_URL = window.env?.NOTIFIER_URL;

const jobsTableBody = document.getElementById("jobs-table-body");
const searchInput = document.getElementById("search-input");

// Initial state for filters
let filters = { applied: null, favourite: null, search: "" };

// Function to fetch jobs with filters
async function  fetchJobs() {
    try {
        const params = new URLSearchParams();
        if (filters.applied !== null) params.append("applied", filters.applied);
        if (filters.favourite !== null) params.append("favourite", filters.favourite);
        if (filters.search) params.append("search", filters.search);

        const response = await fetch(`${BACKEND_HEALTH_URL}/jobs/?${params}`);
        const jobs = await response.json();
        displayJobs(jobs);
    } catch (error) {
        console.error("Error fetching jobs:", error);
    }
}

function displayJobs(jobs) {
    jobsTableBody.innerHTML = "";

    if (jobs.length === 0) {
        jobsTableBody.innerHTML = "<tr><td colspan='6'>No jobs found.</td></tr>";
        return;
    }

    jobs.forEach(job => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${job.title}</td>
            <td>${job.company}</td>
            <td>${job.location}</td>
            <td>${job.date_posted}</td>
            <td><a href="${job.job_url}" target="_blank">View Job</a></td>
            <td>
                <button onclick="markAsApplied(${job.id})">
                    ${job.applied ? "✅ Applied" : "📝 Apply"}
                </button>
                <button onclick="toggleFavourite(${job.id})">
                    ${job.favourite ? "★ Favourite" : "☆ Favourite"}
                </button>
            </td>
        `;
        jobsTableBody.appendChild(row);
    });
}

// Function to mark job as applied
async function markAsApplied(jobId) {
    try {
        await fetch(`${BACKEND_HEALTH_URL}/jobs/${jobId}/apply`, { method: "PUT" });
        fetchJobs();
    } catch (error) {
        console.error("Error marking job as applied:", error);
    }
}

// Function to toggle favourite status
async function toggleFavourite(jobId) {
    try {
        await fetch(`${BACKEND_HEALTH_URL}/jobs/${jobId}/favourite`, { method: "PUT" });
        fetchJobs();
    } catch (error) {
        console.error("Error toggling favourite:", error);
    }
}

// ✅ Add event listeners for filter buttons
document.getElementById("filter-applied").addEventListener("click", () => {
    filters.applied = filters.applied === null ? true : null;
    fetchJobs();
});

document.getElementById("filter-favourite").addEventListener("click", () => {
    filters.favourite = filters.favourite === null ? true : null;
    fetchJobs();
});

document.getElementById("refresh-jobs").addEventListener("click", fetchJobs);

// ✅ Search Functionality
document.getElementById("search-button").addEventListener("click", () => {
    filters.search = searchInput.value.trim();
    fetchJobs();
});

searchInput.addEventListener("keypress", (event) => {
    if (event.key === "Enter") {
        filters.search = searchInput.value.trim();
        fetchJobs();
    }
});

// Fetch jobs when the page loads
fetchJobs();

function updateHealthDot(dotId, color) {
  const dot = document.getElementById(dotId);
  if (!dot) return;
  dot.style.backgroundColor = color;
}

async function pingHealthEndpoints() {
  try {
    const backendRes = await fetch(`${BACKEND_HEALTH_URL}/health`);
    const backendStatus = await backendRes.json();
    updateHealthDot("backend-dot", backendStatus.color);
  } catch {
    updateHealthDot("backend-dot", "fail");
  }

  try {
    const notifierRes = await fetch(`${BACKEND_HEALTH_URL}/health`);
    const notifierStatus = await notifierRes.json();
    updateHealthDot("notifier-dot", notifierStatus.color);
  } catch {
    updateHealthDot("notifier-dot", "fail");
  }
}

// Ping every 5 seconds
pingHealthEndpoints();
setInterval(pingHealthEndpoints, 5000);


document.getElementById("notify-slack").addEventListener("click", async () => {
  const notifyUrl = window.location.hostname === "localhost"
    ? "http://localhost:8000/notify/refresh-and-notify"
    : (window.env?.BACKEND_URL?.replace(/\/$/, "") || "") + "/notify/refresh-and-notify";

  try {
    const res = await fetch(notifyUrl);
    const data = await res.json();
    alert(data.message || "Slack notified!");
  } catch (error) {
    console.error("Error notifying Slack:", error);
    alert("❌ Failed to notify Slack.");
  }
});
