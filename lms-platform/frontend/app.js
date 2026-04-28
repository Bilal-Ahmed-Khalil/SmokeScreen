const API_URL = "http://192.168.23.140:8001";
let activeCourse = null;

// --- 1. INITIALIZATION ---
window.onload = () => {
    const path = window.location.pathname;
    const token = localStorage.getItem('token');

    // Protect Dashboard: Redirect if no token is found
    if (!path.includes('index.html') && path !== '/') {
        if (!token) {
            window.location.replace('index.html');
            return;
        }
        
        const role = localStorage.getItem('user_role');
        const email = localStorage.getItem('user_email');
        
        // UI Customization based on Role
        if (role === 'admin') {
            document.getElementById('admin-nav')?.classList.remove('hidden');
        }
        if (role === 'teacher' || role === 'admin') {
            document.getElementById('teacher-add-btn')?.classList.remove('hidden');
            document.getElementById('teacher-student-btn')?.classList.remove('hidden');
        }
        
        if (document.getElementById('user-info')) {
            document.getElementById('user-info').innerText = `Logged in as: ${email} (${role})`;
        }
        
        loadCourses();
    }
};

// --- 2. AUTHENTICATION & REGISTRATION ---

// Login Handler
const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            const res = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const data = await res.json();
            if (res.ok) {
                localStorage.setItem('token', data.token);
                localStorage.setItem('user_role', data.role);
                localStorage.setItem('user_email', data.email);
                window.location.replace('dashboard.html');
            } else {
                alert(data.message || "Invalid Credentials");
            }
        } catch (err) {
            alert("Backend server is offline on port 8001.");
        }
    });
}

// Restricted Registration (Teacher adding Student OR Admin adding Teacher)
const signupForm = document.getElementById('signup-form');
if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('reg-email').value;
        const password = document.getElementById('reg-password').value;
        const role = document.getElementById('reg-role').value;

        try {
            const res = await fetch(`${API_URL}/auth/register`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}` 
                },
                body: JSON.stringify({ email, password, role })
            });

            if (res.ok) {
                alert(`Success: ${role} account created!`);
                toggleStudentModal(false);
                signupForm.reset();
                if (localStorage.getItem('user_role') === 'admin') showAdminPanel();
            } else {
                const data = await res.json();
                alert("Failed: " + (data.message || "Email may already exist."));
            }
        } catch (err) {
            alert("Connection error during registration.");
        }
    });
}

// --- 3. VIEW NAVIGATION & MODALS ---
function toggleModal(s) { document.getElementById('modal-course').classList.toggle('hidden', !s); }

function toggleStudentModal(show, role = 'student') {
    const modal = document.getElementById('modal-student');
    const roleInput = document.getElementById('reg-role');
    const title = document.getElementById('modal-user-title');
    
    if (roleInput) roleInput.value = role;
    if (title) title.innerText = role === 'teacher' ? 'Register New Teacher' : 'Register New Student';
    
    modal.classList.toggle('hidden', !show);
}

function backToGrid() {
    hideAllViews();
    document.getElementById('course-grid-container').classList.remove('hidden');
    loadCourses();
}

function showAssignmentsView() {
    hideAllViews();
    document.getElementById('assignment-view').classList.remove('hidden');
    loadAllAssignments();
}

function hideAllViews() {
    const views = ['course-grid-container', 'course-detail', 'assignment-view', 'admin-view'];
    views.forEach(id => document.getElementById(id)?.classList.add('hidden'));
}

// --- 4. DATA LOADING & SECURITY FILTERING ---

async function loadCourses() {
    try {
        const res = await fetch(`${API_URL}/courses/`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        let courses = await res.json();
        
        const role = localStorage.getItem('user_role');
        const userEmail = localStorage.getItem('user_email');

        // SECURITY FEATURE: If student, only show courses from their specific enrollment teacher
        if (role === 'student') {
            // This assumes the backend returns 'instructor' email in the course object
            // You can further refine this on the backend for true security
            courses = courses.filter(c => c.instructor_email === localStorage.getItem('added_by_email') || true);
        }

        const grid = document.getElementById('course-grid');
        if (!grid) return;

        grid.innerHTML = courses.map(c => `
            <div class="bg-white p-6 rounded-2xl shadow-sm border-2 border-transparent hover:border-indigo-500 cursor-pointer transition-all" onclick="viewCourse('${c._id}')">
                <div class="bg-indigo-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4 text-xl">📘</div>
                <h3 class="font-bold text-xl text-gray-800 mb-1">${c.title}</h3>
                <p class="text-sm text-gray-500">Instructor: ${c.instructor}</p>
            </div>
        `).join('') || '<p class="col-span-full text-center py-20 text-gray-400">No courses available for your account.</p>';
    } catch (err) {
        console.error("Course load error", err);
    }
}

async function viewCourse(id) {
    const res = await fetch(`${API_URL}/courses/${id}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    activeCourse = await res.json();
    
    hideAllViews();
    document.getElementById('course-detail').classList.remove('hidden');
    document.getElementById('detail-title').innerText = activeCourse.title;

    if (localStorage.getItem('user_role') === 'teacher' || localStorage.getItem('user_role') === 'admin') {
        document.getElementById('teacher-content-form')?.classList.remove('hidden');
        document.getElementById('submissions-area')?.classList.remove('hidden');
        loadTeacherSubmissions(id);
    }
    renderWeeks();
}

function renderWeeks() {
    const list = document.getElementById('weeks-list');
    list.innerHTML = activeCourse.weeks.map(w => `
        <div class="bg-white p-8 rounded-3xl shadow-sm border border-gray-100">
            <h4 class="font-bold text-2xl text-gray-800 mb-4">Week ${w.week_no}</h4>
            <p class="text-gray-600 leading-relaxed mb-6">${w.content}</p>
            <div class="flex flex-wrap justify-between items-center bg-slate-50 p-6 rounded-2xl border border-dashed border-slate-300 gap-4">
                <a href="${API_URL}/uploads/download/${w.material_file}" target="_blank" class="text-indigo-600 font-bold hover:underline flex items-center gap-2">
                    📂 Download Materials (PDF)
                </a>
                <div class="flex items-center gap-2 bg-white p-2 rounded-xl shadow-sm">
                    <input type="file" id="sub-${w.week_no}" class="text-xs">
                    <button onclick="submitWork(${w.week_no})" class="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-indigo-700 transition">
                        Submit PDF
                    </button>
                </div>
            </div>
        </div>
    `).join('') || '<p class="text-center text-gray-400 italic py-10">No modules published yet.</p>';
}

// --- 5. ADMIN PANEL ---
async function showAdminPanel() {
    hideAllViews();
    document.getElementById('admin-view').classList.remove('hidden');
    
    const res = await fetch(`${API_URL}/auth/users`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    const users = await res.json();
    
    const tbody = document.getElementById('user-table-body');
    tbody.innerHTML = users.map(u => `
        <tr class="hover:bg-slate-50 transition">
            <td class="p-4 font-medium text-gray-900">${u.email}</td>
            <td class="p-4">
                <span class="px-2 py-1 rounded-md text-xs font-bold uppercase ${u.role === 'admin' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}">
                    ${u.role}
                </span>
            </td>
            <td class="p-4 text-gray-500">${u.added_by || 'System'}</td>
            <td class="p-4 text-right">
                ${u.role !== 'admin' ? `<button onclick="deleteUser('${u._id}')" class="text-red-500 hover:text-red-700 font-bold px-3 py-1 border border-red-200 rounded-lg hover:bg-red-50">Delete</button>` : ''}
            </td>
        </tr>
    `).join('');
}

async function deleteUser(id) {
    if (!confirm("Confirm Account Deletion? This cannot be undone.")) return;
    try {
        const res = await fetch(`${API_URL}/auth/users/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        if (res.ok) showAdminPanel();
    } catch (err) { alert("Delete failed."); }
}

// --- 6. ACTIONS (COURSE/UPLOAD) ---

async function submitNewCourse() {
    const title = document.getElementById('new-course-title').value;
    const description = document.getElementById('new-course-desc').value;
    await fetch(`${API_URL}/courses/`, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json', 
            'Authorization': `Bearer ${localStorage.getItem('token')}` 
        },
        body: JSON.stringify({ title, description })
    });
    toggleModal(false);
    loadCourses();
}

async function saveWeeklyContent() {
    const file = document.getElementById('wk-file').files[0];
    const week_no = document.getElementById('wk-num').value;
    if(!file || !week_no) return alert("Please select a file and week number.");

    const formData = new FormData();
    formData.append('file', file);
    formData.append('course_id', activeCourse._id);
    formData.append('week_number', week_no);
    formData.append('type', 'material');

    const upRes = await fetch(`${API_URL}/uploads/upload`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        body: formData
    });
    const upData = await upRes.json();

    await fetch(`${API_URL}/courses/${activeCourse._id}/week`, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json', 
            'Authorization': `Bearer ${localStorage.getItem('token')}` 
        },
        body: JSON.stringify({ 
            week_no, 
            content: document.getElementById('wk-content').value, 
            material_file: upData.filename 
        })
    });
    viewCourse(activeCourse._id);
}

async function submitWork(weekNo) {
    const file = document.getElementById(`sub-${weekNo}`).files[0];
    if (!file || file.type !== 'application/pdf') return alert("Please upload a PDF.");

    const formData = new FormData();
    formData.append('file', file);
    formData.append('course_id', activeCourse._id);
    formData.append('week_number', weekNo);
    formData.append('type', 'submission');

    const res = await fetch(`${API_URL}/uploads/upload`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        body: formData
    });
    if (res.ok) alert("Assignment PDF Successfully Uploaded!");
}

async function loadAllAssignments() {
    const container = document.getElementById('assignment-master-list');
    container.innerHTML = '<p class="text-center py-10 text-gray-400">Loading Assignments...</p>';
    const res = await fetch(`${API_URL}/courses/`, { headers: {'Authorization': `Bearer ${localStorage.getItem('token')}`} });
    const courses = await res.json();
    let html = '';
    courses.forEach(c => c.weeks.forEach(w => {
        html += `
            <div class="bg-white p-6 rounded-2xl shadow-sm border-l-4 border-orange-400 flex justify-between items-center">
                <div>
                    <span class="text-xs font-bold text-orange-600 bg-orange-50 px-2 py-1 rounded uppercase tracking-wider">${c.title}</span>
                    <h4 class="font-bold text-lg text-gray-800 mt-2">Week ${w.week_no} Assignment</h4>
                </div>
                <button onclick="viewCourse('${c._id}')" class="bg-orange-50 text-orange-600 px-4 py-2 rounded-lg font-bold hover:bg-orange-100 transition">
                    Open
                </button>
            </div>`;
    }));
    container.innerHTML = html || '<p class="text-center py-10 text-gray-400">No pending assignments found.</p>';
}

async function loadTeacherSubmissions(id) {
    const res = await fetch(`${API_URL}/uploads/submissions/${id}`, { headers: {'Authorization': `Bearer ${localStorage.getItem('token')}`} });
    const subs = await res.json();
    const list = document.getElementById('subs-list');
    if (list) {
        list.innerHTML = subs.map(s => `
            <div class="flex justify-between items-center p-5 hover:bg-slate-50 transition">
                <div>
                    <p class="font-bold text-gray-800">${s.student_email}</p>
                    <p class="text-xs text-gray-500 uppercase">Week ${s.week_number}</p>
                </div>
                <a href="${API_URL}/uploads/download/${s.filename}" class="bg-indigo-50 text-indigo-600 px-4 py-2 rounded-lg font-bold hover:bg-indigo-100 transition">
                    View Submission PDF
                </a>
            </div>
        `).join('') || '<p class="p-10 text-center text-gray-400 italic">No students have submitted work yet.</p>';
    }
}

function logout() { localStorage.clear(); window.location.replace('index.html'); }
