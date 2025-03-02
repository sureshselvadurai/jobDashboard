// API URL - Use localhost when running outside Docker
const API_URL = window.location.hostname === "localhost"
    ? "http://localhost:8000/jobs/"
    : "http://127.0.0.1:8000/jobs/";

const jobsTableBody = document.getElementById("jobs-table-body");

// Initial state for filters
let filters = { applied: null, favourite: null };

// Function to fetch jobs with filters
async function fetchJobs() {
    try {
        const params = new URLSearchParams();
        if (filters.applied !== null) params.append("applied", filters.applied);
        if (filters.favourite !== null) params.append("favourite", filters.favourite);

        const response = await fetch(`${API_URL}?${params}`);
        const jobs = await response.json();
        displayJobs(jobs);
    } catch (error) {
        console.error("Error fetching jobs:", error);
    }
}

// Function to display jobs in the table
function displayJobs(jobs) {
    jobsTableBody.innerHTML = "";

    if (jobs.length === 0) {
        jobsTableBody.innerHTML = "<tr><td colspan='5'>No jobs found.</td></tr>";
        return;
    }

    jobs.forEach(job => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${job.title}</td>
            <td>${job.company}</td>
            <td>${job.location}</td>
            <td>${job.date_posted}</td>
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
        await fetch(`${API_URL}${jobId}/apply`, { method: "PUT" });
        fetchJobs();
    } catch (error) {
        console.error("Error marking job as applied:", error);
    }
}

// Function to toggle favourite status
async function toggleFavourite(jobId) {
    try {
        await fetch(`${API_URL}${jobId}/favourite`, { method: "PUT" });
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

// Fetch jobs when the page loads
fetchJobs();
