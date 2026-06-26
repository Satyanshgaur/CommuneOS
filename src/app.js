// app.js - CommuneOS Frontend Logic with Supabase Auth and Backend Integration

const API_BASE_URL = "http://localhost:8000/api/v1";

// Supabase Instance
let supabase = null;

// State Variables
let currentUserId = null;
let currentUserProfile = null;
let currentRole = "member"; // "member" or "organizer"

// Intercept all fetch requests to automatically add X-User-Id header if currentUserId is set
const originalFetch = window.fetch;
window.fetch = function(url, options = {}) {
  if (currentUserId) {
    options.headers = options.headers || {};
    if (options.headers instanceof Headers) {
      if (!options.headers.has("X-User-Id")) {
        options.headers.append("X-User-Id", currentUserId);
      }
    } else if (Array.isArray(options.headers)) {
      const hasHeader = options.headers.some(([key]) => key.toLowerCase() === 'x-user-id');
      if (!hasHeader) {
        options.headers.push(["X-User-Id", currentUserId]);
      }
    } else {
      if (!options.headers["X-User-Id"]) {
        options.headers["X-User-Id"] = currentUserId;
      }
    }
  }
  return originalFetch(url, options);
};

// Dynamic Community Branding Placeholder
const communityBranding = {
  name: "AgentField Community",
  logo: "⚛",
  description: "A secure cooperative space connecting developer intelligence with infrastructure, skills, and mentors."
};

// DOM Elements Cache
const elements = {
  mainHeader: null,
  roleToggleMember: null,
  roleToggleOrganizer: null,
  
  // Auth Containers
  authContainer: null,
  loginPanel: null,
  signupPanel: null,
  verificationPanel: null,
  authConfigWarning: null,
  communityAssignmentContainer: null,
  
  loginForm: null,
  signupForm: null,
  btnVerificationDone: null,
  linkShowSignup: null,
  linkShowLogin: null,

  // Profile Creation / Onboarding
  onboardingContainer: null,
  onboardingForm: null,
  
  mainDashboard: null,
  organizerDashboard: null,
  
  // Member Dashboard details
  heroHeadline: null,
  heroBody: null,
  heroPills: null,
  
  priorityGrid: null,
  
  kpiPathsName: null,
  kpiPathsProgress: null,
  kpiPathsNext: null,
  kpiSkillsList: null,
  kpiInterestsList: null,
  
  mentorSection: null,
  mentorList: null,
  
  communitiesList: null,
  
  resourcesList: null,
  
  eventsList: null,
  
  insightsList: null,
  
  // Organizer Dashboard Details
  orgHealthScore: null,
  orgNewMembers: null,
  orgActiveMembers: null,
  orgAtRiskMembers: null,
  orgTrendingTopics: null,
  orgUnanswered: null,
  orgActionsList: null,
  orgMentorsList: null,
  
  // Agent Pipeline Details
  agentTimeline: null,
  
  // Modal Details
  modalOverlay: null,
  modalTitle: null,
  modalBody: null,
  modalClose: null,

  // User Profile wrapper / Auth User Details
  userProfileWrapper: null,
  authUserName: null,
  btnSignout: null,

  // Community Branding elements
  communityName: null,
  communityLogo: null,
  communityDesc: null
};

// Initialization & Event Bindings
document.addEventListener("DOMContentLoaded", async () => {
  // Initialize elements cache
  elements.mainHeader = document.getElementById("main-header");
  elements.roleToggleMember = document.getElementById("role-member");
  elements.roleToggleOrganizer = document.getElementById("role-organizer");
  
  elements.authContainer = document.getElementById("auth-container");
  elements.loginPanel = document.getElementById("login-panel");
  elements.signupPanel = document.getElementById("signup-panel");
  elements.verificationPanel = document.getElementById("verification-panel");
  elements.authConfigWarning = document.getElementById("auth-config-warning");
  elements.communityAssignmentContainer = document.getElementById("community-assignment-container");
  
  elements.loginForm = document.getElementById("login-form");
  elements.signupForm = document.getElementById("signup-form");
  elements.btnVerificationDone = document.getElementById("btn-verification-done");
  elements.linkShowSignup = document.getElementById("link-show-signup");
  elements.linkShowLogin = document.getElementById("link-show-login");

  elements.onboardingContainer = document.getElementById("onboarding-container");
  elements.onboardingForm = document.getElementById("onboarding-form");
  
  elements.mainDashboard = document.getElementById("main-dashboard");
  elements.organizerDashboard = document.getElementById("organizer-dashboard");
  
  elements.heroHeadline = document.getElementById("hero-headline");
  elements.heroBody = document.getElementById("hero-body");
  elements.heroPills = document.getElementById("hero-pills");
  
  elements.priorityGrid = document.getElementById("priority-grid");
  
  elements.kpiPathsName = document.getElementById("kpi-paths-name");
  elements.kpiPathsProgress = document.getElementById("kpi-paths-progress");
  elements.kpiPathsNext = document.getElementById("kpi-paths-next");
  elements.kpiSkillsList = document.getElementById("kpi-skills-list");
  elements.kpiInterestsList = document.getElementById("kpi-interests-list");
  
  elements.mentorSection = document.getElementById("mentor-section");
  elements.mentorList = document.getElementById("mentor-list");
  
  elements.communitiesList = document.getElementById("communities-list");
  
  elements.resourcesList = document.getElementById("resources-list");
  
  elements.eventsList = document.getElementById("events-list");
  
  elements.insightsList = document.getElementById("insights-list");
  
  elements.orgHealthScore = document.getElementById("org-health-score");
  elements.orgNewMembers = document.getElementById("org-new-members");
  elements.orgActiveMembers = document.getElementById("org-active-members");
  elements.orgAtRiskMembers = document.getElementById("org-at-risk-members");
  elements.orgTrendingTopics = document.getElementById("org-trending-topics");
  elements.orgUnanswered = document.getElementById("org-unanswered");
  elements.orgActionsList = document.getElementById("org-actions-list");
  elements.orgMentorsList = document.getElementById("org-mentors-list");
  
  elements.agentTimeline = document.getElementById("agent-timeline");
  
  elements.modalOverlay = document.getElementById("modal-overlay");
  elements.modalTitle = document.getElementById("modal-title");
  elements.modalBody = document.getElementById("modal-body");
  elements.modalClose = document.getElementById("modal-close");

  elements.userProfileWrapper = document.getElementById("user-profile-wrapper");
  elements.authUserName = document.getElementById("auth-user-name");
  elements.btnSignout = document.getElementById("btn-signout");

  elements.communityName = document.getElementById("community-name");
  elements.communityLogo = document.getElementById("community-logo");
  elements.communityDesc = document.getElementById("community-desc");

  // Bind community branding details
  renderCommunityBranding();

  // Event bindings
  elements.roleToggleMember.addEventListener("click", () => switchRole("member"));
  elements.roleToggleOrganizer.addEventListener("click", () => switchRole("organizer"));
  elements.onboardingForm.addEventListener("submit", handleProfileSubmit);
  elements.modalClose.addEventListener("click", closeModal);
  elements.modalOverlay.addEventListener("click", (e) => {
    if (e.target === elements.modalOverlay) closeModal();
  });

  // Sprint 2 Modal Event bindings
  const profileOverlay = document.getElementById("profile-modal-overlay");
  const profileClose = document.getElementById("profile-modal-close");
  const profileCancel = document.getElementById("btn-profile-edit-cancel");
  const profileForm = document.getElementById("profile-edit-form");

  if (profileClose) profileClose.onclick = closeProfileEditModal;
  if (profileCancel) profileCancel.onclick = closeProfileEditModal;
  if (profileForm) profileForm.onsubmit = handleProfileEditSubmit;
  if (profileOverlay) {
    profileOverlay.addEventListener("click", (e) => {
      if (e.target === profileOverlay) closeProfileEditModal();
    });
  }

  if (elements.btnSignout) {
    elements.btnSignout.addEventListener("click", handleSignOut);
  }

  // Auth panel links
  elements.linkShowSignup.addEventListener("click", (e) => {
    e.preventDefault();
    elements.loginPanel.style.display = "none";
    elements.signupPanel.style.display = "block";
  });

  elements.linkShowLogin.addEventListener("click", (e) => {
    e.preventDefault();
    elements.signupPanel.style.display = "none";
    elements.loginPanel.style.display = "block";
  });

  elements.btnVerificationDone.addEventListener("click", () => {
    elements.verificationPanel.style.display = "none";
    elements.loginPanel.style.display = "block";
  });

  elements.loginForm.addEventListener("submit", handleLoginSubmit);
  elements.signupForm.addEventListener("submit", handleSignupSubmit);

  // Initialize Supabase from Backend config
  await initSupabase();
});

// Fetch config from backend and initialize Supabase Auth
async function initSupabase() {
  try {
    const res = await fetch(`${API_BASE_URL}/users/config`);
    if (!res.ok) throw new Error("Failed to load backend config");
    const json = await res.json();
    
    const url = json.data.supabase_url;
    const anonKey = json.data.supabase_anon_key;

    if (!url || !anonKey) {
      console.warn("Supabase credentials not configured in backend .env");
      if (elements.authConfigWarning) elements.authConfigWarning.style.display = "block";
      showAuthScreen();
      return;
    }

    if (elements.authConfigWarning) elements.authConfigWarning.style.display = "none";

    // Initialize Supabase Client
    supabase = window.supabase.createClient(url, anonKey);

    // Check existing session
    const { data: { session } } = await supabase.auth.getSession();
    
    // Set up auth state change listener
    supabase.auth.onAuthStateChange((event, newSession) => {
      handleAuthStateChange(newSession);
    });

    // Handle initial state
    await handleAuthStateChange(session);

  } catch (error) {
    console.error("Error initializing Supabase Auth:", error);
    if (elements.authConfigWarning) {
      elements.authConfigWarning.textContent = "Error: Backend server is offline. Please start the backend service.";
      elements.authConfigWarning.style.display = "block";
    }
    showAuthScreen();
  }
}

// Handle changes in Supabase Session
async function handleAuthStateChange(session) {
  if (session) {
    currentUserId = session.user.id;
    // Check if user profile already exists in the backend
    await checkUserProfile(currentUserId, session.user.email);
  } else {
    currentUserId = null;
    currentUserProfile = null;
    showAuthScreen();
  }
}

// Query backend to verify if the profile has been created
async function checkUserProfile(userId, email) {
  try {
    const res = await fetch(`${API_BASE_URL}/users/${userId}`);
    if (res.status === 404) {
      // Authenticated but profile is not created yet
      showProfileCreation(email);
    } else if (res.ok) {
      const json = await res.json();
      const profile = json.data;
      
      if (!profile.community_id) {
        // Profile exists but has not joined a community yet
        showCommunityAssignment();
      } else {
        // Profile exists and has joined a community, load dashboard
        selectedCommunityId = profile.community_id;
        
        // Fetch community branding from the list
        const listRes = await fetch(`${API_BASE_URL}/community/list`);
        if (listRes.ok) {
          const listJson = await listRes.json();
          const currentComm = listJson.data.communities.find(c => c.community_id === selectedCommunityId);
          if (currentComm) {
            communityBranding.name = currentComm.name;
            communityBranding.logo = currentComm.logo;
            communityBranding.description = currentComm.description;
            renderCommunityBranding();
          }
        }
        
        showDashboard(profile.username);
        await loadMemberPersonalization(userId);
      }
    } else {
      throw new Error("API error while checking profile");
    }
  } catch (error) {
    console.error("Failed to check user profile:", error);
    // Offline / error check fallback: let user create profile anyway
    showProfileCreation(email);
  }
}

// Show Authentication panels
function showAuthScreen() {
  elements.mainHeader.style.display = "none";
  elements.mainDashboard.style.display = "none";
  elements.organizerDashboard.style.display = "none";
  document.getElementById("agent-view").style.display = "none";
  elements.onboardingContainer.style.display = "none";
  elements.communityAssignmentContainer.style.display = "none";
  elements.userProfileWrapper.style.display = "none";
  
  elements.authContainer.style.display = "block";
  elements.loginPanel.style.display = "block";
  elements.signupPanel.style.display = "none";
  elements.verificationPanel.style.display = "none";
}

// Show Profile Creation form
function showProfileCreation(email) {
  elements.authContainer.style.display = "none";
  elements.mainDashboard.style.display = "none";
  elements.organizerDashboard.style.display = "none";
  document.getElementById("agent-view").style.display = "none";
  elements.communityAssignmentContainer.style.display = "none";
  elements.userProfileWrapper.style.display = "none";
  elements.mainHeader.style.display = "none";
  
  // Show Onboarding Card as Profile Creation Form
  elements.onboardingContainer.style.display = "block";
  
  // Reset profile form and set email if available
  elements.onboardingForm.reset();
  const cancelBtn = document.getElementById("btn-onboard-cancel");
  if (cancelBtn) cancelBtn.style.display = "none"; // Unauthenticated profile creation cannot be bypassed
}

// Show Community Assignment Loader
let selectedCommunityId = null;

// Show Community Assignment Loader & Selection Screen
async function showCommunityAssignment() {
  elements.authContainer.style.display = "none";
  elements.onboardingContainer.style.display = "none";
  elements.mainDashboard.style.display = "none";
  elements.organizerDashboard.style.display = "none";
  document.getElementById("agent-view").style.display = "none";
  elements.userProfileWrapper.style.display = "none";
  elements.mainHeader.style.display = "none";
  
  elements.communityAssignmentContainer.style.display = "block";
  document.getElementById("community-selection-view").style.display = "block";
  document.getElementById("community-loading-view").style.display = "none";

  const cardsList = document.getElementById("community-cards-list");
  cardsList.innerHTML = '<p style="text-align: center; color: var(--color-slate);">Loading communities...</p>';

  selectedCommunityId = null;
  const joinBtn = document.getElementById("btn-join-community");
  joinBtn.disabled = true;
  joinBtn.onclick = handleJoinCommunitySubmit;

  try {
    const res = await fetch(`${API_BASE_URL}/community/list`);
    if (!res.ok) throw new Error("Failed to load community list");
    const result = await res.json();
    const communities = result.data.communities;

    cardsList.innerHTML = communities.map(c => `
      <div class="community-selection-card" data-id="${c.community_id}" style="border: 1px solid var(--color-chalk); border-radius: var(--radius-cards); padding: 16px; cursor: pointer; text-align: left; transition: all 0.2s ease; background-color: var(--color-paper); margin-bottom: 8px;">
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
          <span style="font-size: 24px; margin-right: 12px;">${c.logo || '🌐'}</span>
          <h3 style="margin: 0; color: var(--color-carbon); font-size: 16px;">${c.name}</h3>
        </div>
        <p style="margin: 0; font-size: 13px; color: var(--color-slate); line-height: 1.4;">${c.description}</p>
      </div>
    `).join("");

    const cards = cardsList.querySelectorAll(".community-selection-card");
    cards.forEach(card => {
      card.addEventListener("click", () => {
        cards.forEach(c => {
          c.style.borderColor = "var(--color-chalk)";
          c.style.boxShadow = "none";
        });
        card.style.borderColor = "var(--color-signal-orange)";
        card.style.boxShadow = "0 0 0 2px var(--color-signal-orange)";
        selectedCommunityId = card.getAttribute("data-id");
        joinBtn.disabled = false;
      });
    });
  } catch (error) {
    console.error("Error loading communities:", error);
    cardsList.innerHTML = `<p style="text-align: center; color: red;">Error loading communities: ${error.message}</p>`;
  }
}

// Handle joining community and triggers personalization
async function handleJoinCommunitySubmit() {
  if (!selectedCommunityId) return;

  document.getElementById("community-selection-view").style.display = "none";
  document.getElementById("community-loading-view").style.display = "block";

  try {
    const joinRes = await fetch(`${API_BASE_URL}/community/join`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        user_id: currentUserId,
        community_id: selectedCommunityId
      })
    });

    if (!joinRes.ok) throw new Error("Failed to join community");

    // Fetch and update branding
    const listRes = await fetch(`${API_BASE_URL}/community/list`);
    if (listRes.ok) {
      const listJson = await listRes.json();
      const currentComm = listJson.data.communities.find(c => c.community_id === selectedCommunityId);
      if (currentComm) {
        communityBranding.name = currentComm.name;
        communityBranding.logo = currentComm.logo;
        communityBranding.description = currentComm.description;
        renderCommunityBranding();
      }
    }

    // Run Personalization
    await loadMemberPersonalization(currentUserId);

    // Show Dashboard
    const nameInput = document.getElementById("onboard-name").value.trim() || currentUserId;
    showDashboard(nameInput);
  } catch (error) {
    console.error("Join/Personalization failed:", error);
    alert(`Setup failed: ${error.message}`);
    showCommunityAssignment();
  }
}

// Transition into dashboard view
function showDashboard(username) {
  elements.authContainer.style.display = "none";
  elements.onboardingContainer.style.display = "none";
  elements.communityAssignmentContainer.style.display = "none";
  
  elements.mainHeader.style.display = "block";
  elements.userProfileWrapper.style.display = "flex";
  if (elements.authUserName) elements.authUserName.textContent = username;
  
  if (currentRole === "member") {
    elements.mainDashboard.style.display = "block";
  } else {
    elements.organizerDashboard.style.display = "block";
  }
  document.getElementById("agent-view").style.display = "block";
}

// Handle Login submit
async function handleLoginSubmit(e) {
  e.preventDefault();
  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;

  if (!supabase) {
    alert("Supabase authentication is offline. Check backend logs.");
    return;
  }

  try {
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw error;
  } catch (error) {
    console.error("Login failed:", error);
    alert(`Login failed: ${error.message}`);
  }
}

// Handle Signup submit
async function handleSignupSubmit(e) {
  e.preventDefault();
  const email = document.getElementById("signup-email").value.trim();
  const password = document.getElementById("signup-password").value;

  if (!supabase) {
    alert("Supabase authentication is offline.");
    return;
  }

  try {
    const { error } = await supabase.auth.signUp({ email, password });
    if (error) throw error;
    
    // Switch to verification panel
    elements.signupPanel.style.display = "none";
    elements.verificationPanel.style.display = "block";
  } catch (error) {
    console.error("Signup failed:", error);
    alert(`Signup failed: ${error.message}`);
  }
}

// Handle Profile submit (onboarding)
async function handleProfileSubmit(e) {
  e.preventDefault();
  
  const name = document.getElementById("onboard-name").value.trim();
  const github = document.getElementById("onboard-github").value.trim();
  const linkedin = document.getElementById("onboard-linkedin").value.trim();
  
  if (!name || !github || !linkedin) {
    alert("Please fill out all fields for your profile.");
    return;
  }

  try {
    const { data: { user } } = await supabase.auth.getUser();
    
    const body = {
      user_id: currentUserId,
      username: name,
      email: user.email,
      bio: `GitHub Profile: ${github}. LinkedIn Profile: ${linkedin}. Authenticated account profile.`,
      tags: [github.toLowerCase().includes("cuda") ? "cuda" : "python"],
      interests: [github.toLowerCase().includes("cuda") ? "Systems Programming" : "Machine Learning"],
      goals: ["Complete personalized onboarding", "Build AI integration frameworks"],
      github_url: github,
      linkedin_url: linkedin,
      timezone: "Asia/Kolkata"
    };

    // Create user profile on backend
    const res = await fetch(`${API_BASE_URL}/users/create`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    if (!res.ok) throw new Error("Failed to create profile on backend");

    // Proceed to community selection
    showCommunityAssignment();

  } catch (error) {
    console.error("Profile creation failed:", error);
    alert(`Failed to create profile: ${error.message}`);
    showProfileCreation();
  }
}

// Handle Sign Out
async function handleSignOut() {
  if (supabase) {
    await supabase.auth.signOut();
  }
  currentUserId = null;
  currentUserProfile = null;
  showAuthScreen();
}

// Render dynamic community branding
function renderCommunityBranding() {
  if (elements.communityName) elements.communityName.textContent = communityBranding.name;
  if (elements.communityLogo) elements.communityLogo.textContent = communityBranding.logo;
  if (elements.communityDesc) elements.communityDesc.textContent = communityBranding.description;
}

// Card state renderer (supports loading, empty, success, error)
function renderCardState(element, state, message = "") {
  if (!element) return;
  if (state === "loading") {
    element.innerHTML = `
      <div class="loading-state" style="padding: 16px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; width: 100%;">
        <div class="spinner" style="border: 2px solid var(--color-chalk); border-top: 2px solid var(--color-signal-orange); border-radius: 50%; width: 20px; height: 20px; animation: spin 1s linear infinite;"></div>
        <span style="font-size: 11px; color: var(--color-slate);">Ingesting data...</span>
      </div>
    `;
  } else if (state === "error") {
    element.innerHTML = `
      <div class="error-state" style="padding: 12px; color: #ef4444; font-size: 12px; font-weight: 500; text-align: center; border: 1px dashed rgba(239, 68, 68, 0.3); border-radius: var(--radius-cards); background: rgba(239, 68, 68, 0.02); width: 100%;">
        ${message || "Telemetry error"}
      </div>
    `;
  } else if (state === "empty") {
    element.innerHTML = `
      <div class="empty-state" style="padding: 16px; color: var(--color-slate); font-size: 12px; text-align: center; border: 1px dashed var(--color-chalk); border-radius: var(--radius-cards); background: var(--color-fog); width: 100%;">
        ${message || "No data points."}
      </div>
    `;
  }
}

// Switch Member/Organizer views
function switchRole(role) {
  currentRole = role;
  
  if (role === "member") {
    elements.roleToggleMember.classList.add("active");
    elements.roleToggleOrganizer.classList.remove("active");
    
    elements.mainDashboard.style.display = "block";
    elements.organizerDashboard.style.display = "none";
    document.getElementById("agent-view").style.display = "block";
  } else {
    elements.roleToggleMember.classList.remove("active");
    elements.roleToggleOrganizer.classList.add("active");
    
    elements.mainDashboard.style.display = "none";
    elements.organizerDashboard.style.display = "block";
    document.getElementById("agent-view").style.display = "block";
    loadOrganizerData();
  }
  
  renderApp();
}

// Main Render Router
function renderApp() {
  if (currentRole === "member") {
    renderMemberDashboard();
  } else {
    renderOrganizerDashboard();
  }
  renderAgentFlow();
}

// Member Dashboard Renderer
function renderMemberDashboard() {
  const u = currentUserProfile;
  if (!u) return;
  
  // Hero section
  elements.heroHeadline.textContent = u.headline;
  elements.heroBody.textContent = u.subtext;
  
  // Hero CTA Buttons
  elements.heroPills.innerHTML = `
    <button class="btn-filled" onclick="alert('Continuing path: ${u.learning_paths[0]?.name || 'General Core'}')">Continue Path</button>
    ${u.github_url ? `
      <a href="${u.github_url}" target="_blank" class="btn-outlined">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
        GitHub Profile
      </a>
    ` : ""}
  `;

  // Render Priority list / Action items
  elements.priorityGrid.innerHTML = "";
  let prioritiesAdded = 0;
  
  if (u.learning_paths && u.learning_paths.length > 0) {
    const path = u.learning_paths[0];
    createPriorityCard("Active learning path progress", path.name, `${path.progress}% Complete`, `Next: ${path.next_milestone}`, "Identity/Learning Agents", "path-progress");
    prioritiesAdded++;
  }
  
  if (u.events && u.events.length > 0) {
    const event = u.events[0];
    createPriorityCard("High-confidence recommended event", event.title, event.time, `Compatibility Score: ${event.score}%`, "Discovery Agent", event.id);
    prioritiesAdded++;
  }
  
  if (u.recommended_people && u.recommended_people.length > 0) {
    const mentor = u.recommended_people[0];
    createPriorityCard("Top mentor match for goals", mentor.name, mentor.role, `Compatibility Score: ${mentor.match}%`, "Mentor Agent", "mentor-match");
    prioritiesAdded++;
  }

  if (prioritiesAdded === 0) {
    renderCardState(elements.priorityGrid, "empty", "No Focus Items Today.");
  }

  // Render KPI Card Metrics
  if (u.learning_paths && u.learning_paths.length > 0) {
    const path = u.learning_paths[0];
    elements.kpiPathsName.textContent = path.name;
    elements.kpiPathsProgress.textContent = `${path.progress}%`;
    const bar = document.getElementById("kpi-paths-progress-bar");
    if (bar) bar.style.width = `${path.progress}%`;
    elements.kpiPathsNext.textContent = path.next_milestone;
  } else {
    elements.kpiPathsName.textContent = "No active roadmaps";
    elements.kpiPathsProgress.textContent = "0%";
    const bar = document.getElementById("kpi-paths-progress-bar");
    if (bar) bar.style.width = "0%";
    elements.kpiPathsNext.textContent = "Complete profile to generate paths.";
  }

  // Verified Skills
  if (u.verified_skills && u.verified_skills.length > 0) {
    elements.kpiSkillsList.innerHTML = u.verified_skills.map(s => `
      <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px; border-bottom: 1px dashed var(--color-chalk); padding-bottom: 4px;">
        <span style="font-weight: 500;">${s.name}</span>
        <span style="color: var(--color-signal-orange); font-weight: 600;">Lvl ${s.level}</span>
      </div>
    `).join("");
  } else {
    renderCardState(elements.kpiSkillsList, "empty", "No verified skills on profile.");
  }

  // Stated Interests
  if (u.interests && u.interests.length > 0) {
    elements.kpiInterestsList.innerHTML = u.interests.map(i => `
      <span class="card-badge orange" style="margin-right: 6px; margin-bottom: 6px; display: inline-block;">${i}</span>
    `).join("");
  } else {
    renderCardState(elements.kpiInterestsList, "empty", "No interests configured.");
  }

  // Recommended People / Mentors
  if (u.recommended_people && u.recommended_people.length > 0) {
    elements.mentorSection.style.display = "block";
    elements.mentorList.innerHTML = u.recommended_people.map(p => createMentorCard(p)).join("");
  } else {
    renderCardState(elements.mentorList, "empty", "No mentor matches computed yet.");
  }

  // Recommended Communities (show visible, hide filtered out)
  elements.communitiesList.innerHTML = "";
  let communitiesAdded = 0;
  if (u.communities && u.communities.show) {
    u.communities.show.forEach(c => {
      const pill = document.createElement("span");
      pill.className = "community-pill";
      pill.textContent = `# ${c}`;
      pill.onclick = () => alert(`Entering channel: #${c}`);
      elements.communitiesList.appendChild(pill);
      communitiesAdded++;
    });
  }
  if (u.communities && u.communities.hide) {
    u.communities.hide.forEach(c => {
      const pill = document.createElement("span");
      pill.className = "community-pill hidden";
      pill.title = "Filtered out by Discovery Agent to reduce clutter. Click to reveal.";
      pill.textContent = `# ${c}`;
      pill.onclick = () => {
        if (confirm(`This channel was hidden by the Discovery Agent. Enter anyway?`)) {
          alert(`Entering channel: #${c}`);
        }
      };
      elements.communitiesList.appendChild(pill);
      communitiesAdded++;
    });
  }

  if (communitiesAdded === 0) {
    renderCardState(elements.communitiesList, "empty", "No recommended channels available.");
  }

  // Recommended Resources, Projects, and Events loaded from DB
  loadCommunityKnowledge();

  // Render Telemetry Widget (GitHub connect, resume upload)
  renderTelemetryWidget();

  // Insights / Notifications
  if (u.insights && u.insights.length > 0) {
    elements.insightsList.innerHTML = u.insights.map(i => `
      <div style="display: flex; align-items: center; gap: 12px; padding: 12px; background-color: var(--color-fog); border-radius: var(--radius-cards); margin-bottom: 8px; border-left: 3px solid var(--color-signal-orange);">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--color-signal-orange);"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
        <span style="font-size: 13px; font-weight: 500; color: var(--color-carbon);">${i.message}</span>
      </div>
    `).join("");
  } else {
    renderCardState(elements.insightsList, "empty", "No orchestration insights.");
  }
}

// Helper to construct priority cards
function createPriorityCard(label, title, val, footerText, agentText, decisionId) {
  const card = document.createElement("div");
  card.className = "card";
  card.innerHTML = `
    <div class="card-header-row">
      <span class="card-badge">${label}</span>
      <button class="why-btn" onclick="openExplainabilityModal('${decisionId}')">Why?</button>
    </div>
    <h3 class="card-title" style="margin-top: 8px; font-size: 18px; line-height: 1.2;">${title}</h3>
    <div class="kpi-value" style="font-size: 24px; margin: 8px 0;">${val}</div>
    <div style="margin-top: auto; display: flex; justify-content: space-between; font-size: 11px; color: var(--color-slate); border-top: 1px solid var(--color-chalk); padding-top: 8px;">
      <span>${footerText}</span>
      <span style="color: var(--color-sienna-bronze);">${agentText}</span>
    </div>
  `;
  elements.priorityGrid.appendChild(card);
}

// Helper to render mentor cards
function createMentorCard(mentor) {
  const avatar = mentor.avatar || mentor.name.substring(0, 2).toUpperCase();
  return `
    <div class="mentor-item">
      <div class="mentor-info">
        <div class="mentor-avatar">${avatar}</div>
        <div class="mentor-details">
          <span class="mentor-name">${mentor.name}</span>
          <span class="mentor-role">${mentor.role}</span>
          <p style="font-size: 12px; color: var(--color-graphite); margin-top: 4px;">${mentor.reason}</p>
        </div>
      </div>
      <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 8px;">
        <span class="mentor-score-pill"><span class="mentor-score-label">${mentor.match}%</span> match</span>
        <button class="btn-filled btn-small" onclick="alert('Connection request sent to ${mentor.name}')">Connect</button>
      </div>
    </div>
  `;
}

// Organizer Dashboard Renderer
function renderOrganizerDashboard() {
  // Loaded dynamically via loadOrganizerData()
}

// Action executor
window.approveAction = async function(actionId) {
  try {
    const response = await fetch(`${API_BASE_URL}/organizer/actions/${actionId}/complete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    if (!response.ok) throw new Error("Failed to complete organizer action");
    alert(`Action Approved! In Execution Pipeline.`);
    loadOrganizerData();
  } catch (error) {
    console.error("Failed to approve action:", error);
    alert("Error completing action.");
  }
};

// Agent Execution Timeline Flow Renderer
function renderAgentFlow() {
  const steps = [
    { name: "Identity Agent", desc: "Profile understanding & verified skills detection", timing: "0.8ms - 1.5ms" },
    { name: "Learning Agent", desc: "Learning path milestone check & active skill gaps analysis", timing: "1.5ms - 2.4ms" },
    { name: "Discovery Agent", desc: "Relevance calculations, interest matching, decay applied", timing: "2.2ms - 4.1ms" },
    { name: "Mentor Agent", desc: "Co-collaborator & teacher search matrix comparison", timing: "2.8ms - 3.8ms" }
  ];

  if (currentRole === "organizer") {
    steps.push({ name: "Organizer Agent", desc: "Aggregate overall stats & churn vector evaluations", timing: "4.5ms" });
  }

  elements.agentTimeline.innerHTML = steps.map((s, index) => `
    <div class="agent-node ${index === steps.length - 1 ? 'active' : ''}">
      <div class="agent-node-header">
        <span>${s.name}</span>
        <span style="color: var(--color-signal-orange);">${s.timing}</span>
      </div>
      <div class="agent-node-desc">${s.desc}</div>
      <div class="agent-node-meta">Inputs parsed: user_id, active_session_logs, graph_nodes_cache</div>
    </div>
  `).join("") + `
    <div style="font-size: 13px; color: #10b981; font-weight: 600; margin-top: 12px; display: flex; align-items: center; gap: 8px;">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
      Dashboard refreshed and layout orchestrated successfully.
    </div>
  `;
}

// Explainability Modal
window.openExplainabilityModal = function(decisionId) {
  const u = currentUserProfile;
  if (!u) return;

  let title = "Reasoning Details";
  let reasoning = [];
  let score = "85%";
  let agents = ["Identity", "Discovery"];
  let timings = { "Identity": "1.1ms", "Discovery": "2.3ms" };

  if (decisionId === "path-progress") {
    title = u.learning_paths[0]?.name || "Active Path";
    reasoning = [
      "Identity Agent: Verified user capability metrics.",
      "Learning Agent: Constructed milestone sequences matching current tags and skill parameters."
    ];
  } else if (decisionId === "mentor-match") {
    title = u.recommended_people[0]?.name || "Top Mentor Match";
    reasoning = [
      `Identity Agent: Read primary stated growth goals: [${(u.goals || []).join(", ")}].`,
      `Mentor Agent: Queried expert profile directories for alignment. Computed compatibility match based on availability and background.`
    ];
  } else {
    // Find matching resource/event
    const resource = (u.resources || []).find(r => r.id === decisionId);
    const event = (u.events || []).find(e => e.id === decisionId);
    const item = resource || event;
    if (item) {
      title = item.title;
      reasoning = [
        `Identity Agent: Evaluated growth areas and interests.`,
        `Discovery Agent: Ranked resource match based on relevance score of ${item.score || 85}%.`,
        `Learning Agent: Recommended to support milestone progress objectives.`
      ];
      score = `${item.score || 85}%`;
    } else {
      title = `Decision ${decisionId}`;
      reasoning = [
        "Identity Agent: Read profile criteria.",
        "Discovery Agent: Extracted relative matching topics from active streams."
      ];
    }
  }

  // Populate Modal contents
  elements.modalTitle.textContent = "Why am I seeing this?";
  
  elements.modalBody.innerHTML = `
    <div style="margin-bottom: 20px;">
      <h4 style="font-size: 16px; font-weight: 600; color: var(--color-carbon); margin-bottom: 4px;">${title}</h4>
      <p style="font-size: 13px; color: var(--color-slate);">Multiple cooperative AI agents collaborated to rank this card for your viewport.</p>
    </div>
    
    <div style="margin-bottom: 24px;">
      <label class="form-label" style="font-weight: 600;">Cooperating Agents and Execution Timings</label>
      <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px;">
        ${agents.map(agent => `
          <div style="background-color: var(--color-fog); border: 1px solid var(--color-chalk); border-radius: var(--radius-tags); padding: 4px 12px; font-size: 12px; display: flex; justify-content: space-between; width: calc(50% - 4px);">
            <strong style="color: var(--color-carbon);">${agent} Agent</strong>
            <span style="color: var(--color-sienna-bronze);">${timings[agent] || '—'}</span>
          </div>
        `).join("")}
      </div>
    </div>
    
    <div style="margin-bottom: 24px;">
      <label class="form-label" style="font-weight: 600;">Agent Reasoning Chain Details</label>
      <div class="reasoning-list">
        ${reasoning.map(step => `
          <div class="reasoning-item" style="font-size: 12px; color: var(--color-graphite); margin-bottom: 6px; padding-left: 12px; border-left: 2px solid var(--color-signal-orange);">${step}</div>
        `).join("")}
      </div>
    </div>

    <div class="confidence-gauge" style="margin-top: 16px; padding: 12px; background: var(--color-fog); border-radius: var(--radius-cards); display: flex; justify-content: space-between; align-items: center;">
      <span class="confidence-title" style="font-size: 12px; font-weight: 600; color: var(--color-carbon);">Overall Recommendation Confidence</span>
      <span class="confidence-value" style="font-size: 16px; font-weight: 700; color: var(--color-signal-orange);">${score}</span>
    </div>
  `;
  
  elements.modalOverlay.classList.add("active");
};

function closeModal() {
  elements.modalOverlay.classList.remove("active");
}

// Backend Integration Helper Functions

async function loadMemberPersonalization(userId) {
  // Show loading states
  elements.heroHeadline.textContent = "AI Orchestration Running...";
  elements.heroBody.innerHTML = `
    <div style="display: flex; flex-direction: column; gap: 8px;">
      <p>Please wait while the Agent Orchestrator runs: <strong>Identity Agent</strong> → (<strong>Discovery Agent</strong> + <strong>Learning Agent</strong>) → <strong>Mentor Agent</strong>...</p>
      <div style="width: 100%; height: 6px; background-color: var(--color-chalk); border-radius: 3px; overflow: hidden; position: relative;">
        <div style="width: 50%; height: 100%; background-color: var(--color-signal-orange); position: absolute; animation: loading-bar 2s infinite ease-in-out;"></div>
      </div>
    </div>
  `;
  elements.heroPills.innerHTML = "";
  
  renderCardState(elements.priorityGrid, "loading");
  renderCardState(elements.kpiSkillsList, "loading");
  renderCardState(elements.kpiInterestsList, "loading");
  renderCardState(elements.mentorList, "loading");
  renderCardState(elements.communitiesList, "loading");
  renderCardState(elements.resourcesList, "loading");
  renderCardState(elements.eventsList, "loading");
  renderCardState(elements.insightsList, "loading");

  if (!document.getElementById("backend-integration-styles")) {
    const style = document.createElement("style");
    style.id = "backend-integration-styles";
    style.innerHTML = `
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      @keyframes loading-bar {
        0% { left: -50%; }
        100% { left: 100%; }
      }
    `;
    document.head.appendChild(style);
  }

  try {
    const start = Date.now();
    const response = await fetch(`${API_BASE_URL}/agents/personalize/${userId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    const elapsed = Date.now() - start;
    console.log(`Backend pipeline took ${elapsed}ms:`, result);

    if (result.success && result.data) {
      const adapted = adaptBackendProfileToFrontend(result.data, userId);
      
      // Load current profile from database to enrich adapted fields
      try {
        const profileRes = await fetch(`${API_BASE_URL}/profile`);
        if (profileRes.ok) {
          const profileJson = await profileRes.json();
          Object.assign(adapted, profileJson.data);
          // Overwrite adapted name with database username
          if (profileJson.data.username) {
            adapted.name = profileJson.data.username;
            adapted.avatar = profileJson.data.username.substring(0, 2).toUpperCase();
            adapted.headline = `Welcome back, ${profileJson.data.username} 👋`;
          }
        }
      } catch (profileErr) {
        console.error("Failed to load detailed profile from DB:", profileErr);
      }
      
      currentUserProfile = adapted;
      
      elements.userProfileWrapper.style.display = "flex";
      elements.authUserName.textContent = adapted.name;
      
      renderApp();
      renderAgentFlowWithTimings(result.data);
    } else {
      throw new Error("API succeeded but returned failure payload");
    }
  } catch (error) {
    console.error("Failed to fetch personalization from backend:", error);
    elements.heroHeadline.textContent = "Telemetry Sync Error";
    elements.heroBody.textContent = "Unable to load environment recommendations. Please ensure the backend is running.";
    
    renderCardState(elements.priorityGrid, "error", "Failed to retrieve focus items.");
    renderCardState(elements.kpiSkillsList, "error", "Skills data unavailable.");
    renderCardState(elements.kpiInterestsList, "error", "Interests data unavailable.");
    renderCardState(elements.mentorList, "error", "Mentors list unavailable.");
    renderCardState(elements.communitiesList, "error", "Channels list unavailable.");
    renderCardState(elements.resourcesList, "error", "Resource recommendations unavailable.");
    renderCardState(elements.eventsList, "error", "Events calendar unavailable.");
    renderCardState(elements.insightsList, "error", "Insight logs unavailable.");
  }
}

function renderAgentFlowWithTimings(backendData) {
  const steps = [];
  const identityMs = backendData.step_timings_ms?.identity_ms || "1.2s";
  const discLearnMs = backendData.step_timings_ms?.discovery_learning_ms || "1.5s";
  const mentorMs = backendData.step_timings_ms?.mentor_ms || "1.0s";
  const totalMs = backendData.pipeline_time_ms ? `${(backendData.pipeline_time_ms / 1000).toFixed(1)}s` : "3.0s";

  steps.push({ name: "Identity Agent", desc: "Profile understanding & verified skills detection", timing: `${identityMs}ms` });
  steps.push({ name: "Discovery Agent", desc: "Relevance calculations, interest matching", timing: `${discLearnMs}ms (parallel)` });
  steps.push({ name: "Learning Agent", desc: "Learning path milestone check & active skill gaps analysis", timing: `${discLearnMs}ms (parallel)` });
  steps.push({ name: "Mentor Agent", desc: "Co-collaborator & teacher search matrix comparison", timing: `${mentorMs}ms` });

  elements.agentTimeline.innerHTML = steps.map((s, index) => `
    <div class="agent-node active">
      <div class="agent-node-header">
        <span>${s.name}</span>
        <span style="color: var(--color-signal-orange);">${s.timing}</span>
      </div>
      <div class="agent-node-desc">${s.desc}</div>
      <div class="agent-node-meta">Inputs parsed: user_id, active_session_logs, graph_nodes_cache</div>
    </div>
  `).join("") + `
    <div style="font-size: 13px; color: #10b981; font-weight: 600; margin-top: 12px; display: flex; align-items: center; gap: 8px;">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
      Dashboard refreshed in ${totalMs} (Fallback used: ${backendData.fallback_used}).
    </div>
  `;
}

async function loadOrganizerData() {
  elements.orgHealthScore.textContent = "--%";
  elements.orgActiveMembers.textContent = "---";
  elements.orgAtRiskMembers.textContent = "---";
  elements.orgNewMembers.textContent = "---";
  
  renderCardState(elements.orgTrendingTopics, "loading");
  renderCardState(elements.orgActionsList, "loading");
  renderCardState(elements.orgMentorsList, "loading");

  try {
    const response = await fetch(`${API_BASE_URL}/agents/community/health`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    if (!response.ok) throw new Error("Failed to load community health metrics");
    const result = await response.json();
    console.log("Community health report loaded:", result);

    if (result.success && result.data) {
      const data = result.data;
      const h = data.health || {};
      const a = data.actions || {};

      const score = Math.round((h.community_health_score || 0) * 100);
      elements.orgHealthScore.textContent = score ? `${score}%` : "0%";
      
      const healthDelta = document.getElementById("org-health-delta");
      if (healthDelta) {
        healthDelta.innerHTML = `<span class="kpi-delta neutral">${h.summary || 'Stable'}</span>`;
      }
      
      elements.orgActiveMembers.textContent = h.total_members || 0;
      elements.orgNewMembers.textContent = `+${h.active_members_7d || 0}`;
      
      elements.orgAtRiskMembers.textContent = `${(h.at_risk_members || []).length} members`;
      const atRiskWrapper = document.getElementById("org-at-risk-wrapper");
      if (atRiskWrapper) {
        atRiskWrapper.textContent = "At risk of churning (>30d inactivity)";
      }

      // Trending tags
      const trends = h.trending_topics || [];
      if (trends.length > 0) {
        elements.orgTrendingTopics.innerHTML = trends.map(t => `
          <span class="card-badge orange" style="margin-right: 6px; margin-bottom: 6px; display: inline-block;"># ${t}</span>
        `).join("");
      } else {
        renderCardState(elements.orgTrendingTopics, "empty", "No trending conversation topics.");
      }

      // Suggested Actions List
      const actions = a.action_items || [];
      if (actions.length > 0) {
        elements.orgActionsList.innerHTML = actions.map(item => `
          <div style="padding: 16px; background-color: var(--color-fog); border-radius: var(--radius-cards); margin-bottom: 12px; border-left: 3px solid ${item.completed ? '#10b981' : 'var(--color-signal-orange)'};">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
              <span style="font-weight: 600; font-size: 14px; color: var(--color-carbon);">${item.title}</span>
              <span class="card-badge" style="text-transform: capitalize; background-color: ${item.completed ? 'rgba(16, 185, 129, 0.1)' : 'var(--color-chalk)'}; color: ${item.completed ? '#10b981' : 'var(--color-graphite)'};">${item.completed ? 'approved' : 'suggested'}</span>
            </div>
            <p style="font-size: 12px; color: var(--color-graphite); margin: 8px 0 4px 0;"><strong>Reason:</strong> ${item.description}</p>
            <p style="font-size: 12px; color: var(--color-sienna-bronze); margin-bottom: 8px;"><strong>Impact Projection:</strong> ${item.expected_impact || 'Improves member retention.'}</p>
            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px dashed var(--color-chalk); padding-top: 8px; margin-top: 4px;">
              <span style="font-size: 11px; color: var(--color-slate);">Assignee suggestion: <strong>${item.assignee || 'Organizer'}</strong></span>
              ${!item.completed ? `
                <button class="btn-filled btn-small" onclick="approveAction('${item.action_id}')">Approve & Execute</button>
              ` : `
                <span style="font-size: 12px; color: #10b981; font-weight: 500;">✓ In Execution Pipeline</span>
              `}
            </div>
          </div>
        `).join("");
      } else {
        renderCardState(elements.orgActionsList, "empty", "No pending actions recommended.");
      }

      // Expert Mentors Pool
      renderCardState(elements.orgMentorsList, "empty", "No active mentors registered in community directory.");
    }
  } catch (error) {
    console.error("Failed to load organizer data from backend:", error);
    elements.orgHealthScore.textContent = "Error";
    elements.orgActiveMembers.textContent = "Error";
    elements.orgAtRiskMembers.textContent = "Error";
    renderCardState(elements.orgTrendingTopics, "error", "Failed to load community health metrics.");
    renderCardState(elements.orgActionsList, "error", "Failed to load recommended actions.");
    renderCardState(elements.orgMentorsList, "error", "Failed to load expert mentors directory.");
  }
}

function adaptBackendProfileToFrontend(backendProfile, user_id) {
  const identity = backendProfile.identity || {};
  const discovery = backendProfile.discovery || {};
  const learning = backendProfile.learning || {};
  const mentor = backendProfile.mentor || {};

  const levelMap = { "Beginner": 2, "Intermediate": 3, "Advanced": 4, "Expert": 5 };
  const verified_skills = (identity.detected_skills || []).map(s => ({
    name: s.name,
    level: levelMap[s.proficiency] || 3
  }));

  const roadmapName = learning.roadmap_title || "Custom Pathway";
  const milestones = learning.milestones || [];
  const nextMilestone = milestones[0] ? `Week ${milestones[0].week}: ${milestones[0].title}` : "Milestone 1: Getting Started";
  const learning_paths = [
    {
      name: roadmapName,
      progress: 25,
      completed: 1,
      total: milestones.length || 4,
      next_milestone: nextMilestone
    }
  ];

  const recommended_people = [];
  if (mentor.primary_mentor) {
    const pm = mentor.primary_mentor;
    recommended_people.push({
      name: pm.name,
      role: pm.role || "Expert Mentor",
      match: Math.round((pm.compatibility_score || 0.9) * 100),
      avatar: pm.avatar || pm.name.substring(0, 2).toUpperCase(),
      reason: pm.match_reason || "Aligned with your learning goals."
    });
  }
  (mentor.backup_mentors || []).forEach(bm => {
    recommended_people.push({
      name: bm.name,
      role: bm.role || "Backup Mentor",
      match: Math.round((bm.compatibility_score || 0.8) * 100),
      avatar: bm.avatar || bm.name.substring(0, 2).toUpperCase(),
      reason: bm.match_reason || "Expert in overlapping interests."
    });
  });

  const showChannels = (discovery.recommended_channels || []).map(ch => ch.name);
  const allChannels = ["Systems Programming", "GPU & Accelerators", "AI Infrastructure", "Machine Learning", "Data Science & Python", "Frontend Development", "Design Systems & UI UX", "Web3 & Blockchain", "Mobile Design", "React Frameworks", "Open Source Contribution"];
  const hideChannels = allChannels.filter(c => !showChannels.includes(c));

  const resources = (discovery.recommended_resources || []).map(r => ({
    id: r.resource_id || `res-${Math.random().toString(36).substr(2, 9)}`,
    title: r.title,
    type: r.type || "Article",
    duration: r.duration || "20 min",
    difficulty: r.difficulty || "Intermediate",
    score: Math.round((r.relevance_score || 0.85) * 100),
    reasoning: r.reason || "Highly relevant resource for your active milestone."
  }));

  const primaryChannel = showChannels[0] || "General";
  const events = [
    {
      id: `evt-1`,
      title: `${primaryChannel} Deep Dive Session`,
      time: "Tonight, 7:00 PM (1h 30m)",
      type: "Workshop",
      difficulty: "Intermediate",
      score: 95,
      reasoning: `Highly relevant for your ${roadmapName} goals. Led by community mentors.`
    },
    {
      id: `evt-2`,
      title: "Rust FFI & Python Interop Panel",
      time: "Tomorrow, 5:30 PM (1h)",
      type: "AMA",
      difficulty: "Advanced",
      score: 82,
      reasoning: "Great complement to low level programming and MLOps paths."
    }
  ];

  const insights = [
    { message: identity.summary || "Your custom learning environment is now fully active.", type: "momentum" }
  ];
  if (mentor.primary_mentor) {
    insights.push({ message: `${mentor.primary_mentor.name} is available for scheduling sessions.`, type: "match" });
  }

  const formattedName = backendProfile.username || user_id.charAt(0).toUpperCase() + user_id.slice(1);

  return {
    id: user_id,
    name: formattedName,
    avatar: formattedName.substring(0, 2).toUpperCase(),
    role: "member",
    skill_level: identity.growth_areas ? "Intermediate" : "Beginner",
    headline: `Welcome back, ${formattedName} 👋`,
    subtext: identity.summary || "Your personalized path is active.",
    verified_skills: verified_skills,
    goals: identity.growth_areas || [],
    learning_paths: learning_paths,
    interests: identity.expertise_areas || [],
    recommended_people: recommended_people,
    communities: {
      show: showChannels,
      hide: hideChannels.slice(0, 4)
    },
    resources: resources,
    events: events,
    insights: insights
  };
}

// ─── Sprint 2 Community Knowledge & Telemetry Ingestion ──────────────────────

async function loadCommunityKnowledge() {
  try {
    // 1. Fetch Resources
    const resResponse = await fetch(`${API_BASE_URL}/resources`);
    if (resResponse.ok) {
      const resJson = await resResponse.json();
      renderResources(resJson.data.resources);
    } else {
      renderCardState(elements.resourcesList, "error", "Failed to load resources");
    }

    // 2. Fetch Projects
    const projResponse = await fetch(`${API_BASE_URL}/projects`);
    if (projResponse.ok) {
      const projJson = await projResponse.json();
      renderProjects(projJson.data.projects);
    } else {
      renderCardState(document.getElementById("projects-list"), "error", "Failed to load projects");
    }

    // 3. Fetch Events
    const evtResponse = await fetch(`${API_BASE_URL}/events`);
    if (evtResponse.ok) {
      const evtJson = await evtResponse.json();
      renderEvents(evtJson.data.events);
    } else {
      renderCardState(elements.eventsList, "error", "Failed to load events");
    }
  } catch (error) {
    console.error("Error loading community knowledge:", error);
  }
}

function renderResources(resources) {
  if (!resources || resources.length === 0) {
    renderCardState(elements.resourcesList, "empty", "No resources available for this community.");
    return;
  }
  elements.resourcesList.innerHTML = resources.map(r => `
    <div class="card">
      <div class="card-header-row">
        <div>
          <span class="card-badge">${r.type || 'Resource'}</span>
        </div>
        <button class="why-btn" onclick="openExplainabilityModal('${r.resource_id}')">Why?</button>
      </div>
      <h3 class="card-title" style="margin-top: 6px; font-size: 15px;">${r.title}</h3>
      <p style="font-size: 12px; color: var(--color-slate); margin-top: 4px;">Est: ${r.duration || '20 min'} • Difficulty: ${r.difficulty || 'Intermediate'}</p>
      <div style="margin-top: auto; padding-top: 16px; display: flex; justify-content: space-between; align-items: center;">
        <p style="font-size: 11px; color: var(--color-graphite); max-width: 70%; line-height: 1.2;">${r.reason || 'Highly recommended for your path.'}</p>
        <button class="btn-filled btn-small" onclick="alert('Opening resource: ${r.title}')">Open</button>
      </div>
    </div>
  `).map((h, i) => h).join(""); // standard conversion
}

function renderProjects(projects) {
  const container = document.getElementById("projects-list");
  if (!container) return;
  if (!projects || projects.length === 0) {
    renderCardState(container, "empty", "No community projects active.");
    return;
  }
  container.innerHTML = projects.map(p => `
    <div class="card">
      <div class="card-header-row">
        <span class="card-badge">Project</span>
      </div>
      <h3 class="card-title" style="margin-top: 6px; font-size: 15px;">${p.title}</h3>
      <p style="font-size: 12px; color: var(--color-graphite); margin-top: 6px; line-height: 1.4;">${p.description}</p>
      <div style="margin-top: auto; padding-top: 16px; display: flex; justify-content: flex-end;">
        <button class="btn-filled btn-small" onclick="alert('Viewing code repository for: ${p.title}')">View Project</button>
      </div>
    </div>
  `).join("");
}

function renderEvents(events) {
  if (!events || events.length === 0) {
    renderCardState(elements.eventsList, "empty", "No upcoming events scheduled.");
    return;
  }
  elements.eventsList.innerHTML = events.map(e => `
    <div class="event-row" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid var(--color-chalk);">
      <div class="event-info" style="display: flex; flex-direction: column; gap: 4px; text-align: left;">
        <span class="event-title" style="font-weight: 600; font-size: 14px; color: var(--color-carbon);">${e.title}</span>
        <span class="event-time" style="font-size: 12px; color: var(--color-slate);">${e.time}</span>
      </div>
      <div style="display: flex; gap: 8px;">
        <button class="why-btn" style="padding: 4px 10px;" onclick="openExplainabilityModal('${e.event_id}')">Why?</button>
        <button class="btn-filled btn-small" onclick="alert('Registered successfully for ${e.title}')">Register</button>
      </div>
    </div>
  `).join("");
}

function renderTelemetryWidget() {
  const container = document.getElementById("hero-right-container");
  if (!container || !currentUserProfile) return;

  const githubUser = currentUserProfile.github_username || "";
  const resumeName = currentUserProfile.resume_name || "";

  container.innerHTML = `
    <div class="card" style="padding: 24px; border: 1px dashed var(--color-slate); border-radius: var(--radius-cards); height: 100%; display: flex; flex-direction: column; text-align: left; background-color: transparent; width: 100%;">
      <h4 style="font-size: 15px; font-weight: 600; color: var(--color-carbon); margin: 0 0 12px 0; display: flex; align-items: center; gap: 8px;">
        <span>📊</span> Identity Telemetry Ingestion
      </h4>
      <div style="display: flex; flex-direction: column; gap: 12px; font-size: 12px; flex-grow: 1;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--color-chalk); padding-bottom: 8px;">
          <span>GitHub Connection:</span>
          <span id="tel-github-status" style="font-weight: 600; color: ${githubUser ? 'var(--color-signal-orange)' : 'var(--color-slate)'};">${githubUser || 'Not connected'}</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--color-chalk); padding-bottom: 8px;">
          <span>Resume Ingest:</span>
          <span id="tel-resume-status" style="font-weight: 600; color: ${resumeName ? 'var(--color-signal-orange)' : 'var(--color-slate)'};">${resumeName || 'Not uploaded'}</span>
        </div>
        
        <div style="margin-top: auto; display: flex; flex-direction: column; gap: 8px;">
          <div id="quick-github-connect" style="display: flex; gap: 8px;">
            <input type="text" id="quick-github-username" class="form-input" style="padding: 4px 8px; font-size: 11px; height: 26px; flex-grow: 1;" placeholder="GitHub User" value="${githubUser}">
            <button id="btn-quick-github" class="btn-filled" style="padding: 4px 10px; font-size: 11px; height: 26px; border-radius: 4px; cursor: pointer; white-space: nowrap;">${githubUser ? 'Reconnect' : 'Connect'}</button>
          </div>
          
          <div id="quick-resume-upload">
            <label for="resume-file-input" class="btn-outlined" style="display: block; text-align: center; padding: 4px 8px; font-size: 11px; cursor: pointer; border-radius: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
              ${resumeName ? '📄 Replace Resume' : '📄 Upload Resume (PDF/TXT)'}
            </label>
            <input type="file" id="resume-file-input" style="display: none;" accept=".pdf,.txt">
          </div>
          
          <button id="btn-open-profile-edit" class="btn-outlined" style="margin-top: 4px; padding: 6px; font-size: 11px; width: 100%; border-radius: 4px;">⚙️ Edit Detailed Profile</button>
        </div>
      </div>
    </div>
  `;

  // Bind quick connect github
  const connectBtn = document.getElementById("btn-quick-github");
  connectBtn.onclick = async () => {
    const usernameInput = document.getElementById("quick-github-username").value.trim();
    if (!usernameInput) {
      alert("Please enter a GitHub username");
      return;
    }
    connectBtn.textContent = "Connecting...";
    try {
      const response = await fetch(`${API_BASE_URL}/profile`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ github_username: usernameInput })
      });
      if (!response.ok) throw new Error("Failed to connect GitHub");
      alert("GitHub profile connected successfully! Enriching profile...");
      await loadMemberPersonalization(currentUserId);
    } catch (e) {
      alert(`Error connecting GitHub: ${e.message}`);
      connectBtn.textContent = githubUser ? 'Reconnect' : 'Connect';
    }
  };

  // Bind file upload
  const fileInput = document.getElementById("resume-file-input");
  fileInput.onchange = async () => {
    if (fileInput.files.length === 0) return;
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    const label = document.querySelector("label[for='resume-file-input']");
    label.textContent = "Parsing Resume...";

    try {
      const response = await fetch(`${API_BASE_URL}/resume`, {
        method: "POST",
        body: formData
      });
      if (!response.ok) throw new Error("Failed to upload resume");
      alert("Resume uploaded and processed successfully! Identity Agent updated your profile.");
      await loadMemberPersonalization(currentUserId);
    } catch (e) {
      alert(`Error uploading resume: ${e.message}`);
      label.textContent = resumeName ? '📄 Replace Resume' : '📄 Upload Resume (PDF/TXT)';
    }
  };

  // Bind open modal
  document.getElementById("btn-open-profile-edit").onclick = openProfileEditModal;
}

function openProfileEditModal() {
  const u = currentUserProfile;
  if (!u) return;

  // Pre-populate fields
  document.getElementById("edit-bio").value = u.bio || "";
  document.getElementById("edit-experience-level").value = u.experience_level || "Intermediate";
  document.getElementById("edit-availability").value = u.availability || "";
  document.getElementById("edit-github-username").value = u.github_username || "";
  document.getElementById("edit-portfolio-url").value = u.portfolio_url || "";
  document.getElementById("edit-career-goals").value = (u.career_goals || []).join(", ");
  document.getElementById("edit-preferred-tech").value = (u.preferred_technologies || []).join(", ");
  document.getElementById("edit-preferred-domains").value = (u.preferred_domains || []).join(", ");
  document.getElementById("edit-learning-pref").value = (u.learning_preferences || []).join(", ");

  const overlay = document.getElementById("profile-modal-overlay");
  overlay.classList.add("active");
}

function closeProfileEditModal() {
  const overlay = document.getElementById("profile-modal-overlay");
  overlay.classList.remove("active");
}

async function handleProfileEditSubmit(e) {
  e.preventDefault();
  
  const payload = {
    bio: document.getElementById("edit-bio").value.trim(),
    experience_level: document.getElementById("edit-experience-level").value,
    availability: document.getElementById("edit-availability").value.trim(),
    github_username: document.getElementById("edit-github-username").value.trim(),
    portfolio_url: document.getElementById("edit-portfolio-url").value.trim(),
    career_goals: document.getElementById("edit-career-goals").value.split(",").map(s => s.trim()).filter(Boolean),
    preferred_technologies: document.getElementById("edit-preferred-tech").value.split(",").map(s => s.trim()).filter(Boolean),
    preferred_domains: document.getElementById("edit-preferred-domains").value.split(",").map(s => s.trim()).filter(Boolean),
    learning_preferences: document.getElementById("edit-learning-pref").value.split(",").map(s => s.trim()).filter(Boolean)
  };

  try {
    const res = await fetch(`${API_BASE_URL}/profile`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error("Failed to update profile");
    
    closeProfileEditModal();
    alert("Profile saved successfully! Re-running personalization...");
    await loadMemberPersonalization(currentUserId);
  } catch (error) {
    alert(`Failed to save profile: ${error.message}`);
  }
}

