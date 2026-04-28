/**
 * LMS CONTROLLER - COMPLETE
 * Handles: Auth, Dashboard, Course Publishing, Content Management, Upload Traps
 */

const CONFIG = {
    // Ensure this matches your VM IP
    API_BASE: "http://192.168.23.133:8001",
    ENDPOINTS: {
        LOGIN: "/auth/login",
        COURSES: "/courses/",
        MODULES: "/courses/modules/",
        UPLOAD: "/courses/upload/"
    }
};

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;
    const token = localStorage.getItem('token');

    // Route Protection
    if ((path.includes('dashboard.html') || path.includes('course-content.html')) && !token) {
        window.location.href = 'index.html';
        return;
    }

    if (path.includes('index.html') || path === '/' || path.endsWith('/')) {
        initLogin();
    } else if (path.includes('dashboard.html')) {
        initDashboard();
    } else if (path.includes('course-content.html')) {
        initContentPage();
    }
});

// --- AUTHENTICATION ---
function initLogin() {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const btn = document.getElementById('login-btn');

            btn.innerText = "Authenticating...";
            try {
                const response = await fetch(`${CONFIG.API_BASE}${CONFIG.ENDPOINTS.LOGIN}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                const data = await response.json();

                if (response.ok) {
                    localStorage.setItem('token', data.token);
                    localStorage.setItem('role', data.role);
                    localStorage.setItem('userEmail', email);
                    window.location.href = 'dashboard.html';
                } else {
                    alert(data.message || "Login failed");
                }
            } catch (err) {
                alert("Database connection failed. Attempt logged.");
            } finally {
                btn.innerText = "Sign In";
            }
        });
    }
}

// --- DASHBOARD ---
async function initDashboard() {
    const role = localStorage.getItem('role');
    const token = localStorage.getItem('token');
    
    document.getElementById('user-display').innerText = localStorage.getItem('userEmail');

    // Show "New Course" button for Admins
    if (role === 'admin' || role === 'teacher') {
        const btn = document.getElementById('add-course-btn');
        if (btn) {
            btn.classList.remove('hidden');
            btn.onclick = () => toggleModal(true);
        }
    }
    await loadCourses(token);
}

async function loadCourses(token) {
    const container = document.getElementById('courses-container');
    try {
        const response = await fetch(`${CONFIG.API_BASE}${CONFIG.ENDPOINTS.COURSES}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const courses = await response.json();

        if (courses.length === 0) {
            container.innerHTML = `<p class="text-center text-gray-500 col-span-full py-10">No courses available.</p>`;
            return;
        }

        container.innerHTML = courses.map(c => `
            <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-lg transition">
                <h3 class="text-xl font-bold text-gray-800 mb-2">${sanitize(c.title)}</h3>
                <p class="text-gray-600 text-sm mb-4 line-clamp-2">${sanitize(c.description)}</p>
                <button onclick="viewCourse('${c._id}')" class="text-indigo-600 font-bold text-sm hover:underline">
                    Manage Content &rarr;
                </button>
            </div>
        `).join('');
    } catch (err) {
        console.error(err);
    }
}

async function createCourse() {
    const token = localStorage.getItem('token');
    const title = document.getElementById('new-course-title').value;
    const desc = document.getElementById('new-course-desc').value;

    if (!title || !desc) return alert("All fields required");

    try {
        const response = await fetch(`${CONFIG.API_BASE}${CONFIG.ENDPOINTS.COURSES}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ title, description: desc })
        });

        if (response.ok) {
            toggleModal(false);
            loadCourses(token);
        }
    } catch (err) {
        alert("Action logged.");
    }
}

// --- CONTENT PAGE (Where your error was) ---
function viewCourse(id) {
    localStorage.setItem('activeCourseId', id);
    window.location.href = 'course-content.html';
}

async function initContentPage() {
    const courseId = localStorage.getItem('activeCourseId');
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');

    if (!courseId) return window.location.href = 'dashboard.html';

    // CRITICAL: Force show admin tools if role is correct
    if (role === 'admin' || role === 'teacher') {
        const tools = document.getElementById('add-content-section');
        if (tools) tools.classList.remove('hidden');
    }

    try {
        const response = await fetch(`${CONFIG.API_BASE}${CONFIG.ENDPOINTS.COURSES}${courseId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const course = await response.json();
        
        document.getElementById('course-title-display').innerText = course.title;
        document.getElementById('course-desc-display').innerText = course.description;
        renderModules(course.modules || []);
    } catch (err) {
        console.error(err);
    }
}

function renderModules(modules) {
    const container = document.getElementById('modules-container');
    if (!container) return;
    
    if (modules.length === 0) {
        container.innerHTML = `<p class="text-gray-400 italic">No content uploaded yet.</p>`;
        return;
    }

    container.innerHTML = modules.map((m, i) => `
        <div class="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
            <h4 class="font-bold text-lg text-indigo-900 mb-2">Module ${i+1}: ${sanitize(m.title)}</h4>
            <div class="text-gray-700 whitespace-pre-wrap">${sanitize(m.content)}</div>
        </div>
    `).join('');
}

async function addModule() {
    const courseId = localStorage.getItem('activeCourseId');
    const token = localStorage.getItem('token');
    const title = document.getElementById('module-title').value;
    const content = document.getElementById('module-content').value;

    if (!title || !content) return alert("Fill in module details");

    try {
        const response = await fetch(`${CONFIG.API_BASE}${CONFIG.ENDPOINTS.MODULES}${courseId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ title, content })
        });
        if (response.ok) location.reload();
    } catch (err) {
        alert("Failed to publish module.");
    }
}

// --- FILE UPLOAD TRAP ---
async function uploadFile() {
    const fileInput = document.getElementById('file-upload');
    const courseId = localStorage.getItem('activeCourseId');
    const token = localStorage.getItem('token');

    if (!fileInput.files[0]) return alert("Select a file");

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch(`${CONFIG.API_BASE}${CONFIG.ENDPOINTS.UPLOAD}${courseId}`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });
        const result = await response.json();
        alert(result.message || "Upload complete");
    } catch (err) {
        alert("Security Alert: Upload flagged.");
    }
}

// --- UTILS ---
function toggleModal(show) {
    const modal = document.getElementById('course-modal');
    if (modal) {
        modal.classList.toggle('hidden', !show);
        modal.classList.toggle('flex', show);
    }
}

function logout() {
    localStorage.clear();
    window.location.href = 'index.html';
}

function sanitize(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
